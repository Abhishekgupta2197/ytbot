import sys
import os
import datetime
sys.path.append('/home/ubuntu/ytbot')
from config import OUTPUT_FOLDER
from core.emailer import send_email
from core.voiceover import generate_voiceover
from core.downloader import download_music
from core.thumbnail import generate_thumbnail
from core.video import build_video
from core.youtube import get_youtube_service, upload_video, reply_comments
from core.channel_growth import update_channel_description, pin_comment
from channels.stoicism.scripts import get_script
from channels.stoicism.channel_config import (
    CLIENT_SECRETS, TOKEN_FILE,
    THUMBNAIL_BG_COLOR, THUMBNAIL_ACCENT_COLOR,
    THUMBNAIL_BADGE_TEXT, TAGS, CATEGORY_ID
)

LOG_FILE = '/home/ubuntu/ytbot/upload_log.txt'

def log_upload(title, video_id):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} | STOICISM | {title} | https://youtube.com/watch?v={video_id}\n")

def cleanup():
    print("🧹 Cleaning up output folder...")
    exts = ['.mp4', '.mp3', '.ass', '.jpg', '.json']
    for f in os.listdir(OUTPUT_FOLDER):
        if any(f.endswith(ext) for ext in exts):
            try:
                os.remove(os.path.join(OUTPUT_FOLDER, f))
            except:
                pass
    print("✅ Output folder cleared!")

def run():
    print("\n" + "="*50)
    print("🏛️ Stoicism & Mindset Channel Pipeline")
    print("="*50 + "\n")
    try:
        audio_path  = f"{OUTPUT_FOLDER}/voiceover.mp3"
        bg_video    = "/home/ubuntu/ytbot/backgrounds/Stoicism.mp4"
        music_path  = f"{OUTPUT_FOLDER}/music.mp3"
        final_video = f"{OUTPUT_FOLDER}/final_video.mp4"
        thumb_path  = f"{OUTPUT_FOLDER}/thumbnail.jpg"

        title, hook, script = get_script()
        generate_voiceover(script, audio_path)
        download_music(music_path)
        generate_thumbnail(
            title, THUMBNAIL_BADGE_TEXT, thumb_path,
            bg_color=THUMBNAIL_BG_COLOR,
            accent_color=THUMBNAIL_ACCENT_COLOR
        )
        build_video(bg_video, audio_path, music_path, script, final_video, 'STOICISM')

        youtube = get_youtube_service(CLIENT_SECRETS, TOKEN_FILE)
        update_channel_description(youtube, "stoicism")

        description = f"""🏛️ {hook}
{script}
Follow for daily stoic wisdom that will change how you think.
📌 Also follow our Dark Psychology channel: https://www.youtube.com/channel/UCIyD9eS62o5t4IE8OGRa2Lw
#Stoicism #MarcusAurelius #Mindset #SelfImprovement #Shorts"""

        video_id = upload_video(
            youtube, final_video, thumb_path,
            f"{title} #Shorts",
            description, TAGS, CATEGORY_ID
        )

        pin_comment(youtube, video_id, "stoicism")
        reply_comments(youtube)
        log_upload(title, video_id)
        cleanup()

        send_email(
            "✅ Stoicism — Video Uploaded!",
            f"Title: {title}\nHook: {hook}\nURL: https://youtube.com/watch?v={video_id}"
        )
        print(f"\n🎉 Done! https://www.youtube.com/watch?v={video_id}\n")

    except Exception as e:
        import traceback
        msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        print(f"❌ {msg}")
        send_email("❌ Stoicism Bot Error!", msg)

if __name__ == "__main__":
    run()
