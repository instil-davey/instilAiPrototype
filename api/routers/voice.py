"""Voice synthesis proxy for OpenVoice or fallback tone."""
import base64
import io
import os
import subprocess
import tempfile
import json
import logging
import math
import struct
import wave
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import urllib.request

from config import settings
from api.schemas import VoiceAgentRequest, VoiceAgentResponse
from api.services.voice_agent import VoiceAgentOrchestrator


logger = logging.getLogger(__name__)


class VoiceRequest(BaseModel):
    text: str = Field(..., min_length=1)
    speaker: Optional[str] = None


class VoiceResponse(BaseModel):
    audio_base64: str
    mime_type: str = "audio/wav"


router = APIRouter(prefix="/voice", tags=["Voice"])


def get_voice_agent() -> VoiceAgentOrchestrator:
    if not settings.ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="Anthropic API key not configured")
    return VoiceAgentOrchestrator()


def _generate_tone(duration: float = 0.4, freq: int = 440) -> bytes:
    sample_rate = 16000
    amplitude = 16000
    frames = []
    for i in range(int(duration * sample_rate)):
        value = int(amplitude * math.sin(2 * math.pi * freq * i / sample_rate))
        frames.append(struct.pack('<h', value))
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    return buffer.getvalue()


def _speech_fallback_tts(text: str) -> bytes:
    """Use macOS `say` to generate PCM audio and return bytes."""
    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp_in:
        input_path = tmp_in.name
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_out:
        output_path = tmp_out.name

    try:
        subprocess.run(
            ["say", "-o", input_path, text],
            check=True,
            timeout=15,
        )
        subprocess.run(
            ["afconvert", input_path, output_path, "-d", "LEI16", "-f", "WAVE"],
            check=True,
            timeout=10,
        )
        with open(output_path, "rb") as audio_file:
            return audio_file.read()
    finally:
        try:
            os.remove(input_path)
        except OSError:
            pass
        try:
            os.remove(output_path)
        except OSError:
            pass


@router.post("/speak", response_model=VoiceResponse)
def speak(request: VoiceRequest) -> VoiceResponse:
    """
    Generate speech audio using OpenVoice server or a local placeholder tone.
    """
    base_url = settings.OPENVOICE_SERVER_URL if settings.OPENVOICE_ENABLED else None
    if base_url:
        try:
            prompt = request.text.strip()
            max_chars = getattr(settings, "OPENVOICE_MAX_CHARS", 0)
            if max_chars and len(prompt) > max_chars:
                prompt = prompt[:max_chars] + "…"
            payload = {
                "text": prompt,
                "speaker": request.speaker or settings.OPENVOICE_SPEAKER_ID or "default",
            }
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                base_url,
                data=data,
                headers={'Content-Type': 'application/json'},
            )
            timeout = getattr(settings, "OPENVOICE_TIMEOUT_SECONDS", 45)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp_data = json.loads(resp.read().decode('utf-8'))
            audio_b64 = resp_data.get('audio_base64')
            if not audio_b64:
                raise ValueError("OpenVoice response missing audio_base64")
            return VoiceResponse(audio_base64=audio_b64, mime_type=resp_data.get('mime_type', 'audio/wav'))
        except Exception as exc:
            logger.warning("OpenVoice synthesis failed (%s). Falling back to placeholder audio.", exc)

    # Fallback placeholder tone
    try:
        fallback_audio = _speech_fallback_tts(request.text)
    except Exception as tts_error:
        logger.warning("Fallback TTS failed (%s). Using tone.", tts_error)
        fallback_audio = _generate_tone()
    return VoiceResponse(audio_base64=base64.b64encode(fallback_audio).decode('utf-8'))


@router.post("/agent", response_model=VoiceAgentResponse)
def voice_agent(
    request: VoiceAgentRequest,
    orchestrator: VoiceAgentOrchestrator = Depends(get_voice_agent),
):
    return orchestrator.process(request)
