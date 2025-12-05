#!/usr/bin/env python3
"""
Shared Google Workspace authentication module.
Uses service account with domain-wide delegation for Gmail and Drive APIs.
"""
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to service account key (relative to project root)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
SERVICE_ACCOUNT_FILE = os.path.join(PROJECT_ROOT, 'user', 'skills-data', 'google-workspace', 'service-account-key.json')

# All scopes used by Google Workspace skills
GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose'
]

DRIVE_SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly'
]

DOCS_SCOPES = [
    'https://www.googleapis.com/auth/documents.readonly'
]

ALL_SCOPES = GMAIL_SCOPES + DRIVE_SCOPES + DOCS_SCOPES


def get_credentials(user_email, scopes=None):
    """
    Get delegated credentials for a specific user.
    
    Args:
        user_email: Email address to impersonate (must be in your Google Workspace domain)
        scopes: List of OAuth scopes (defaults to ALL_SCOPES)
    
    Returns:
        Delegated credentials for the specified user
    
    Raises:
        FileNotFoundError: If service account key file is not found
    """
    if scopes is None:
        scopes = ALL_SCOPES
    
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Service account key file not found: {SERVICE_ACCOUNT_FILE}\n"
            "Please ensure the JSON key file is located at user/skills-data/google-workspace/service-account-key.json\n"
            "See skills/google-workspace/README.md for setup instructions."
        )
    
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scopes)
    return credentials.with_subject(user_email)


def get_gmail_service(user_email):
    """
    Get Gmail API service for a specific user.
    
    Args:
        user_email: Email address to impersonate
    
    Returns:
        Gmail API service object
    """
    credentials = get_credentials(user_email, GMAIL_SCOPES)
    return build('gmail', 'v1', credentials=credentials)


def get_drive_service(user_email):
    """
    Get Drive API service for a specific user.
    
    Args:
        user_email: Email address to impersonate
    
    Returns:
        Drive API service object
    """
    credentials = get_credentials(user_email, DRIVE_SCOPES)
    return build('drive', 'v3', credentials=credentials)


def get_docs_service(user_email):
    """
    Get Docs API service for a specific user.
    
    Args:
        user_email: Email address to impersonate
    
    Returns:
        Docs API service object
    """
    credentials = get_credentials(user_email, DOCS_SCOPES)
    return build('docs', 'v1', credentials=credentials)

