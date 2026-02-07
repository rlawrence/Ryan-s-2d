#!/usr/bin/env bash
# Quick helper to save a voice note and commit it to the repo.
#
# Usage:
#   ./scripts/add-voice-note.sh "Your transcription text here"
#   ./scripts/add-voice-note.sh -t "Meeting Notes" "Your transcription text here"
#   echo "transcription" | ./scripts/add-voice-note.sh --stdin

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

cd "$REPO_DIR"

# Pass all arguments through to the Python script
FILEPATH=$(python3 scripts/save_transcription.py "$@")

echo "$FILEPATH"

# Auto-commit if inside a git repo
if git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    git add voice-notes/
    FILENAME=$(basename "$FILEPATH" | sed 's/Saved: //')
    git commit -m "Add voice note: $FILENAME"
    echo "Committed to git. Run 'git push' to sync to GitHub."
fi
