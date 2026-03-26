import os
import sys
sys.path.append('/home/ubuntu/ytbot')
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def get_youtube_service(client_secrets, token_file):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("✅ Token refreshed silently!")
        else:
            print("🔐 First time auth — copy URL to browser...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
            auth_url, _ = flow.authorization_url()
            print(f"\n👉 Open this URL:\n{auth_url}\n")
            code = input("Paste the code here: ")
            flow.fetch_token(code=code)
            creds = flow.credentials
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, file_path, thumbnail_path, title, description, tags, category_id="27"):
    print("📤 Uploading to YouTube...")
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media)
    response = request.execute()
    video_id = response["id"]
    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path)
        ).execute()
        print("✅ Thumbnail uploaded!")
    except Exception as e:
        print(f"⚠️ Thumbnail failed: {e}")
    print(f"✅ Uploaded! https://www.youtube.com/watch?v={video_id}")
    return video_id

def reply_comments(youtube):
    print("💬 Checking comments...")
    replies = [
        "This is why understanding psychology is so important 🧠",
        "Knowledge is protection. Share this with someone who needs it 🔴",
        "More dark psychology facts dropping daily — follow for more! 👁️",
        "Understanding this could literally change your life 🧠"
    ]
    import random, time
    try:
        response = youtube.commentThreads().list(
            part="snippet",
            allThreadsRelatedToChannelId="mine",
            maxResults=20
        ).execute()
        count = 0
        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            if snippet.get("totalReplyCount", 0) == 0:
                youtube.comments().insert(
                    part="snippet",
                    body={"snippet": {
                        "parentId": item["id"],
                        "textOriginal": random.choice(replies)
                    }}
                ).execute()
                count += 1
                time.sleep(1)
        print(f"✅ Replied to {count} comments!")
    except Exception as e:
        print(f"⚠️ Comments error: {e}")
