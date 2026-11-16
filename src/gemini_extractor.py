from pydantic import BaseModel
from typing import List
from google import genai
from google.genai import types
from src.config import GEMINI_API_KEY

class DailyJournalEntry(BaseModel):
    summary: str
    daily_win: str
    mood: int  # 1 a 5
    energy: int  # 1 a 5
    tags: List[str]
    full_transcription: str

def process_input_with_gemini(input_data: dict) -> DailyJournalEntry:
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = (
        "Analitza aquesta reflexió diària (ja sigui text escrit o transcripció d'àudio) de Pòsit. "
        "Estructura el resultat segons l'esquema sol·licitat: "
        "Fes un resum executiu (summary), extreu la victòria o èxit del dia (daily_win), "
        "puntua l'estat d'ànim de l'1 al 5 (mood), l'energia de l'1 al 5 (energy), "
        "assigna etiquetes rellevants en català (ex: Entrenament, Productivitat, Universitat, Hàbits, Descans) (tags), "
        "i neteja o adjunta el text sencer (full_transcription)."
    )

    contents = []

    if input_data["type"] == "voice":
        audio_file_ref = client.files.upload(file=input_data["path"])
        contents = [audio_file_ref, prompt]
    else:
        contents = [f"Text de l'usuari: {input_data['content']}", prompt]

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DailyJournalEntry,
            temperature=0.2,
        ),
    )

    return response.parsed
