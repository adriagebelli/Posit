import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from google import genai
from src.config import validate_config, GEMINI_API_KEY, GEMINI_MODEL
from src.telegram_bot import send_message, get_unprocessed_updates
from src.gemini_extractor import process_input_with_gemini
from src.notion_sync import create_daily_entry
from src.weekly_engine import run_weekly_synthesis

def build_daily_prompt_instructions() -> str:
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    weekday = now.weekday()  # 0=Dl, 1=Dt, 2=Dc, 3=Dj, 4=Dv, 5=Ds, 6=Dg
    dies = ["dilluns", "dimarts", "dimecres", "dijous", "divendres", "dissabte", "diumenge"]
    nom_dia = dies[weekday]

    temes = [
        "1. HABIT TRACKER (OBLIGATORI): Pregunta directament i sense embuts si avui ha posposat l'alarma o s'ha llevat a la primera, i si s'ha fet el llit.",
        "2. VICTÒRIA DEL DIA (OBLIGATORI): Pregunta per una victòria concreta d'avui (gran o petita)."
    ]

    if weekday < 5:  # Dilluns a Divendres
        temes.append(
            "3. CLASSES I ENTRENO (OBLIGATORI AVUI): Pregunta com han anat les classes d'avui i com s'ha sentit a l'entrenament."
        )

    if weekday in [1, 3, 5]:  # Dimarts, Dijous, Dissabte (3 cops/setmana)
        temes.append(
            "4. PROJECTES PERSONALS (TOCA AVUI): Pregunta si està avançant amb els seus projectes personals, què li està fallant o en quin punt es trava."
        )

    if weekday in [0, 2, 6]:  # Dilluns, Dimecres, Diumenge (3 cops/setmana)
        temes.append(
            "4. ESTUDIS (TOCA AVUI): Pregunta com porta l'estudi i digues-li que si alguna assignatura concreta se li està travant o va malament, t'ho expliqui perquè li muntis un pla d'estudi."
        )

    llista_temes = "\n".join(temes)

    return (
        f"Avui és {nom_dia}. Ets Pòsit, el company de seguiment nocturn i rendiment personal de l'usuari. "
        "Redacta un missatge en català per a Telegram que sigui directe, àgil, amb personalitat i motivador "
        "(EVITA frases cursis o de teràpia com 'regala't una pausa breu' o 'com t'has sentit en aquell instant'). "
        "Ha de sonar com un col·lega exigent que vol que milloris cada dia, variant la forma d'escriure cada nit perquè no sigui avorrit.\n\n"
        "Has d'incloure OBLIGATÒRIAMENT tots aquests punts en el missatge:\n"
        f"{llista_temes}\n\n"
        "Acaba recordant breument que pot contestar amb text o nota de veu. "
        "IMPORTANT: NO utilitzis asteriscs (*), guions baixos (_) ni format Markdown, només text pla i algun emoji puntual."
    )

def main():
    validate_config()
    
    parser = argparse.ArgumentParser(description="Pòsit Journal Automation")
    parser.add_argument("--mode", choices=["prompt", "ingest", "weekly"], required=True)
    args = parser.parse_args()

    if args.mode == "prompt":
        client = genai.Client(api_key=GEMINI_API_KEY)
        instructions = build_daily_prompt_instructions()
        dynamic_prompt = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=instructions
        ).text
        
        send_message(f"☕ Pòsit de la nit\n\n{dynamic_prompt}")

    elif args.mode == "ingest":
        update = get_unprocessed_updates()
        if not update:
            print("No hi ha cap missatge o àudio nou pendent a Telegram.")
            return

        print("Processant contingut amb Gemini...")
        parsed_data = process_input_with_gemini(update)

        print("Guardant a Notion...")
        page_url = create_daily_entry(parsed_data)

        alarma_icon = "✅" if parsed_data.no_snooze else "❌"
        llit_icon = "✅" if parsed_data.bed_made else "❌"

        missatge_confirmacio = (
            f"✅ Entrada registrada a Pòsit!\n\n"
            f"⏰ Alarma a la 1a: {alarma_icon} | 🛏️ Llit fet: {llit_icon}\n"
            f"🧠 Resum: {parsed_data.summary}\n"
            f"🔥 Victòria: {parsed_data.daily_win}\n\n"
            f"💡 Feedback / Pla:\n{parsed_data.actionable_feedback}\n\n"
            f"🔗 Notion: {page_url}"
        )
        send_message(missatge_confirmacio)

    elif args.mode == "weekly":
        print("Generant revisió setmanal...")
        run_weekly_synthesis()

if __name__ == "__main__":
    main()
