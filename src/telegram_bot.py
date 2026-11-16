import os
import requests
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
OFFSET_FILE = ".telegram_offset"

def send_message(text: str):
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

def _get_saved_offset() -> int:
    if os.path.exists(OFFSET_FILE):
        try:
            with open(OFFSET_FILE, "r") as f:
                return int(f.read().strip())
        except ValueError:
            return 0
    return 0

def _save_offset(offset: int):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(offset))

def get_unprocessed_updates():
    """
    Recull missatges de text o notes de veu de Telegram de manera flexible.
    """
    offset = _get_saved_offset()
    url = f"{BASE_URL}/getUpdates"
    params = {"offset": offset, "timeout": 10}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    results = data.get("result", [])
    if not results:
        return None

    update = results[-1]
    update_id = update["update_id"]
    _save_offset(update_id + 1)

    message = update.get("message", {})
    chat_id = str(message.get("chat", {}).get("id", ""))

    if chat_id != str(TELEGRAM_CHAT_ID):
        return None

    # Si l'usuari ha enviat una nota de veu
    if "voice" in message:
        file_id = message["voice"]["file_id"]
        file_path = _download_telegram_file(file_id, "voice.ogg")
        return {"type": "voice", "path": file_path}
    
    # Si l'usuari ha escrit text lliure
    elif "text" in message:
        return {"type": "text", "content": message["text"]}

    return None

def _download_telegram_file(file_id: str, output_filename: str) -> str:
    file_info_url = f"{BASE_URL}/getFile"
    r = requests.get(file_info_url, params={"file_id": file_id})
    r.raise_for_status()
    file_path_in_telegram = r.json()["result"]["file_path"]

    download_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_path_in_telegram}"
    file_res = requests.get(download_url)
    file_res.raise_for_status()

    with open(output_filename, "wb") as f:
        f.write(file_res.content)

    return output_filename
    with open(output_filename, "wb") as f:
        f.write(file_res.content)

    return output_filename
