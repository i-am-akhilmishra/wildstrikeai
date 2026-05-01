"""
generate_video.py
─────────────────
Steps 1-5 only: Script → Voiceover → Footage → Video → Thumbnail
Saves outputs locally and writes script to script.txt for review.
Does NOT upload to YouTube — that is done after manual approval.
"""

import os
import sys

from script_generator import generate_script
from voiceover import generate_voiceover
from footage_fetcher import fetch_wildlife_clips
from video_assembler import assemble_video
from thumbnail_generator import generate_thumbnail


def main():
    print("=" * 50)
    print("  WildStrikeAI — Video Generation (Step 1/2)")
    print("=" * 50)

    # ── Step 1: Generate script + get matched footage search term ──
    print("\n[1/5] Generating script...")
    script, search_term = generate_script()  # returns (script, footage_search_term)

    # Save script to file so it shows in GitHub Actions summary + artifact
    with open("script.txt", "w", encoding="utf-8") as f:
        f.write(f"Footage search term: {search_term}\n\n{script}")

    # Write to GitHub Actions Job Summary (visible in Actions UI)
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write("## 📋 Generated Script\n\n")
            f.write(f"**Footage topic:** `{search_term}`\n\n")
            f.write(f"```\n{script}\n```\n\n")
            f.write("## 📥 Review Checklist\n")
            f.write("- [ ] Script sounds natural and dramatic\n")
            f.write("- [ ] No inappropriate content\n")
            f.write("- [ ] Download & watch `final_short.mov` from the artifact below\n")
            f.write("- [ ] Approve the `upload` job when satisfied\n\n")
            f.write("> ⏳ **Upload job is paused — waiting for your approval.**\n")

    # ── Step 2: Voiceover ──
    print("\n[2/5] Generating voiceover...")
    audio_path = generate_voiceover(script, "voiceover.mp3")

    # ── Step 3: Footage — matched to the script topic ──
    print("\n[3/5] Fetching wildlife footage from Pexels...")
    clips = fetch_wildlife_clips(
        api_key=os.environ["PEXELS_API_KEY"],
        search_term=search_term,   # ← matched to narration topic
        num_clips=6,
        save_dir="clips",
    )
    if not clips:
        print("[ERROR] No footage downloaded. Check your PEXELS_API_KEY.")
        sys.exit(1)

    # ── Step 4: Assemble video ──
    print("\n[4/5] Assembling 4K 60fps 70-second video...")
    video_path = assemble_video(clips, audio_path, script, "final_short.mov")

    # ── Step 5: Thumbnail ──
    print("\n[5/5] Generating thumbnail...")
    generate_thumbnail(video_path, "thumbnail.jpg")

    print("\n" + "=" * 50)
    print("  Video ready for review!")
    print("  Go to Actions → this run → Artifacts → download 'review-package'")
    print("  Then approve the 'upload' job to publish to YouTube.")
    print("=" * 50)


if __name__ == "__main__":
    main()
