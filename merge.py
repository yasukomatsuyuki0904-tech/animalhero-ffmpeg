import os
import sys
import requests
import subprocess

def download_file(url, output_path):
    headers = {'User-Agent': 'Mozilla/5.0'}
    session = requests.Session()
    r = session.get(url, stream=True, allow_redirects=True, headers=headers)
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
        '-map', '0:v:0',
        '-map', '1:a:0',
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-shortest',
        output_name
    ]
    subprocess.run(cmd, check=True)
    print(f"Done: {output_name}")

if __name__ == '__main__':
    main()
