"""
upload_video.py
───────────────
Step 6 only: Upload the already-generated video + thumbnail to YouTube.
Fetches live trending hashtags before uploading for maximum reach.
Runs AFTER manual approval in GitHub Actions environment gate.
"""

import os
import sys
from youtube_uploader import upload_short
from trending_hashtags import get_trending_hashtags, build_hashtag_string


def main():
    print("=" * 50)
    print("  WildStrikeAI — YouTube Upload (Step 2/2)")
    print("=" * 50)

    # ── Fetch trending hashtags ──
    print("\n[Trending] Fetching live trending hashtags...")
    tags = get_trending_hashtags(
        youtube_api_key=os.environ["YOUTUBE_API_KEY"],
    )
    hashtag_str = build_hashtag_string(tags)

    # Build title using top trending tag
    top_tag = tags[0].capitalize() if tags else "Wildlife"
    title = (
        f"Wild Predator Strikes! \U0001f981 #{top_tag} "
        f"#Shorts #Wildlife #WildStrikeAI"
    )

    # Build description with trending hashtags
    description = (
        "Watch nature's most powerful predators in action!\n\n"
        "AI-generated wildlife narration by WildStrikeAI.\n\n"
        f"{hashtag_str}\n\n"
        "#Shorts #WildStrikeAI #Wildlife #NatureShorts #Animals"
    )

    print(f"\n[Upload] Title: {title}")
    print(f"[Upload] Tags: {tags[:8]}...")

    # ── Upload ──
    print("\n[6/6] Uploading approved video to YouTube...")
    upload_short("final_short.mov", "thumbnail.jpg", title=title, description=description)

    print("\n" + "=" * 50)
    print("  Done! Check your YouTube channel.")
    print("=" * 50)


if __name__ == "__main__":
    main()

