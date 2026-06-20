import os
import random
import requests
import subprocess

GITHUB_RAW = "https://raw.githubusercontent.com/yasukomatsuyuki0904-tech/animalhero-ffmpeg/main/BGM"

TENSION_BGM = [
    {"file": "Duty Calls - Rod Kim.mp3",                        "start": "00:00:00", "duration": "10"},
    {"file": "Frodo's Quest - Ezra Lipp.mp3",                   "start": "00:00:00", "duration": "10"},
    {"file": "The Marble Cinematic University - Ezra Lipp.mp3", "start": "00:01:07", "duration": "10"},
    {"file": "The Road To Mordor - Ezra Lipp.mp3",              "start": "00:00:07", "duration": "10"},
]

WARM_BGM = [
    {"file": "Alpine Bierhalle - Aaron Kenny.mp3",              "start": "00:00:11", "duration": "5"},
    {"file": "Everything Has a Beginning - Joel Cummins.mp3",   "start": "00:00:00", "duration": "5"},
    {"file": "Fiesta de la Vida - Aaron Kenny.mp3",             "start": "00:01:24", "duration": "5"},
    {"file": "Gaiety in the Golden Age - Aaron Kenny.mp3",      "start": "00:01:44", "duration": "5"},
]


def download_file(url, output_path):
    headers = {'User-Agent': 'Mozilla/5.0'}
    session = requests.Session()
    r = session.get(url, stream=True, allow_redirects=True, headers=headers)
    r.raise_for_status()
    with open(output_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)


def main():
    video_url_1  = os.environ['VIDEO_URL_1']
    video_url_2  = os.environ['VIDEO_URL_2']
    video_url_3  = os.environ['VIDEO_URL_3']
    webhook_url  = os.environ['WEBHOOK_URL']
    run_id       = os.environ['GITHUB_RUN_ID']

    tension = random.choice(TENSION_BGM)
    warm    = random.choice(WARM_BGM)
    print(f"Tension BGM: {tension['file']}")
    print(f"Warm BGM:    {warm['file']}")

    # 下載三段影片
    for i, url in enumerate([video_url_1, video_url_2, video_url_3], 1):
        print(f"Downloading video {i} from {url}")
        download_file(url, f"input_video_{i}.mp4")

    # 下載 BGM
    tension_url = f"{GITHUB_RAW}/{requests.utils.quote(tension['file'])}"
    warm_url    = f"{GITHUB_RAW}/{requests.utils.quote(warm['file'])}"
    download_file(tension_url, "tension.mp3")
    download_file(warm_url,    "warm.mp3")

    # Step 1: 串接三段影片
    with open("concat_list.txt", 'w') as f:
        for i in range(1, 4):
            f.write(f"file 'input_video_{i}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", "concat_list.txt", "-c", "copy", "merged_video.mp4"], check=True)

    # Step 2: 裁切 tension BGM（10秒）
    subprocess.run(["ffmpeg", "-y", "-ss", tension["start"], "-t", tension["duration"],
                    "-i", "tension.mp3", "-c:a", "aac", "-b:a", "128k", "tension_trim.aac"], check=True)

    # Step 3: 裁切 warm BGM（5秒）
    subprocess.run(["ffmpeg", "-y", "-ss", warm["start"], "-t", warm["duration"],
                    "-i", "warm.mp3", "-c:a", "aac", "-b:a", "128k", "warm_trim.aac"], check=True)

    # Step 4: 拼接 BGM
    with open("bgm_list.txt", 'w') as f:
        f.write("file 'tension_trim.aac'\n")
        f.write("file 'warm_trim.aac'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", "bgm_list.txt", "-c", "copy", "full_bgm.aac"], check=True)

    # Step 5: 合併影片 + BGM
    subprocess.run(["ffmpeg", "-y", "-i", "merged_video.mp4", "-i", "full_bgm.aac",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                    "-shortest", "output.mp4"], check=True)

    print("Done: output.mp4")

    # Step 6: 通知 Make.com
    print(f"Notifying webhook with run_id={run_id}")
    requests.post(webhook_url, json={"status": "done", "run_id": run_id})


if __name__ == '__main__':
    main()
