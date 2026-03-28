import os
import subprocess
import json

TELEGRAM_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "@your_channel")
SEGMENT_DURATION = 58

def get_video_duration(video_path):
    result = subprocess.run([
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', video_path
    ], capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data['format']['duration'])

def process_segment(input_path, video_name, segment_index):
    start = segment_index * SEGMENT_DURATION
    part = segment_index + 1
    output_path = f"/tmp/segment_{part}.mp4"
    final_path = f"/tmp/final_{part}.mp4"

    subprocess.run([
        'ffmpeg', '-i', input_path,
        '-ss', str(start), '-t', str(SEGMENT_DURATION),
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black',
        '-c:v', 'libx264', '-crf', '23',
        '-c:a', 'aac', '-b:a', '128k',
        '-y', output_path
    ], check=True, capture_output=True)

    subprocess.run([
        'ffmpeg', '-i', output_path,
        '-vf', f"drawtext=text='Подпишись {TELEGRAM_CHANNEL}':fontsize=40:fontcolor=white:x=(w-text_w)/2:y=h-80:box=1:boxcolor=black@0.5:boxborderw=10",
        '-c:a', 'copy', '-y', final_path
    ], check=True, capture_output=True)

    if os.path.exists(output_path):
        os.remove(output_path)

    title = f"ИИ на практике часть {part} | {video_name[:25]}"
    description = f"Всё об ИИ и автоматизации 🤖 Подпишись {TELEGRAM_CHANNEL}"

    return final_path, title, description
