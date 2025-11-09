import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import edge_tts
import base64
import re
import os

import uuid
from DB.deps import db_dependency
from DB.db_models import VoiceExplanation
from auth.deps import user_dependency

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
router = APIRouter(prefix="/voice", tags=["Voice"])

class TTSRequest(BaseModel):
    text: str
    note_id: str


# Initialize OpenAI client with Hugging Face router
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)


# ----------- Helper: Clean Markdown and Symbols -----------
def clean_markdown(text: str) -> str:
    """Remove markdown symbols and fix abbreviations."""
    text = re.sub(r"[*_#>-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ----------- Helper: Call Hugging Face model -----------
def format_explanation_text(text: str) -> str:
    """Call a Hugging Face model to make text expressive and polite."""
    prompt = f"""
You are an educational narrator.
Rewrite the following notes into a clear, polite, and expressive explanation.
Make it sound engaging and natural, without markdown or bullet symbols.

Input Notes:
{text}
    """

    try:
        response = client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.2:featherless-ai",
            messages=[
                {"role": "system", "content": "You are a friendly and expressive narrator."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
        )

        # Extract formatted text
        output = response.choices[0].message.content
        return output.strip()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HF API error: {e}")


# ----------- Helper: Generate TTS (MODIFIED FUNCTION) -----------
async def synthesize_audio_with_timestamps(text: str, file_name: str):
    os.makedirs("outputs/voice_cache", exist_ok=True)
    output_audio_path = f"outputs/voice_cache/{file_name}.wav"
    output_timing_path = f"outputs/voice_cache/{file_name}_timing.json"

    # ❗ DO NOT manually wrap in <speak> or <voice> here — edge_tts does it internally.
    communicate = edge_tts.Communicate(
    text=text,
    voice="en-GB-RyanNeural",  # ✅ Supports word boundaries
    rate="+10%",
    pitch="-10Hz",
)

    timings = []
    audio_data = b""

    print(f"--- TTS: Starting synthesis for {len(text)} chars ---")

    try:
        async for event in communicate.stream():
            etype = event["type"]
            if etype == "WordBoundary":
                offset_sec = event["offset"] / 10_000_000
                duration_sec = event["duration"] / 10_000_000
                timings.append({
                    "text": event["text"],
                    "time": offset_sec,
                    "end": offset_sec + duration_sec,
                })
            elif etype == "audio":
                audio_data += event["data"]
            elif etype == "end":
                print(f"--- TTS stream finished ---")
                break
    except Exception as e:
        print(f"[ERROR] edge_tts stream failed: {e}")
        raise e

    # Save both audio + timings
    with open(output_audio_path, "wb") as f:
        f.write(audio_data)

    with open(output_timing_path, "w") as f:
        json.dump(timings, f)

    print(f"✅ Generated {len(timings)} word timings for {file_name}.wav")

    audio_b64 = base64.b64encode(audio_data).decode("utf-8")
    return audio_b64, timings, output_audio_path
def _timing_path_from_audio(audio_path: str) -> str:
    root, ext = os.path.splitext(audio_path)
    return f"{root}_timing.json"


# ----------- Route -----------
@router.post("/tts")
async def text_to_speech(req: TTSRequest, db: db_dependency, user: user_dependency):
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text not allowed")

    existing = (
        db.query(VoiceExplanation)
        .filter_by(note_id=req.note_id, user_id=user.id)
        .first()
    )

    if existing and os.path.exists(existing.audio_path):
        # ... (rest of your caching logic is fine)
        timing_path = _timing_path_from_audio(existing.audio_path)
        if not os.path.exists(timing_path):
            formatted_text = format_explanation_text(text)
            cleaned_text = clean_markdown(formatted_text)
            file_name = os.path.splitext(os.path.basename(existing.audio_path))[0]
            audio_b64, timings, audio_path = await synthesize_audio_with_timestamps(cleaned_text, file_name)
            
            if audio_path != existing.audio_path:
                existing.audio_path = audio_path
                existing.formatted_text = formatted_text
                existing.cleaned_text = cleaned_text
                db.commit()
        
        with open(existing.audio_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")
        with open(_timing_path_from_audio(existing.audio_path), "r") as tf:
            timings = json.load(tf)

        return {
            "audio": audio_b64,
            "formatted_text": existing.formatted_text,
            "cleaned_text": existing.cleaned_text,
            "timings": timings,
            "cached": True,
        }

    # No cache ‚Üí generate fresh
    try:
        formatted_text = format_explanation_text(text)
        cleaned_text = clean_markdown(formatted_text)
        file_name = str(uuid.uuid4())
        audio_b64, timings, audio_path = await synthesize_audio_with_timestamps(cleaned_text, file_name)
    except Exception as e:
        # This will now catch the error from synthesize_audio_async
        print(f"[ERROR] TTS generation failed in main route: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}")

    new_voice = VoiceExplanation(
        note_id=req.note_id,
        user_id=user.id,
        formatted_text=formatted_text,
        cleaned_text=cleaned_text,
        audio_path=audio_path,
    )
    db.add(new_voice)
    db.commit()

    return {
        "audio": audio_b64,
        "formatted_text": formatted_text,
        "cleaned_text": cleaned_text,
        "timings": timings,
        "cached": False,
    }