import argparse
from google import genai
from src.config import validate_config, GEMINI_API_KEY
from src.telegram_bot import send_message, get_unprocessed_updates
from src.gemini_extractor import process_input_with_gemini
from src.notion_sync import create_daily_entry
from src.weekly_engine import run_weekly_synthesis

def main():
    validate_config()
    
    parser = argparse.ArgumentParser(description="Pòsit Journal Automation")
    parser.add_argument("--mode", choices=["prompt", "ingest", "weekly"], required=True)
    args = parser.parse_args()

    if args.mode == "prompt":
        # Generem un missatge dinàmic i fresc cada nit amb Gemini
        client = genai.Client(api_key=GEMINI_API_KEY)
        dynamic_prompt = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=(
                "Genera un missatge breu en català per a Telegram per iniciar el journaling nocturn de Pòsit. "
                "El missatge ha de ser motivador, proper i no avorrit. Ha de convidar a reflexionar de manera natural "
                "sobre com ha anat el dia (energia i estat d'ànim), l'entrenament o activitat física, la productivitat/estudi, "
                "i algun hàbit o reflexió de desenvolupament personal. "
                "Recorda-li que pot respondre tant escrivint un missatge de text com enviant una nota de veu. "
                "Evita llistes de preguntes rígides; planteja-ho com un xat amigable."
            )
        ).text
        
        send_message(f"☕ *Pòsit de la nit*\n\n{dynamic_prompt}")

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
            f"✅ *Entrada registrada a Pòsit (Notion)!*\n\n"
            f"🧠 *Resum:* {parsed_data.summary}\n"
            f"🔥 *Victòria:* {parsed_data.daily_win}\n"
            f"[🔗 Obrir a Notion]({page_url})"
        )

    elif args.mode == "weekly":
        print("Generant revisió setmanal...")
        run_weekly_synthesis()

if __name__ == "__main__":
    main()
