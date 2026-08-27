# Transcribe - Setup Guide

## Prerequisites

- Node.js installed
- ElevenLabs account with API access

## 1. Get ElevenLabs API Key

1. Go to [elevenlabs.io](https://elevenlabs.io)
2. Sign up or log in
3. Go to Profile → API Key
4. Copy your API key

## 2. Configure Environment

```bash
cd ~/.claude/skills/transcribe/scripts
cp .env.example .env
```

Edit `.env`:
```
ELEVENLABS_API_KEY=your_actual_api_key_here
```

## 3. Install Dependencies

```bash
cd ~/.claude/skills/transcribe/scripts
npm install
```

## 4. Test

```bash
# Test with a sample audio file
npx ts-node transcribe.ts --help
```

If help appears, setup is complete!

## 5. Mark Setup Complete

Edit `SKILL.md` and change:
```yaml
setup_complete: true
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Invalid API key | Check .env has correct key |
| File not found | Use absolute paths |
| Unsupported format | Convert to mp3/wav first |
