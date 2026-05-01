from google import genai
import os
import random


TOPICS = [
    "a cheetah chasing a gazelle at full sprint across the savanna",
    "a lion pride ambushing a wildebeest at dusk",
    "a leopard silently stalking its prey through tall grass",
    "a crocodile launching from a river to catch a zebra",
    "a pack of wild dogs cornering an impala",
    "a great white shark ambushing a seal from below",
    "a wolf pack chasing an elk through deep snow",
    "a golden eagle diving at 200mph to snatch a rabbit",
]

# Models tried in order — falls back to next if quota exceeded
GEMINI_MODELS = [
    "gemini-2.0-flash-lite",   # highest free quota
    "gemini-1.5-flash-8b",     # backup free tier
    "gemini-2.0-flash",        # last resort
]

# Pre-written fallback scripts — used when ALL Gemini models hit quota
FALLBACK_SCRIPTS = [
    "The savanna holds its breath. A cheetah locks eyes on a distant gazelle. "
    "Every muscle coils. The world slows. Then pure explosion. "
    "Sixty miles per hour in three seconds. The gazelle twists. Turns. Runs for its life. "
    "But the cheetah is faster. Smarter. Unstoppable. "
    "One final lunge. Silence. "
    "Nature has no mercy. Only winners and the forgotten.",

    "The Nile glitters under a blazing African sun. "
    "A zebra steps toward the water. It does not see what waits below. "
    "The crocodile has not moved in six hours. Stone-still. Patient. Ancient. "
    "One second. One explosion of power. "
    "Four hundred million years of evolution — unleashed in a single strike. "
    "The river runs red. The crocodile wins again.",

    "Darkness falls across the Serengeti. "
    "A lion pride moves like shadows through the tall grass. "
    "Their target: a lone wildebeest, separated from the herd. "
    "The lions split — left, right, cutting off every escape. "
    "There is no running now. Nowhere to go. "
    "This is what the top of the food chain looks like. Raw. Absolute. Final.",

    "High above the Scottish highlands, a golden eagle circles. "
    "Below, a rabbit grazes, completely unaware. "
    "The eagle folds its wings. Becomes a missile. "
    "Two hundred miles per hour. Razor talons forward. "
    "The rabbit has zero warning. Zero chance. "
    "From sky to strike in under three seconds. Nature's perfect hunter.",

    "The African wild dogs have been running for forty minutes. "
    "Their prey, an impala, is slowing down. "
    "These hunters never quit. They never give up. "
    "Working together, perfectly coordinated, cutting every angle. "
    "The impala stumbles. The pack closes in. "
    "In the wild, endurance beats speed. Every single time.",

    "A leopard moves through the night like liquid shadow. "
    "It has stalked this antelope for two hours. Unseen. Unheard. "
    "Closer. Closer. Twenty metres. Ten. Five. "
    "One explosive leap. Powerful jaws lock on. "
    "The struggle lasts seconds. "
    "Darkness reclaims the bush. The leopard disappears with its prize.",
]


def _try_gemini(topic: str, prompt: str):
    """Attempts Gemini API with model fallback. Returns script string or None."""
    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    except Exception as e:
        print(f"[Script] Gemini client init failed: {e}")
        return None

    for model in GEMINI_MODELS:
        try:
            print(f"[Script] Trying model: {model}...")
            response = client.models.generate_content(model=model, contents=prompt)
            print(f"[Script] Success with {model}")
            return response.text.strip()
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
                print(f"[Script] {model} quota exceeded — trying next...")
            else:
                print(f"[Script] {model} error: {err[:100]}")

    return None


def generate_script() -> str:
    topic = random.choice(TOPICS)
    print(f"[Script] Topic: {topic}")

    prompt = (
        f"Write a dramatic wildlife narration script for a 40-second YouTube Shorts video.\n\n"
        f"Topic: {topic}\n\n"
        f"Requirements:\n"
        f"- Exactly 90 to 100 words total (matches ~40 seconds at natural speaking pace)\n"
        f"- Dramatic, gripping, David Attenborough style\n"
        f"- Short punchy sentences, maximum 12 words per sentence\n"
        f"- No stage directions, no scene descriptions, pure narration only\n"
        f"- Build tension and end with a powerful single-line conclusion\n\n"
        f"Output ONLY the narration text. No titles, no labels, no quotes."
    )

    script = _try_gemini(topic, prompt)

    if script:
        print(f"[Script — Gemini]\n{script}\n")
        return script

    # All Gemini quota exhausted — use rotating pre-written bank
    print("[Script] All Gemini models exhausted — using pre-written script bank")
    script = random.choice(FALLBACK_SCRIPTS)
    print(f"[Script — Fallback]\n{script}\n")
    return script
