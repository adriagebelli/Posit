import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DAILY_DB_ID = os.getenv("NOTION_DAILY_DB_ID")
NOTION_WEEKLY_DB_ID = os.getenv("NOTION_WEEKLY_DB_ID")

def validate_config():
    missing = []
    if not TELEGRAM_BOT_TOKEN: missing.append("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_CHAT_ID: missing.append("TELEGRAM_CHAT_ID")
    if not GEMINI_API_KEY: missing.append("GEMINI_API_KEY")
    if not NOTION_API_KEY: missing.append("NOTION_API_KEY")
    if not NOTION_DAILY_DB_ID: missing.append("NOTION_DAILY_DB_ID")
    if missing:
        raise ValueError(f"Falten les següents variables d'entorn obligatòries: {', '.join(missing)}")
