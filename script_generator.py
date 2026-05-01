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


def generate_script() -> str:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    topic = random.choice(TOPICS)

    prompt = f"""Write a dramatic wildlife narration script for a 40-second YouTube Shorts video.

Topic: {topic}

Requirements:
- Exactly 90 to 100 words total (this matches ~40 seconds at natural speaking pace)
- Dramatic, gripping, David Attenborough style
- Short punchy sentences — maximum 12 words per sentence
- No stage directions, no scene descriptions, pure narration only
- Build tension across the script and end with a powerful single-line conclusion

Output ONLY the narration text. No titles, no labels, no quotes — just the raw script."""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    script = response.text.strip()
    print(f"[Script Generated]\n{script}\n")
    return script
