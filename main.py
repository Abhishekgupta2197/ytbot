from dotenv import load_dotenv
load_dotenv()

import schedule
import time
import sys
import random
from datetime import datetime, timedelta

sys.path.append('/home/ubuntu/ytbot')

from channels.dark_psychology.run import run as run_dark_psychology
# from channels.stoicism.run import run as run_stoicism


print("\n" + "="*50)
print("🤖 YTBot Pro — Growth Mode Enabled")
print("="*50)
print("🔥 Strategy: High volume + randomized timing")
print("📈 Goal: Break 1K → 10K views barrier")
print("="*50 + "\n")


# -------------------------------
# CONFIG
# -------------------------------
POSTS_PER_DAY = 6   # 🔥 increase volume (was 4)
MIN_INTERVAL = 60   # minutes
MAX_INTERVAL = 180  # minutes


def run_with_log():
    now = datetime.now().strftime("%H:%M:%S")
    print(f"\n🚀 Posting at {now}")
    try:
        run_dark_psychology()
        print("✅ Upload complete")
    except Exception as e:
        print(f"❌ Error: {e}")


def schedule_random_posts():
    print("🧠 Generating today's random schedule...\n")

    now = datetime.now()
    start_time = now.replace(hour=7, minute=0, second=0)
    
    current_time = start_time

    for i in range(POSTS_PER_DAY):
        delay = random.randint(MIN_INTERVAL, MAX_INTERVAL)
        current_time += timedelta(minutes=delay)

        time_str = current_time.strftime("%H:%M")
        print(f"📅 Scheduled post {i+1} at {time_str}")

        schedule.every().day.at(time_str).do(run_with_log)


# -------------------------------
# INITIAL SCHEDULE
# -------------------------------
schedule_random_posts()


# -------------------------------
# DAILY RESET (VERY IMPORTANT)
# -------------------------------
def reset_schedule():
    print("\n🔄 Resetting schedule for new day...\n")
    schedule.clear()
    schedule_random_posts()


# reset every day at midnight
schedule.every().day.at("00:00").do(reset_schedule)


print("\n✅ Smart Scheduler running...\n")


# -------------------------------
# LOOP
# -------------------------------
while True:
    schedule.run_pending()
    time.sleep(30)
