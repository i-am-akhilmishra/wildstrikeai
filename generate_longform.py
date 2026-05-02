"""
generate_longform.py
────────────────────
Generates a 20-22 minute long-form YouTube wildlife documentary.
5 animal segments (~4 min each) with title cards between them.
Output: final_longform.mp4 (1920x1080 landscape)
"""

import os
import sys
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pipeline"))

from pipeline.longform_script_gen import generate_longform_segments
from pipeline.voiceover import generate_voiceover, ALL_VOICES
from pipeline.footage_fetcher import fetch_wildlife_clips
from pipeline.longform_assembler import (
    assemble_segment, create_title_card, assemble_longform, get_duration
)
from pipeline.thumbnail_generator import generate_thumbnail


def main():
    print("=" * 58)
    print("  WildStrikeAI — Long-Form Documentary (20-22 min)")
    print("=" * 58)

    # Pick ONE narrator voice — consistent throughout the full documentary
    voice = random.choice(ALL_VOICES)
    print(f"\n[Narrator] {voice}")

    # ── Step 1: Generate 5 segment scripts ──
    print("\n[1/4] Generating 5 segment scripts...")
    segments = generate_longform_segments(n=5)
    for i, (title, script, term) in enumerate(segments):
        print(f"  Segment {i+1}: '{title}' | footage: '{term}' | {len(script.split())} words")

    # Save full script for artifact review
    with open("longform_script.txt", "w", encoding="utf-8") as f:
        for i, (title, script, term) in enumerate(segments):
            f.write(f"{'='*52}\nSEGMENT {i+1}: {title}\nFootage: {term}\n{'='*52}\n\n{script}\n\n")

    # GitHub Actions Job Summary
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as f:
            f.write("## 🎬 Long-Form Documentary — Segment Overview\n\n")
            for i, (title, script, term) in enumerate(segments):
                f.write(f"**Segment {i+1}: {title}** — footage: `{term}` — {len(script.split())} words\n\n")
            f.write("\n> ⏳ Upload job is paused — waiting for your approval.\n")

    # ── Step 2: Voiceovers + footage per segment ──
    print("\n[2/4] Generating voiceovers and fetching footage for each segment...")
    segment_audio = []
    segment_clips = []

    for i, (title, script, search_term) in enumerate(segments):
        print(f"\n  [{i+1}/5] {title}")

        audio_path = f"longform_audio_{i}.mp3"
        generate_voiceover(script, audio_path, voice=voice)

        clips = fetch_wildlife_clips(
            api_key=os.environ["PEXELS_API_KEY"],
            search_term=search_term,
            num_clips=10,
            save_dir=f"clips/seg_{i}",
        )
        if not clips:
            print(f"  [WARNING] No clips for segment {i+1}, reusing segment 0 clips")
            clips = segment_clips[0] if segment_clips else []

        segment_audio.append(audio_path)
        segment_clips.append(clips)

    # ── Step 3: Assemble segments + title cards ──
    print("\n[3/4] Assembling segments and title cards...")
    os.makedirs("longform_temp", exist_ok=True)
    segment_files = []
    title_card_files = []

    for i, (title, _, _) in enumerate(segments):
        print(f"  Building title card {i+1}: '{title}'...")
        tc_path = f"longform_temp/titlecard_{i}.mp4"
        create_title_card(title, tc_path, duration=3.0)
        title_card_files.append(tc_path)

        print(f"  Assembling segment {i+1}/5...")
        seg_path = f"longform_temp/segment_{i}.mp4"
        assemble_segment(segment_clips[i], segment_audio[i], seg_path)
        segment_files.append(seg_path)

    # ── Step 4: Final concat ──
    print("\n[4/4] Concatenating all segments into final video...")
    final_path = assemble_longform(segment_files, title_card_files, "final_longform.mp4")

    # Thumbnail from 15% into the video (first segment, past title card)
    print("\n[+] Generating thumbnail...")
    generate_thumbnail(final_path, "longform_thumbnail.jpg")

    # Write chapter timestamps for YouTube description
    _write_chapters(segments, title_card_files, segment_files)

    total_dur = get_duration(final_path)
    mins = int(total_dur // 60)
    secs = int(total_dur % 60)

    print("\n" + "=" * 58)
    print(f"  Done! Final video: {mins}m {secs}s")
    print("  Artifacts: final_longform.mp4 | longform_thumbnail.jpg")
    print("  Approve the upload job to publish to YouTube.")
    print("=" * 58)


def _write_chapters(segments, title_card_files, segment_files):
    """Calculates YouTube chapter timestamps and writes to longform_chapters.txt."""
    lines = ["0:00 Introduction — WildStrikeAI"]
    elapsed = 0.0

    for i, (title, _, _) in enumerate(segments):
        try:
            tc_dur = get_duration(title_card_files[i])
        except Exception:
            tc_dur = 3.0
        elapsed += tc_dur

        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        lines.append(f"{minutes}:{seconds:02d} {title}")

        try:
            seg_dur = get_duration(segment_files[i])
        except Exception:
            seg_dur = 240.0
        elapsed += seg_dur

    with open("longform_chapters.txt", "w") as f:
        f.write("\n".join(lines))

    print("\n[Chapters]")
    for line in lines:
        print(f"  {line}")


if __name__ == "__main__":
    main()
