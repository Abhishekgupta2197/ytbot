import subprocess
import os
import json

def create_ass_subtitles(timings, ass_path):
    print("📝 Creating subtitle file...")

    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Normal,Arial,85,&H00E5FF,&H80FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,2,0,5,60,60,500,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def to_ass_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    def get_fontsize(line_chars):
        if line_chars <= 10:
            return 85
        elif line_chars <= 14:
            return 75
        elif line_chars <= 18:
            return 65
        elif line_chars <= 24:
            return 55
        else:
            return 48

    line_size = 3
    lines = [timings[i:i+line_size] for i in range(0, len(timings), line_size)]

    events = []
    for line in lines:
        if not line:
            continue

        start = line[0]["start"]
        end = line[-1]["start"] + line[-1]["duration"] + 0.08

        clean = []
        for wd in line:
            word = wd["word"].upper()
            for ch in ["'", ":", ",", ".", '"', "!", "?", "(", ")", "-", ";"]:
                word = word.replace(ch, "")
            word = word.strip()
            clean.append((word, wd))

        total_chars = sum(len(w) for w, _ in clean) + len(clean) - 1
        fs = get_fontsize(total_chars)

        parts = []
        for word, wd in clean:
            if not word:
                continue
            duration_cs = max(1, int(wd["duration"] * 100))
            parts.append(f"{{\\kf{duration_cs}}}{word}")

        if not parts:
            continue

        line_text = "{\\q2\\an5\\pos(540,885)" + f"\\fs{fs}" + "}" + " ".join(parts)

        events.append(
            f"Dialogue: 0,{to_ass_time(start)},{to_ass_time(end)},"
            f"Normal,,0,0,0,,{line_text}"
        )

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events))

    print(f"✅ Subtitle file created!")

def build_video(bg_video, audio_path, music_path, script_text, output_path, channel_label="DARK PSYCHOLOGY"):
    print("🎬 Building video...")

    result = subprocess.run([
        "ffprobe", "-v", "quiet", "-show_entries",
        "format=duration", "-of", "csv=p=0", audio_path
    ], capture_output=True, text=True)
    duration = float(result.stdout.strip())
    print(f"⏱️ Duration: {duration:.1f}s")

    bg_processed = output_path.replace(".mp4", "_bg.mp4")
    mixed_audio  = output_path.replace(".mp4", "_audio.mp3")
    ass_path     = output_path.replace(".mp4", ".ass")

    subprocess.run([
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", bg_video,
        "-t", str(duration),
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "eq=brightness=-0.3:contrast=1.3:saturation=0.2,"
        "drawbox=x=40:y=820:w=1000:h=130:color=black@0.65:t=fill,"
        "drawbox=x=200:y=748:w=680:h=48:color=black@0.7:t=fill,"
        f"drawtext=text='{channel_label}':"
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        "fontsize=32:fontcolor=red:x=(w-text_w)/2:y=758:"
        "borderw=1:bordercolor=black@0.8,"
        "drawbox=x=200:y=798:w=680:h=2:color=red@0.9:t=fill",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-an",
        bg_processed
    ], capture_output=True, text=True)
    print("✅ Background processed!")

    subprocess.run([
        "ffmpeg", "-y",
        "-i", audio_path,
        "-stream_loop", "-1",
        "-i", music_path,
        "-filter_complex",
        f"[1:a]volume=0.03,atrim=0:{duration}[music];"
        f"[0:a][music]amix=inputs=2:duration=first",
        "-t", str(duration),
        mixed_audio
    ], capture_output=True, text=True)
    print("✅ Audio mixed!")

    timing_path = audio_path.replace(".mp3", "_timings.json")
    if not os.path.exists(timing_path):
        print("⚠️ No timing file!")
        return

    with open(timing_path) as f:
        timings = json.load(f)

    create_ass_subtitles(timings, ass_path)

    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", bg_processed,
        "-i", mixed_audio,
        "-vf", f"ass={ass_path}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "23",
        "-c:a", "aac",
        "-shortest",
        output_path
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Error: {result.stderr[-300:]}")
    else:
        print("✅ Video built!")

    for f in [bg_processed, mixed_audio]:
        if os.path.exists(f):
            os.remove(f)
