"""
NeuTTS Air Streaming API Server

Clean, production-ready FastAPI server for TTS with voice cloning.
"""

import io
import os
import time
import uuid
from pathlib import Path
from typing import Generator

import numpy as np
import soundfile as sf
import torch
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from neuttsair.neutts import NeuTTSAir
from api.models import (
    SynthesizeRequest,
    SynthesizeResponse,
    VoiceListResponse,
    VoiceInfo,
    StatusResponse
)
from api.voice_manager import VoiceManager


# Directories
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

# Global state
tts_model = None
voice_manager = VoiceManager()


def initialize_model():
    """Initialize TTS model at startup"""
    global tts_model

    print("Initializing NeuTTS Air model...")
    tts_model = NeuTTSAir(
        backbone_repo="neuphonic/neutts-air-q8-gguf",
        backbone_device="cpu",
        codec_repo="neuphonic/neucodec-onnx-decoder",
        codec_device="cpu"
    )
    print("✓ Model initialized!")

    voice_manager.load_all_voices()
    print("✓ Server ready!")


def cleanup_old_files(max_files: int = 100):
    """Remove oldest generated audio files if count exceeds max"""
    files = sorted(OUTPUT_DIR.glob("*.wav"), key=lambda p: p.stat().st_mtime)
    if len(files) > max_files:
        for old_file in files[:-max_files]:
            old_file.unlink()
            print(f"Cleaned up: {old_file.name}")


# Create FastAPI app
app = FastAPI(
    title="NeuTTS Air API",
    description="Real-time TTS with voice cloning",
    version="2.0.0"
)

# Mount output directory for static file serving
app.mount("/audio", StaticFiles(directory=str(OUTPUT_DIR)), name="audio")


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    initialize_model()


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "model": "NeuTTS Air Q4 GGUF",
        "available_voices": list(voice_manager.voices.keys()),
        "default_voice": "dave"
    }


@app.get("/voices", response_model=VoiceListResponse)
async def list_voices():
    """List all available voices"""
    voices = voice_manager.list_voices()
    return VoiceListResponse(
        voices=[VoiceInfo(**v) for v in voices],
        count=len(voices)
    )


@app.post("/voices/add", response_model=StatusResponse)
async def add_voice(
    voice_name: str = Form(...),
    audio_file: UploadFile = File(...),
    reference_text: str = Form(...)
):
    """Add new voice reference"""
    if not tts_model:
        raise HTTPException(status_code=503, detail="Model not initialized")

    voice_name = voice_name.lower().strip()
    if not voice_name.isalnum():
        raise HTTPException(status_code=400, detail="Voice name must be alphanumeric")

    if voice_manager.get_voice(voice_name):
        raise HTTPException(status_code=400, detail=f"Voice '{voice_name}' already exists")

    try:
        # Save audio
        audio_path = Path("samples") / f"{voice_name}.wav"
        content = await audio_file.read()
        audio_path.write_bytes(content)

        # Encode reference
        print(f"Encoding voice: {voice_name}")
        ref_codes = tts_model.encode_reference(str(audio_path))

        # Add to manager
        voice_manager.add_voice(voice_name, ref_codes, reference_text, str(audio_path))

        print(f"✓ Voice '{voice_name}' added")
        return StatusResponse(status="success", message=f"Voice '{voice_name}' added")

    except Exception as e:
        # Cleanup on error
        if audio_path.exists():
            audio_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/voices/{voice_name}", response_model=StatusResponse)
async def delete_voice(voice_name: str):
    """Delete voice reference"""
    try:
        voice_manager.delete_voice(voice_name.lower())
        return StatusResponse(status="success", message=f"Voice '{voice_name}' deleted")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize(request: SynthesizeRequest, req: Request):
    """
    Synthesize speech and return audio URL

    Returns JSON with FULL audio URL (http://host:port/audio/file.wav)
    Perfect for mobile apps - can play URL directly.
    """
    if not tts_model:
        raise HTTPException(status_code=503, detail="Model not initialized")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    # Get voice
    voice_data = voice_manager.get_voice(request.voice)
    if not voice_data:
        raise HTTPException(
            status_code=404,
            detail=f"Voice '{request.voice}' not found. Available: {list(voice_manager.voices.keys())}"
        )

    try:
        start_time = time.time()
        print(f"[{request.voice}] Synthesizing: {request.text[:50]}...")

        # Generate audio
        chunks = []
        for chunk in tts_model.infer_stream(
            request.text,
            voice_data["codes"],
            voice_data["text"]
        ):
            chunks.append(chunk)

        full_audio = np.concatenate(chunks)

        # Save to file
        filename = f"{uuid.uuid4()}.wav"
        filepath = OUTPUT_DIR / filename
        sf.write(filepath, full_audio, 24000, format='WAV', subtype='PCM_16')

        # Cleanup old files
        cleanup_old_files()

        # Calculate metrics
        total_time = time.time() - start_time
        duration = len(full_audio) / 24000

        print(f"[{request.voice}] ✓ Generated {duration:.2f}s in {total_time:.2f}s")

        # Build full URL for mobile apps
        base_url = os.getenv("BASE_URL", f"{req.url.scheme}://{req.url.netloc}")
        full_audio_url = f"{base_url}/audio/{filename}"

        return SynthesizeResponse(
            audio_url=full_audio_url,
            duration=duration,
            voice=request.voice,
            generation_time=total_time
        )

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/synthesize/stream")
async def synthesize_stream(request: SynthesizeRequest):
    """
    Stream audio synthesis in real-time

    Returns streaming audio chunks as they're generated.
    """
    if not tts_model:
        raise HTTPException(status_code=503, detail="Model not initialized")

    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    voice_data = voice_manager.get_voice(request.voice)
    if not voice_data:
        raise HTTPException(status_code=404, detail=f"Voice '{request.voice}' not found")

    def generate_audio_stream() -> Generator[bytes, None, None]:
        try:
            start_time = time.time()
            first_chunk = True

            for chunk in tts_model.infer_stream(
                request.text,
                voice_data["codes"],
                voice_data["text"]
            ):
                if first_chunk:
                    ttfb = time.time() - start_time
                    print(f"[{request.voice}] First chunk: {ttfb:.2f}s")
                    first_chunk = False

                buffer = io.BytesIO()
                sf.write(buffer, chunk, 24000, format='WAV', subtype='PCM_16')
                buffer.seek(0)

                if not first_chunk:
                    buffer.seek(44)  # Skip WAV header

                yield buffer.read()

        except Exception as e:
            print(f"Streaming error: {e}")
            raise

    return StreamingResponse(
        generate_audio_stream(),
        media_type="audio/wav",
        headers={
            "Content-Disposition": f'inline; filename="{request.voice}_stream.wav"',
            "Cache-Control": "no-cache"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
