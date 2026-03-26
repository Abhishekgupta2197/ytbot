import requests
import random
import os
import sys
sys.path.append('/home/ubuntu/ytbot')
from config import PEXELS_API_KEY

MUSIC_URLS = [
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
]

BACKGROUNDS_FOLDER = "/home/ubuntu/ytbot/backgrounds"

def download_background_video(queries, output_path):
    print("🎬 Selecting background video...")
    
    # Use local backgrounds if available
    local_files = [f for f in os.listdir(BACKGROUNDS_FOLDER) 
                   if f.endswith(('.mp4', '.mov', '.avi'))]
    
    if local_files:
        chosen = random.choice(local_files)
        src = os.path.join(BACKGROUNDS_FOLDER, chosen)
        import shutil
        shutil.copy(src, output_path)
        print(f"✅ Using local background: {chosen}")
        return

    # Fallback to Pexels if no local files
    print("⬇️ No local files, downloading from Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    query = random.choice(queries)
    params = {"query": query, "per_page": 10, "orientation": "portrait"}
    response = requests.get("https://api.pexels.com/videos/search",
                           headers=headers, params=params)
    data = response.json()
    videos = data.get("videos", [])
    if not videos:
        raise Exception(f"No videos found for: {query}")
    video = random.choice(videos)
    video_files = sorted(video["video_files"],
                        key=lambda x: x.get("width", 0), reverse=True)
    video_url = video_files[0]["link"]
    video_data = requests.get(video_url, stream=True)
    with open(output_path, "wb") as f:
        for chunk in video_data.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"✅ Downloaded from Pexels: {query}")

def download_music(output_path):
    print("🎵 Downloading background music...")
    url = random.choice(MUSIC_URLS)
    response = requests.get(url, stream=True)
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("✅ Music ready!")
