#!/usr/bin/env python3
"""
English Voice Conversation Assistant — powered by Claude
Run with: python main.py
"""

import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

from assistant.claude_client import ClaudeClient
from assistant.prompts import TOPICS, get_topic_menu_text, get_topic_by_id
from session.tracker import SessionTracker
from voice.stt import record_until_silence, transcribe
from voice.tts import speak


EXIT_PHRASES = {"stop", "exit", "quit", "end session", "goodbye", "bye"}


def is_exit_command(text: str) -> bool:
    normalized = text.lower().strip().rstrip(".,!?")
    return any(phrase in normalized for phrase in EXIT_PHRASES)


def select_topic_by_voice(claude: ClaudeClient) -> dict:
    """Play topic menu via TTS and listen for voice selection."""
    menu_intro = (
        "Hello! I'm Alex, your English conversation coach. "
        "Please choose a topic by saying its number. "
        "Here are your options: "
    )
    topic_list = ", ".join(
        f"Option {t['id']}: {t['name']}" for t in TOPICS
    )
    speak(menu_intro + topic_list + ". Which topic would you like?")

    print("\n" + get_topic_menu_text())
    print("\nSay a number (1-10) to choose your topic...\n")

    while True:
        pcm = record_until_silence()
        if pcm is None:
            speak("I didn't catch that. Please say a number between 1 and 10.")
            continue

        text = transcribe(pcm).strip()
        print(f"You said: {text}")

        # Extract number from spoken text
        topic_id = _extract_number(text)
        if topic_id and 1 <= topic_id <= len(TOPICS):
            topic = get_topic_by_id(topic_id)
            speak(f"Great choice! Let's talk about {topic['name']}.")
            return topic

        speak(
            f"I heard '{text}' but didn't catch a number. "
            "Please say a number between 1 and 10."
        )


def _extract_number(text: str) -> int | None:
    """Extract a digit (1-10) from spoken text like 'number three' or 'seven'."""
    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    }
    text_lower = text.lower()

    for word, num in word_to_num.items():
        if word in text_lower:
            return num

    # Try digit extraction
    import re
    matches = re.findall(r'\b(10|[1-9])\b', text)
    if matches:
        return int(matches[0])

    return None


def run_conversation(topic: dict):
    """Main conversation loop."""
    claude = ClaudeClient()
    tracker = SessionTracker()
    tracker.set_topic(topic["name"])

    print(f"\n{'='*55}")
    print(f"  Topic: {topic['name']}")
    print(f"  Say 'stop' or 'exit' to end the session")
    print(f"{'='*55}\n")

    # Alex opens with the topic starter
    opener = topic["opener"]
    print(f"Alex: {opener}\n")
    speak(opener)

    while True:
        # Record user speech
        pcm = record_until_silence()
        if pcm is None:
            speak("I didn't catch that. Could you say that again?")
            continue

        user_text = transcribe(pcm).strip()
        if not user_text:
            speak("I couldn't make that out. Could you repeat?")
            continue

        print(f"You : {user_text}")

        # Check for exit command
        if is_exit_command(user_text):
            farewell = "It was great chatting with you! Let me give you a quick summary of our session."
            print(f"Alex: {farewell}")
            speak(farewell)
            break

        # Get Claude's response
        try:
            response = claude.chat(user_text)
        except Exception as e:
            print(f"⚠️  Claude error: {e}")
            speak("Sorry, I had a technical hiccup. Could you say that again?")
            continue

        print(f"Alex: {response}\n")
        tracker.record_exchange(response)

        # Speak response (strip the 📝 note for natural flow — read it separately)
        import re
        spoken = re.sub(r'📝\s*Quick note:.*', '', response).strip()
        note_match = re.search(r'📝\s*Quick note:\s*(.+)', response)

        speak(spoken)

        if note_match:
            note_text = note_match.group(1).strip()
            speak(f"Quick grammar note: {note_text}")

    # Session complete
    print(tracker.get_summary())
    speak(tracker.get_spoken_summary())


def main():
    print("\n" + "="*55)
    print("   ENGLISH VOICE CONVERSATION ASSISTANT")
    print("   Powered by Claude & Alex")
    print("="*55 + "\n")

    # Validate API key
    from config import GROQ_API_KEY
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY not set. Copy .env.example to .env and add your free key from console.groq.com")
        sys.exit(1)

    try:
        topic = select_topic_by_voice(ClaudeClient())
        run_conversation(topic)
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted. Goodbye!")
        speak("Goodbye! See you next time.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
