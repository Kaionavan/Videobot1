import os
import io
import json
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID")
PROGRESS_FILE = "progress.json"

def get_service(creds):
    return build('drive', 'v3', credentials=creds)

def load_progress(service):
    results = service.files().list(
        q=f"name='{PROGRESS_FILE}' and '{FOLDER_ID}' in parents and trashed=false",
        fields="files(id)"
    ).execute()
    files = results.get('files', [])
    if not files:
        return {}
    file_id = files[0]['id']
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return json.loads(fh.getvalue().decode())

def save_progress(service, progress):
    data = json.dumps(progress).encode()
    results = service.files().list(
        q=f"name='{PROGRESS_FILE}' and '{FOLDER_ID}' in parents and trashed=false",
        fields="files(id)"
    ).execute()
    files = results.get('files', [])
    media = MediaFileUpload(
        io.BytesIO(data),
        mimetype='application/json',
        resumable=False
    )
    if files:
        service.files().update(
            fileId=files[0]['id'],
            media_body=media
        ).execute()
    else:
        service.files().create(
            body={'name': PROGRESS_FILE, 'parents': [FOLDER_ID]},
            media_body=media
        ).execute()

def get_next_segment(creds):
    service = get_service(creds)
    progress = load_progress(service)

    query = f"'{FOLDER_ID}' in parents and mimeType contains 'video/' and trashed=false"
    results = service.files().list(
        q=query,
        orderBy='createdTime',
        fields="files(id, name)"
    ).execute()

    files = results.get('files', [])

    for file in files:
        file_id = file['id']
        file_name = file['name']
        done_segments = progress.get(file_id, [])

        # Скачиваем файл
        local_path = f"/tmp/{file_name}"
        if not os.path.exists(local_path):
            request = service.files().get_media(fileId=file_id)
            with io.FileIO(local_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()

        # Считаем сегменты
        from video_processor import get_video_duration, SEGMENT_DURATION
        duration = get_video_duration(local_path)
        import math
        total_segments = math.ceil(duration / SEGMENT_DURATION)

        # Найди первый неопубликованный сегмент
        for i in range(total_segments):
            if i not in done_segments:
                # Отмечаем как опубликованный
                done_segments.append(i)
                progress[file_id] = done_segments
                save_progress(service, progress)
                return local_path, file_name, i

        # Все сегменты опубликованы — удаляем локальный файл
        if os.path.exists(local_path):
            os.remove(local_path)

    return None, None, None
