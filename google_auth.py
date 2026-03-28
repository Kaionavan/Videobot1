import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/youtube.upload'
]

def get_credentials():
    token_data = os.environ.get("GOOGLE_TOKEN")
    creds = Credentials.from_authorized_user_info(json.loads(token_data), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds
