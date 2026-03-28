import os
import logging
from google_auth import get_credentials
from drive_handler import get_next_video
from video_processor import process_video
from youtube_uploader import upload_to_youtube

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def job():
    logger.info("🔄 Начинаем публикацию...")
    try:
        creds = get_credentials()
        video_path, video_name = get_next_video(creds)
        if not video_path:
            logger.info("📭 Нет новых видео")
            return

        segments = process_video(video_path, video_name)
        logger.info(f"🎬 Нарезано {len(segments)} сегментов")

        for i, (processed_path, title, description) in enumerate(segments):
            logger.info(f"📤 Публикуем {i+1}/{len(segments)}: {title}")
            upload_to_youtube(creds, processed_path, title, description)
            if os.path.exists(processed_path):
                os.remove(processed_path)

        if os.path.exists(video_path):
            os.remove(video_path)

        logger.info("✅ Все сегменты опубликованы!")

    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    logger.info("🚀 Запуск!")
    job()
