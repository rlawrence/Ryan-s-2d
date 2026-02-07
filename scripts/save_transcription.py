#!/usr/bin/env python3
"""Save a speech-to-text transcription as a markdown file in voice-notes/.

Usage:
    python scripts/save_transcription.py "Your transcription text here"
    python scripts/save_transcription.py --title "Meeting Notes" "Your transcription text here"
    python scripts/save_transcription.py --tags "meeting,project" "Your transcription text here"
    echo "Your transcription" | python scripts/save_transcription.py --stdin
"""

import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime

VOICE_NOTES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "voice-notes")


def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text[:60].strip("-")


def generate_title_openai(transcription: str) -> str | None:
    """Use OpenAI API to generate a concise title for the transcription."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    body = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Generate a short, concise title (3-6 words) that summarizes "
                    "the following voice note transcription. Return ONLY the title "
                    "text, no quotes, no punctuation at the end."
                ),
            },
            {"role": "user", "content": transcription[:1000]},
        ],
        "max_tokens": 20,
        "temperature": 0.3,
    }).encode()

    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            title = data["choices"][0]["message"]["content"].strip().strip('"\'')
            return title
    except Exception:
        return None


def title_from_transcription(transcription: str, max_words: int = 6) -> str:
    """Generate a title: try OpenAI first, fall back to first words."""
    ai_title = generate_title_openai(transcription)
    if ai_title:
        return ai_title

    words = transcription.strip().split()[:max_words]
    title = " ".join(words)
    title = title.rstrip(".,;:!?")
    return title.title()


def generate_filename(title: str | None, timestamp: datetime) -> str:
    """Generate a markdown filename from title and timestamp."""
    date_str = timestamp.strftime("%Y-%m-%d")
    if title:
        slug = slugify(title)
        return f"{date_str}-{slug}.md"
    return f"{date_str}-voice-note-{timestamp.strftime('%H%M%S')}.md"


def build_markdown(
    transcription: str,
    title: str | None,
    tags: list[str],
    timestamp: datetime,
    source: str | None,
) -> str:
    """Build the markdown content for a voice note."""
    lines = []

    # YAML front matter
    lines.append("---")
    lines.append(f"date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("type: voice-note")
    if source:
        lines.append(f"source: {source}")
    if tags:
        lines.append(f"tags: [{', '.join(tags)}]")
    lines.append("---")
    lines.append("")

    # Title
    display_title = title or f"Voice Note - {timestamp.strftime('%B %d, %Y %I:%M %p')}"
    lines.append(f"# {display_title}")
    lines.append("")

    # Transcription body
    lines.append(transcription.strip())
    lines.append("")

    return "\n".join(lines)


def save_transcription(
    transcription: str,
    title: str | None = None,
    tags: list[str] | None = None,
    source: str | None = None,
) -> str:
    """Save a transcription as a markdown file. Returns the file path."""
    timestamp = datetime.now()
    tags = tags or []

    # Auto-generate title from transcription if none provided
    if not title:
        title = title_from_transcription(transcription)

    os.makedirs(VOICE_NOTES_DIR, exist_ok=True)

    filename = generate_filename(title, timestamp)
    filepath = os.path.join(VOICE_NOTES_DIR, filename)

    # Avoid overwriting existing files
    counter = 1
    base, ext = os.path.splitext(filepath)
    while os.path.exists(filepath):
        filepath = f"{base}-{counter}{ext}"
        counter += 1

    content = build_markdown(transcription, title, tags, timestamp, source)

    with open(filepath, "w") as f:
        f.write(content)

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Save a voice transcription as markdown.")
    parser.add_argument("transcription", nargs="?", help="The transcription text.")
    parser.add_argument("--title", "-t", help="Title for the voice note.")
    parser.add_argument("--tags", help="Comma-separated tags (e.g. 'meeting,ideas').")
    parser.add_argument("--source", "-s", help="Source app (e.g. 'whisper', 'otter').")
    parser.add_argument("--stdin", action="store_true", help="Read transcription from stdin.")

    args = parser.parse_args()

    if args.stdin:
        transcription = sys.stdin.read()
    elif args.transcription:
        transcription = args.transcription
    else:
        parser.error("Provide transcription text as an argument or use --stdin.")

    if not transcription.strip():
        print("Error: Empty transcription.", file=sys.stderr)
        sys.exit(1)

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []

    filepath = save_transcription(transcription, args.title, tags, args.source)
    print(f"Saved: {filepath}")


if __name__ == "__main__":
    main()
