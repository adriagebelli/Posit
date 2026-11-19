from google import genai
from datetime import datetime
from zoneinfo import ZoneInfo
from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.notion_sync import get_last_7_days_entries, create_weekly_review_entry
from src.telegram_bot import send_message

def run_weekly_synthesis():
    weekly_data = get_last_7_days_entries()
    if not weekly_data["text"]:
        send_message("⚠️ No s'han trobat entrades de diari aquesta setmana per generar la revisió.")
        return

    alarm_fails = weekly_data["alarm_fails"]
    bed_fails = weekly_data["bed_fails"]
    total_days = weekly_data["total_days"]

    if alarm_fails > 1 or bed_fails > 1:
        habit_instruction = (
            f"ATENCIÓ - BRONCA OBLIGATÒRIA: Aquesta setmana (sobre {total_days} dies registrats), l'usuari ha posposat l'alarma {alarm_fails} dies "
            f"i no s'ha fet el llit {bed_fails} dies. Com que ha fallat més d'un dia, dedica un apartat específic a fotre-li una bona bronca directa, "
            "sense paternalismes ni suavitzar-ho: digues-li que aquests dos hàbits són la base mínima del dia i que la setmana vinent s'ha d'esforçar molt més."
        )
    else:
        habit_instruction = (
            f"CONTROL D'HÀBITS SUPERAT: Sobre {total_days} dies, només ha fallat l'alarma {alarm_fails} cop i el llit {bed_fails} cop. "
            "Felicita'l breument per mantenir la disciplina matinal."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = (
        f"Aquí tens el registre dels últims {total_days} dies de Pòsit:\n\n"
        f"{weekly_data['text']}\n\n"
        f"{habit_instruction}\n\n"
        "Redacta l'informe setmanal en català (text pla, SENSE asteriscs ni Markdown) estructurat en:\n"
        "1. Veredicte d'hàbits (Alarma i Llit).\n"
        "2. Èxits principals de la setmana (victòries, entrenaments, projectes i estudis).\n"
        "3. Patrons de cansament o bloquejos detectats.\n"
        "4. Exactament 3 accions concretes per a la setmana vinent."
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )
    
    synthesis = response.text
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    week_title = f"Setmana {now.isocalendar()[1]} ({now.year})"
    
    page_url = create_weekly_review_entry(synthesis, week_title)

    message = (
        f"🏆 Revisió Setmanal Pòsit ({week_title})\n"
        f"📊 Fallades alarma: {alarm_fails}/{total_days} | Fallades llit: {bed_fails}/{total_days}\n\n"
        f"{synthesis}\n\n"
        f"📄 Veure a Notion: {page_url}"
    )
    send_message(message)
