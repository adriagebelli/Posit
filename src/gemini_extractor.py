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
    no_snooze: bool  # True si s'ha llevat a la primera (no ha posposat l'alarma)
    bed_made: bool  # True si s'ha fet el llit
    tags: List[str]
    actionable_feedback: str  # Pla d'estudi, desbloqueig de projectes o feedback directe
    full_transcription: str

def process_input_with_gemini(input_data: dict) -> DailyJournalEntry:
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = (
        "Analitza aquesta reflexió nocturna (text o nota de veu) de Pòsit i extreu les dades segons l'esquema JSON en català estàndard sense faltes d'ortografia:\n"
        "- summary: Resum executiu del dia en 2-3 frases.\n"
        "- daily_win: La victòria o assoliment principal del dia.\n"
        "- mood: Estat d'ànim de l'1 al 5.\n"
        "- energy: Nivell d'energia de l'1 al 5.\n"
        "- no_snooze: True NOMÉS si indica clarament que s'ha llevat a la primera o que NO ha posposat l'alarma. False si l'ha posposat o no ho menciona.\n"
        "- bed_made: True NOMÉS si indica clarament que s'ha fet el llit. False si no se l'ha fet o no ho menciona.\n"
        "- tags: Etiquetes rellevants en català estàndard (ex: Entrenament, Universitat, Projectes, Estudi, Hàbits, Descans).\n"
        "- actionable_feedback: Text pla en català estàndard (SENSE asteriscs ni Markdown). "
        "Si explica que va malament o encallat en una assignatura concreta, proposa un pla d'estudi pràctic en 3-4 passos concrets. "
        "Si comenta un bloqueig en un projecte personal, proposa el següent pas mínim per desencallar-lo. "
        "Si tot ha anat bé, fes un retorn breu i directe (amb un toc d'atenció curt si ha fallat l'alarma o el llit).\n"
        "- full_transcription: Transcripció completa i neta del missatge o àudio."
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
            temperature=0.2,
        ),
    )

    return response.parsed
