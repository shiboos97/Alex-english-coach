import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Optional: for Whisper API

# Groq settings — llama-3.3-70b-versatile is the best model for conversation
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 1024

# ElevenLabs settings
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel voice
ELEVENLABS_MODEL_ID = "eleven_monolingual_v1"

# STT settings
STT_BACKEND = os.getenv("STT_BACKEND", "faster-whisper")  # "faster-whisper" or "openai-whisper"
WHISPER_MODEL_SIZE = "base"  # tiny, base, small, medium, large

# Audio recording settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
SILENCE_THRESHOLD = 500       # RMS threshold for silence detection
SILENCE_DURATION = 1.5        # Seconds of silence before stopping recording
MAX_RECORD_SECONDS = 60       # Maximum recording duration

# TTS backend: "elevenlabs" or "gtts"
TTS_BACKEND = os.getenv("TTS_BACKEND", "gtts")
