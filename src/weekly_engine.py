from google import genai
from datetime import datetime
from zoneinfo import ZoneInfo
from src.config import GEMINI_API_KEY, GEMINI_MODEL
from src.notion_sync import get_last_7_days_entries, create_weekly_review_entry
from src.telegram_bot import send_message

def run_weekly_synthesis():
    weekly_data = get_last_7_days_entries()
    if not weekly_data["text"]:
        send_message("⚠️ No s'han trobat entrades dels últims 7 dies per generar la revisió setmanal.")
        return

    alarm_fails = weekly_data["alarm_fails"]
    bed_fails = weekly_data["bed_fails"]
    days_with_any_fail = weekly_data["days_with_any_fail"]
    total_days = weekly_data["total_days"]

    habit_summary = (
        f"Dies registrats: {total_days} | "
        f"Fallades alarma: {alarm_fails} | "
        f"Fallades llit: {bed_fails} | "
        f"Dies amb alguna fallada d'hàbits: {days_with_any_fail}"
    )

    if alarm_fails > 1 or bed_fails > 1 or days_with_any_fail > 1:
        habit_instruction = (
            f"ATENCIÓ - BRONCA OBLIGATÒRIA: Aquesta setmana ({habit_summary}), l'usuari ha fallat els hàbits matinals més d'un dia. "
            "Dedica el primer apartat a fotre-li una bona bronca directa i exigent: deixa-li clar que posposar l'alarma o deixar el llit sense fer "
            "és fallar en el mínim bàsic del dia i que la setmana vinent s'ha d'esforçar molt més per no repetir aquests errors."
        )
    else:
        habit_instruction = (
            f"CONTROL D'HÀBITS SUPERAT: Aquesta setmana ({habit_summary}) ha mantingut el compromís amb l'alarma i el llit. "
            "Reconeix-li breument la disciplina i anima'l a mantenir el nivell."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = (
        f"Aquí tens el registre dels últims 7 dies de Pòsit:\n\n"
        f"{weekly_data['text']}\n\n"
        f"{habit_instruction}\n\n"
        "Redacta l'informe setmanal en català estàndard impecable (revisa ortografia i accents abans de respondre; "
        "text pla SENSE asteriscs ni Markdown) estructurat en:\n"
        "1. Veredicte d'hàbits (Alarma a la 1a i Llit fet).\n"
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

    page_url = create_weekly_review_entry(synthesis, week_title, habit_summary)

    message = (
        f"🏆 Revisió Setmanal Pòsit ({week_title})\n"
        f"📊 {habit_summary}\n\n"
        f"{synthesis}\n\n"
        f"📄 Veure a Notion: {page_url}"
    )
    send_message(message)
