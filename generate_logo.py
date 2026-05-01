"""
generate_logo.py
────────────────
Run this once locally to generate your WildStrikeAI YouTube channel logo.
Produces a 800x800 PNG — upload it as your YouTube channel profile picture.

Usage:
    python generate_logo.py

Output: wildstrikeai_logo.png (800x800)
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import os


def draw_lion_silhouette(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int):
    """Draws a stylised lion head silhouette using overlapping ellipses and polygons."""
    r = size // 2

    # Mane (large dark-orange outer circle)
    mane_color = (200, 90, 10, 255)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=mane_color)

    # Mane highlight ring
    draw.ellipse(
        [cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
        fill=(220, 110, 20, 255),
    )

    # Face (inner circle)
    fr = int(r * 0.62)
    face_color = (200, 140, 60, 255)
    draw.ellipse([cx - fr, cy - fr, cx + fr, cy + fr], fill=face_color)

    # Eyes
    eye_y = cy - int(fr * 0.18)
    eye_rx = int(fr * 0.38)
    eye_ry = int(fr * 0.12)
    eye_color = (30, 20, 10, 255)
    pupil_color = (255, 200, 0, 255)

    for ex in [cx - int(fr * 0.30), cx + int(fr * 0.30)]:
        draw.ellipse([ex - eye_rx, eye_y - eye_ry, ex + eye_rx, eye_y + eye_ry], fill=eye_color)
        draw.ellipse(
            [ex - int(eye_rx * 0.4), eye_y - int(eye_ry * 0.6),
             ex + int(eye_rx * 0.4), eye_y + int(eye_ry * 0.6)],
            fill=pupil_color,
        )

    # Nose
    nose_y = cy + int(fr * 0.12)
    nose_size = int(fr * 0.14)
    nose_pts = [
        (cx, nose_y - nose_size),
        (cx - nose_size, nose_y + nose_size),
        (cx + nose_size, nose_y + nose_size),
    ]
    draw.polygon(nose_pts, fill=(120, 60, 30, 255))

    # Mouth lines
    line_color = (100, 50, 20, 255)
    lw = 3
    draw.line([(cx, nose_y + nose_size), (cx - int(fr * 0.25), nose_y + int(fr * 0.32))],
              fill=line_color, width=lw)
    draw.line([(cx, nose_y + nose_size), (cx + int(fr * 0.25), nose_y + int(fr * 0.32))],
              fill=line_color, width=lw)

    # Ears (triangles poking above mane)
    ear_color = (180, 80, 10, 255)
    ear_h = int(r * 0.45)
    ear_w = int(r * 0.28)
    for side in [-1, 1]:
        ear_cx = cx + side * int(r * 0.52)
        ear_top = cy - r - int(ear_h * 0.3)
        ear_pts = [
            (ear_cx - ear_w, cy - int(r * 0.55)),
            (ear_cx + ear_w, cy - int(r * 0.55)),
            (ear_cx, ear_top),
        ]
        draw.polygon(ear_pts, fill=ear_color)


def generate_logo(output_path: str = "wildstrikeai_logo.png"):
    size = 800
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ── Background circle (dark charcoal) ──
    bg_margin = 10
    draw.ellipse(
        [bg_margin, bg_margin, size - bg_margin, size - bg_margin],
        fill=(18, 14, 10, 255),
    )

    # ── Dramatic orange-red gradient ring ──
    ring_steps = 18
    for i in range(ring_steps, 0, -1):
        alpha = int(180 * (i / ring_steps))
        r_val = int(220 - i * 4)
        g_val = int(60 - i * 2)
        ring_m = bg_margin + i * 3
        draw.ellipse(
            [ring_m, ring_m, size - ring_m, size - ring_m],
            outline=(r_val, g_val, 0, alpha),
            width=2,
        )

    # ── Lion silhouette (centred, top half) ──
    lion_cx = size // 2
    lion_cy = size // 2 - 55
    lion_size = 290
    draw_lion_silhouette(draw, lion_cx, lion_cy, lion_size)

    # ── Channel name text ──
    def load_font(sz: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        candidates = [
            r"C:\Windows\Fonts\ArialBd.ttf" if bold else r"C:\Windows\Fonts\Arial.ttf",
            r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
            r"C:\Windows\Fonts\impact.ttf",
        ]
        for p in candidates:
            if os.path.exists(p):
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()

    font_main = load_font(88, bold=True)
    font_ai   = load_font(88, bold=True)
    font_tag  = load_font(30, bold=False)

    text1 = "WildStrike"
    text2 = "AI"
    tag   = "NATURE'S DEADLIEST IN 40 SECONDS"

    bb1 = draw.textbbox((0, 0), text1, font=font_main)
    tw1 = bb1[2] - bb1[0]
    bb2 = draw.textbbox((0, 0), text2, font=font_ai)
    tw2 = bb2[2] - bb2[0]

    gap   = 6
    total = tw1 + gap + tw2
    tx1   = (size - total) // 2
    tx2   = tx1 + tw1 + gap
    ty    = 570

    # Shadows
    draw.text((tx1 + 4, ty + 4), text1, font=font_main, fill=(0, 0, 0, 200))
    draw.text((tx2 + 4, ty + 4), text2, font=font_ai,   fill=(0, 0, 0, 200))
    # Text
    draw.text((tx1, ty), text1, font=font_main, fill=(255, 255, 255, 255))
    draw.text((tx2, ty), text2, font=font_ai,   fill=(210, 30, 30, 255))

    # Tagline (centred, below)
    bb3 = draw.textbbox((0, 0), tag, font=font_tag)
    tw3 = bb3[2] - bb3[0]
    draw.text(((size - tw3) // 2, ty + 96), tag, font=font_tag, fill=(200, 150, 50, 220))

    # ── Subtle blur/glow on the ring ──
    img = img.filter(ImageFilter.SMOOTH)

    # Save
    img.convert("RGB").save(output_path, "PNG")
    print(f"[Logo] Saved: {output_path}  (800x800 — upload as YouTube channel picture)")
    return output_path


if __name__ == "__main__":
    generate_logo()
