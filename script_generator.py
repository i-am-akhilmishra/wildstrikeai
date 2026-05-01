from google import genai
import os
import random
import datetime


# Each entry: (script topic description, footage search term for Pexels)
TOPICS = [
    ("a cheetah chasing a gazelle at full sprint across the open savanna",         "cheetah running fast"),
    ("a lion pride ambushing a wildebeest herd at dusk in the Serengeti",           "lion hunting africa"),
    ("a leopard silently stalking prey through dense jungle undergrowth",            "leopard wildlife jungle"),
    ("a crocodile launching from a river to catch a zebra drinking at the bank",    "crocodile river attack"),
    ("a pack of wild dogs relentlessly cornering an impala across the plains",      "wild dogs hunting africa"),
    ("a great white shark breaching the surface to ambush a seal",                  "great white shark ocean"),
    ("a wolf pack driving an elk to exhaustion through a frozen forest",            "wolf pack hunting snow"),
    ("a golden eagle stooping at 200mph onto a mountain hare",                      "eagle hunting bird prey"),
    ("a jaguar ambushing a caiman in the dense Amazon rainforest",                  "jaguar jungle amazon"),
    ("a tiger stalking a deer through tall grass at the edge of a jungle stream",   "tiger wild jungle"),
    ("a komodo dragon ambushing a deer on a remote Indonesian island",              "komodo dragon wildlife"),
    ("a nile crocodile and hippo fighting over territory in a muddy river",         "hippo river africa"),
]

# Pre-written fallback scripts paired with their search terms
FALLBACK_SCRIPTS = [
    (
        "The savanna bakes under a merciless sun. Nothing moves. Nothing breathes. "
        "Then a cheetah rises from the golden grass. Its eyes lock on a gazelle three hundred metres away. "
        "Every muscle in its body tightens. It lowers. It waits. "
        "The gazelle lifts its head. Looks around. Senses nothing. "
        "The cheetah explodes forward. Zero to seventy miles per hour in three strides. "
        "The gazelle bolts left. The cheetah cuts inside. "
        "Closer. Closer. A swipe of the paw. The gazelle tumbles. "
        "Dust rises. Silence falls. "
        "In the open wild, speed is the difference between life and death. "
        "Today, the cheetah lives. The gazelle does not.",
        "cheetah running fast",
    ),
    (
        "The Nile moves slowly under the midday heat. "
        "A herd of zebra approaches the bank. They hesitate. They sense something. "
        "But thirst wins. One zebra steps forward into the shallows. "
        "Below the surface, two yellow eyes have been watching for six hours. "
        "The crocodile has not moved. It does not need to. "
        "In an instant, the water explodes. Jaws close with three thousand pounds of force. "
        "The zebra fights. Kicks. Screams. The crocodile rolls. "
        "The death roll is ancient. Unstoppable. Absolute. "
        "The river settles. The surface goes calm again. "
        "Four hundred million years of evolution just played out in eight seconds.",
        "crocodile river attack",
    ),
    (
        "Midnight in the Serengeti. The lions have been watching the wildebeest herd for two hours. "
        "They move in silence. Splitting left and right through the darkness. "
        "One wildebeest stands apart from the herd. Old. Slow. Exposed. "
        "The lead lioness drops low. Ten metres. Five. Two. "
        "She launches. Five hundred pounds of muscle and hunger. "
        "The wildebeest bellows. The herd scatters. Too late. "
        "Three more lions arrive within seconds. "
        "The struggle is fierce. But the outcome was decided the moment it stepped away from the herd. "
        "The savanna goes dark again. "
        "The lions feed. This is the law of the wild. Brutal. Honest. Final.",
        "lion hunting africa",
    ),
    (
        "The Amazon is ancient. Dense. Alive with unseen danger. "
        "A caiman rests on the muddy bank, completely still in the morning heat. "
        "In the branches above, a jaguar watches. It has been there for forty minutes. "
        "The jaguar moves like water. Silent. Liquid. Down through the branches and onto the bank. "
        "The caiman does not hear a single sound. "
        "The jaguar strikes with a bite force that crushes bone. "
        "No chase. No warning. No second chances in the jungle. "
        "The caiman thrashes once. Then twice. Then nothing. "
        "The jaguar drags its kill into the shadows of the rainforest. "
        "In here, the apex predator strikes without mercy.",
        "jaguar jungle amazon",
    ),
    (
        "The tiger waits at the edge of the jungle stream. Perfectly still. Invisible in the dappled light. "
        "A spotted deer steps into the shallows to drink. It does not look up. "
        "It cannot see the orange and black shape crouched fifteen metres away. "
        "The tiger reads every movement. Every flicker. Every breath. "
        "It waits for the deer to lower its head. "
        "Then it moves. A low sprint through the long grass. "
        "Twelve metres. Eight. Four. "
        "The strike is explosive. Jaws locked on the throat. "
        "The deer collapses in seconds. "
        "The jungle absorbs everything. The tiger disappears. As if nothing ever happened.",
        "tiger wild jungle",
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
        f"Write a dramatic wildlife narration script for a 70-second YouTube Shorts video.\n\n"
        f"Topic: {topic_desc}\n\n"
        f"Requirements:\n"
        f"- Exactly 155 to 165 words total (matches ~70 seconds at natural speaking pace)\n"
        f"- Dramatic, raw, gripping — like a David Attenborough jungle documentary\n"
        f"- Short punchy sentences, maximum 12 words per sentence\n"
        f"- No stage directions, no scene descriptions, pure narration only\n"
        f"- Build tension steadily, reach a violent climax, end with one brutal conclusion line\n\n"
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
