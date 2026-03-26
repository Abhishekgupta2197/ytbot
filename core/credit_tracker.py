import json
import os
import datetime
import sys
sys.path.append('/home/ubuntu/ytbot')
from core.emailer import send_email

TRACKER_FILE = '/home/ubuntu/ytbot/credit_usage.json'
MONTHLY_LIMIT = 40000
RESET_DAY = 21
WARNING_THRESHOLD = 5000  # Send warning email when below this

def load_tracker():
    if not os.path.exists(TRACKER_FILE):
        return {"month": datetime.datetime.now().month, "year": datetime.datetime.now().year, "used": 0, "warned": False}
    with open(TRACKER_FILE) as f:
        return json.load(f)

def save_tracker(data):
    with open(TRACKER_FILE, 'w') as f:
        json.dump(data, f)

def check_and_reset(tracker):
    now = datetime.datetime.now()
    # Reset if we're in a new month past reset day
    if (now.day >= RESET_DAY and (now.month != tracker["month"] or now.year != tracker["year"])):
        print("🔄 ElevenLabs credits reset! Starting fresh...")
        tracker["used"] = 0
        tracker["month"] = now.month
        tracker["year"] = now.year
        tracker["warned"] = False
        save_tracker(tracker)
    return tracker

def can_generate(text):
    tracker = load_tracker()
    tracker = check_and_reset(tracker)

    chars = len(text)
    remaining = MONTHLY_LIMIT - tracker["used"]

    # Out of credits
    if remaining <= 0:
        now = datetime.datetime.now()
        # Calculate days until reset
        if now.day < RESET_DAY:
            days_left = RESET_DAY - now.day
        else:
            next_month = now.replace(day=1) + datetime.timedelta(days=32)
            reset_date = next_month.replace(day=RESET_DAY)
            days_left = (reset_date - now).days

        send_email(
            "⛔ YTBot Paused — ElevenLabs Credits Exhausted!",
            f"You have used all {MONTHLY_LIMIT} ElevenLabs credits this month.\n\n"
            f"Credits used: {tracker['used']}/{MONTHLY_LIMIT}\n"
            f"Bot will automatically resume in {days_left} days on the 21st.\n\n"
            f"To resume immediately, upgrade your ElevenLabs plan at:\n"
            f"https://elevenlabs.io/subscription"
        )
        print(f"⛔ Out of ElevenLabs credits! Bot paused. Resets on the 21st.")
        return False

    # Low credits warning
    if remaining <= WARNING_THRESHOLD and not tracker["warned"]:
        send_email(
            "⚠️ YTBot Warning — ElevenLabs Credits Running Low!",
            f"You are running low on ElevenLabs credits.\n\n"
            f"Credits used: {tracker['used']}/{MONTHLY_LIMIT}\n"
            f"Credits remaining: {remaining}\n"
            f"Estimated videos left: {remaining // 300}\n\n"
            f"The bot will keep running but will pause when credits hit 0.\n"
            f"To add more credits visit:\n"
            f"https://elevenlabs.io/subscription"
        )
        tracker["warned"] = True
        save_tracker(tracker)
        print(f"⚠️ Low credits warning sent! {remaining} chars remaining.")

    return True

def track_usage(text):
    tracker = load_tracker()
    chars = len(text)
    tracker["used"] += chars
    save_tracker(tracker)
    remaining = MONTHLY_LIMIT - tracker["used"]
    print(f"📊 ElevenLabs: {tracker['used']}/{MONTHLY_LIMIT} chars used | {remaining} remaining")
