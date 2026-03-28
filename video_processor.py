import os
import subprocess
import json
import anthropic

TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "@your_channel")
SEGMENT_DURATION = 58

def get_video_duration(video_path):
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', video_path
    ], capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

def generate_title_description(video_name, part=None):
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    part_text = f" часть {part}" if part else ""
    prompt = f"""На основе названия видео "{video_name}{part_text}" создай:
1. Короткий цепляющий заголовок для YouTube Shorts (до 60 символов)
2. Описание (до 200 символов) с призывом подписаться на {TELEGRAM_CHANNEL}
Ответь строго в формате JSON:
{{"title": "...", "description": "..."}}"""
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    try:
        data = json.loads(message.content[0].text)
        return data["title"], data["description"]
    except:
        return f"ИИ на практике{part_text}", f"Подпишись {TELEGRAM_CHANNEL} 🚀"

def split_and_process(input_path, video_name):
    duration = get_video_duration(input_path)
    segments = []
    start = 0
    part = 1

    while start < duration:
        output_path = f"/tmp/segment_{part}_{os.path.basename(input_path)}"
        final_path = f"/tmp/final_{part}_{os.path.basename(input_path)}"

        # Нарезаем сегмент
        subprocess.run([
            'ffmpeg', '-i', input_path,
            '-ss', str(start), '-t', str(SEGMENT_DURATION),
            '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black',
            '-c:v', 'libx264', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-y', output_path
        ], check=True, capture_output=True)

        # Добавляем текст
        subprocess.run([
            'ffmpeg', '-i', output_path,
            '-vf', f"drawtext=text='Подпишись {TELEGRAM_CHANNEL}':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=h-80:box=1:boxcolor=black@0.5:boxborderw=10",
            '-c:a', 'copy', '-y', final_path
        ], check=True, capture_output=True)

        if os.path.exists(output_path):
            os.remove(output_path)

        title, description = generate_title_description(video_name, part)
        segments.append((final_path, title, description))

        start += SEGMENT_DURATION
        part += 1

    return segments

def process_video(input_path, video_name):
    segments = split_and_process(input_path, video_name)
    return segments
