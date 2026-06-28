import io
import os
import tempfile
from config import (
    TTS_BACKEND, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL_ID
)


def speak(text: str):
    """Convert text to speech and play it. Falls back to gTTS if ElevenLabs fails."""
    if TTS_BACKEND == "elevenlabs" and ELEVENLABS_API_KEY:
        try:
            _speak_elevenlabs(text)
            return
        except Exception as e:
            print(f"⚠️  ElevenLabs failed ({e}), falling back to gTTS...")

    _speak_gtts(text)


def _speak_elevenlabs(text: str):
    from elevenlabs.client import ElevenLabs
    from elevenlabs import play

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=ELEVENLABS_VOICE_ID,
        model_id=ELEVENLABS_MODEL_ID,
        output_format="mp3_44100_128",
    )
    play(audio)


def _speak_gtts(text: str):
    from gtts import gTTS

    tts = gTTS(text=text, lang="en", slow=False)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tmp_path = f.name
        tts.save(tmp_path)

    try:
        _play_mp3(tmp_path)
    finally:
        os.unlink(tmp_path)


def _play_mp3(path: str):
    """Play an MP3 file using available system tools."""
    import subprocess
    import sys

    if sys.platform == "darwin":
        subprocess.run(["afplay", path], check=True)
    elif sys.platform.startswith("linux"):
        # Try mpg123, then ffplay
        for player in ["mpg123", "ffplay"]:
            try:
                subprocess.run([player, "-q", path], check=True)
                return
            except FileNotFoundError:
                continue
        raise RuntimeError("No audio player found. Install mpg123 or ffplay.")
    elif sys.platform == "win32":
        import winsound
        winsound.PlaySound(path, winsound.SND_FILENAME)
    else:
        raise RuntimeError(f"Unsupported platform: {sys.platform}")
