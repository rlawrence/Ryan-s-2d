# Apple Shortcuts: Voice Note to GitHub

Capture your voice on iPhone and send it to your GitHub repo as a markdown file -- no third-party apps required.

## What you'll end up with

A Shortcut you can trigger by:
- Tapping it on your Home Screen
- Saying "Hey Siri, save voice note"
- Pressing the Action Button (iPhone 15 Pro and later)

It will: dictate your speech → upload it to GitHub → a workflow adds the title and formatting.

---

## Prerequisites

1. An iPhone or Mac running iOS 16+ / macOS 13+
2. A GitHub account with access to this repo
3. A GitHub Personal Access Token (PAT) -- setup instructions below

---

## Step 1: Create a GitHub Personal Access Token

1. Open **github.com** → click your profile picture → **Settings**
2. Scroll down to **Developer settings** (bottom of the left sidebar)
3. Click **Personal access tokens** → **Fine-grained tokens** → **Generate new token**
4. Configure the token:
   - **Token name**: `Voice Notes Shortcut`
   - **Expiration**: Choose a duration (e.g. 90 days, or "No expiration" for convenience)
   - **Repository access**: Select **Only select repositories** → choose `Ryan-s-2d`
   - **Permissions**:
     - **Contents**: Read and Write
5. Click **Generate token**
6. **Copy the token immediately** -- you won't be able to see it again

---

## Step 2: Build the Shortcut

Open the **Shortcuts** app on your iPhone or Mac and tap **+** to create a new Shortcut.

### Action 1: Dictate Text

1. Tap **Add Action**
2. Search for **Dictate Text** and add it
3. Configure:
   - **Language**: English (or your preferred language)
   - **Stop Listening**: After Pause

### Action 2: Format Date

1. Tap **+** to add another action
2. Search for **Date** and add the **Date** action (this gets the current date)
3. Tap **+** again, search for **Format Date** and add it
4. Set **Date Format** to **Custom**
5. Set the format string to: `yyyy-MM-dd-HHmmss`

This produces a timestamp like `2026-02-07-143022` for the filename.

### Action 3: Base64 Encode

1. Tap **+** to add another action
2. Search for **Base64 Encode** and add it
3. Set the input to **Dictated Text** (from Action 1)
4. Make sure **Encode** is selected (not Decode)
5. Tap the action's output and set **Line Breaks** to **None**

### Action 4: Get Contents of URL (upload the file)

1. Tap **+** to add another action
2. Search for **Get Contents of URL** and add it
3. Configure:

**URL:**
Tap into the URL field and build it by typing and inserting variables:
```
https://api.github.com/repos/rlawrence/Ryan-s-2d/contents/voice-notes/raw-[Formatted Date].md
```
- Type: `https://api.github.com/repos/rlawrence/Ryan-s-2d/contents/voice-notes/raw-`
- Tap the variable button → select **Formatted Date** (from Action 2)
- Type: `.md`

**Method:** `PUT`

**Headers** (tap "Add new header" for each):

| Key | Value |
|-----|-------|
| `Authorization` | `Bearer YOUR_TOKEN_HERE` |
| `Accept` | `application/vnd.github.v3+json` |

> Replace `YOUR_TOKEN_HERE` with the token from Step 1.

**Request Body:** select **JSON**

Add these keys:

| Key | Type | Value |
|-----|------|-------|
| `message` | Text | `Add voice note via Shortcuts` |
| `content` | Text | *(tap variable button → select **Base64 Encoded**)* |

### Action 5: Show Notification

1. Tap **+** to add another action
2. Search for **Show Notification** and add it
3. Type the message: `Voice note saved to GitHub!`

---

## Step 3: Name and Configure the Shortcut

1. Tap the dropdown arrow at the top
2. **Rename** to `Save Voice Note`
3. Tap **Choose Icon** and pick a microphone icon
4. Optional -- tap **Add to Home Screen**

---

## Step 4: Siri Trigger

With the name `Save Voice Note`, just say: **"Hey Siri, Save Voice Note"**

---

## Step 5: Action Button (iPhone 15 Pro+)

1. Go to **Settings** → **Action Button**
2. Scroll to **Shortcut** → select **Save Voice Note**

---

## Complete Shortcut Summary

```
1. Dictate Text
      ↓ (produces "Dictated Text")
2. Date → Format Date (custom: yyyy-MM-dd-HHmmss)
      ↓ (produces "Formatted Date")
3. Base64 Encode [Dictated Text]
      ↓ (produces "Base64 Encoded")
4. Get Contents of URL
      URL: https://api.github.com/repos/rlawrence/Ryan-s-2d/contents/voice-notes/raw-[Formatted Date].md
      Method: PUT
      Headers: Authorization, Accept
      Body: JSON
        message: "Add voice note via Shortcuts"
        content: [Base64 Encoded]
      ↓ (returns 201 Created)
5. Show Notification: "Voice note saved to GitHub!"
```

---

## How It Works

1. The Shortcut dictates text, base64 encodes it, and uploads it directly to the repo as `voice-notes/raw-2026-02-07-143022.md`
2. The push triggers a GitHub Actions workflow that:
   - Reads the raw transcription
   - Generates an AI title using OpenAI (if configured)
   - Creates a formatted markdown file with YAML front matter
   - Removes the raw file
3. You end up with a clean voice note like `voice-notes/2026-02-07-grocery-run-and-dentist-call.md`

---

## Testing

1. Run the Shortcut
2. Speak a test phrase
3. You should get a notification (no "cannot parse response" -- this API returns a proper response!)
4. Check the repo -- you'll see a `raw-*.md` file appear, then moments later the workflow processes it into a formatted note

---

## Troubleshooting

### 422 "sha" is required / file already exists
Two notes were saved in the same second. Try again -- the timestamp will be different.

### "Couldn't communicate with a helper application"
Your token may have expired. Generate a new one with **Contents: Read and Write**.

### Raw file appears but isn't processed
Make sure the `process-voice-note.yml` workflow exists on the `main` branch and that you've added the `OPENAI_API_KEY` secret (optional -- titles will use first words as fallback).
