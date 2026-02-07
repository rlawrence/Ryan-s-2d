# Apple Shortcuts: Voice Note to GitHub

This guide walks you through building an iOS/macOS Shortcut that captures your voice, transcribes it, and sends it straight to your GitHub repo as a markdown file -- no third-party apps or subscriptions required.

## What you'll end up with

A Shortcut you can trigger by:
- Tapping it on your Home Screen
- Saying "Hey Siri, save voice note"
- Pressing the Action Button (iPhone 15 Pro and later)

It will: dictate your speech → ask for an optional title → POST to the GitHub API → commit a markdown file to `voice-notes/`.

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
     - **Actions**: Read and Write
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
   - **Stop Listening**: After Pause (this stops recording when you stop talking)

### Action 2: Ask for Title (optional but recommended)

1. Tap **+** to add another action
2. Search for **Ask for Input** and add it
3. Configure:
   - **Question**: `Title for this voice note?`
   - **Input Type**: Text
   - **Default Answer**: (leave blank)

> This lets you give each note a meaningful name. If you want to skip this and auto-name everything, you can omit this action.

### Action 3: Set Variable -- Build JSON Body

1. Tap **+** to add another action
2. Search for **Text** and add the **Text** action
3. Paste the following into the text field, using the variable picker to insert the magic variables:

```
{"ref":"main","inputs":{"transcription":"[Dictated Text]","title":"[Provided Input]","source":"apple-shortcuts"}}
```

To insert the variables correctly:
- Tap where `[Dictated Text]` is → delete the placeholder text → tap the variable button above the keyboard → select **Dictated Text** (from Action 1)
- Tap where `[Provided Input]` is → delete the placeholder text → tap the variable button → select **Provided Input** (from Action 2)

> **Important**: If your dictation might contain quotes or special characters, add a **Replace Text** action before this step to escape double quotes (`"` → `\"`). See the Troubleshooting section below.

### Action 4: Get Contents of URL (the API call)

1. Tap **+** to add another action
2. Search for **Get Contents of URL** and add it
3. Configure each field:

**URL:**
```
https://api.github.com/repos/rlawrence/Ryan-s-2d/actions/workflows/add-voice-note.yml/dispatches
```

**Method:** `POST`

**Headers** (tap "Add new header" for each):

| Key | Value |
|-----|-------|
| `Authorization` | `Bearer ghp_YOUR_TOKEN_HERE` |
| `Accept` | `application/vnd.github.v3+json` |
| `Content-Type` | `application/json` |

> Replace `ghp_YOUR_TOKEN_HERE` with the token you generated in Step 1.

**Request Body:** select **File** and set it to the **Text** variable from Action 3

> Why "File" instead of "JSON"? The Shortcuts JSON editor can mangle nested objects. Using "File" with a pre-built JSON string sends the payload exactly as written.

### Action 5: Show Notification (confirmation)

1. Tap **+** to add another action
2. Search for **Show Notification** and add it
3. Set the message to: `Voice note saved to GitHub!`

---

## Step 3: Name and Configure the Shortcut

1. Tap the dropdown arrow at the top (next to the Shortcut name)
2. **Rename** it to `Save Voice Note`
3. Tap **Choose Icon** and pick a microphone icon
4. Optional -- tap **Add to Home Screen** to create a one-tap launcher

---

## Step 4: Set Up Siri Trigger

1. In the Shortcut editor, tap the dropdown arrow at the top
2. Tap **Rename** -- the name you set here is what you'll say to Siri
3. With the name `Save Voice Note`, you can now say:
   - "Hey Siri, Save Voice Note"

---

## Step 5: Action Button Setup (iPhone 15 Pro+)

1. Go to **Settings** → **Action Button**
2. Scroll to **Shortcut**
3. Select **Save Voice Note**
4. Now pressing and holding the Action Button will launch your voice note flow

---

## Complete Shortcut Summary

When finished, your Shortcut should have these actions in order:

```
1. Dictate Text
      ↓ (produces "Dictated Text")
2. Ask for Input: "Title for this voice note?"
      ↓ (produces "Provided Input")
3. Text: {"ref":"main","inputs":{"transcription":"[Dictated Text]","title":"[Provided Input]","source":"apple-shortcuts"}}
      ↓ (produces "Text")
4. Get Contents of URL
      URL: https://api.github.com/repos/rlawrence/Ryan-s-2d/actions/workflows/add-voice-note.yml/dispatches
      Method: POST
      Headers: Authorization: Bearer ghp_xxx, Accept: application/vnd.github.v3+json, Content-Type: application/json
      Body: File → [Text]
      ↓
5. Show Notification: "Voice note saved to GitHub!"
```

---

## Testing

1. Run the Shortcut
2. Speak a test phrase like "This is a test voice note"
3. Enter a title like "Test Note"
4. Wait a few seconds for the notification
5. Check the repo: go to **Actions** tab on GitHub and you should see a workflow run
6. After the workflow completes (~30 seconds), a new markdown file will appear in `voice-notes/`

If the API returns a **204 No Content** response, that means it worked -- GitHub returns 204 for successful workflow dispatches.

---

## Troubleshooting

### "Couldn't communicate with a helper application"
Your token may have expired or lack the right permissions. Generate a new one with **Contents: Read and Write** and **Actions: Read and Write**.

### Workflow doesn't appear in the Actions tab
Make sure the workflow file exists on the `main` branch. The `workflow_dispatch` trigger only works for workflows that are already on the target `ref` branch.

### JSON errors from special characters in dictation
Speech can include characters like quotes, newlines, or ampersands that break JSON. To handle this, add a **Replace Text** action between the Dictate and Text actions:

1. Add **Replace Text** action
   - Find: `"` (a double quote)
   - Replace with: `\"` (escaped quote)
   - Input: Dictated Text
2. Add another **Replace Text** action
   - Find: (a newline -- press Enter/Return in the field)
   - Replace with: `\n` (literal backslash-n)
   - Input: Updated Text
3. In Action 3 (the Text/JSON action), use the output of the last Replace instead of the raw Dictated Text

### Rate limits
GitHub allows 5,000 API requests per hour with a PAT. Even if you record 20 voice notes a day, you won't come close to this limit.

---

## Simplified Version (no title prompt)

If you want a one-tap, zero-input experience:

```
1. Dictate Text
      ↓
2. Text: {"ref":"main","inputs":{"transcription":"[Dictated Text]","source":"apple-shortcuts"}}
      ↓
3. Get Contents of URL (same config as above, Body: File → [Text])
      ↓
4. Show Notification: "Voice note saved!"
```

This skips the title prompt. Notes will be auto-named with the date and time (e.g. `2026-02-07-voice-note-143022.md`).
