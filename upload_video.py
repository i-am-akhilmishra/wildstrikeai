"""
upload_video.py
───────────────
Step 6 only: Upload the already-generated video + thumbnail to YouTube.
Runs AFTER manual approval in GitHub Actions environment gate.
"""

import sys
from youtube_uploader import upload_short


def main():
    print("=" * 50)
    print("  WildStrikeAI — YouTube Upload (Step 2/2)")
    print("=" * 50)

    print("\n[6/6] Uploading approved video to YouTube...")
    upload_short("final_short.mp4", "thumbnail.jpg")

    print("\n" + "=" * 50)
    print("  Done! Check your YouTube channel.")
    print("=" * 50)


if __name__ == "__main__":
    main()
