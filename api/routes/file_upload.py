from fastapi import APIRouter, Query, UploadFile, File, Form, HTTPException
from typing import Literal
import json

from utils.redis_handler import redis_client as redis
from utils.pdf_parser import extract_text_from_pdf
from utils.image_parser import extract_text_from_image

router = APIRouter()

MAX_FILES = 5

@router.post("/upload-file")
async def upload_file(file: UploadFile = File(...), session_id: str = Form(...)):
    filename = file.filename.lower()

    # Validate file type
    if not (filename.endswith(".pdf") or filename.endswith((".png", ".jpg", ".jpeg"))):
        raise HTTPException(status_code=400, detail="Unsupported file format")

    contents = await file.read()

    # Extract based on file type
    if filename.endswith(".pdf"):
        extracted_text = extract_text_from_pdf(contents)
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        extracted_text = extract_text_from_image(contents)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Store extracted text temporarily in Redis
    redis_key = f"session_extracted_text:{session_id}"

    # Get existing uploads
    existing = await redis.get(redis_key)
    file_list = json.loads(existing) if existing else []

    if len(file_list) >= MAX_FILES:
        raise HTTPException(status_code=400, detail="You can upload a maximum of 5 files per session.")

    # Append new file
    file_list.append({
        "filename": filename,
        "text": extracted_text[:1000]  # optionally truncate if text is very large
    })

    await redis.set(redis_key, json.dumps(file_list), ex=3600)

    return {"text": extracted_text, "uploaded_count": len(file_list)}

@router.delete("/reset-upload")
async def reset_uploaded_files(session_id: str = Query(...)):
    redis_key = f"session_extracted_text:{session_id}"
    await redis.delete(redis_key)
    return {"status": "reset done"}