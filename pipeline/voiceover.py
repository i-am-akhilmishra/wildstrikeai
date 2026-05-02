import asyncio
import edge_tts
import random


# Most natural/human-sounding Edge Neural TTS voices
# These are the closest to real documentary narrators
ALL_VOICES = [
    "en-US-ChristopherNeural",  # warm, natural American male — most human-sounding
    "en-US-EricNeural",          # clear, calm American male
    "en-US-JennyNeural",         # warm, natural American female
    "en-GB-RyanNeural",          # natural British male — documentary tone
    "en-US-GuyNeural",           # authoritative American male
    "en-US-AriaNeural",          # expressive American female
]


async def _generate_async(script: str, output_path: str, voice: str = None):
    selected = voice if voice else random.choice(ALL_VOICES)
    print(f"[Voiceover] Using voice: {selected}")
    communicate = edge_tts.Communicate(
        text=script,
        voice=selected,
        rate="-20%",      # noticeably slower — natural documentary pace
        pitch="-3Hz",    # very slight depth, keeps voice sounding natural
    )
    await communicate.save(output_path)


def generate_voiceover(script: str, output_path: str = "voiceover.mp3", voice: str = None) -> str:
    """
    Converts script to AI speech using Microsoft Edge Neural TTS.
    Completely free — no API key needed. Supports male & female dramatic voices.
    Pass voice= to fix a specific narrator across multiple segments.
    """
    asyncio.run(_generate_async(script, output_path, voice))
    print(f"[Voiceover] Saved to {output_path}")
    return output_path
