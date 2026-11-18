import argparse
from google import genai
from src.config import validate_config, GEMINI_API_KEY
from src.telegram_bot import send_message, get_unprocessed_updates
from src.gemini_extractor import process_input_with_gemini
from src.notion_sync import create_daily_entry
from src.weekly_engine import run_weekly_synthesis
from google.genai import types

def main():
    validate_config()
    
    parser = argparse.ArgumentParser(description="Pòsit Journal Automation")
    parser.add_argument("--mode", choices=["prompt", "ingest", "weekly"], required=True)
    args = parser.parse_args()

    if args.mode == "prompt":
        # Generem un missatge dinàmic i fresc cada nit amb Gemini
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=(
        "Escriu el missatge nocturn de journaling de Pòsit, en català estàndard i "
        "amb ortografia i gramàtica impecables.\n\n"
        "Requisits:\n"
        "- Adreça't a la persona amb un to proper, natural i respectuós.\n"
        "- Fes una pregunta principal concreta i oberta, no una pregunta genèrica "
        "com «Com ha anat el dia?».\n"
        "- Afegeix com a màxim dues preguntes breus per aprofundir.\n"
        "- Tria un focus per al missatge: estat d'ànim i energia, activitat física, "
        "estudi o feina, hàbits o una petita victòria del dia. No intentis cobrir-ho tot.\n"
        "- Convida a explicar un moment o exemple concret d'avui.\n"
        "- No inventis informació sobre la persona ni repeteixis idees amb altres paraules.\n"
        "- Recorda que pot respondre amb text o amb una nota de veu.\n"
        "- Retorna només el missatge final, revisat, sense explicacions ni etiquetes."
    ),
    config=types.GenerateContentConfig(temperature=0.3),
)

dynamic_prompt = (response.text or "").strip()
        
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
