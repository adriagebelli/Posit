from notion_client import Client
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from src.config import NOTION_API_KEY, NOTION_DAILY_DB_ID, NOTION_WEEKLY_DB_ID

notion = Client(auth=NOTION_API_KEY)

DIES_CATALA = ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte", "Diumenge"]

def create_daily_entry(data):
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    nom_dia = DIES_CATALA[now.weekday()]
    today_str = f"{now.strftime('%Y-%m-%d')} - {nom_dia}"

    new_page = notion.pages.create(
        parent={"database_id": NOTION_DAILY_DB_ID},
        properties={
            "Nom": {
                "title": [{"text": {"content": today_str}}]
            },
            "Data": {
                "date": {"start": now.strftime("%Y-%m-%d")}
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

def get_last_7_days_entries():
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    seven_days_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")

    response = notion.databases.query(
        database_id=NOTION_DAILY_DB_ID,
        filter={
            "property": "Data",
            "date": {
                "on_or_after": seven_days_ago
            }
        },
        sorts=[{"property": "Data", "direction": "descending"}],
        page_size=14
    )

    entries_text = []
    alarm_fails = 0
    bed_fails = 0
    days_with_any_fail = 0

    for page in response.get("results", []):
        props = page["properties"]
        try:
            date = props["Data"]["date"]["start"] if props.get("Data", {}).get("date") else "Sense data"
            summary = props["Resum breu"]["rich_text"][0]["text"]["content"] if props.get("Resum breu", {}).get("rich_text") else ""
            win = props["Victòria del dia"]["rich_text"][0]["text"]["content"] if props.get("Victòria del dia", {}).get("rich_text") else ""

            no_snooze = props.get("Alarma a la 1a", {}).get("checkbox", False)
            bed_made = props.get("Llit fet", {}).get("checkbox", False)

            if not no_snooze:
                alarm_fails += 1
            if not bed_made:
                bed_fails += 1
            if not no_snooze or not bed_made:
                days_with_any_fail += 1

            entries_text.append(
                f"Data: {date} | Alarma a la 1a: {'Sí' if no_snooze else 'FALLAT'} | "
                f"Llit fet: {'Sí' if bed_made else 'FALLAT'} | Resum: {summary} | Victòria: {win}"
            )
        except Exception:
            continue

    return {
        "text": "\n".join(entries_text),
        "total_days": len(entries_text),
        "alarm_fails": alarm_fails,
        "bed_fails": bed_fails,
        "days_with_any_fail": days_with_any_fail
    }

def create_weekly_review_entry(synthesis_text: str, week_title: str, habit_summary: str):
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    new_page = notion.pages.create(
        parent={"database_id": NOTION_WEEKLY_DB_ID},
        properties={
            "Setmana": {
                "title": [{"text": {"content": week_title}}]
            },
            "Rang de dates": {
                "date": {"start": now.strftime("%Y-%m-%d")}
            },
            "Patró detectat": {
                "rich_text": [{"text": {"content": habit_summary[:2000]}}]
            },
            "Accions Clau": {
                "rich_text": [{"text": {"content": synthesis_text[:2000]}}]
            }
        }
    )
    return new_page.get("url")
