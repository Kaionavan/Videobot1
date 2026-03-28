import os
import subprocess
import anthropic

TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "@your_channel")

def generate_title_description(video_name):
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    prompt = f"""На основе названия видео "{video_name}" создай:
1. Короткий цепляющий заголовок для YouTube Shorts (до 60 символов) про ИИ/технологии
2. Описание (до 200 символов) с призывом подписаться на Telegram {TELEGRAM_CHANNEL}

Ответь строго в формате JSON:
{{"title": "...", "description": "..."}}"""
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    import json
    try:
        data = json.loads(message.content[0].text)
        return data["title"], data["description"]
    except:
        return f"ИИ на практике", f"Подпишись {TELEGRAM_CHANNEL} 🚀"

def process_video(input_path, video_name):
    output_path = f"/tmp/processed_{os.path.basename(input_path)}"
    final_path = f"/tmp/final_{os.path.basename(input_path)}"
    subprocess.run([
        'ffmpeg', '-i', input_path, '-t', '58',
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black',
        '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-b:a', '128k',
        '-y', output_path
    ], check=True, capture_output=True)
    subprocess.run([
        'ffmpeg', '-i', output_path,
        '-vf', f"drawtext=text='Подпишись {TELEGRAM_CHANNEL}':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=h-80:box=1:boxcolor=black@0.5:boxborderw=10",
        '-c:a', 'copy', '-y', final_path
    ], check=True, capture_output=True)
    if os.path.exists(output_path):
        os.remove(output_path)
    title, description = generate_title_description(video_name)
    return final_path, title, description
