import subprocess
import json
import os
import textwrap


def get_duration(file_path: str) -> float:
    """Returns duration of a media file in seconds using ffprobe."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            file_path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def make_vertical_clip(input_path: str, output_path: str, duration: float):
    """
    Converts any landscape or portrait clip to 1080x1920 (9:16 vertical).
    Applies cinematic effects:
      - Smart scale + pad to fill 9:16
      - Slow Ken Burns zoom-in (zoompan)
      - Cinematic colour grade: boosted contrast, warm orange-teal tint
      - Slight vignette via curves
    """
    # Cinematic colour grade + vignette via eq and curves filters
    grade = (
        "eq=contrast=1.25:brightness=0.02:saturation=1.3:gamma_r=1.05:gamma_b=0.92,"
        "curves=r='0/0 0.5/0.55 1/1':b='0/0 0.5/0.45 1/0.92'"
    )

    vf = (
        # 1. Scale to fill 1080x1920 (crop center)
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "setsar=1,fps=30,"
        # 2. Slow zoom-in (Ken Burns) — 1.0 to 1.08 scale over full clip
        f"zoompan=z='min(zoom+0.0008,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={max(1, int(duration * 30))}:s=1080x1920:fps=30,"
        # 3. Cinematic colour grade
        f"{grade}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-an",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def build_caption_filter(script: str, total_duration: float) -> str:
    """
    Splits script into 4 equal caption chunks shown across the video duration.
    Each chunk is shown for ~10 seconds.
    """
    sentences = [s.strip() for s in script.replace("\n", " ").split(".") if s.strip()]
    if not sentences:
        sentences = textwrap.wrap(script, width=60)

    chunk_count = min(4, len(sentences))
    chunk_dur = total_duration / chunk_count
    filters = []

    for i in range(chunk_count):
        chunk_sentences = sentences[i * (len(sentences) // chunk_count): (i + 1) * (len(sentences) // chunk_count)]
        text = ". ".join(chunk_sentences)
        if not text:
            continue

        # Wrap text to 2 lines max
        wrapped = textwrap.wrap(text, width=32)
        display = "\\n".join(wrapped[:2])

        # Escape special characters for ffmpeg drawtext
        display = (
            display
            .replace("\\", "\\\\")
            .replace("'", "\u2019")   # replace apostrophe with curly quote to avoid ffmpeg parse error
            .replace(":", "\\:")
            .replace("%", "\\%")
            .replace(",", "\\,")
        )

        t_start = i * chunk_dur
        t_end = (i + 1) * chunk_dur

        filters.append(
            f"drawtext=text='{display}'"
            f":fontsize=44"
            f":fontcolor=white"
            f":borderw=4"
            f":bordercolor=black"
            f":x=(w-text_w)/2"
            f":y=h*0.78"
            f":enable='between(t,{t_start:.2f},{t_end:.2f})'"
        )

    return ",".join(filters) if filters else "null"


def assemble_video(clips: list, audio_path: str, script: str, output_path: str = "final_short.mp4") -> str:
    """
    Full pipeline:
    1. Convert all clips to 9:16 vertical
    2. Concatenate clips to cover audio duration
    3. Overlay voiceover audio
    4. Burn caption text
    5. Export final_short.mp4
    """
    audio_duration = get_duration(audio_path)
    target_duration = audio_duration + 1.0  # 1s fade buffer
    print(f"[Video] Audio: {audio_duration:.1f}s — building {target_duration:.1f}s video")

    os.makedirs("temp_clips", exist_ok=True)

    # Step 1: Make vertical clips, looping through sources until target filled
    vertical_clips = []
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
        use_dur = min(src_dur, max(remaining, 3.0))  # at least 3s per clip

        out = os.path.abspath(f"temp_clips/v_{idx}.mp4")
        print(f"[Video] Converting clip {idx + 1} ({use_dur:.1f}s)...")
        make_vertical_clip(src, out, use_dur)

        vertical_clips.append(out)
        time_used += use_dur
        idx += 1

        if idx > 60:
            break

    # Step 2: Write concat list
    concat_file = os.path.abspath("temp_clips/concat.txt")
    with open(concat_file, "w") as f:
        for c in vertical_clips:
            f.write(f"file '{c}'\n")

    concat_out = os.path.abspath("temp_clips/concat_raw.mp4")
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", concat_out],
        check=True,
        capture_output=True,
    )

    # Step 3: Build caption filter
    caption_filter = build_caption_filter(script, audio_duration)

    # Step 4: Final composite — video + audio + captions + fade-in + channel brand
    abs_audio = os.path.abspath(audio_path)
    abs_concat = concat_out

    # Channel branding overlay (top-left watermark) using drawtext
    brand_filter = (
        "drawtext=text='\\U0001f981 WildStrikeAI'"
        ":fontsize=36"
        ":fontcolor=yellow"
        ":borderw=3"
        ":bordercolor=black"
        ":x=20:y=30"
        ":enable='between(t,0,{dur})'".format(dur=target_duration)
    )

    # Fade in first 0.5s
    fade_filter = "fade=t=in:st=0:d=0.5"

    full_vf = f"{caption_filter},{brand_filter},{fade_filter}"

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", abs_concat,
            "-i", abs_audio,
            "-filter_complex", f"[0:v]{full_vf}[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "128k",
            "-t", str(target_duration),
            "-shortest",
            "-movflags", "+faststart",
            output_path,
        ],
        check=True,
        capture_output=True,
    )

    print(f"[Video] Final short ready: {output_path}")
    return output_path
