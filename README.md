# Ryan's Voice Notes

Speech-to-text transcription repo. Voice notes are transcribed and saved as markdown files in `voice-notes/`.

## How It Works

Each voice note is saved as a markdown file with YAML front matter containing the date, tags, and source app. Files are named with the date and an optional title slug (e.g. `2026-02-07-meeting-notes.md`).

## Usage

### Option 1: Local script

Save a transcription directly from the command line:

```bash
# Basic usage
python scripts/save_transcription.py "Your transcription text here"

# With a title and tags
python scripts/save_transcription.py --title "Meeting Notes" --tags "meeting,project" "Text here"

# Pipe from another program (e.g. a speech-to-text CLI)
my-stt-app record | python scripts/save_transcription.py --stdin --title "Quick Note"

# Use the shell wrapper to auto-commit
./scripts/add-voice-note.sh "Your transcription text here"
```

### Option 2: GitHub Actions API (remote / from any app)

Trigger the workflow from any app that can make HTTP requests (Shortcuts, Zapier, IFTTT, a custom app, etc.):

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/rlawrence/Ryan-s-2d/actions/workflows/add-voice-note.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "transcription": "Your transcribed text goes here.",
      "title": "Morning Thoughts",
      "tags": "personal,ideas",
      "source": "whisper"
    }
  }'
```

### Option 3: Apple Shortcuts / iOS (no third-party apps)

Dictate a voice note on your iPhone and send it directly to this repo using only built-in iOS features and the GitHub API. The Shortcut flow:

```
Dictate Text → Ask for Title → Build JSON → POST to GitHub API → Done
```

**[Full step-by-step setup guide →](docs/apple-shortcut-setup.md)**

The guide covers token creation, building the Shortcut action-by-action, Siri activation, Action Button setup, and troubleshooting.

## Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/rlawrence/Ryan-s-2d.git
   cd Ryan-s-2d
   ```

2. **For API/remote usage**, create a GitHub Personal Access Token:
   - Go to GitHub Settings > Developer Settings > Personal Access Tokens > Fine-grained tokens
   - Create a token with **Contents: Read and Write** and **Actions: Read and Write** permissions for this repo
   - Use this token in the `Authorization` header when triggering the workflow

## Voice Note Format

Each note is saved as a markdown file like this:

```markdown
---
date: 2026-02-07 14:30:00
type: voice-note
source: whisper
tags: [meeting, ideas]
---

# Meeting Notes

Your transcribed text appears here as the body of the document.
```

## Project Structure

```
voice-notes/               # All transcribed voice notes (markdown)
scripts/
  save_transcription.py    # Core script to save transcriptions
  add-voice-note.sh        # Shell wrapper that auto-commits
.github/workflows/
  add-voice-note.yml       # GitHub Actions workflow for remote intake
docs/
  apple-shortcut-setup.md  # Step-by-step iOS Shortcut build guide
```
