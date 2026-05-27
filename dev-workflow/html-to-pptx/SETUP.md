# HTML to PPTX - Setup Guide

## Prerequisites

- Node.js installed

## 1. Install Dependencies

```bash
cd ~/.claude/skills/html-to-pptx
npm install
```

## 2. Test

```bash
# Create test HTML
echo "<h1>Slide 1</h1><hr><h1>Slide 2</h1>" > /tmp/test.html

# Convert to PPTX
node scripts/html-to-pptx.js /tmp/test.html /tmp/test.pptx

# Check output
ls -la /tmp/test.pptx
```

If PPTX is created, setup is complete!

## 3. Mark Setup Complete

Edit `SKILL.md` and change:
```yaml
setup_complete: true
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| npm install fails | Try `npm install --legacy-peer-deps` |
| Permission denied | Check write permissions |
| Hebrew/RTL issues | The script handles RTL automatically |
| Slides not splitting | Use `<hr>` or `---` to separate slides |
