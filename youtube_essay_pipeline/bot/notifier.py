"""
notifier.py - Telegram Push Notification Service for YouTube Video Essays
Sends progress updates, thumbnail previews, and rendered video clips directly to Telegram.
"""

import os
import sys
import asyncio
import requests

from bot.config import TELEGRAM_BOT_TOKEN, ALLOWED_CHAT_IDS

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

def is_configured() -> bool:
    return bool(TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN_HERE")

def get_target_chat_ids(chat_id=None):
    if chat_id:
        return [chat_id]
    return ALLOWED_CHAT_IDS

def send_telegram_message(text: str, chat_id=None, parse_mode: str = "Markdown") -> bool:
    """Sends a text message to authorized Telegram chats."""
    if not is_configured():
        return False
        
    success = True
    for cid in get_target_chat_ids(chat_id):
        try:
            url = f"{API_BASE}/sendMessage"
            payload = {
                "chat_id": cid,
                "text": text,
                "parse_mode": parse_mode
            }
            resp = requests.post(url, json=payload, timeout=10)
            if not resp.ok:
                # Retry without markdown if markdown parsing failed
                payload.pop("parse_mode", None)
                resp = requests.post(url, json=payload, timeout=10)
            if not resp.ok:
                success = False
        except Exception as e:
            print(f"[NOTIFIER ERROR] Failed to send message: {e}")
            success = False
    return success

def send_telegram_photo(photo_path: str, caption: str = None, chat_id=None) -> bool:
    """Sends a photo to authorized Telegram chats."""
    if not is_configured() or not os.path.exists(photo_path):
        return False
        
    success = True
    for cid in get_target_chat_ids(chat_id):
        try:
            url = f"{API_BASE}/sendPhoto"
            with open(photo_path, "rb") as f:
                data = {"chat_id": cid}
                if caption:
                    data["caption"] = caption
                    data["parse_mode"] = "Markdown"
                resp = requests.post(url, data=data, files={"photo": f}, timeout=30)
                if not resp.ok:
                    success = False
        except Exception as e:
            print(f"[NOTIFIER ERROR] Failed to send photo: {e}")
            success = False
    return success

def send_telegram_video(video_path: str, caption: str = None, chat_id=None) -> bool:
    """
    Sends a video file to authorized Telegram chats.
    Note: Telegram Bot API enforces a 50MB per-file upload limit for bots.
    """
    if not is_configured() or not os.path.exists(video_path):
        return False
        
    size_mb = os.path.getsize(video_path) / 1024 / 1024
    if size_mb > 50.0:
        send_telegram_message(
            f"⚠️ *Video Exceeds Telegram 50MB Limit* ({size_mb:.1f} MB)\n"
            f"File: `{os.path.basename(video_path)}`\n"
            f"Use chapter cuts or access locally from disk.",
            chat_id=chat_id
        )
        return False
        
    success = True
    for cid in get_target_chat_ids(chat_id):
        try:
            url = f"{API_BASE}/sendVideo"
            with open(video_path, "rb") as f:
                data = {
                    "chat_id": cid,
                    "supports_streaming": "true"
                }
                if caption:
                    data["caption"] = caption
                    data["parse_mode"] = "Markdown"
                resp = requests.post(url, data=data, files={"video": f}, timeout=180)
                if not resp.ok:
                    success = False
        except Exception as e:
            print(f"[NOTIFIER ERROR] Failed to send video: {e}")
            success = False
    return success
