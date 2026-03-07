"""
Voice utilities — OpenAI Whisper STT and TTS helpers.
"""

from openai import OpenAI

client = OpenAI()


def transcribe(audio_file) -> str:
    """Transcribe audio to text using OpenAI Whisper."""
    result = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
    )
    return result.text


def speak(text: str, voice: str = "alloy") -> bytes:
    """Convert text to speech using OpenAI TTS. Returns MP3 bytes."""
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )
    return response.content
