# 🦁 WildStrikeAI

> Fully automated AI-powered YouTube Shorts channel — wildlife predator scenes, dramatic narration, cinematic visuals. Zero manual work after setup.

---

## What It Does

Every day at 9 AM UTC, GitHub Actions automatically:

1. **Generates a script** — Google Gemini 1.5 Flash writes a dramatic 40-second wildlife narration
2. **Records voiceover** — Microsoft Edge Neural TTS (free, no API key) narrates in a dramatic male/female British/Australian voice
3. **Downloads footage** — Pexels API fetches real HD wildlife clips (lions, cheetahs, leopards, crocodiles, wolves, eagles and more)
4. **Assembles the video** — FFmpeg builds a 9:16 vertical Short with:
   - Cinematic Ken Burns zoom-in effect
   - Orange-teal colour grade
   - Burned-in captions
   - WildStrikeAI watermark
   - Fade-in opening
5. **Generates thumbnail** — Pillow creates a dramatic custom thumbnail with title + red bar
6. **Uploads to YouTube** — YouTube Data API v3 publishes the Short directly to your channel

---

## Tech Stack — 100% Free

| Component | Tool | Cost |
|---|---|---|
| Script generation | Google Gemini 1.5 Flash | Free (1500 req/day) |
| Voiceover | Microsoft Edge Neural TTS (`edge-tts`) | Free, no key needed |
| Wildlife footage | Pexels API | Free (200 req/hour) |
| Video assembly | FFmpeg | Free, open source |
| Thumbnail | Pillow (Python) | Free, open source |
| YouTube upload | YouTube Data API v3 | Free (OAuth) |
| Automation | GitHub Actions | Free (public repo = unlimited) |

---

## Project Structure

```
wildstrikeai/
├── .github/
│   └── workflows/
│       └── generate_short.yml   # GitHub Actions — daily schedule + manual trigger
├── main.py                      # Master orchestrator (runs all 6 steps)
├── script_generator.py          # Gemini API — generates 40-sec narration script
├── voiceover.py                 # Edge TTS — dramatic male/female AI voiceover
├── footage_fetcher.py           # Pexels API — downloads wildlife video clips
├── video_assembler.py           # FFmpeg — assembles final 9:16 Short
├── thumbnail_generator.py       # Pillow — generates YouTube thumbnail
├── youtube_uploader.py          # YouTube Data API v3 — uploads Short + thumbnail
├── get_youtube_token.py         # One-time local script to get OAuth refresh token
├── generate_logo.py             # One-time local script to generate channel logo
└── requirements.txt             # Python dependencies
```

---

## Setup Guide

### Prerequisites
- Python 3.10+
- Git
- A GitHub account
- A dedicated Google/Gmail account for the YouTube channel

---

### Step 1 — Get Free API Keys

**Gemini API Key (script generation)**
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Click **Get API Key** → **Create API key in new project**
3. Copy the key

**Pexels API Key (wildlife footage)**
1. Go to [pexels.com/api](https://www.pexels.com/api) → register free account
2. Your API key appears immediately on the API page

---

### Step 2 — Create YouTube Channel

1. Create a new Gmail account (e.g. `wildstrikeai@gmail.com`)
2. Go to [youtube.com](https://youtube.com) → sign in → **Create a channel** → name it `WildStrikeAI`

---

### Step 3 — Enable YouTube Data API v3

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → sign in with the new Gmail
2. Create a new project named `WildStrikeAI`
3. **APIs & Services** → **Library** → search `YouTube Data API v3` → **Enable**
4. **APIs & Services** → **Credentials** → **+ Create Credentials** → **OAuth Client ID**
   - Configure consent screen first if prompted: **External** user type, add your Gmail as test user under **Audience → Test users**
   - Application type: **Desktop app** → Create
5. Copy the **Client ID** and **Client Secret**

---

### Step 4 — Get YouTube Refresh Token (run once locally)

```bash
pip install google-auth-oauthlib
python get_youtube_token.py
```

- Paste Client ID and Client Secret when prompted
- Browser opens → sign in with WildStrikeAI Gmail → **Allow**
- Terminal prints your `YOUTUBE_REFRESH_TOKEN` — copy it

---

### Step 5 — Add GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret Name | Where to get |
|---|---|
| `GEMINI_API_KEY` | Step 1 — Google AI Studio |
| `PEXELS_API_KEY` | Step 1 — Pexels API page |
| `YOUTUBE_CLIENT_ID` | Step 3 — Google Cloud Console |
| `YOUTUBE_CLIENT_SECRET` | Step 3 — Google Cloud Console |
| `YOUTUBE_REFRESH_TOKEN` | Step 4 — get_youtube_token.py output |

---

### Step 6 — Push & Run

```bash
git clone https://github.com/i-am-akhilmishra/wildstrikeai.git
cd wildstrikeai
```

Or if already cloned, just go to:

**GitHub → Actions → WildStrikeAI - Generate YouTube Short → Run workflow**

Your first Short will be generated and uploaded in ~3–5 minutes.

---

## Customisation

**Change upload schedule** — edit `.github/workflows/generate_short.yml`:
```yaml
- cron: '0 9 * * *'   # 9 AM UTC daily — change as needed
```

**Change animal topics** — edit `script_generator.py`:
```python
TOPICS = [
    "a cheetah chasing a gazelle at full sprint across the savanna",
    "a lion pride ambushing a wildebeest at dusk",
    # add your own...
]
```

**Change voice style** — edit `voiceover.py`:
```python
MALE_VOICES = ["en-GB-RyanNeural", ...]   # swap voice names
FEMALE_VOICES = ["en-GB-SoniaNeural", ...]
```

---

## License

MIT — free to use, fork, and modify.
