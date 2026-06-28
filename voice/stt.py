import io
import wave
import tempfile
import os
import numpy as np
import pyaudio
from config import (
    SAMPLE_RATE, CHANNELS, CHUNK_SIZE,
    SILENCE_THRESHOLD, SILENCE_DURATION, MAX_RECORD_SECONDS,
    STT_BACKEND, WHISPER_MODEL_SIZE, OPENAI_API_KEY
)


def _rms(data: bytes) -> float:
    """Calculate RMS amplitude of audio chunk."""
    samples = np.frombuffer(data, dtype=np.int16).astype(np.float32)
    if len(samples) == 0:
        return 0.0
    return float(np.sqrt(np.mean(samples ** 2)))


def record_until_silence() -> bytes | None:
    """
    Record audio from microphone until silence is detected.
    Returns raw PCM bytes, or None if nothing was captured.
    """
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
    )

    print("🎤 Listening... (speak now)")

    frames = []
    silent_chunks = 0
    speaking_started = False
    max_chunks = int(SAMPLE_RATE / CHUNK_SIZE * MAX_RECORD_SECONDS)
    silence_chunks_needed = int(SAMPLE_RATE / CHUNK_SIZE * SILENCE_DURATION)

    for _ in range(max_chunks):
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        frames.append(data)
        rms = _rms(data)

        if rms > SILENCE_THRESHOLD:
            speaking_started = True
            silent_chunks = 0
        elif speaking_started:
            silent_chunks += 1
            if silent_chunks >= silence_chunks_needed:
                break

    stream.stop_stream()
    stream.close()
    pa.terminate()

    if not speaking_started:
        print("⚠️  No speech detected.")
        return None

    return b"".join(frames)


def _pcm_to_wav_bytes(pcm_data: bytes) -> bytes:
    """Convert raw PCM to WAV format in memory."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_data)
    return buf.getvalue()


def transcribe(pcm_data: bytes) -> str:
    """Transcribe audio using the configured STT backend."""
    if STT_BACKEND == "openai-whisper":
        return _transcribe_openai(pcm_data)
    return _transcribe_faster_whisper(pcm_data)


def _transcribe_faster_whisper(pcm_data: bytes) -> str:
    from faster_whisper import WhisperModel

    # Cache model globally to avoid reloading
    if not hasattr(_transcribe_faster_whisper, "_model"):
        print(f"⏳ Loading Whisper model ({WHISPER_MODEL_SIZE})...")
        _transcribe_faster_whisper._model = WhisperModel(
            WHISPER_MODEL_SIZE, device="cpu", compute_type="int8"
        )

    model = _transcribe_faster_whisper._model

    wav_bytes = _pcm_to_wav_bytes(pcm_data)
    audio_file = io.BytesIO(wav_bytes)

    segments, _ = model.transcribe(audio_file, beam_size=5, language="en")
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return text


def _transcribe_openai(pcm_data: bytes) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    wav_bytes = _pcm_to_wav_bytes(pcm_data)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(wav_bytes)
        tmp_path = f.name

    try:
        with open(tmp_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",
            )
        return transcript.text.strip()
    finally:
        os.unlink(tmp_path)
