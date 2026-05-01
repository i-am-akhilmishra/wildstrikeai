import requests
import os
import random


# Rotating search terms — all wild predator themed
SEARCH_TERMS = [
    "lion hunting",
    "cheetah running",
    "leopard wildlife",
    "wild animals savanna",
    "crocodile river",
    "wild dogs africa",
    "eagle hunt",
    "wolf pack",
    "tiger wild",
    "hyena wildlife",
    "hippo attack",
    "shark ocean",
    "jaguar jungle",
    "bear hunting fish",
    "hawk bird prey",
]


def fetch_wildlife_clips(api_key: str, search_term: str = None, num_clips: int = 6, save_dir: str = "clips") -> list:
    """
    Downloads wildlife video clips from Pexels matching the script's topic.
    search_term is passed from generate_script() to ensure footage matches narration.
    """
    os.makedirs(save_dir, exist_ok=True)

    # Use the topic-matched term; fall back to random only if not provided
    term = search_term if search_term else random.choice(SEARCH_TERMS)
    print(f"[Pexels] Footage search term: '{term}'")
    headers = {"Authorization": api_key}
    downloaded = []

    for orientation in ["landscape", "portrait"]:
        if len(downloaded) >= num_clips:
            break

        params = {
            "query": term,
            "per_page": 20,
            "orientation": orientation,
            "size": "medium",
        }

        print(f"[Pexels] Searching '{term}' ({orientation})...")
        try:
            response = requests.get(
                "https://api.pexels.com/videos/search",
                headers=headers,
                params=params,
                timeout=30,
            )
            response.raise_for_status()
        except Exception as e:
            print(f"[Pexels] Search failed: {e}")
            continue

        videos = response.json().get("videos", [])
        random.shuffle(videos)

        for video in videos:
            if len(downloaded) >= num_clips:
                break

            video_files = sorted(
                video.get("video_files", []),
                key=lambda x: x.get("width", 0),
                reverse=True,
            )
            if not video_files:
                continue

            # Pick HD but not oversized
            chosen = None
            for vf in video_files:
                if 720 <= vf.get("width", 0) <= 1920:
                    chosen = vf
                    break
            if not chosen:
                chosen = video_files[-1]

            url = chosen.get("link")
            if not url:
                continue

            clip_path = os.path.join(save_dir, f"clip_{len(downloaded)}.mp4")
            print(f"[Pexels] Downloading clip {len(downloaded) + 1}/{num_clips}...")

            try:
                r = requests.get(url, stream=True, timeout=120)
                r.raise_for_status()
                with open(clip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=16384):
                        f.write(chunk)
                downloaded.append(clip_path)
            except Exception as e:
                print(f"[Pexels] Failed to download clip: {e}")
                continue

    print(f"[Pexels] Downloaded {len(downloaded)} clips")
    return downloaded
