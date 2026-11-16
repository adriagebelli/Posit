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
        "Analitza aquest missatge o nota de veu de journaling nocturn d'un estudiant d'enginyeria. "
        "Fes una transcripció íntegra o netejada del text (full_transcription), "
        "redacta un resum breu (summary), destaca la victòria o èxit del dia (daily_win), "
        "puntuació l'estat d'ànim de l'1 al 5 (mood), l'energia de l'1 al 5 (energy), "
        "i assigna etiquetes rellevants en català com ara Entrenament, Projectes, Universitat, Social o Descans (tags)."
    )

    contents = []

    if input_data["type"] == "voice":
        # Pugem el fitxer d'àudio temporalment a Gemini File API
        audio_file_ref = client.files.upload(file=input_data["path"])
        contents = [audio_file_ref, prompt]
    else:
        contents = [f"Text de l'usuari: {input_data['content']}", prompt]

    # Crida estructurada amb gemini-2.5-flash
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DailyJournalEntry,
            temperature=0.2,
        ),
    )

    # El SDK retorna un objecte estructurat directament validat per Pydantic gràcies a response.parsed
    return response.parsed
