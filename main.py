import os
import time
import schedule
import logging
from google_auth import get_credentials
from drive_handler import get_next_video
from video_processor import process_video
from youtube_uploader import upload_to_youtube

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def job():
    logger.info("🔄 Начинаем цикл публикации...")
    try:
        creds = get_credentials()
        video_path, video_name = get_next_video(creds)
        if not video_path:
            logger.info("📭 Нет новых видео")
            return
        processed_path, title, description = process_video(video_path, video_name)
        upload_to_youtube(creds, processed_path, title, description)
        logger.info(f"✅ Опубликовано: {title}")
        for p in [processed_path, video_path]:
            if os.path.exists(p):
                os.remove(p)
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    logger.info("🚀 Бот запущен!")
    schedule.every().day.at("09:00").do(job)
    schedule.every().day.at("14:00").do(job)
    schedule.every().day.at("19:00").do(job)
    job()
    while True:
        schedule.run_pending()
        time.sleep(60)
