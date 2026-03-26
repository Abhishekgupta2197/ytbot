import sys
sys.path.append('/home/ubuntu/ytbot')

DP_CHANNEL_ID = "UCIyD9eS62o5t4IE8OGRa2Lw"
ST_CHANNEL_ID = "UCMWo8vpEpc4wv-8Jgnbxujg"

DP_CHANNEL_URL = f"https://www.youtube.com/channel/{DP_CHANNEL_ID}"
ST_CHANNEL_URL = f"https://www.youtube.com/channel/{ST_CHANNEL_ID}"

def update_channel_description(youtube, channel_type):
    if channel_type == "dark_psychology":
        description = (
            "🧠 Daily Dark Psychology secrets that will change how you see the world.\n\n"
            "We expose the hidden manipulation tactics, mind control techniques, and "
            "psychological tricks used against you every single day.\n\n"
            "Subscribe for daily Dark Psychology Shorts.\n\n"
            "📌 Also follow our Stoicism & Mindset channel for daily mental strength:\n"
            f"{ST_CHANNEL_URL}\n\n"
            "#DarkPsychology #Psychology #MindControl #Manipulation #Shorts"
        )
    else:
        description = (
            "🏛️ Daily Stoic wisdom from Marcus Aurelius, Seneca and Epictetus.\n\n"
            "We break down ancient stoic philosophy into powerful lessons you can "
            "apply to your life today. Build mental strength, discipline and inner peace.\n\n"
            "Subscribe for daily Stoicism Shorts.\n\n"
            "📌 Also follow our Dark Psychology channel to protect your mind:\n"
            f"{DP_CHANNEL_URL}\n\n"
            "#Stoicism #MarcusAurelius #Mindset #SelfImprovement #Shorts"
        )

    try:
        youtube.channels().update(
            part="brandingSettings",
            body={
                "id": DP_CHANNEL_ID if channel_type == "dark_psychology" else ST_CHANNEL_ID,
                "brandingSettings": {
                    "channel": {
                        "description": description
                    }
                }
            }
        ).execute()
        print(f"✅ Channel description updated!")
    except Exception as e:
        print(f"⚠️ Description update failed: {e}")

def pin_comment(youtube, video_id, channel_type):
    if channel_type == "dark_psychology":
        comment = (
            "🧠 Follow for daily Dark Psychology secrets that will change how you think! "
            f"Also check our Stoicism channel for daily mental strength 👉 {ST_CHANNEL_URL}"
        )
    else:
        comment = (
            "🏛️ Follow for daily Stoic wisdom from Marcus Aurelius & Seneca! "
            f"Also check our Dark Psychology channel 👉 {DP_CHANNEL_URL}"
        )

    try:
        response = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": comment
                        }
                    }
                }
            }
        ).execute()

        comment_id = response["id"]

        # Pin the comment
        youtube.comments().setModerationStatus(
            id=comment_id,
            moderationStatus="published",
            banAuthor=False
        ).execute()

        youtube.videos().update(
            part="snippet",
            body={
                "id": video_id,
                "snippet": {
                    "pinnedCommentId": comment_id
                }
            }
        ).execute()

        print(f"✅ Comment pinned!")
    except Exception as e:
        print(f"⚠️ Pin comment failed: {e}")
