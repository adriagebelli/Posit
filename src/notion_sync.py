from notion_client import Client
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from src.config import NOTION_API_KEY, NOTION_DAILY_DB_ID, NOTION_WEEKLY_DB_ID

notion = Client(auth=NOTION_API_KEY)

DIES_CATALA = ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte", "Diumenge"]

def create_daily_entry(data):
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    
    # Si s'executa de matinada (abans de les 8:00 h), l'entrada correspon al dia anterior
    if now.hour < 8:
        entry_date = now - timedelta(days=1)
    else:
        entry_date = now

    nom_dia = DIES_CATALA[entry_date.weekday()]
    # Títol en format DD/MM/AAAA - Dia (ex: 22/11/2026 - Diumenge)
    title_str = f"{entry_date.strftime('%d/%m/%Y')} - {nom_dia}"
    # Format ISO obligatori per a la columna de tipus Date de Notion
    iso_date = entry_date.strftime("%Y-%m-%d")

    new_page = notion.pages.create(
        parent={"database_id": NOTION_DAILY_DB_ID},
        properties={
            "Nom": {
                "title": [{"text": {"content": title_str}}]
            },
            "Data": {
                "date": {"start": iso_date}
            },
            "Victòria del dia": {
                "rich_text": [{"text": {"content": data.daily_win[:2000]}}]
            },
            "Resum breu": {
                "rich_text": [{"text": {"content": data.summary[:2000]}}]
            },
            "Estat d'ànim": {
                "number": data.mood
            },
            "Energia": {
                "number": data.energy
            },
            "Alarma a la 1a": {
                "checkbox": data.no_snooze
            },
            "Llit fet": {
                "checkbox": data.bed_made
            },
            "Etiquetes": {
                "multi_select": [{"name": tag} for tag in data.tags]
            }
        },
        children=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Feedback i pla d'acció"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": data.actionable_feedback[:2000]}}]
                }
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Transcripció íntegra"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": data.full_transcription[:2000]}}]
                }
            }
        ]
    )
    return new_page.get("url")
