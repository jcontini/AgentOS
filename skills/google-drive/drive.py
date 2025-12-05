#!/usr/bin/env python3
"""
Google Drive API wrapper using service account with domain-wide delegation.
Supports listing, searching, and reading files (including Google Docs as Markdown).
"""
import os
import sys
import json
import argparse
import io
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_drive_service, get_docs_service

# MIME types for Google Workspace documents
GOOGLE_DOC_MIME = 'application/vnd.google-apps.document'
GOOGLE_SHEET_MIME = 'application/vnd.google-apps.spreadsheet'
GOOGLE_SLIDE_MIME = 'application/vnd.google-apps.presentation'
GOOGLE_FOLDER_MIME = 'application/vnd.google-apps.folder'

# Export formats for Google Workspace documents
EXPORT_FORMATS = {
    GOOGLE_DOC_MIME: 'text/plain',  # Google Docs -> plain text (cleanest for AI)
    GOOGLE_SHEET_MIME: 'text/csv',   # Google Sheets -> CSV
    GOOGLE_SLIDE_MIME: 'text/plain', # Google Slides -> plain text
}


def list_files(user_email, folder_id=None, max_results=20, page_token=None):
    """
    List files in Drive or a specific folder.
    
    Args:
        user_email: Email address to impersonate
        folder_id: Optional folder ID to list contents of (None = root/all)
        max_results: Maximum number of results to return
        page_token: Token for pagination
    
    Returns:
        Dict with files list and nextPageToken (if more results exist)
    """
    try:
        service = get_drive_service(user_email)
        
        # Build query
        query_parts = ["trashed = false"]
        if folder_id:
            query_parts.append(f"'{folder_id}' in parents")
        query = " and ".join(query_parts)
        
        results = service.files().list(
            q=query,
            pageSize=max_results,
            pageToken=page_token,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime, size, parents, webViewLink)",
            orderBy="modifiedTime desc"
        ).execute()
        
        files = results.get('files', [])
        return {
            'files': [{
                'id': f['id'],
                'name': f['name'],
                'mimeType': f['mimeType'],
                'modifiedTime': f.get('modifiedTime', ''),
                'size': f.get('size', ''),  # Not available for Google Docs
                'isFolder': f['mimeType'] == GOOGLE_FOLDER_MIME,
                'isGoogleDoc': f['mimeType'] == GOOGLE_DOC_MIME,
                'webViewLink': f.get('webViewLink', '')
            } for f in files],
            'nextPageToken': results.get('nextPageToken')
        }
    
    except HttpError as error:
        raise Exception(f"Drive API error listing files: {error.resp.status} - {error.content.decode()}")
    except Exception as e:
        raise Exception(f"Error listing files: {str(e)}")


def search_files(user_email, query_text, file_type=None, max_results=20):
    """
    Search for files by name or content.
    
    Args:
        user_email: Email address to impersonate
        query_text: Text to search for in file names
        file_type: Optional filter: 'doc', 'sheet', 'slide', 'folder', 'pdf', or MIME type
        max_results: Maximum number of results to return
    
    Returns:
        Dict with matching files
    """
    try:
        service = get_drive_service(user_email)
        
        # Build query
        query_parts = ["trashed = false"]
        
        # Name search (contains)
        if query_text:
            # Escape single quotes in search text
            escaped_text = query_text.replace("'", "\\'")
            query_parts.append(f"name contains '{escaped_text}'")
        
        # File type filter
        type_map = {
            'doc': GOOGLE_DOC_MIME,
            'document': GOOGLE_DOC_MIME,
            'sheet': GOOGLE_SHEET_MIME,
            'spreadsheet': GOOGLE_SHEET_MIME,
            'slide': GOOGLE_SLIDE_MIME,
            'presentation': GOOGLE_SLIDE_MIME,
            'folder': GOOGLE_FOLDER_MIME,
            'pdf': 'application/pdf',
        }
        if file_type:
            mime_type = type_map.get(file_type.lower(), file_type)
            query_parts.append(f"mimeType = '{mime_type}'")
        
        query = " and ".join(query_parts)
        
        results = service.files().list(
            q=query,
            pageSize=max_results,
            fields="files(id, name, mimeType, modifiedTime, size, webViewLink)",
            orderBy="modifiedTime desc"
        ).execute()
        
        files = results.get('files', [])
        return {
            'query': query_text,
            'fileType': file_type,
            'files': [{
                'id': f['id'],
                'name': f['name'],
                'mimeType': f['mimeType'],
                'modifiedTime': f.get('modifiedTime', ''),
                'size': f.get('size', ''),
                'isFolder': f['mimeType'] == GOOGLE_FOLDER_MIME,
                'isGoogleDoc': f['mimeType'] == GOOGLE_DOC_MIME,
                'webViewLink': f.get('webViewLink', '')
            } for f in files]
        }
    
    except HttpError as error:
        raise Exception(f"Drive API error searching files: {error.resp.status} - {error.content.decode()}")
    except Exception as e:
        raise Exception(f"Error searching files: {str(e)}")


def get_file_metadata(user_email, file_id):
    """
    Get detailed metadata for a file.
    
    Args:
        user_email: Email address to impersonate
        file_id: Drive file ID
    
    Returns:
        File metadata dict
    """
    try:
        service = get_drive_service(user_email)
        
        file = service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, modifiedTime, createdTime, size, parents, webViewLink, description, owners"
        ).execute()
        
        return {
            'id': file['id'],
            'name': file['name'],
            'mimeType': file['mimeType'],
            'modifiedTime': file.get('modifiedTime', ''),
            'createdTime': file.get('createdTime', ''),
            'size': file.get('size', ''),
            'isFolder': file['mimeType'] == GOOGLE_FOLDER_MIME,
            'isGoogleDoc': file['mimeType'] == GOOGLE_DOC_MIME,
            'webViewLink': file.get('webViewLink', ''),
            'description': file.get('description', ''),
            'owners': [o.get('emailAddress', '') for o in file.get('owners', [])]
        }
    
    except HttpError as error:
        raise Exception(f"Drive API error getting metadata: {error.resp.status} - {error.content.decode()}")
    except Exception as e:
        raise Exception(f"Error getting metadata: {str(e)}")


def read_file(user_email, file_id, max_chars=None, offset_chars=0):
    """
    Read file content. For Google Docs, exports as plain text.
    
    Args:
        user_email: Email address to impersonate
        file_id: Drive file ID
        max_chars: Maximum characters to return (None = all). Useful for large files.
        offset_chars: Character offset to start reading from (default 0)
    
    Returns:
        Dict with file metadata and content
    """
    try:
        service = get_drive_service(user_email)
        
        # First get file metadata
        file = service.files().get(
            fileId=file_id,
            fields="id, name, mimeType, size"
        ).execute()
        
        mime_type = file['mimeType']
        content = ''
        
        # Handle Google Workspace documents (need export)
        if mime_type in EXPORT_FORMATS:
            export_mime = EXPORT_FORMATS[mime_type]
            request = service.files().export_media(fileId=file_id, mimeType=export_mime)
            
            # Download to memory
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            content = fh.read().decode('utf-8', errors='ignore')
        
        # Handle regular files (binary download)
        elif mime_type.startswith('text/') or mime_type in ['application/json', 'application/xml']:
            request = service.files().get_media(fileId=file_id)
            
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            content = fh.read().decode('utf-8', errors='ignore')
        
        else:
            # For binary files, just return metadata
            return {
                'id': file['id'],
                'name': file['name'],
                'mimeType': mime_type,
                'size': file.get('size', ''),
                'content': None,
                'error': f"Binary file type '{mime_type}' - content not readable as text. Use download instead."
            }
        
        # Apply offset and limit
        total_chars = len(content)
        if offset_chars > 0:
            content = content[offset_chars:]
        if max_chars is not None and len(content) > max_chars:
            content = content[:max_chars]
            truncated = True
        else:
            truncated = False
        
        return {
            'id': file['id'],
            'name': file['name'],
            'mimeType': mime_type,
            'totalChars': total_chars,
            'offsetChars': offset_chars,
            'returnedChars': len(content),
            'truncated': truncated,
            'content': content
        }
    
    except HttpError as error:
        raise Exception(f"Drive API error reading file: {error.resp.status} - {error.content.decode()}")
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")


def read_google_doc(user_email, file_id, max_chars=None, start_index=0):
    """
    Read a Google Doc using the Docs API (more efficient for large docs).
    
    Unlike read_file() which exports the entire document first, this uses the
    Docs API to get structured content and can efficiently read portions of
    very large documents.
    
    Args:
        user_email: Email address to impersonate
        file_id: Google Doc file ID
        max_chars: Maximum characters to return (None = all)
        start_index: Character index to start reading from (0-based)
    
    Returns:
        Dict with document content and metadata
    """
    try:
        docs_service = get_docs_service(user_email)
        drive_service = get_drive_service(user_email)
        
        # Get document from Docs API
        doc = docs_service.documents().get(documentId=file_id).execute()
        
        # Get file metadata from Drive for additional info
        file_meta = drive_service.files().get(
            fileId=file_id,
            fields="id, name, modifiedTime, webViewLink"
        ).execute()
        
        # Extract text content from document body
        content_parts = []
        
        def extract_text(elements):
            """Recursively extract text from document elements."""
            text = ''
            for element in elements:
                if 'paragraph' in element:
                    for elem in element['paragraph'].get('elements', []):
                        if 'textRun' in elem:
                            text += elem['textRun'].get('content', '')
                elif 'table' in element:
                    for row in element['table'].get('tableRows', []):
                        for cell in row.get('tableCells', []):
                            text += extract_text(cell.get('content', []))
                elif 'tableOfContents' in element:
                    text += extract_text(element['tableOfContents'].get('content', []))
            return text
        
        body = doc.get('body', {})
        full_text = extract_text(body.get('content', []))
        
        # Apply start_index and max_chars
        total_chars = len(full_text)
        
        if start_index > 0:
            full_text = full_text[start_index:]
        
        if max_chars is not None and len(full_text) > max_chars:
            content = full_text[:max_chars]
            truncated = True
        else:
            content = full_text
            truncated = False
        
        return {
            'id': file_id,
            'name': doc.get('title', file_meta.get('name', '')),
            'mimeType': GOOGLE_DOC_MIME,
            'modifiedTime': file_meta.get('modifiedTime', ''),
            'webViewLink': file_meta.get('webViewLink', ''),
            'totalChars': total_chars,
            'startIndex': start_index,
            'returnedChars': len(content),
            'truncated': truncated,
            'content': content
        }
    
    except HttpError as error:
        raise Exception(f"Docs API error reading document: {error.resp.status} - {error.content.decode()}")
    except Exception as e:
        raise Exception(f"Error reading document: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Google Drive API wrapper using service account')
    parser.add_argument('--user', required=True, help='User email to impersonate (e.g., user@example.com)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List files command
    list_parser = subparsers.add_parser('list', help='List files')
    list_parser.add_argument('--folder-id', help='Folder ID to list contents of (omit for all files)')
    list_parser.add_argument('--max-results', type=int, default=20, help='Maximum number of results (default: 20)')
    list_parser.add_argument('--page-token', help='Page token for pagination')
    
    # Search files command
    search_parser = subparsers.add_parser('search', help='Search for files')
    search_parser.add_argument('--query', required=True, help='Search query (file name)')
    search_parser.add_argument('--type', dest='file_type', help='File type filter: doc, sheet, slide, folder, pdf')
    search_parser.add_argument('--max-results', type=int, default=20, help='Maximum number of results (default: 20)')
    
    # Get metadata command
    meta_parser = subparsers.add_parser('metadata', help='Get file metadata')
    meta_parser.add_argument('--file-id', required=True, help='Drive file ID')
    
    # Read file command (uses Drive export - downloads entire file)
    read_parser = subparsers.add_parser('read', help='Read file content (downloads entire file first)')
    read_parser.add_argument('--file-id', required=True, help='Drive file ID')
    read_parser.add_argument('--max-chars', type=int, help='Maximum characters to return (for large files)')
    read_parser.add_argument('--offset', type=int, default=0, help='Character offset to start reading from')
    
    # Read Google Doc command (uses Docs API - efficient for large docs)
    readdoc_parser = subparsers.add_parser('read-doc', help='Read Google Doc (efficient for large docs, uses Docs API)')
    readdoc_parser.add_argument('--file-id', required=True, help='Google Doc file ID')
    readdoc_parser.add_argument('--max-chars', type=int, help='Maximum characters to return')
    readdoc_parser.add_argument('--start', type=int, default=0, help='Character index to start reading from')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'list':
            result = list_files(args.user, args.folder_id, args.max_results, args.page_token)
            print(json.dumps(result, indent=2))
        
        elif args.command == 'search':
            result = search_files(args.user, args.query, args.file_type, args.max_results)
            print(json.dumps(result, indent=2))
        
        elif args.command == 'metadata':
            result = get_file_metadata(args.user, args.file_id)
            print(json.dumps(result, indent=2))
        
        elif args.command == 'read':
            result = read_file(args.user, args.file_id, args.max_chars, args.offset)
            print(json.dumps(result, indent=2))
        
        elif args.command == 'read-doc':
            result = read_google_doc(args.user, args.file_id, args.max_chars, args.start)
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(json.dumps({'error': str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

