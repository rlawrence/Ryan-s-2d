# Apple Shortcuts: Voice Note to GitHub

This guide walks you through building an iOS/macOS Shortcut that captures your voice, transcribes it, and sends it straight to your GitHub repo as a markdown file -- no third-party apps or subscriptions required.

## What you'll end up with

A Shortcut you can trigger by:
- Tapping it on your Home Screen
- Saying "Hey Siri, save voice note"
- Pressing the Action Button (iPhone 15 Pro and later)

It will: dictate your speech → POST to the GitHub API → a workflow commits a markdown file to `voice-notes/`.

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
   - **Stop Listening**: After Pause (this stops recording when you stop talking)

### Action 2: Get Contents of URL (the API call)

1. Tap **+** to add another action
2. Search for **Get Contents of URL** and add it
3. Configure each field:

**URL:**
```
https://api.github.com/repos/rlawrence/Ryan-s-2d/dispatches
```

**Method:** `POST`

**Headers** (tap "Add new header" for each):

| Key | Value |
|-----|-------|
| `Authorization` | `Bearer YOUR_TOKEN_HERE` |
| `Accept` | `application/vnd.github.v3+json` |

> Replace `YOUR_TOKEN_HERE` with the token you generated in Step 1.

**Request Body:** select **JSON**

Add these keys in the JSON editor:

| Key | Type | Value |
|-----|------|-------|
| `event_type` | Text | `voice-note` |
| `client_payload` | Dictionary | *(tap to expand, then add keys below)* |

Inside `client_payload`, add:

| Key | Type | Value |
|-----|------|-------|
| `transcription` | Text | *(tap variable button → select **Dictated Text**)* |
| `source` | Text | `apple-shortcuts` |

### Action 3: Show Notification

1. Tap **+** to add another action
2. Search for **Show Notification** and add it
3. Type the message: `Voice note saved to GitHub!`

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
2. Get Contents of URL
      URL: https://api.github.com/repos/rlawrence/Ryan-s-2d/dispatches
      Method: POST
      Headers: Authorization: Bearer YOUR_TOKEN, Accept: application/vnd.github.v3+json
      Body: JSON
        event_type: "voice-note"
        client_payload:
          transcription: [Dictated Text]
          source: "apple-shortcuts"
      ↓
3. Show Notification: "Voice note saved to GitHub!"
```

---

## Testing

1. Run the Shortcut
2. Speak a test phrase like "This is a test voice note"
3. Wait for the notification
4. Check the repo: go to **Actions** tab on GitHub and you should see a workflow run
5. After the workflow completes (~30 seconds), a new markdown file will appear in `voice-notes/`

The API returns a **204 No Content** response on success -- this is normal.

---

## Troubleshooting

### "Cannot parse response"
This is normal! GitHub returns an empty 204 response on success. The notification will still show. If workflows aren't running, double-check your token permissions.

### "Couldn't communicate with a helper application"
Your token may have expired or lack the right permissions. Generate a new one with **Contents: Read and Write** scoped to this repo.

### Rate limits
GitHub allows 5,000 API requests per hour with a PAT. Even if you record 20 voice notes a day, you won't come close to this limit.
