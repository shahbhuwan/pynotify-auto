
import urllib.request
import json
import logging

def send_ntfy(topic, message, title=None):
    """Send notification via ntfy.sh"""
    url = f"https://ntfy.sh/{topic}"
    headers = {}
    if title:
        headers["Title"] = title
    
    try:
        req = urllib.request.Request(url, data=message.encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.getcode() == 200
    except Exception as e:
        print(f"[pynotify-auto] Debug: Remote failure ({type(e).__name__}: {e})")
        return False

def send_telegram(token, chat_id, message):
    """Send notification via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.getcode() == 200
    except Exception as e:
        return False
