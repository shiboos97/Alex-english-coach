SYSTEM_PROMPT = """You are Michu, a friendly native English speaker helping someone practice conversational English.

Your behavior rules:
1. Keep replies SHORT — 1 to 2 sentences maximum. Never write long paragraphs.
2. Ask only ONE follow-up question per reply, not multiple.
3. ALWAYS end your reply with a grammar correction if the user made ANY mistake — no matter how small. Use this exact format on a new line: "📝 Quick note: [what they said] → [correct version]. [one-line explanation]"
4. If their grammar was perfect, write: "📝 Grammar: Perfect!" instead.
5. Correct mistakes like: wrong tense, missing articles (a/an/the), wrong prepositions, subject-verb agreement, wrong word choice.
6. Be warm but brief. Do not over-explain or over-encourage.

Example:
User: "Yesterday I go to market and buyed some vegetable."
Alex: "Nice! What did you get there? 🛒
📝 Quick note: 'I go' → 'I went', 'buyed' → 'bought', 'vegetable' → 'vegetables'. Use past tense for past events, and 'buy' has an irregular past form."

When the user says "stop", "exit", or "end session", say goodbye in one sentence."""

TOPICS = [
    {
        "id": 1,
        "name": "Daily Life & Routines",
        "description": "Talk about your day, hobbies, and everyday activities",
        "opener": "Hey! What does a typical day look like for you?"
    },
    {
        "id": 2,
        "name": "Travel & Adventure",
        "description": "Discuss travel experiences, dream destinations, and adventures",
        "opener": "Have you traveled anywhere interesting recently?"
    },
    {
        "id": 3,
        "name": "Food & Cooking",
        "description": "Share recipes, restaurant recommendations, and food culture",
        "opener": "Do you enjoy cooking, or do you prefer eating out?"
    },
    {
        "id": 4,
        "name": "Work & Career",
        "description": "Talk about your job, career goals, and professional life",
        "opener": "What do you do for work?"
    },
    {
        "id": 5,
        "name": "Movies, Music & Entertainment",
        "description": "Discuss films, songs, shows, and pop culture",
        "opener": "What have you been watching or listening to lately?"
    },
    {
        "id": 6,
        "name": "Technology & The Future",
        "description": "Explore tech trends, gadgets, and what the future might look like",
        "opener": "What do you think about all the AI developments happening these days?"
    },
    {
        "id": 7,
        "name": "Free Conversation",
        "description": "No set topic — just chat naturally about anything",
        "opener": "Hey, I'm Alex! What's on your mind today?"
    },
    {
        "id": 8,
        "name": "Job Interview Practice",
        "description": "Practice common job interview questions and professional English",
        "opener": "Let's do a mock interview. Tell me a little about yourself."
    },
    {
        "id": 9,
        "name": "Storytelling",
        "description": "Share personal stories and practice narrative English",
        "opener": "Tell me about something interesting that happened to you recently."
    },
    {
        "id": 10,
        "name": "Debates & Opinions",
        "description": "Share and defend opinions on interesting topics",
        "opener": "Has social media made the world more connected or more divided — what do you think?"
    },
]

def get_topic_menu_text():
    lines = ["Choose a conversation topic:\n"]
    for t in TOPICS:
        lines.append(f"  {t['id']:2}. {t['name']}")
        lines.append(f"      {t['description']}")
    return "\n".join(lines)

def get_topic_by_id(topic_id: int) -> dict | None:
    for t in TOPICS:
        if t["id"] == topic_id:
            return t
    return None
