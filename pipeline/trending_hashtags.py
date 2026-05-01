"""
trending_hashtags.py
─────────────────────
Fetches currently trending hashtags using two free sources:

1. YouTube Data API v3 — trending videos in "Pets & Animals" category (cat 15)
   Extracts tags from top trending wildlife/animal videos right now.

2. pytrends (Google Trends) — free, no API key needed
   Pulls trending search terms related to wildlife topics.

Combines both sources and returns a ranked deduplicated hashtag list.
"""

import os
import re
import time
import random
from collections import Counter

import requests


# Base wildlife hashtags — always included as fallback
BASE_TAGS = [
    "wildlife", "wildanimals", "predator", "nature", "NatureShorts",
    "WildStrikeAI", "animals", "shorts", "lion", "cheetah",
    "leopard", "hunting", "safari", "animalplanet", "wildnature",
]

# Seed keywords for Google Trends
TREND_SEEDS = [
    "wildlife", "wild animals", "lion hunting", "animal attack",
    "nature documentary", "predator prey", "safari",
]


def _fetch_youtube_trending_tags(api_key: str) -> list:
    """
    Pulls top 20 trending videos in Pets & Animals category
    and extracts their tags as hashtags.
    """
    try:
        params = {
            "part": "snippet",
            "chart": "mostPopular",
            "videoCategoryId": "15",   # Pets & Animals
            "regionCode": "US",
            "maxResults": 20,
            "key": api_key,
        }
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])

        tags = []
        for item in items:
            snippet_tags = item.get("snippet", {}).get("tags", [])
            for t in snippet_tags:
                clean = re.sub(r"[^a-zA-Z0-9]", "", t).strip()
                if 3 <= len(clean) <= 25:
                    tags.append(clean.lower())

            # Also extract hashtags from description
            desc = item.get("snippet", {}).get("description", "")
            found = re.findall(r"#(\w+)", desc)
            tags.extend([f.lower() for f in found if 3 <= len(f) <= 25])

        print(f"[Trends] YouTube trending tags fetched: {len(tags)} raw tags")
        return tags

    except Exception as e:
        print(f"[Trends] YouTube trending fetch failed: {e}")
        return []


def _fetch_google_trends() -> list:
    """
    Uses pytrends to get rising/top queries for wildlife seed terms.
    Completely free — no API key needed.
    """
    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-US", tz=0, timeout=(10, 30))
        seed = random.choice(TREND_SEEDS)

        pytrends.build_payload([seed], cat=0, timeframe="now 1-d", geo="", gprop="youtube")
        related = pytrends.related_queries()

        tags = []
        for kw, data in related.items():
            for kind in ["top", "rising"]:
                df = data.get(kind)
                if df is not None and not df.empty:
                    for query in df["query"].tolist()[:10]:
                        clean = re.sub(r"[^a-zA-Z0-9]", "", query).strip()
                        if 3 <= len(clean) <= 25:
                            tags.append(clean.lower())

        print(f"[Trends] Google Trends tags fetched: {len(tags)} raw tags")
        return tags

    except Exception as e:
        print(f"[Trends] Google Trends fetch failed (non-critical): {e}")
        return []


def get_trending_hashtags(youtube_api_key: str, max_tags: int = 30) -> list:
    """
    Returns a combined, ranked, deduplicated list of trending hashtags.
    Always includes WildStrikeAI brand tags.
    Format: plain strings without # prefix (YouTube API uses tags without #).
    """
    all_tags = []

    # Source 1: YouTube trending
    yt_tags = _fetch_youtube_trending_tags(youtube_api_key)
    all_tags.extend(yt_tags)

    # Small delay to avoid rate limiting
    time.sleep(2)

    # Source 2: Google Trends
    gt_tags = _fetch_google_trends()
    all_tags.extend(gt_tags)

    # Rank by frequency across sources
    counter = Counter(all_tags)

    # Build final list: top trending first, then base tags, deduplicated
    seen = set()
    final = []

    # Top trending (appear in both sources = higher rank)
    for tag, _ in counter.most_common(20):
        if tag not in seen:
            final.append(tag)
            seen.add(tag)

    # Always include brand + base tags
    for tag in BASE_TAGS:
        tl = tag.lower()
        if tl not in seen:
            final.append(tag)
            seen.add(tl)

    final = final[:max_tags]
    print(f"[Trends] Final hashtag set ({len(final)}): {final[:10]}...")
    return final


def build_hashtag_string(tags: list, max_in_description: int = 15) -> str:
    """Returns a formatted hashtag string for YouTube description."""
    return " ".join(f"#{t}" for t in tags[:max_in_description])
