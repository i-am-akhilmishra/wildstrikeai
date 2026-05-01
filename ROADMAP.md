# WildStrikeAI — Roadmap & Growth Plan

Current state: automated daily pipeline — script → voice → footage → 4K video → approval gate → YouTube upload.
Everything below is planned work, ordered by expected impact.

---

## Priority 1 — Biggest Quality Jump (AI Upgrades)

### Scene-Matched B-Roll Per Sentence
**Status: Not started | Impact: Highest**

Right now the pipeline downloads 6 clips for the whole video and loops them.
The upgrade: parse the script sentence by sentence, extract the key visual noun from each
(`"crocodile"`, `"river bank"`, `"zebra herd"`), fetch a dedicated Pexels clip per noun, then
cut between clips timed to the narration.

Result: the video feels like a real edited wildlife documentary, not a slideshow.
This is the single biggest watch-time improvement possible — the difference between 10% and 90% retention.

Files to change: `script_generator.py` (return scene list), `footage_fetcher.py` (fetch per scene),
`video_assembler.py` (cut on sentence boundaries from voiceover timestamps).

---

### CLIP Semantic Clip Scoring
**Status: Not started | Impact: High**

OpenAI's CLIP model (free, runs locally, no API key) can score each downloaded video clip against
the script text. Only keep clips that visually match what the narrator says.
Eliminates the mismatch problem (lion footage with eagle narration) completely.

Add to `footage_fetcher.py` after download: score all clips, discard bottom 50%, keep best matches.
Requires: `pip install git+https://github.com/openai/CLIP.git torch torchvision`

---

### Two-Model Script Chain
**Status: Not started | Impact: Medium-High**

Instead of one Gemini call: 
1. Model A generates raw story outline
2. Model B (Claude Haiku or GPT-4o mini — both have free tiers) rewrites for emotional punch

Output quality jump is significant. Hooks become sharper, pacing tighter.
Add as optional second pass in `script_generator.py` — falls back gracefully if API unavailable.

---

### Perplexity AI Real-Time Animal Facts
**Status: Not started | Impact: Medium**

Before generating the script, query Perplexity API for *"latest news [animal species] [current year]"*.
If a rare jaguar was filmed last week, your script can reference it.
Makes the channel feel like a news source, not a generic wildlife archive.

Perplexity has a free tier. Add as optional enrichment step in `script_generator.py`.

---

### Freesound Ambient Audio Layer
**Status: Not started | Impact: Medium**

Add jungle ambience / savanna wind / river sounds under the narration.
Freesound.org has thousands of CC-licensed clips accessible via their free API.
A simple topic classifier picks the right environment per animal automatically.

Add as optional step in `generate_video.py` between voiceover and assembly.

---

## Priority 2 — Channel Growth (Distribution)

### Post to 2 Videos Per Day
**Status: Planned**

Two separate series posted at different times:
- **9 AM UTC** — "The Kill" series (predator wins, current pipeline)
- **6 PM UTC** — "Survival" series (prey escapes — same footage, different script angle)

Change: add second cron trigger in `.github/workflows/generate_short.yml`, pass `SERIES=survival`
env var, update `script_generator.py` to alternate topic focus based on series.

GitHub Actions cost: ~600 min/month at 2/day — well within the 2000 min free limit.

---

### Auto-Crosspost to 4 Platforms
**Status: Not started | Impact: High**

One video → four platforms automatically after YouTube upload:
- Instagram Reels (same MOV file)
- TikTok
- Twitter/X (thumbnail + first line as tweet)
- Reddit (r/NatureIsFuckingLit, r/interestingasfuck)

Use a small LLM to rewrite the YouTube description into platform-specific captions per platform.
Add as final step in `upload_video.py`.

---

### Comment Response Bot
**Status: Not started | Impact: Medium**

After upload, a scheduled job reads new comments via YouTube Data API v3 and auto-replies with
a follow-up animal fact. *"Did you know cheetahs can't roar?"*

Drives comment velocity which is a direct YouTube ranking signal.
Add as a third job in the workflow, runs 2 hours after upload job completes.

---

### Channel SEO — Title Formula
**Status: Ongoing**

Proven title formats for wildlife Shorts:
- `This [Animal] Has ZERO Mercy 😮 #Shorts`
- `Nature's Deadliest Moment (You Won't Believe This) #Shorts`
- `[Animal] vs [Animal] — Only One Survives #Shorts`

Always include `WildStrikeAI` as a keyword — builds brand search over time.
`trending_hashtags.py` already injects top trending tags automatically.

---

### Community Engagement (Manual — First 90 Days)
**Status: Ongoing**

- Comment on BBC Earth, Nat Geo Wild, ViralHog — genuine comments, not spam
- Reply to every comment on own videos within first hour of posting
- Pin a comment on each video: *"Which predator should we cover next? 👇"*

These three actions directly affect the comment velocity signal YouTube uses for ranking.

---

## Realistic Growth Timeline

| Posting Rate | Month 1 | Month 2 | Month 3 |
|---|---|---|---|
| 1/day | 50–200 subs | 200–500 | 500–1500 |
| 2/day | 100–400 subs | 400–1200 | 1000–4000 |

1000-sub monetisation threshold is ~2x faster at 2/day.
YouTube monetisation also requires 10M Shorts views — consistent daily posting is the only path.

---

## What NOT to Do

- Do not delete videos — YouTube penalises removed content
- Do not miss posting days — even one gap resets the sandbox phase
- Do not change channel name/handle in first 30 days
- Do not buy fake views — instant channel strike
- Do not use movie/TV clips — Content ID auto-detects within hours → channel strike
