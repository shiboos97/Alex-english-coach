import sys
import os
import uuid
import base64
import re
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gtts import gTTS

from assistant.claude_client import ClaudeClient
from assistant.prompts import TOPICS, get_topic_by_id
from session.tracker import SessionTracker

app = FastAPI(title="English Voice Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: session_id -> {client, tracker, topic}
sessions: dict = {}


# ---------- Models ----------

class TopicRequest(BaseModel):
    topic_id: int

class ChatRequest(BaseModel):
    session_id: str
    message: str

class EndRequest(BaseModel):
    session_id: str


# ---------- Helpers ----------

def tts_to_base64(text: str) -> str:
    """Convert text to gTTS mp3 and return as base64 string."""
    buf = io.BytesIO()
    gTTS(text=text, lang="en", slow=False).write_to_fp(buf)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def split_response(response: str) -> tuple[str, str | None]:
    """Split Alex's reply into spoken text and the 📝 grammar note."""
    match = re.search(r'📝', response)
    if match:
        spoken = response[:match.start()].strip()
        correction = response[match.start():].strip()
    else:
        spoken = response.strip()
        correction = None
    return spoken, correction


def correction_for_tts(correction: str) -> str:
    """Clean up correction text so gTTS reads it naturally."""
    text = re.sub(r'📝\s*Quick note:\s*', 'Quick grammar note. ', correction)
    text = re.sub(r'📝\s*Grammar:\s*', '', text)
    text = text.replace('→', 'should be')
    text = re.sub(r'[^\w\s.,!?\'-]', '', text)
    return text.strip()


# ---------- API Routes ----------

@app.get("/api/topics")
def get_topics():
    return {"topics": TOPICS}


@app.post("/api/start")
def start_session(req: TopicRequest):
    topic = get_topic_by_id(req.topic_id)
    if not topic:
        raise HTTPException(status_code=400, detail="Invalid topic ID")

    session_id = str(uuid.uuid4())
    client = ClaudeClient()
    tracker = SessionTracker()
    tracker.set_topic(topic["name"])

    sessions[session_id] = {
        "client": client,
        "tracker": tracker,
        "topic": topic,
    }

    opener = topic["opener"]
    audio = tts_to_base64(opener)

    return {
        "session_id": session_id,
        "opener": opener,
        "audio": audio,
    }


@app.post("/api/chat")
def chat(req: ChatRequest):
    session = sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")

    client: ClaudeClient = session["client"]
    tracker: SessionTracker = session["tracker"]

    response = client.chat(req.message)
    tracker.record_exchange(response)

    spoken, _ = split_response(response)

    # Only speak Alex's reply — corrections are saved for the end-of-session summary
    audio = tts_to_base64(spoken)

    return {
        "spoken": spoken,
        "audio": audio,
    }


@app.post("/api/end")
def end_session(req: EndRequest):
    session = sessions.pop(req.session_id, None)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    tracker: SessionTracker = session["tracker"]

    return {
        "summary_text": tracker.get_summary(),
        "corrections": tracker.corrections,
        "vocabulary": tracker.vocabulary_suggestions,
        "exchange_count": tracker.exchange_count,
        "duration": tracker.get_duration_str(),
        "topic": tracker.topic_name,
        "audio": tts_to_base64(tracker.get_spoken_summary()),
    }


# ---------- Serve Frontend ----------

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
