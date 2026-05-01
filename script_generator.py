import google.generativeai as genai
import os
import random


TOPICS = [
    "a cheetah chasing a gazelle at full sprint across the savanna",
    "a lion pride ambushing a wildebeest at dusk",
    "a leopard silently stalking its prey through tall grass",
    "a crocodile launching from a river to catch a zebra",
    "a pack of wild dogs cornering an impala",
]


def generate_script() -> str:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")

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

    response = model.generate_content(prompt)
    script = response.text.strip()
    print(f"[Script Generated]\n{script}\n")
    return script
