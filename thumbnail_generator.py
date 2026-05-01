"""
thumbnail_generator.py
───────────────────────
Generates a dramatic YouTube thumbnail using Pillow (free, no API key).
Creates a 1280x720 image with:
  - Dark vignette overlay
  - Bold channel branding text
  - Dramatic title text
  - Bottom warning/tagline bar
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os
import random


TITLES = [
    "THE HUNT BEGINS",
    "NO ESCAPE",
    "NATURE'S DEADLIEST",
    "KILL OR BE KILLED",
    "SURVIVAL OF THE FASTEST",
    "THE PREDATOR STRIKES",
    "WILD & DEADLY",
    "CAUGHT IN THE WILD",
]

TAGLINES = [
    "WATCH TILL THE END",
    "YOU WON'T BELIEVE THIS",
    "CAUGHT ON CAMERA",
    "NATURE IS BRUTAL",
]


def generate_thumbnail(
    video_path: str = "final_short.mp4",
    output_path: str = "thumbnail.jpg",
) -> str:
    """
    Extracts a frame from the video and overlays dramatic text to create a thumbnail.
    Falls back to a solid dark background if frame extraction fails.
    """
    import subprocess
    import tempfile

    # Try to extract a mid-point frame from the assembled video
    frame_path = os.path.join(tempfile.gettempdir(), "thumb_frame.png")
    extracted = False

    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json", "-show_format",
                video_path,
            ],
            capture_output=True, text=True, check=True,
        )
        import json
        dur = float(json.loads(result.stdout)["format"]["duration"])
        seek = dur * 0.3  # grab frame at 30% through video

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(seek),
                "-i", video_path,
                "-vframes", "1",
                "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720",
                frame_path,
            ],
            check=True, capture_output=True,
        )
        base_img = Image.open(frame_path).convert("RGBA").resize((1280, 720))
        extracted = True
    except Exception as e:
        print(f"[Thumbnail] Frame extract failed ({e}), using dark base")
        base_img = Image.new("RGBA", (1280, 720), (15, 10, 5, 255))

    # Darken + boost contrast for cinematic feel
    if extracted:
        enhancer = ImageEnhance.Brightness(base_img)
        base_img = enhancer.enhance(0.55)
        enhancer = ImageEnhance.Contrast(base_img)
        base_img = enhancer.enhance(1.4)

    draw = ImageDraw.Draw(base_img)

    # ── Vignette overlay ──
    vignette = Image.new("RGBA", (1280, 720), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for i in range(120):
        alpha = int(i * 1.8)
        vdraw.rectangle([i, i, 1280 - i, 720 - i], outline=(0, 0, 0, alpha))
    base_img = Image.alpha_composite(base_img, vignette)
    draw = ImageDraw.Draw(base_img)

    # ── Font loading (system fonts available on Ubuntu runner) ──
    def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        candidates = [
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
        for path in candidates:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    # ── Channel brand (top-left) ──
    brand_font = load_font(36, bold=True)
    draw.text((30, 25), "🦁 WildStrikeAI", font=brand_font, fill=(255, 200, 0, 255))

    # ── Main dramatic title (centre) ──
    title = random.choice(TITLES)
    title_font = load_font(110, bold=True)
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    tx = (1280 - tw) // 2

    # Shadow
    draw.text((tx + 5, 258), title, font=title_font, fill=(0, 0, 0, 200))
    # Red accent
    draw.text((tx, 255), title, font=title_font, fill=(220, 30, 30, 255))

    # ── Red bottom bar with tagline ──
    draw.rectangle([0, 630, 1280, 720], fill=(180, 0, 0, 230))
    tagline_font = load_font(46, bold=True)
    tag = random.choice(TAGLINES)
    tbbox = draw.textbbox((0, 0), tag, font=tagline_font)
    tw2 = tbbox[2] - tbbox[0]
    draw.text(((1280 - tw2) // 2, 648), tag, font=tagline_font, fill=(255, 255, 255, 255))

    # ── "#Shorts" badge (top-right) ──
    shorts_font = load_font(34, bold=True)
    draw.rounded_rectangle([1100, 20, 1260, 65], radius=10, fill=(255, 0, 0, 220))
    draw.text((1113, 28), "#Shorts", font=shorts_font, fill=(255, 255, 255, 255))

    # Save as JPEG
    final = base_img.convert("RGB")
    final.save(output_path, "JPEG", quality=95)
    print(f"[Thumbnail] Saved: {output_path}")
    return output_path
