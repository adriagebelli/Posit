import argparse
from src.config import validate_config
from src.telegram_bot import send_message, get_unprocessed_updates
from src.gemini_extractor import process_input_with_gemini
from src.notion_sync import create_daily_entry
from src.weekly_engine import run_weekly_synthesis

def main():
    validate_config()
    
    parser = argparse.ArgumentParser(description="NexLog Journal Automation")
    parser.add_argument("--mode", choices=["prompt", "ingest", "weekly"], required=True)
    args = parser.parse_args()

    if args.mode == "prompt":
        send_message(
            "🌙 *Hora de fer el teu journaling diari!*\n\n"
            "Com ha anat el dia? Què has fet bé avui? "
            "Pots respondre directament amb un missatge de text o enviant una **nota de veu** de 45 segons."
        )

    elif args.mode == "ingest":
        update = get_unprocessed_updates()
        if not update:
            print("No hi ha cap missatge o àudio nou pendent a Telegram.")
            return

        print("Processant contingut amb Gemini...")
        parsed_data = process_input_with_gemini(update)

        print("Guardant a Notion...")
        page_url = create_daily_entry(parsed_data)

        send_message(
            f"✅ *Entrada registrada correctament a Notion!*\n\n"
            f"🧠 *Resum:* {parsed_data.summary}\n"
            f"🔥 *Victòria:* {parsed_data.daily_win}\n"
            f"[🔗 Obrir a Notion]({page_url})"
        )

    elif args.mode == "weekly":
        print Generant revisió setmanal...
        run_weekly_synthesis()

if __name__ == "__main__":
    main()
