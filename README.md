# 🦁 WildStrikeAI

> Fully automated AI-powered YouTube Shorts channel — wildlife predator scenes, dramatic narration, cinematic visuals. Zero manual work after setup. Built-in human review gate before every upload.

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
6. **⏸ Pauses for your review** — uploads the script + video as a downloadable artifact, then waits for your manual approval (up to 4 hours)
7. **Fetches live trending hashtags** — pulls currently trending tags from YouTube (Animals category) + Google Trends, injects them into title + description
8. **Uploads to YouTube** — only after you approve, publishes the Short to your channel

---

## Review & Approval Flow

```
Pipeline triggers (daily 9AM UTC or manual)
        ↓
🎬 JOB 1 — Generate (runs automatically ~4 min)
   Gemini script → Edge TTS voice → Pexels clips
   → FFmpeg 40s Short → Pillow thumbnail
        ↓
📧 GitHub emails you: "Deployment waiting for your approval"
        ↓
You open Actions → read the script in the summary
Download "review-package" artifact → watch final_short.mp4
        ↓
✅ Click "Approve and deploy"   OR   ❌ "Reject"
        ↓
🚀 JOB 2 — Upload (only if approved)
   Fetches live trending hashtags → uploads to YouTube
```

---

## Tech Stack — 100% Free

| Component | Tool | Cost |
|---|---|---|
| Script generation | Google Gemini 1.5 Flash | Free (1500 req/day) |
| Voiceover | Microsoft Edge Neural TTS (`edge-tts`) | Free, no key needed |
| Wildlife footage | Pexels API | Free (200 req/hour) |
| Video assembly | FFmpeg | Free, open source |
| Thumbnail | Pillow (Python) | Free, open source |
| Trending hashtags | YouTube Data API v3 + pytrends (Google Trends) | Free |
| YouTube upload | YouTube Data API v3 | Free (OAuth) |
| Automation | GitHub Actions | Free (public repo = unlimited) |

---

## Project Structure

```
wildstrikeai/
├── .github/
│   └── workflows/
│       └── generate_short.yml   # 2-job pipeline: generate → approve → upload
├── main.py                      # Legacy single-run orchestrator (local use)
├── generate_video.py            # JOB 1: Script → Voice → Footage → Video → Thumbnail
├── upload_video.py              # JOB 2: Trending hashtags → YouTube upload (post-approval)
├── script_generator.py          # Gemini API — generates 40-sec narration script
├── voiceover.py                 # Edge TTS — dramatic male/female AI voiceover
├── footage_fetcher.py           # Pexels API — downloads wildlife video clips
├── video_assembler.py           # FFmpeg — assembles final 9:16 Short with effects
├── thumbnail_generator.py       # Pillow — generates YouTube thumbnail
├── trending_hashtags.py         # YouTube trending + Google Trends hashtag engine
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

### Step 3 — Google Cloud Setup (YouTube APIs)

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → sign in with the new Gmail
2. Create a new project named `WildStrikeAI`
3. **APIs & Services → Library** → search `YouTube Data API v3` → **Enable**

**Create OAuth credentials (for uploading):**
1. **Credentials → + Create Credentials → OAuth Client ID**
   - Configure consent screen: **External**, add your Gmail under **Audience → Test users**
   - Application type: **Desktop app** → name: `WildStrikeAI` → Create
2. Copy **Client ID** and **Client Secret**

**Create API Key (for reading trending data):**
1. **Credentials → + Create Credentials → API Key**
2. Click Create → copy the key immediately shown

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

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret Name | Where to get |
|---|---|
| `GEMINI_API_KEY` | Step 1 — Google AI Studio |
| `PEXELS_API_KEY` | Step 1 — Pexels API page |
| `YOUTUBE_CLIENT_ID` | Step 3 — OAuth Client ID |
| `YOUTUBE_CLIENT_SECRET` | Step 3 — OAuth Client Secret |
| `YOUTUBE_REFRESH_TOKEN` | Step 4 — get_youtube_token.py output |
| `YOUTUBE_API_KEY` | Step 3 — API Key (for trending hashtags) |

---

### Step 6 — Create GitHub `production` Environment (approval gate)

1. Go to **Settings → Environments → New environment** → name it `production`
2. Tick **"Required reviewers"** → add your GitHub username → **Save protection rules**
3. Set **"Wait timer"** to `240` minutes (auto-cancel if not reviewed in 4 hours)

This is what pauses the pipeline and emails you before uploading.

---

### Step 7 — Push & Run

```bash
git clone https://github.com/i-am-akhilmishra/wildstrikeai.git
cd wildstrikeai
git push -u origin main
```

Then go to **GitHub → Actions → WildStrikeAI - Generate YouTube Short → Run workflow**

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
MALE_VOICES = ["en-GB-RyanNeural", ...]
FEMALE_VOICES = ["en-GB-SoniaNeural", ...]
```

**Change hashtag count in description** — edit `upload_video.py`:
```python
hashtag_str = build_hashtag_string(tags, max_in_description=15)
```

---

## License

MIT — free to use, fork, and modify.

