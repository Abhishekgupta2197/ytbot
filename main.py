import schedule
import time
import sys
sys.path.append('/home/ubuntu/ytbot')

from channels.dark_psychology.run import run as run_dark_psychology
from channels.stoicism.run import run as run_stoicism

print("\n" + "="*50)
print("🤖 YTBot Pro — Multi Channel Manager")
print("="*50)
print("🧠 Dark Psychology: 12PM & 8PM")
print("🏛️ Stoicism: 7AM & 7PM")
print("📧 Email alerts active")
print("🔄 Auto pauses when credits low, resumes on 21st")
print("="*50 + "\n")

schedule.every().day.at("07:00").do(run_stoicism)
schedule.every().day.at("12:00").do(run_dark_psychology)
schedule.every().day.at("19:00").do(run_stoicism)
schedule.every().day.at("20:00").do(run_dark_psychology)

print("✅ Scheduler running!\n")

while True:
    schedule.run_pending()
    time.sleep(60)
