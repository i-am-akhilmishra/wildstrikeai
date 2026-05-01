import asyncio
import edge_tts
import random


# Dramatic male and female voices — Microsoft Edge Neural TTS (100% free, no API key)
MALE_VOICES = [
    "en-GB-RyanNeural",       # British male — deep, authoritative
    "en-US-GuyNeural",        # American male — commanding
    "en-AU-WilliamNeural",    # Australian male — gritty
]

FEMALE_VOICES = [
    "en-GB-SoniaNeural",      # British female — dramatic, bold
    "en-US-AriaNeural",       # American female — expressive
    "en-AU-NatashaNeural",    # Australian female — strong tone
]

# Pick one male + one female randomly per run for variety
ALL_VOICES = MALE_VOICES + FEMALE_VOICES


async def _generate_async(script: str, output_path: str):
    voice = random.choice(ALL_VOICES)
    print(f"[Voiceover] Using voice: {voice}")
    communicate = edge_tts.Communicate(
        text=script,
        voice=voice,
        rate="-8%",       # slightly slower = more dramatic, easier to follow
        pitch="-8Hz",     # deeper pitch for gravitas
    )
    await communicate.save(output_path)


def generate_voiceover(script: str, output_path: str = "voiceover.mp3") -> str:
    """
    Converts script to AI speech using Microsoft Edge Neural TTS.
    Completely free — no API key needed. Supports male & female dramatic voices.
    """
    asyncio.run(_generate_async(script, output_path))
    print(f"[Voiceover] Saved to {output_path}")
    return output_path
