from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types
from src.config import GEMINI_API_KEY, GEMINI_MODEL

class DailyJournalEntry(BaseModel):
    summary: str
    daily_win: str
    mood: int  # 1 a 5
    energy: int  # 1 a 5
    no_snooze: bool  # True si NO ha posposat l'alarma, False si l'ha posposat o no ha complert
    bed_made: bool  # True si s'ha fet el llit, False si no se l'ha fet
    tags: List[str]
    actionable_feedback: str  # Pla d'estudi si va malament en alguna assignatura, consell per desbloquejar projectes o feedback breu
    full_transcription: str

def process_input_with_gemini(input_data: dict) -> DailyJournalEntry:
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = (
        "Analitza aquesta reflexió nocturna (text o nota de veu) de Pòsit i extreu les dades segons l'esquema JSON:\n"
        "- summary: Resum executiu del dia en 2-3 frases en català.\n"
        "- daily_win: La victòria o moment positiu destacat.\n"
        "- mood: Estat d'ànim de l'1 al 5.\n"
        "- energy: Nivell d'energia de l'1 al 5.\n"
        "- no_snooze: True NOMÉS si diu que s'ha llevat a la primera / NO ha posposat l'alarma. False si l'ha posposat o no ho menciona.\n"
        "- bed_made: True NOMÉS si diu que s'ha fet el llit. False si no se l'ha fet o no ho menciona.\n"
        "- tags: Etiquetes rellevants en català (ex: Entrenament, Universitat, Projectes, Estudi, Hàbits, Descans).\n"
        "- actionable_feedback: Camp clau en català (sense asteriscs ni Markdown). "
        "Si menciona que va malament o encallat en alguna assignatura concreta, proposa-li un pla d'estudi pràctic i concret en 3-4 passos per remuntar-la. "
        "Si menciona que està travat en un projecte personal, proposa-li el següent pas mínim per desbloquejar-se. "
        "Si tot va bé, fes un comentari directe de reforç (o un toc d'atenció breu si ha fallat l'alarma o el llit).\n"
        "- full_transcription: Transcripció completa i neta del que ha dit/escrit."
    )

    if input_data["type"] == "voice":
        audio_file_ref = client.files.upload(file=input_data["path"])
        contents = [audio_file_ref, prompt]
    else:
        contents = [f"Text de l'usuari: {input_data['content']}", prompt]

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DailyJournalEntry,
            temperature=0.3,
        ),
    )

    return response.parsed
