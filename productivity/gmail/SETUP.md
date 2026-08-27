# Gmail Skill - Setup Guide

## Prerequisites

- Google account with Gmail
- Node.js (v16+)
- `clasp` CLI tool

## 1. Install Clasp

```bash
npm install -g @google/clasp
clasp login
```

Browser opens → authorize with your Google account.

## 2. Enable Apps Script API

Go to: https://script.google.com/home/usersettings
Toggle ON: "Google Apps Script API"

## 3. Create Apps Script Project

```bash
cd ~/.claude/skills/gmail/scripts

# Create your project (generates .clasp.json with your ID)
clasp create --title "Gmail API" --type webapp

# Push the code
clasp push
```

## 4. Set Your Secret Token

Generate a secure token:
```bash
openssl rand -hex 16
```
Copy the output (e.g., `a1b2c3d4e5f6...`).

Open the project in browser:
```bash
clasp open
```

In the Apps Script editor:
1. Open `Code.gs`
2. Find `setupToken()` function
3. Replace `'YOUR_SECRET_TOKEN_HERE'` with your generated token
4. Click **Run** > select `setupToken` > click **Run**
5. Click **Run** > select `testAuth` > click **Run**

## 5. Authorize Gmail Access (OAuth)

When you run `testAuth`, Google will ask for permissions:

1. Click **Review permissions**
2. Select your Google account
3. You'll see **"Google hasn't verified this app"** warning
4. Click **Advanced** → **Go to Gmail API (unsafe)**
5. Click **Allow** to grant Gmail access

> **Why "unsafe"?** Your script isn't published to Google Marketplace. It's safe - it's YOUR code running on YOUR account.

## 6. Deploy as Web App

In Apps Script UI: Deploy > New deployment > Web app:
- Execute as: **Me**
- Who has access: **Anyone**

Or via CLI:
```bash
clasp deploy --description "Gmail API v1"
clasp deployments  # Copy the URL
```

## 7. Configure Environment

Add to `~/.zshrc` or `~/.bashrc`:

```bash
export GMAIL_API_URL="https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec"
export GMAIL_API_TOKEN="your-secret-token"
```

Then: `source ~/.zshrc`

## 8. Test

```bash
# Test inbox
curl -sL "$GMAIL_API_URL?token=$GMAIL_API_TOKEN&action=inbox&maxResults=1"

# Test send (careful - this actually sends!)
curl -sL "$GMAIL_API_URL?token=$GMAIL_API_TOKEN&action=send&to=YOUR_EMAIL&subject=Test&body=Hello"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 error | Check token matches in Code.gs |
| Redirect loop | Use `-L` with curl |
| No emails returned | Check Gmail permissions granted |
| Script API not enabled | Enable at script.google.com/home/usersettings |

## Update Existing Deployment

```bash
clasp push
clasp deploy -i DEPLOYMENT_ID --description "v2"
```

## References

- [Code.js](scripts/Code.js) - The Apps Script code
