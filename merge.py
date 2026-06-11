import os
import sys
import requests
import subprocess

def download_file(url, output_path):
    session = requests.Session()
    r = session.get(url, stream=True, allow_redirects=True)
    # 處理 Google Drive 確認頁面
    for key, value in r.cookies.items():
        if key.startswith('download_warning'):
            params = {'confirm': value}
            r = session.get(url, params=params, stream=True)
            break
    with open(output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

def main():
    video_url = os.environ['VIDEO_URL']
    audio_url = os.environ['AUDIO_URL']
    audio_start = os.environ.get('AUDIO_START', '0')
    output_name = os.environ.get('OUTPUT_NAME', 'output.mp4')

    print(f"Downloading video from {video_url}")
    download_file(video_url, 'input_video.mp4')

    print(f"Downloading audio from {audio_url}")
    download_file(audio_url, 'input_audio.mp3')

    print("Merging video and audio...")
    cmd = [
        'ffmpeg', '-y',
        '-i', 'input_video.mp4',
        '-i', 'input_audio.mp3',
        '-ss', audio_start,
        '-t', '6',
        '-map', '0:v',
        '-map', '1:a',
        '-shortest',
        '-c:v', 'copy',
        output_name
    ]
    subprocess.run(cmd, check=True)
    print(f"Done: {output_name}")

if __name__ == '__main__':
    main()
