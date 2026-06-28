from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, MAX_TOKENS
from assistant.prompts import SYSTEM_PROMPT


class ClaudeClient:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.conversation_history: list[dict] = []

    def chat(self, user_message: str) -> str:
        """Send a message and get a response. Maintains conversation history."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + self.conversation_history

        response = self.client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=MAX_TOKENS,
            messages=messages,
        )

        assistant_message = response.choices[0].message.content
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })

        return assistant_message

    def reset(self):
        """Clear conversation history for a new session."""
        self.conversation_history = []
