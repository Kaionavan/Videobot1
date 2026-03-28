import os
import io
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID")
PUBLISHED_FILE = "published.json"

def get_published():
    if os.path.exists(PUBLISHED_FILE):
        with open(PUBLISHED_FILE, 'r') as f:
            return json.load(f)
    return []

def mark_published(file_id):
    published = get_published()
    published.append(file_id)
    with open(PUBLISHED_FILE, 'w') as f:
        json.dump(published, f)

def get_next_video(creds):
    service = build('drive', 'v3', credentials=creds)
    published = get_published()
    query = f"'{FOLDER_ID}' in parents and mimeType contains 'video/' and trashed=false"
    results = service.files().list(q=query, orderBy='createdTime', fields="files(id, name)").execute()
    for file in results.get('files', []):
        if file['id'] not in published:
            request = service.files().get_media(fileId=file['id'])
            local_path = f"/tmp/{file['name']}"
            with io.FileIO(local_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            mark_published(file['id'])
            return local_path, file['name']
    return None, None
