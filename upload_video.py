"""
upload_video.py
───────────────
Step 6 only: Upload the already-generated video + thumbnail to YouTube.
Fetches live trending hashtags before uploading for maximum reach.
Runs AFTER manual approval in GitHub Actions environment gate.
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pipeline"))

from pipeline.youtube_uploader import upload_short
from pipeline.trending_hashtags import get_trending_hashtags


def main():
    print("=" * 50)
    print("  WildStrikeAI — YouTube Upload (Step 2/2)")
    print("=" * 50)

    # Fetch 7-10 trending hashtags for description
    print("\n[Trending] Fetching live trending hashtags...")
    tags = get_trending_hashtags(
        youtube_api_key=os.environ["YOUTUBE_API_KEY"],
    )
    # Use 7-10 trending tags in description
    trending = tags[:10]
    hashtag_line = " ".join(f"#{t.lstrip('#')}" for t in trending)

    # Build title using top trending tag
    top_tag = tags[0].capitalize() if tags else "Wildlife"
    title = (
        f"Wild Predator Strikes! \U0001f981 #{top_tag} "
        f"#Shorts #Wildlife #WildStrikeAI"
    )

    # Description: hook + trending hashtags (7-10) in the caption section
    description = (
        "Watch nature's most powerful predators in action — real footage, cinematic narration.\n\n"
        "New wildlife Short every day. Subscribe so you never miss a hunt.\n\n"
        f"{hashtag_line}\n"
        "#Shorts #WildStrikeAI #Wildlife #NatureDocumentary #Animals"
    )

    print(f"\n[Upload] Title: {title}")
    print(f"[Upload] Tags: {tags[:8]}...")

    # ── Upload ──
    print("\n[6/6] Uploading approved video to YouTube...")
    try:
        upload_short("final_short.mov", "thumbnail.jpg", title=title, description=description)
    except Exception as e:
        print(f"\n[FAILED] Video was NOT uploaded to YouTube.")
        print(f"[FAILED] Reason: {e}")
        print("=" * 50)
        sys.exit(1)

    print("\n" + "=" * 50)
    print("  Done! Check your YouTube channel.")
    print("=" * 50)


if __name__ == "__main__":
    main()

