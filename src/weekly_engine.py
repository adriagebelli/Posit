from google import genai
from datetime import datetime
from src.config import GEMINI_API_KEY
from src.notion_sync import get_last_7_days_entries, create_weekly_review_entry
from src.telegram_bot import send_message

def run_weekly_synthesis():
    raw_data = get_last_7_days_entries()
    if not raw_data:
        send_message("⚠️ No s'han trobat entrades de diari aquesta setmana per generar la revisió.")
        return

    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = (
        "Aquí tens les entrades de diari dels últims 7 dies:\n\n"
        f"{raw_data}\n\n"
        "Fes una anàlisi executiva en català estructurada en:\n"
        "1. Èxits principals de la setmana.\n"
        "2. Patrons de cansament o bloquejos detectats.\n"
        "3. Exactament 3 accions clau i pràctiques per a la setmana vinent."
    )

    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=prompt
    )
    
    synthesis = response.text
    week_title = f"Setmana {datetime.now().isocalendar()[1]} ({datetime.now().year})"
    
    # Guardar a Notion
    page_url = create_weekly_review_entry(synthesis, week_title)

    # Enviar xut de dopamina a Telegram
    message = (
        f"🏆 *Revisió Setmanal Completada* ({week_title})\n\n"
        f"{synthesis}\n\n"
        f"[📄 Veure a Notion]({page_url})"
    )
    send_message(message)
