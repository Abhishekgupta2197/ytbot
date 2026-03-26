import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
sys.path.append('/home/ubuntu/ytbot')
from config import SENDER_EMAIL, SENDER_APP_PASSWORD, RECEIVER_EMAIL

def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        server.quit()
        print("📧 Email alert sent!")
    except Exception as e:
        print(f"⚠️ Email failed: {e}")
