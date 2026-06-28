import time
import re
from datetime import datetime


class SessionTracker:
    def __init__(self):
        self.start_time = time.time()
        self.start_datetime = datetime.now()
        self.corrections: list[str] = []
        self.vocabulary_suggestions: list[str] = []
        self.exchange_count = 0
        self.topic_name = ""

    def set_topic(self, topic_name: str):
        self.topic_name = topic_name

    def record_exchange(self, assistant_response: str):
        """Parse assistant response to extract grammar corrections and vocabulary notes."""
        self.exchange_count += 1

        # Look for the "📝 Quick note:" pattern
        note_match = re.search(r'📝\s*Quick note:\s*(.+?)(?:\n|$)', assistant_response, re.IGNORECASE)
        if note_match:
            note = note_match.group(1).strip()
            self.corrections.append(note)

        # Look for vocabulary suggestions (e.g., "a more natural way to say...")
        vocab_match = re.search(
            r'(?:more natural|better way|you could say|try saying)[:\s]+["""]?(.+?)["""]?(?:\.|$)',
            assistant_response, re.IGNORECASE
        )
        if vocab_match:
            suggestion = vocab_match.group(1).strip()
            if suggestion not in self.vocabulary_suggestions:
                self.vocabulary_suggestions.append(suggestion)

    def get_duration_str(self) -> str:
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        if minutes > 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''} and {seconds} second{'s' if seconds != 1 else ''}"
        return f"{seconds} second{'s' if seconds != 1 else ''}"

    def get_summary(self) -> str:
        duration = self.get_duration_str()
        lines = [
            "",
            "=" * 55,
            "         SESSION SUMMARY",
            "=" * 55,
            f"  Topic        : {self.topic_name or 'Free Conversation'}",
            f"  Duration     : {duration}",
            f"  Exchanges    : {self.exchange_count}",
            f"  Corrections  : {len(self.corrections)}",
            "",
        ]

        if self.corrections:
            lines.append("  Grammar corrections from this session:")
            for i, correction in enumerate(self.corrections, 1):
                lines.append(f"    {i}. {correction}")
            lines.append("")

        if self.vocabulary_suggestions:
            lines.append("  Vocabulary suggestions:")
            for i, suggestion in enumerate(self.vocabulary_suggestions, 1):
                lines.append(f"    {i}. {suggestion}")
            lines.append("")

        if not self.corrections and not self.vocabulary_suggestions:
            lines.append("  Great job! No corrections needed this session.")
            lines.append("")

        lines.append("  Keep practicing — you're doing great!")
        lines.append("=" * 55)
        return "\n".join(lines)

    def get_spoken_summary(self) -> str:
        """A version of the summary suitable for TTS."""
        duration = self.get_duration_str()
        parts = [
            f"Great session! You practiced for {duration} with {self.exchange_count} exchanges."
        ]

        if self.corrections:
            count = len(self.corrections)
            parts.append(
                f"I made {count} grammar correction{'s' if count != 1 else ''} during our chat. "
                "Check the screen for the full list."
            )
        else:
            parts.append("Your grammar was excellent — no corrections needed!")

        parts.append("Keep it up, and see you next time!")
        return " ".join(parts)
