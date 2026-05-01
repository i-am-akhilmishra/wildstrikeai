from google import genai
import os
import random
import datetime


# Each entry: (script topic description, footage search term for Pexels)
TOPICS = [
    ("a cheetah chasing a gazelle at full sprint across the savanna",   "cheetah running fast"),
    ("a lion pride ambushing a wildebeest at dusk",                     "lion hunting africa"),
    ("a leopard silently stalking its prey through tall grass",         "leopard wildlife africa"),
    ("a crocodile launching from a river to catch a zebra",             "crocodile river africa"),
    ("a pack of wild dogs cornering an impala",                         "wild dogs hunting africa"),
    ("a great white shark ambushing a seal from below",                 "great white shark ocean"),
    ("a wolf pack chasing an elk through deep snow",                    "wolf pack hunting snow"),
    ("a golden eagle diving at 200mph to snatch a rabbit",              "eagle hunting bird prey"),
]

# Pre-written fallback scripts paired with their search terms
FALLBACK_SCRIPTS = [
    (
        "The savanna holds its breath. A cheetah locks eyes on a distant gazelle. "
        "Every muscle coils. The world slows. Then pure explosion. "
        "Sixty miles per hour in three seconds. The gazelle twists. Turns. Runs for its life. "
        "But the cheetah is faster. Smarter. Unstoppable. "
        "One final lunge. Silence. "
        "Nature has no mercy. Only winners and the forgotten.",
        "cheetah running fast",
    ),
    (
        "The Nile glitters under a blazing African sun. "
        "A zebra steps toward the water. It does not see what waits below. "
        "The crocodile has not moved in six hours. Stone-still. Patient. Ancient. "
        "One second. One explosion of power. "
        "Four hundred million years of evolution — unleashed in a single strike. "
        "The river runs red. The crocodile wins again.",
        "crocodile river africa",
    ),
    (
        "Darkness falls across the Serengeti. "
        "A lion pride moves like shadows through the tall grass. "
        "Their target: a lone wildebeest, separated from the herd. "
        "The lions split — left, right, cutting off every escape. "
        "There is no running now. Nowhere to go. "
        "This is what the top of the food chain looks like. Raw. Absolute. Final.",
        "lion hunting africa",
    ),
    (
        "High above the Scottish highlands, a golden eagle circles. "
        "Below, a rabbit grazes, completely unaware. "
        "The eagle folds its wings. Becomes a missile. "
        "Two hundred miles per hour. Razor talons forward. "
        "The rabbit has zero warning. Zero chance. "
        "From sky to strike in under three seconds. Nature's perfect hunter.",
        "eagle hunting bird prey",
    ),
    (
        "The African wild dogs have been running for forty minutes. "
        "Their prey, an impala, is slowing down. "
        "These hunters never quit. They never give up. "
        "Working together, perfectly coordinated, cutting every angle. "
        "The impala stumbles. The pack closes in. "
        "In the wild, endurance beats speed. Every single time.",
        "wild dogs hunting africa",
    ),
    (
        "A leopard moves through the night like liquid shadow. "
        "It has stalked this antelope for two hours. Unseen. Unheard. "
        "Closer. Closer. Twenty metres. Ten. Five. "
        "One explosive leap. Powerful jaws lock on. "
        "The struggle lasts seconds. "
        "Darkness reclaims the bush. The leopard disappears with its prize.",
        "leopard wildlife africa",
    ),
    (
        "Deep beneath the cold Atlantic, a great white circles. "
        "The seal swims above, unaware of the shadow rising below. "
        "The shark accelerates. A hundred kilograms of muscle and instinct. "
        "The surface explodes. An eruption of power and spray. "
        "The ocean is calm again in seconds. "
        "Down here, the hunter never announces itself.",
        "great white shark ocean",
    ),
    (
        "Winter has locked the forest in silence. "
        "A lone elk breaks through the snow, breathing hard. "
        "Behind it — seven wolves. Coordinated. Relentless. Patient. "
        "They take turns. They tire it out. They wait for the moment. "
        "The elk stumbles once. That is all it takes. "
        "In the frozen wild, the pack always wins.",
        "wolf pack hunting snow",
    ),
]

# Models tried in order — falls back to next if quota exceeded
GEMINI_MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash-8b",
    "gemini-2.0-flash",
]


def _pick_topic_for_today() -> tuple:
    """
    Rotates through all topics based on day of year.
    Guarantees no consecutive repeats — full 8-day cycle before any topic repeats.
    """
    day_index = datetime.datetime.utcnow().timetuple().tm_yday
    return TOPICS[day_index % len(TOPICS)]


def _try_gemini(topic_desc: str, prompt: str):
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


def generate_script() -> tuple:
    """
    Returns (script_text, footage_search_term) so footage always matches narration.
    Topic rotates daily — no repeats for 8 days.
    """
    topic_desc, search_term = _pick_topic_for_today()
    print(f"[Script] Today's topic: {topic_desc}")
    print(f"[Script] Footage search term: {search_term}")

    prompt = (
        f"Write a dramatic wildlife narration script for a 40-second YouTube Shorts video.\n\n"
        f"Topic: {topic_desc}\n\n"
        f"Requirements:\n"
        f"- Exactly 90 to 100 words total (matches ~40 seconds at natural speaking pace)\n"
        f"- Dramatic, gripping, David Attenborough style\n"
        f"- Short punchy sentences, maximum 12 words per sentence\n"
        f"- No stage directions, no scene descriptions, pure narration only\n"
        f"- Build tension and end with a powerful single-line conclusion\n\n"
        f"Output ONLY the narration text. No titles, no labels, no quotes."
    )

    script = _try_gemini(topic_desc, prompt)

    if script:
        print(f"[Script — Gemini]\n{script}\n")
        return script, search_term

    # Gemini quota exhausted — find matching fallback for today's search term
    print("[Script] All Gemini models exhausted — using pre-written script bank")
    for fallback_script, fallback_term in FALLBACK_SCRIPTS:
        if fallback_term == search_term:
            print(f"[Script — Fallback matched]\n{fallback_script}\n")
            return fallback_script, search_term

    # Last resort — any fallback
    fallback_script, fallback_term = random.choice(FALLBACK_SCRIPTS)
    print(f"[Script — Fallback random]\n{fallback_script}\n")
    return fallback_script, fallback_term
