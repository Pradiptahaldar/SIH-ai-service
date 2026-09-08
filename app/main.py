from fastapi import FastAPI, UploadFile, File, Form, Query, HTTPException, Request, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import os
import tempfile
import secrets

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.ai.similarity.detector import detect_similarity, image_to_text
from app.processing.image import process_image
from app.processing.audio import process_audio
from app.ai.pipeline.analyzer import analyze_challenge

limiter = Limiter(key_func=get_remote_address)
AI_SERVICE_API_KEY= os.getenv("AI_SERVICE_API_KEY")

def verify_api_key(api_key:str | None= Header(None, alias="X-API-Key")):
    if not AI_SERVICE_API_KEY:
        raise HTTPException(status_code=500, detail= "AI service API key is not configured")
    if not api_key or not secrets.compare_digest(api_key, AI_SERVICE_API_KEY):
        raise HTTPException(status_code=401, detail= "invalid API key")

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/m4a",
    "audio/webm"
}
def validate_content_type(file: UploadFile, allowed_types: set[str]):
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

MAX_IMAGE_SIZE = 5 * 1024 * 1024
MAX_AUDIO_SIZE = 10 * 1024 * 1024
MAX_CHALLENGE_LENGTH = 5000

async def read_limited_file(file: UploadFile, max_size: int):
    data = await file.read(max_size + 1)

    if len(data) > max_size:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is too large"
        )

    return data

app = FastAPI(
    title="SIH ai service",
    description="ai for sih 2026",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error"
        }
    )
app.state.limiter = limiter
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests. Please try again later."
        }
    )

@app.get("/")
def root():
    return {"message": "ai service running"}

@app.post("/analyze", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/second")
async def analyze(
    request: Request,
    challenge: str = Query(..., min_length=1, max_length=MAX_CHALLENGE_LENGTH),
    images: list[UploadFile] | None = File(None, description="up to 5 images related to the challenge"),
    audio: UploadFile | None = File(None)
):
    image_result = None
    audio_result = None

    if images:
        if len(images) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 images are allowed"
            )

        image_result = []

        for image in images:
            validate_content_type(image, ALLOWED_IMAGE_TYPES)

            image_data = await read_limited_file(
                image,
                MAX_IMAGE_SIZE
            )

            result = process_image(image_data)
            image_result.append(result)

    if audio:
        validate_content_type(audio, ALLOWED_AUDIO_TYPES)
        audio_data = await read_limited_file(audio, MAX_AUDIO_SIZE)

        suffix = os.path.splitext(audio.filename or "")[1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(audio_data)
            audio_path = temp_file.name

        try:
            audio_result = process_audio(audio_path)
        finally:
            os.unlink(audio_path)

    return analyze_challenge(
        challenge=challenge,
        image_result=image_result,
        audio_result=audio_result
    )
@app.post("/similarity", dependencies=[Depends(verify_api_key)])
@limiter.limit("20/second")
async def similarity(
    request: Request,
    challenge: str | None = Form(None),
    existing_challenges: str = Form(..., max_length=100000),
    images: list[UploadFile] | None = File(default=[], description="up to 5 images related to the challenge")
):

    if existing_challenges:
        existing_list = [
            item.strip()
            for item in existing_challenges.split(",")
            if item.strip()
        ]
    else:
        existing_list = []

    similarity_text = challenge

    if images:
        if len(images) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 images are allowed"
            )

        image_results = []

        for image in images:
            validate_content_type(image, ALLOWED_IMAGE_TYPES)

            image_data = await read_limited_file(
                image,
                MAX_IMAGE_SIZE
            )

            result = process_image(image_data)
            image_results.append(result)

        image_texts = []

        for image_result in image_results:
            text = image_to_text(image_result)

            if text:
                image_texts.append(text)

        if image_texts:
            similarity_text = " ".join(image_texts)

    if not similarity_text:
        return {
            "error": "Challenge text or image is required"
        }

    return detect_similarity(
        challenge=similarity_text,
        existing_challenges=existing_list
    )
@app.post("/upload-image", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/second")
async def upload_image(
    request: Request,
    files: list[UploadFile] = File(
        ...,
        description="Up to 5 images"
    )
):
    if len(files) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 images are allowed"
        )

    results = []

    for file in files:
        validate_content_type(file, ALLOWED_IMAGE_TYPES)

        image_data = await read_limited_file(
            file,
            MAX_IMAGE_SIZE
        )

        image_info = process_image(image_data)

        results.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(image_data),
            "image": image_info
        })

    return {
        "images": results
    }


@app.post("/upload-audio", dependencies=[Depends(verify_api_key)])
@limiter.limit("10/second")
async def upload_audio(request: Request,
                       file: UploadFile = File(...)):
    validate_content_type(file, ALLOWED_AUDIO_TYPES)

    audio_data = await read_limited_file(file, MAX_AUDIO_SIZE)

    suffix = os.path.splitext(file.filename or "")[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(audio_data)
        audio_path = temp_file.name

    try:
        result = process_audio(audio_path)
    finally:
        os.unlink(audio_path)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(audio_data),
        "audio": result
    }