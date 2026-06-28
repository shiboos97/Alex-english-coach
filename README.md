# English Voice Conversation Assistant

A fully voice-based English conversation practice assistant powered by Claude AI. Just speak — no typing required.

## Features

- 🎤 Voice input via microphone (automatic silence detection)
- 🔊 Natural voice output (ElevenLabs TTS, with gTTS fallback)
- 🤖 Powered by Claude (`claude-sonnet-4-6`) as "Alex", a friendly English coach
- 📝 Natural grammar corrections at the end of each response
- 🗂 10 conversation topics to choose from
- 📊 Session summary with corrections and vocabulary tips

## Setup

### 1. Install dependencies

```bash
cd english-voice-assistant
pip install -r requirements.txt
```

**macOS:** You may need `portaudio` for PyAudio:
```bash
brew install portaudio
pip install pyaudio
```

### 2. Configure API keys

```bash
cp .env.example .env
# Edit .env and add your API keys
```

Required:
- `ANTHROPIC_API_KEY` — from [console.anthropic.com](https://console.anthropic.com)

Optional (for best voice quality):
- `ELEVENLABS_API_KEY` — from [elevenlabs.io](https://elevenlabs.io)
- `ELEVENLABS_VOICE_ID` — defaults to Rachel voice

### 3. Run

```bash
python main.py
```

## How It Works

1. Alex (the AI) reads out a topic menu
2. Say a number (1–10) to choose your topic
3. Have a natural conversation — Alex listens and responds
4. Grammar corrections appear at the end of Alex's responses
5. Say **"stop"**, **"exit"**, or **"end session"** to end
6. A session summary is shown and read aloud

## Configuration

Edit `config.py` or set environment variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `STT_BACKEND` | `faster-whisper` | `faster-whisper` (local) or `openai-whisper` (API) |
| `TTS_BACKEND` | `elevenlabs` | `elevenlabs` or `gtts` |
| `WHISPER_MODEL_SIZE` | `base` | `tiny`, `base`, `small`, `medium`, `large` |
| `SILENCE_THRESHOLD` | `500` | Mic sensitivity (lower = more sensitive) |
| `SILENCE_DURATION` | `1.5` | Seconds of silence before sending audio |

## Topics

1. Daily Life & Routines
2. Travel & Adventure
3. Food & Cooking
4. Work & Career
5. Movies, Music & Entertainment
6. Technology & The Future
7. Free Conversation
8. Job Interview Practice
9. Storytelling
10. Debates & Opinions
