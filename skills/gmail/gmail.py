#!/usr/bin/env python3
"""
Gmail API wrapper using service account with domain-wide delegation.
Supports reading emails and creating drafts.
"""
import os
import sys
import json
import argparse
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes required for Gmail API
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose'
]

# Path to service account key (relative to project root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
SERVICE_ACCOUNT_FILE = os.path.join(PROJECT_ROOT, 'user', 'gmail-service-account-key.json')


def get_gmail_service(user_email):
    """Get Gmail API service for a specific user using service account delegation."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Service account key file not found: {SERVICE_ACCOUNT_FILE}\n"
            "Please ensure the JSON key file is located at user/gmail-service-account-key.json"
        )
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    delegated_credentials = credentials.with_subject(user_email)
    return build('gmail', 'v1', credentials=delegated_credentials)


def list_messages(user_email, query=None, max_results=10):
    """
    List messages for a user.
    
    Args:
        user_email: Email address to impersonate
        query: Gmail search query (e.g., "from:example@domain.com", "subject:test")
        max_results: Maximum number of results to return
    
    Returns:
        List of message summaries with id, threadId, snippet
    """
    try:
        service = get_gmail_service(user_email)
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        if not messages:
            return []
        
        # Get full message details
        message_list = []
        for msg in messages:
            message = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            
            headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
            
            message_list.append({
                'id': message['id'],
                'threadId': message['threadId'],
                'snippet': message.get('snippet', ''),
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', ''),
                'internalDate': message.get('internalDate', '')
            })
        
        return message_list
    
    except HttpError as error:
        raise Exception(f"Gmail API error listing messages: {error.resp.status} - {error.content.decode()}")
    except Exception as e:
        raise Exception(f"Error listing messages: {str(e)}")


def get_message(user_email, message_id):
    """
    Get full message content.
    
    Args:
        user_email: Email address to impersonate
        message_id: Gmail message ID
    
    Returns:
        Full message object with body, headers, attachments info
    """
    try:
        service = get_gmail_service(user_email)
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        # Extract headers
        headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
        
        # Extract body text
        body_text = ''
        payload = message.get('payload', {})
        
        if payload.get('body', {}).get('data'):
            body_text = base64.urlsafe_b64decode(
                payload['body']['data']
            ).decode('utf-8', errors='ignore')
        elif 'parts' in payload:
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                    body_text = base64.urlsafe_b64decode(
                        part['body']['data']
                    ).decode('utf-8', errors='ignore')
                    break
                elif part.get('mimeType') == 'text/html' and part.get('body', {}).get('data'):
                    # Fallback to HTML if plain text not available
                    if not body_text:
                        body_text = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
        
        result = {
            'id': message['id'],
            'threadId': message['threadId'],
            'snippet': message.get('snippet', ''),
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'cc': headers.get('Cc', ''),
            'bcc': headers.get('Bcc', ''),
            'subject': headers.get('Subject', ''),
            'date': headers.get('Date', ''),
            'internalDate': message.get('internalDate', ''),
            'body': body_text,
            'labels': message.get('labelIds', [])
        }
        
        return result
    
    except HttpError as error:
        raise Exception(f"Gmail API error getting message: {error.resp.status} - {error.content.decode()}")
    except Exception as e:
        raise Exception(f"Error getting message: {str(e)}")


def create_draft(user_email, to, subject, body):
    """
    Create a draft email.
    
    Args:
        user_email: Email address to impersonate
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
    
    Returns:
        Draft object with id and message
    """
    try:
        service = get_gmail_service(user_email)
        
        # Create message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Create draft
        draft = service.users().drafts().create(
            userId='me',
            body={
                'message': {
                    'raw': raw_message
                }
            }
        ).execute()
        
        return {
            'id': draft['id'],
            'message': {
                'id': draft['message']['id'],
                'threadId': draft['message'].get('threadId', ''),
                'to': to,
                'subject': subject
            }
        }
    
    except HttpError as error:
        raise Exception(f"Gmail API error creating draft: {error.resp.status} - {error.content.decode()}")
    except Exception as e:
        raise Exception(f"Error creating draft: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description='Gmail API wrapper using service account')
    parser.add_argument('--user', required=True, help='User email to impersonate (e.g., user@example.com)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List messages command
    list_parser = subparsers.add_parser('list', help='List messages')
    list_parser.add_argument('--query', help='Gmail search query (e.g., "from:example@domain.com")')
    list_parser.add_argument('--max-results', type=int, default=10, help='Maximum number of results (default: 10)')
    
    # Get message command
    get_parser = subparsers.add_parser('get', help='Get full message content')
    get_parser.add_argument('--message-id', required=True, help='Gmail message ID')
    
    # Create draft command
    draft_parser = subparsers.add_parser('draft', help='Create a draft email')
    draft_parser.add_argument('--to', required=True, help='Recipient email address')
    draft_parser.add_argument('--subject', required=True, help='Email subject')
    draft_parser.add_argument('--body', required=True, help='Email body (plain text)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'list':
            result = list_messages(args.user, args.query, args.max_results)
            print(json.dumps(result, indent=2))
        
        elif args.command == 'get':
            result = get_message(args.user, args.message_id)
            print(json.dumps(result, indent=2))
        
        elif args.command == 'draft':
            result = create_draft(args.user, args.to, args.subject, args.body)
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(json.dumps({'error': str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

