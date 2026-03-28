import os
import logging
from google_auth import get_credentials
from drive_handler import get_next_segment
from video_processor import process_segment
from youtube_uploader import upload_to_youtube

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def job():
    logger.info("🔄 Начинаем публикацию...")
    try:
        creds = get_credentials()
        video_path, video_name, segment_index = get_next_segment(creds)
        if not video_path:
            logger.info("📭 Нет новых сегментов")
            return

        logger.info(f"🎬 Обрабатываем сегмент {segment_index+1}: {video_name}")
        processed_path, title, description = process_segment(video_path, video_name, segment_index)

        logger.info(f"📤 Публикуем: {title}")
        upload_to_youtube(creds, processed_path, title, description)

        if os.path.exists(processed_path):
            os.remove(processed_path)

        logger.info("✅ Готово!")

    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    logger.info("🚀 Запуск!")
    job()
