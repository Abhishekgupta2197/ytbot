#!/usr/bin/env python3
import smtplib, subprocess, socket, json, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

ALERT_EMAIL    = "businessshorts2197@gmail.com"
FROM_EMAIL     = "businessshorts2197@gmail.com"
GMAIL_APP_PASS = "mbcxhnoibfdxuhqd"
SERVICE_NAME   = "ytbot"
STATE_FILE     = "/tmp/ytbot_health_state.json"

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def check_internet():
    try:
        socket.setdefaulttimeout(5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except:
        return False

def check_service():
    result = subprocess.run(["systemctl", "is-active", SERVICE_NAME], capture_output=True, text=True)
    return result.stdout.strip() == "active"

def get_service_last_log(lines=10):
    result = subprocess.run(["journalctl", "-u", SERVICE_NAME, "-n", str(lines), "--no-pager"], capture_output=True, text=True)
    return result.stdout.strip()

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"internet_down": False, "service_down": False, "internet_alert_sent": False, "service_alert_sent": False}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def send_email(subject, body):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = FROM_EMAIL
        msg["To"]      = ALERT_EMAIL
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(FROM_EMAIL, GMAIL_APP_PASS)
            server.sendmail(FROM_EMAIL, ALERT_EMAIL, msg.as_string())
        log(f"Email sent: {subject}")
        return True
    except Exception as e:
        log(f"Failed to send email: {e}")
        return False

def main():
    state = load_state()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    internet_ok = check_internet()
    service_ok  = check_service()
    log(f"Internet: {'OK' if internet_ok else 'DOWN'} | Service: {'OK' if service_ok else 'DOWN'}")

    if not internet_ok:
        if not state["internet_alert_sent"]:
            sent = send_email(f"YTBot ALERT - Server lost internet [{now}]",
                f"Server 140.238.153.151 lost internet at {now}.\nVideos will NOT upload until fixed.\nCheck Oracle Cloud console -> VCN settings.\n\n- YTBot Health Monitor")
            if sent:
                state["internet_alert_sent"] = True
                state["internet_down"] = True
    else:
        if state["internet_down"]:
            send_email(f"YTBot RECOVERED - Internet restored [{now}]",
                f"Server internet restored at {now}.\nBot should resume normally.\n\n- YTBot Health Monitor")
        state["internet_down"] = False
        state["internet_alert_sent"] = False

    if not service_ok:
        if not state["service_alert_sent"]:
            logs = get_service_last_log()
            sent = send_email(f"YTBot ALERT - Bot service stopped [{now}]",
                f"ytbot service stopped at {now}.\n\nTo fix:\n  sudo systemctl restart ytbot\n\nLast logs:\n{'-'*40}\n{logs}\n\n- YTBot Health Monitor")
            if sent:
                state["service_alert_sent"] = True
                state["service_down"] = True
    else:
        if state["service_down"]:
            send_email(f"YTBot RECOVERED - Service is running [{now}]",
                f"ytbot service recovered at {now}.\n\n- YTBot Health Monitor")
        state["service_down"] = False
        state["service_alert_sent"] = False

    save_state(state)

if __name__ == "__main__":
    main()
