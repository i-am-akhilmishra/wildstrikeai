"""
longform_assembler.py
─────────────────────
Assembles a 20-22 minute long-form YouTube video from multiple animal segments.
Output: 1920x1080 landscape MP4 — standard YouTube long-form format.
"""

import subprocess
import json
import os

# Landscape 1080p for long-form YouTube
OUT_W = 1920
OUT_H = 1080
OUT_FPS = 30


def get_duration(file_path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", file_path],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def _make_landscape_clip(input_path: str, output_path: str, duration: float):
    """Converts any clip to 1920x1080 landscape with cinematic colour grade."""
    grade = (
        "eq=contrast=1.22:brightness=0.01:saturation=1.25:gamma_r=1.04:gamma_b=0.93,"
        "curves=r='0/0 0.5/0.54 1/1':b='0/0 0.5/0.46 1/0.92'"
    )
    vf = (
        f"scale={OUT_W}:{OUT_H}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={OUT_W}:{OUT_H},"
        f"setsar=1,"
        f"fps={OUT_FPS},"
        f"{grade}"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-profile:v", "high", "-level", "4.0",
        "-pix_fmt", "yuv420p",
        "-an",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg clip failed (exit {result.returncode}):\n"
            f"{result.stderr.decode(errors='replace')[-1500:]}"
        )


def create_title_card(chapter_title: str, output_path: str, duration: float = 3.0):
    """
    Generates a black title card with chapter name — shown between segments.
    3 seconds by default.
    """
    safe_title = (
        chapter_title
        .replace("'", "\u2019")
        .replace(":", "\\:")
        .replace("%", "\\%")
        .replace(",", "\\,")
    )
    vf = (
        f"drawtext=text='{safe_title}'"
        ":fontsize=72"
        ":fontcolor=white"
        ":borderw=4"
        ":bordercolor=black"
        ":x=(w-text_w)/2"
        ":y=(h-text_h)/2-25,"
        "drawtext=text='WildStrikeAI'"
        ":fontsize=32"
        ":fontcolor=yellow@0.8"
        ":borderw=2"
        ":bordercolor=black"
        ":x=(w-text_w)/2"
        ":y=(h-text_h)/2+55"
    )
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:size={OUT_W}x{OUT_H}:rate={OUT_FPS}:duration={duration}",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-profile:v", "high", "-level", "4.0",
        "-pix_fmt", "yuv420p",
        "-an",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Title card failed: {result.stderr.decode(errors='replace')[-1000:]}"
        )


def assemble_segment(clips: list, audio_path: str, output_path: str) -> str:
    """
    Assembles one animal segment: clips → 1920x1080 landscape → concat → audio overlay.
    Returns output_path.
    """
    audio_duration = get_duration(audio_path)
    target_duration = audio_duration + 0.5

    seg_dir = os.path.join("longform_temp", f"seg_{os.path.basename(output_path).split('.')[0]}")
    os.makedirs(seg_dir, exist_ok=True)

    # Convert clips to landscape, looping until target duration is filled
    converted = []
    time_used = 0.0
    idx = 0

    while time_used < target_duration:
        src = clips[idx % len(clips)]
        try:
            src_dur = get_duration(src)
        except Exception:
            idx += 1
            continue

        remaining = target_duration - time_used
        use_dur = min(src_dur, max(remaining, 3.0))

        clip_out = os.path.abspath(os.path.join(seg_dir, f"c_{idx}.mp4"))
        _make_landscape_clip(src, clip_out, use_dur)
        converted.append(clip_out)
        time_used += use_dur
        idx += 1

        if idx > 60:
            break

    # Concatenate converted clips
    concat_txt = os.path.join(seg_dir, "concat.txt")
    with open(concat_txt, "w") as f:
        for c in converted:
            f.write(f"file '{c}'\n")

    raw_concat = os.path.join(seg_dir, "raw.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", raw_concat],
        check=True, capture_output=True,
    )

    # Watermark + fade-in overlay
    brand_filter = (
        "drawtext=text='WildStrikeAI'"
        ":fontsize=32"
        ":fontcolor=white@0.7"
        ":borderw=2"
        ":bordercolor=black"
        ":x=30:y=30"
        f":enable='between(t,0,{target_duration})'"
    )
    fade_filter = "fade=t=in:st=0:d=0.5"
    full_vf = f"{brand_filter},{fade_filter}"

    abs_audio = os.path.abspath(audio_path)
    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", os.path.abspath(raw_concat),
            "-i", abs_audio,
            "-filter_complex", f"[0:v]{full_vf}[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-profile:v", "high", "-level", "4.0",
            "-pix_fmt", "yuv420p",
            "-vsync", "cfr", "-r", str(OUT_FPS),
            "-c:a", "aac", "-b:a", "192k",
            "-af", "aresample=async=1",
            "-t", str(target_duration),
            "-shortest",
            "-movflags", "+faststart",
            output_path,
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Segment assembly failed: {result.stderr.decode(errors='replace')[-1500:]}"
        )
    return output_path


def assemble_longform(segment_files: list, title_card_files: list, output_path: str) -> str:
    """
    Concatenates [title_card_0, segment_0, title_card_1, segment_1, ...] into final MP4.
    Uses stream-copy concat (fast — no re-encode).
    """
    ordered = []
    for i, seg in enumerate(segment_files):
        if i < len(title_card_files):
            ordered.append(title_card_files[i])
        ordered.append(seg)

    concat_txt = "longform_final_concat.txt"
    with open(concat_txt, "w") as f:
        for p in ordered:
            f.write(f"file '{os.path.abspath(p)}'\n")

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_txt,
            "-c", "copy",
            "-movflags", "+faststart",
            output_path,
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Final concat failed: {result.stderr.decode(errors='replace')[-1500:]}"
        )
    print(f"[LongForm] Final video ready: {output_path}")
    return output_path
