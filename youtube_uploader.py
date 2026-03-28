import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_youtube(creds, video_path, title, description):
    youtube = build('youtube', 'v3', credentials=creds)
    body = {
        'snippet': {
            'title': title,
            'description': description + "\n\n#ИИ #искусственныйинтеллект #технологии #shorts #AI",
            'tags': ['ИИ', 'AI', 'технологии', 'автоматизация', 'shorts'],
            'categoryId': '28'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True, chunksize=1024*1024*5)
    request = youtube.videos().insert(part=','.join(body.keys()), body=body, media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Загружено {int(status.progress() * 100)}%")
    print(f"✅ https://youtube.com/shorts/{response['id']}")
    return response['id']
