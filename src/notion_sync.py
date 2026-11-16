from notion_client import Client
from datetime import datetime
from src.config import NOTION_API_KEY, NOTION_DAILY_DB_ID, NOTION_WEEKLY_DB_ID

notion = Client(auth=NOTION_API_KEY)

def create_daily_entry(data):
    today_str = datetime.now().strftime("%Y-%m-%d - %A")
    
    new_page = notion.pages.create(
        parent={"database_id": NOTION_DAILY_DB_ID},
        properties={
            "Nom": {
                "title": [{"text": {"content": today_str}}]
            },
            "Data": {
                "date": {"start": datetime.now().strftime("%Y-%m-%d")}
            },
            "Victòria del dia": {
                "rich_text": [{"text": {"content": data.daily_win}}]
            },
            "Resum breu": {
                "rich_text": [{"text": {"content": data.summary}}]
            },
            "Estat d'ànim": {
                "number": data.mood
            },
            "Energia": {
                "number": data.energy
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
                    "rich_text": [{"type": "text", "text": {"content": "Transcripció íntegra de la nota"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": data.full_transcription}}]
                }
            }
        ]
    )
    return new_page.get("url")

def get_last_7_days_entries():
    response = notion.databases.query(
        database_id=NOTION_DAILY_DB_ID,
        page_size=7
    )
    entries_text = []
    for page in response.get("results", []):
        props = page["properties"]
        try:
            date = props["Data"]["date"]["start"]
            summary = props["Resum breu"]["rich_text"][0]["text"]["content"]
            win = props["Victòria del dia"]["rich_text"][0]["text"]["content"]
            entries_text.append(h := f"Data: {date} | Resum: {summary} | Victòria: {win}")
        except Exception:
            continue
    return "\n".join(entries_text)

def create_weekly_review_entry(synthesis_text: str, week_title: str):
    new_page = notion.pages.create(
        parent={"database_id": NOTION_WEEKLY_DB_ID},
        properties={
            "Setmana": {
                "title": [{"text": {"content": week_title}}]
            },
            "Rang de dates": {
                "date": {"start": datetime.now().strftime("%Y-%m-%d")}
            },
            "Patró detectat": {
                "rich_text": [{"text": {"content": "Anàlisi setmanal automatitzada generada per Gemini."}}]
            },
            "Accions Clau": {
                "rich_text": [{"text": {"content": synthesis_text[:2000]}}]
            }
        }
    )
    return new_page.get("url")
