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


# Output resolution — 4K vertical (2160x3840) at 60fps
OUT_W = 2160
OUT_H = 3840
OUT_FPS = 60


def make_vertical_clip(input_path: str, output_path: str, duration: float):
    """
    Converts any clip to 2160x3840 (4K 9:16 vertical) at 60fps.
    - Ken Burns zoom runs at 1080p (540x960) to stay within GitHub Actions RAM
    - Final Lanczos upscale to 4K after zoompan
    - Cinematic orange-teal colour grade
    """
    grade = (
        "eq=contrast=1.28:brightness=0.02:saturation=1.35:gamma_r=1.06:gamma_b=0.90,"
        "curves=r='0/0 0.5/0.56 1/1':b='0/0 0.5/0.44 1/0.90'"
    )

    # zoompan at 1080p (540x960) — uses ~16x less RAM than 4K
    ZP_W, ZP_H = 540, 960
    frames = max(1, int(duration * OUT_FPS))

    vf = (
        # 1. Scale + crop to 1080p vertical first
        f"scale={ZP_W}:{ZP_H}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={ZP_W}:{ZP_H},"
        f"setsar=1,fps={OUT_FPS},"
        # 2. Ken Burns zoom at 1080p (RAM-safe)
        f"zoompan=z='min(zoom+0.0004,1.06)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":d={frames}:s={ZP_W}x{ZP_H}:fps={OUT_FPS},"
        # 3. Upscale to 4K with lanczos
        f"scale={OUT_W}:{OUT_H}:flags=lanczos,"
        f"setsar=1,"
        # 4. Colour grade
        f"{grade}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-profile:v", "high", "-level", "5.2",
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
            f":fontsize=88"
            f":fontcolor=white"
            f":borderw=6"
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

    # Step 3: Build caption filter (scale font for 4K width)
    caption_filter = build_caption_filter(script, audio_duration)

    # Step 4: Final composite — 4K 60fps MOV
    abs_audio = os.path.abspath(audio_path)
    abs_concat = concat_out

    brand_filter = (
        "drawtext=text='\\U0001f981 WildStrikeAI'"
        ":fontsize=72"
        ":fontcolor=yellow"
        ":borderw=5"
        ":bordercolor=black"
        ":x=40:y=55"
        ":enable='between(t,0,{dur})'".format(dur=target_duration)
    )

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
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-profile:v", "high", "-level", "5.2",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(target_duration),
            "-shortest",
            "-movflags", "+faststart",
            output_path,   # .mov extension = MOV container
        ],
        check=True,
        capture_output=True,
    )

    print(f"[Video] Final 4K 60fps MOV ready: {output_path}")
    return output_path
