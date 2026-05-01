import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pipeline"))

from pipeline.script_generator import generate_script
from pipeline.voiceover import generate_voiceover
from pipeline.footage_fetcher import fetch_wildlife_clips
from pipeline.video_assembler import assemble_video
from pipeline.thumbnail_generator import generate_thumbnail
from pipeline.youtube_uploader import upload_short


def main():
    print("=" * 50)
    print("  WildStrikeAI — YouTube Shorts Generator")
    print("=" * 50)

    # ── Step 1: Generate 40-second script via Gemini ──
    print("\n[1/6] Generating script...")
    script = generate_script()

    # ── Step 2: Generate voiceover via Edge TTS (free, dramatic) ──
    print("\n[2/6] Generating voiceover...")
    audio_path = generate_voiceover(script, "voiceover.mp3")

    # ── Step 3: Download wildlife clips from Pexels ──
    print("\n[3/6] Fetching wildlife footage from Pexels...")
    clips = fetch_wildlife_clips(
        api_key=os.environ["PEXELS_API_KEY"],
        num_clips=6,
        save_dir="clips",
    )

    if not clips:
        print("[ERROR] No footage downloaded. Check your PIXABAY_API_KEY.")
        sys.exit(1)

    # ── Step 4: Assemble final 40-second vertical video ──
    print("\n[4/6] Assembling video with cinematic effects...")
    video_path = assemble_video(clips, audio_path, script, "final_short.mp4")

    # ── Step 5: Generate dramatic thumbnail ──
    print("\n[5/6] Generating thumbnail...")
    thumb_path = generate_thumbnail(video_path, "thumbnail.jpg")

    # ── Step 6: Upload to YouTube ──
    print("\n[6/6] Uploading to YouTube...")
    upload_short(video_path, thumb_path)

    print("\n" + "=" * 50)
    print("  Done! Check your YouTube channel.")
    print("=" * 50)


if __name__ == "__main__":
    main()
