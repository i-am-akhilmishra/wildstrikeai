"""
longform_script_gen.py
──────────────────────
Generates 5 animal segment scripts for a 20-22 min long-form YouTube video.
Each segment: 400-440 words (~4 minutes at -20% narration rate).
Returns: list of (chapter_title, script, search_term)
"""

import os
import datetime
import random

try:
    from google import genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


# 12 available segment topics — 5 picked per day using rotation
ALL_SEGMENT_TOPICS = [
    ("The Speed of Survival",  "a cheetah mother hunting on the open Serengeti savanna",               "cheetah running savanna"),
    ("Apex of the Pride",      "a lion pride coordinating a night ambush on a wildebeest herd",        "lion hunting africa"),
    ("Ancient Patience",       "a Nile crocodile waiting at a river crossing for migrating wildebeest", "crocodile river attack"),
    ("Terror from the Deep",   "a great white shark launching a breach attack on a Cape fur seal",      "great white shark ocean"),
    ("The Shadow Hunter",      "a leopard stalking prey through dense jungle in total darkness",         "leopard wildlife jungle"),
    ("The Pack Mentality",     "a wolf pack running down an elk across frozen tundra",                  "wolf pack hunting snow"),
    ("Phantom of the Amazon",  "a jaguar ambushing a caiman at the Amazon river edge",                  "jaguar jungle amazon"),
    ("Mastery of the Sky",     "a golden eagle stooping at full speed on mountain prey",                "eagle hunting bird prey"),
    ("The Striped Ghost",      "a Bengal tiger stalking a spotted deer through monsoon jungle",         "tiger wild jungle"),
    ("The Dragon's Patience",  "a Komodo dragon tracking and ambushing a water buffalo",                "komodo dragon wildlife"),
    ("The River King",         "a hippo defending territory against lions and crocodiles",              "hippo river africa"),
    ("The Bone Crusher",       "a spotted hyena clan outwitting lions to claim a carcass",             "hyena wildlife africa"),
]

GEMINI_MODELS = ["gemini-2.0-flash-lite", "gemini-2.0-flash", "gemini-1.5-flash"]

SEGMENT_PROMPT = """Write a dramatic wildlife documentary narration script for this segment:

Animal/Scene: {topic_desc}
Chapter title: "{chapter_title}"

Requirements:
- Exactly 400 to 440 words
- Opens with a powerful atmospheric hook — place the viewer in the scene immediately
- Builds tension progressively through the hunt or encounter
- Peaks at the climactic strike or confrontation
- Closes with a reflection on what this moment reveals about survival
- Tone: David Attenborough meets Planet Earth — calm, authoritative, emotionally resonant
- Mix short punchy sentences at tense moments with longer flowing sentences for atmosphere
- Present tense throughout
- No stage directions, asterisks, chapter headings, or labels — pure narration only

Output only the narration script. Nothing else."""


FALLBACK_SEGMENTS = [
    (
        "The Speed of Survival",
        """The Serengeti stretches endlessly under a white-hot sky. Nothing moves. Even the air seems to hold its breath.

Then, from the golden grass, two amber eyes open.

The cheetah has been watching the gazelle herd for forty minutes. She has already selected her target — a young male, slightly separated from the group. Unaware. Exposed.

She rises slowly, keeping impossibly low. Her spotted coat dissolves into the dry grass. Every muscle in her frame coils, waiting for the precise moment.

The gazelle lowers its head to graze.

She moves.

Zero to forty miles per hour in two strides. Zero to seventy in three. The acceleration is violent, unlike anything else alive on this planet. The ground becomes a blur.

The gazelle snaps its head up. For one terrible fraction of a second, it freezes. Then survival instinct fires and it bolts left, cutting hard across the plain.

But the cheetah has already read the movement. She cuts inside the turn, her spine flexing like a whip, her tail spinning as counterbalance. The gap closes in fractions of a second.

Fifty metres. Twenty. Ten.

Her front paw swipes the hindquarters. The gazelle tumbles in an explosion of dust. The cheetah is on it instantly, jaws locked around the throat, holding until the struggle ends.

Silence falls over the plain.

The cheetah lifts her head. Her sides heave. That seven-second sprint has cost her nearly everything. She pants rapidly, body temperature dangerously high. She cannot eat yet. She must recover.

But there is another problem. Across the plain, two lions have spotted the kill. They walk towards her with the unhurried confidence of animals that fear nothing.

She has four minutes.

The cheetah begins to feed immediately, tearing quickly, eating as much as she can before they arrive. This is the calculation she makes every single day. Sprint at the edge of survival. Risk collapse. Eat fast. Lose the kill anyway.

She has raised three cubs this season using this method. Three small spotted faces waiting for her return, hidden in the long grass two kilometres north.

Every meal she takes is for them.

The lions arrive. The cheetah steps away without confrontation. She watches from twenty metres as they claim what she killed.

She will hunt again before the sun touches the horizon.

That is the arithmetic of her life. Run. Risk everything. Begin again.""",
        "cheetah running savanna",
    ),
    (
        "Ancient Patience",
        """The Nile has moved through this valley for forty million years. Everything here bends to its rhythm. The crocodile understands this better than any creature alive.

He has not moved in eleven hours.

Lying at the bank's edge, half submerged in dark water, he is indistinguishable from the mud around him. His eyes remain open. Nothing in his body betrays a living animal. He is stone. He is the river itself.

On the opposite bank, a wildebeest herd of three hundred animals paces nervously. They need water. The crossing is dangerous and every one of them knows it. They can sense something in the current. One animal steps forward, then retreats. Another follows, then stops.

Eventually, thirst wins.

The first wildebeest enters the shallows. Then ten more. Then the herd pours in — bodies pressed together, hooves churning white water, collective fear making the decision for each individual animal.

The crocodile does not rush. He watches. He selects.

One wildebeest has drifted two metres from the main body. Not much. It is enough.

He moves.

What happens in the next half-second has not changed in four hundred million years. The water erupts. Jaws generating three thousand pounds of force snap shut around the animal's neck. There is no hesitation. No warning. The same strike his ancestors performed when dinosaurs still walked this earth.

The wildebeest fights desperately. It is powerful and terrified, thrashing against the surface with everything it has. The herd abandons it immediately, scattering to the far bank.

The crocodile rolls.

The death roll is absolute. Nothing counters it. The river takes them both beneath the surface for a long moment. Then the water settles into slow, dark eddies.

Other crocodiles arrive within minutes, drawn by the disturbance. They feed methodically, without urgency, the way animals eat when they know the river will always provide again.

The Nile flows on.

The crocodile will not need to eat for another month. He will return to his position. He will become stone and mud and patience once more.

He will wait.

He has always waited. He will still be waiting long after the animals crossing above him have become something else entirely. The river keeps its secrets. And the crocodile keeps the river.""",
        "crocodile river attack",
    ),
    (
        "The Pack Mentality",
        """Winter has locked the boreal forest in silence. The temperature stands at minus thirty. The snow is two feet deep and still falling through the birch trees like ash from a dead fire.

Seven wolves move through it without a sound.

They have been tracking this elk for three hours. He is a large bull, moving with a slight favouring of his left foreleg. The wolves detected this within minutes of picking up his trail. They have been patient since then, keeping their distance, letting the cold and the distance do the work.

The pack does not rush. They are not built for short sprints. Their gift is something rarer and more terrible — they can run for hours without stopping. They can wait days. They can think.

The lead female signals with her body and the pack spreads wide, flanking through the trees on both sides of the elk's path. She knows where the ravine narrows half a kilometre ahead.

The elk senses them now. His head comes up. His nostrils flare. He breaks into a run.

Across open snowfields his power is clear. He crashes through drifts that the wolves wade through. But the wolves are everywhere. Every route he takes, a grey shape materialises to redirect him. He is being herded, though he does not understand this yet.

The ravine approaches.

He hits the deeper snow at the base of the slope and slows dramatically. The foreleg betrays him now, buckling on the uneven ground. He stumbles. Rights himself. Stumbles again.

The lead female is on him in three strides.

The pack closes around their kill with the efficiency of animals who have practised this together for years. It is not dramatic. It does not last long. What it is, is certain.

In the brutal mathematics of the northern winter, certainty is everything.

The wolves will feed for two days from this kill. Ravens will arrive by morning to take what remains. The forest will reclaim the rest by spring.

The elk lived eight winters in this forest. He was powerful, cautious, built for survival.

He was not built for a pack that never stops.

Nothing is.""",
        "wolf pack hunting snow",
    ),
    (
        "Apex of the Pride",
        """Darkness across the Serengeti is not the absence of danger. It is when danger wakes up.

The moon sits three-quarters full, casting silver light across the grass. Enough to see. Not enough to be seen. The lions have been moving since sunset, reading the wind, choosing their moment.

There are eight of them. Four females leading, three males hanging back, one young male on only his second hunt. He watches everything.

Half a kilometre ahead, a wildebeest herd of two hundred animals rests. The lions have already identified their target — a bull on the outer edge, older, moving with a slight stiffness in his hip. Weakness is a language predators read fluently.

The lead female drops low. Seven others mirror her without a signal. No sound passes between them.

They split. Two females peel left around the herd. Two hold the right flank. The manoeuvre takes forty minutes and covers four hundred metres. Patience is not a virtue for a lion. It is the foundation of every meal.

The wildebeest sense something. Heads rise. Ears turn. The unease moves through the herd like a current through dark water.

Too late.

The lead female breaks from forty metres at full speed. The herd erupts. Two thousand hooves moving in every direction at once. Dust fills the air like a storm.

The target bull tries to run with the herd. His hip betrays him. He falls fractionally behind. Just fractionally. It is all the gap the lions need.

The second female cuts his path. He turns. The third blocks the next angle. The fourth completes the trap.

The lead female hits him from behind, driving her weight into his hindquarters. He goes down hard. The others are on him in seconds.

It is over in less than a minute.

The males arrive and take their positions at the kill. The females wait, as they always wait. The young male paces the outer edge, learning how hunger and hierarchy sit beside each other in the pride.

By dawn, little remains. The Serengeti feeds in layers. Everything serves something.

The lions sleep as the sun rises, their stomachs full.

Tomorrow night, they will wake up hungry again.""",
        "lion hunting africa",
    ),
    (
        "Terror from the Deep",
        """Six miles off the coast of South Africa, the cold Benguela Current meets warmer surface water. Where they meet, the ocean becomes one of the most dangerous stretches of sea on earth.

Below the surface, something large is moving upward.

The Cape fur seal is young, perhaps two years old, swimming at the surface in the early morning light. She has made this swim before. She does not look down. Seals rarely do. It would not help much if they did.

The great white shark has been here since before dawn.

She is five metres long and weighs over a thousand kilograms. She has patrolled this stretch of water every morning for weeks, learning the seals' patterns, timing the light, positioning herself in the darkness below the surface where the seals cannot see her.

She watches the young seal from forty metres below.

The shark accelerates.

She comes from directly below, her white belly invisible against the bright surface when seen from above, her dark back invisible against the deep when seen from below. Counter-shading. An evolutionary solution four hundred million years in the making.

The speed of the final ascent is extraordinary. She covers forty metres in under two seconds.

The ocean explodes.

The shark breaches completely clear of the water, the seal gripped in her jaws, both of them momentarily suspended in air above the surface. It lasts less than a second. Then they crash back into the white water.

The seal is gone.

The surface churns briefly, then settles into slow red-tinged swells. The other seals scatter in every direction, their alarm calls sharp across the water.

The shark descends into the darkness again, resuming her patrol.

From above, the ocean looks placid now. The morning light plays across the surface. Gulls call. A distant seal surfaces to breathe.

Everything looks normal.

It never really is.""",
        "great white shark ocean",
    ),
]


def _pick_today_segments(n: int = 5) -> list:
    """Rotates through ALL_SEGMENT_TOPICS using day of year so segments change daily."""
    day = datetime.date.today().timetuple().tm_yday
    start = (day * 3) % len(ALL_SEGMENT_TOPICS)
    indices = [(start + i) % len(ALL_SEGMENT_TOPICS) for i in range(n)]
    return [ALL_SEGMENT_TOPICS[i] for i in indices]


def _generate_with_gemini(api_key: str, chapter_title: str, topic_desc: str) -> str | None:
    if not GENAI_AVAILABLE:
        return None
    client = genai.Client(api_key=api_key)
    prompt = SEGMENT_PROMPT.format(chapter_title=chapter_title, topic_desc=topic_desc)
    for model in GEMINI_MODELS:
        try:
            response = client.models.generate_content(model=model, contents=prompt)
            text = response.text.strip()
            if len(text.split()) >= 380:
                print(f"[Script] '{chapter_title}' via {model} ({len(text.split())} words)")
                return text
        except Exception as e:
            err = str(e)
            if "429" in err or "quota" in err.lower():
                print(f"[Script] {model} quota exceeded")
            else:
                print(f"[Script] {model} error: {err[:80]}")
    return None


def generate_longform_segments(n: int = 5) -> list:
    """
    Returns list of (chapter_title, script, search_term) for n segments.
    Uses Gemini if available, falls back to pre-written scripts.
    """
    topics = _pick_today_segments(n)
    api_key = os.environ.get("GEMINI_API_KEY")

    fallback_by_title = {s[0]: s for s in FALLBACK_SEGMENTS}

    results = []
    for chapter_title, topic_desc, search_term in topics:
        script = None
        if api_key:
            script = _generate_with_gemini(api_key, chapter_title, topic_desc)

        if not script:
            fallback = fallback_by_title.get(chapter_title)
            if fallback:
                script = fallback[1]
                print(f"[Script] '{chapter_title}' using pre-written fallback")
            else:
                fb = random.choice(FALLBACK_SEGMENTS)
                script = fb[1]
                print(f"[Script] '{chapter_title}' using random fallback: {fb[0]}")

        results.append((chapter_title, script, search_term))

    return results
