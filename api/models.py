"""
Pydantic models for API requests and responses
"""

from typing import Optional
from pydantic import BaseModel


class SynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = "dave"


class SynthesizeResponse(BaseModel):
    audio_url: str
    duration: float
    voice: str
    generation_time: float


class VoiceInfo(BaseModel):
    name: str
    text_path: str
    codes_path: str
    audio_path: Optional[str] = None
    has_audio: bool = False


class VoiceListResponse(BaseModel):
    voices: list[VoiceInfo]
    count: int


class StatusResponse(BaseModel):
    status: str
    message: str
