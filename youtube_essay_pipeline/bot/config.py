import os
from dotenv import load_dotenv

# Load .env file from bot directory or project root
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BOT_DIR, ".."))

load_dotenv(os.path.join(BOT_DIR, ".env"))
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# Comma-separated chat IDs or single integer chat ID
ALLOWED_CHAT_IDS = [
    int(cid.strip()) for cid in os.getenv("ALLOWED_CHAT_IDS", "").split(",") if cid.strip().isdigit()
]
