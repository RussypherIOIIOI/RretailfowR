"""Encode actual timestamped browser captures, with timed explanatory annotations.

This is a silent screen walkthrough, not synthesized demonstration footage.
Input timestamps preserve elapsed capture time; no target-duration retiming.
Optional media dependencies: imageio-ffmpeg==0.6.0, pillow==13.0.0.
"""

import hashlib
import json
from pathlib import Path
import subprocess
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
from scripts.databricks_cli import save

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs/assets"
SOURCE = ASSETS / "walkthrough-source"


def main():
    recording = json.loads((SOURCE / "recording.json").read_text())
    frames, cues = recording["frames"], recording["annotations"]
    assert len(frames) >= 30 and all(b["t"] > a["t"] for a, b in zip(frames, frames[1:]))
    assert recording["type"] == "real_browser_screenshots" and recording["playback_speed"] == 1
    assert json.loads((ROOT / "evidence/release-20261030/demo-persisted.json").read_text())["status"] == "passed"
    original = Image.open(SOURCE / frames[0]["file"])
    width = original.width + original.width % 2
    height = original.height + 96
    height += height % 2
    font_path = Path("C:/Windows/Fonts/segoeui.ttf")
    font = ImageFont.truetype(str(font_path), 25)
    output_dir = SOURCE / "annotated"
    output_dir.mkdir(exist_ok=True)
    inventory = []
    for i, frame in enumerate(frames):
        source = SOURCE / frame["file"]
        image = Image.open(source).convert("RGB")
        assert image.size == original.size, "Browser capture size changed mid-recording"
        canvas = Image.new("RGB", (width, height), "#102333")
        canvas.paste(image, ((width - image.width) // 2, 0))
        draw = ImageDraw.Draw(canvas)
        active = [cue for cue in cues if cue["start"] <= frame["t"] < cue["end"]]
        assert len(active) <= 1, "Overlapping explanatory annotations"
        message = active[0]["text"] if active else "RetailFlow · real Databricks screen recording · synthetic data"
        lines, line = [], ""
        for word in message.split():
            candidate = (line + " " + word).strip()
            if draw.textlength(candidate, font=font) > width - 64:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
        assert len(lines) <= 2, message
        for n, line in enumerate(lines):
            draw.text((32, original.height + 14 + n * 31), line, font=font, fill="#ECF4F6")
        destination = output_dir / f"{i:05d}.jpg"
        canvas.save(destination, quality=95)
        inventory.append({"file": frame["file"], "t": frame["t"],
                          "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    concat = SOURCE / "timeline.txt"
    lines = []
    for i, frame in enumerate(frames):
        lines.append("file '" + (output_dir / f"{i:05d}.jpg").as_posix() + "'")
        if i + 1 < len(frames):
            lines.append(f"duration {frames[i + 1]['t'] - frame['t']:.6f}")
    concat.write_text("\n".join(lines) + "\n", encoding="utf8")
    destination = ASSETS / "retailflow-walkthrough.mp4"
    assert not destination.exists(), "Preserve prior video exports; use a new filename for revisions"
    executable = imageio_ffmpeg.get_ffmpeg_exe()
    command = [executable, "-nostdin", "-v", "error", "-n", "-f", "concat", "-safe", "0", "-i", str(concat),
               "-fps_mode", "vfr", "-an", "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", str(destination)]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    (SOURCE / "render-stderr.txt").write_text(result.stderr, encoding="utf8")
    decoder = imageio_ffmpeg.read_frames(str(destination), pix_fmt="rgb24")
    metadata = next(decoder)
    decoded_frames = sum(1 for _ in decoder)
    assert decoded_frames >= len(frames) - 2
    save(ROOT / "evidence/release-20261030/video-manifest.json", {
        "type": "silent_annotated_screen_walkthrough", "source": "Real Databricks console, captured through cua_repl",
        "playback_speed": 1, "source_capture_seconds": frames[-1]["t"], "metadata": metadata,
        "source_frame_count": len(frames), "fully_decoded_frames": decoded_frames,
        "source_frames": inventory, "annotations": cues, "font": str(font_path),
        "ffmpeg_version": imageio_ffmpeg.get_ffmpeg_version(),
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "audio": "None; explanatory annotations are not a transcript of speech",
        "review": "Full decode passed; visual review is recorded separately",
    })
    print(json.dumps({"file": str(destination), "metadata": metadata, "decoded_frames": decoded_frames}))


if __name__ == "__main__":
    main()
