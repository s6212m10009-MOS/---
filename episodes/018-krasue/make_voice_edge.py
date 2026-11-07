"""พากย์บท script.md ด้วย Microsoft Edge TTS ทีละบรรทัด แล้วต่อเป็นไฟล์เดียว

ผลลัพธ์: audio/line-NN.mp3, audio/durations.json, audio/narration.mp3

ตัวอย่าง:
  python make_voice_edge.py
  python make_voice_edge.py --voice th-TH-PremwadeeNeural --rate -5%
"""

import argparse
import asyncio
import json
import re
import subprocess
from pathlib import Path

import edge_tts

HERE = Path(__file__).resolve().parent


def read_lines():
    body = (HERE / "script.md").read_text(encoding="utf-8").split("## บทพากย์", 1)[1]
    return [m.group(1).strip() for m in re.finditer(r"^\d+\.\s+(.+)$", body, re.M)]


def duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


async def synth_all(lines, voice, rate, pitch, outdir):
    for i, text in enumerate(lines, 1):
        await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(
            str(outdir / f"line-{i:02d}.mp3")
        )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="th-TH-NiwatNeural")
    ap.add_argument("--rate", default="-8%", help="ช้าลงเล็กน้อยให้เข้ากับเรื่องหลอน")
    ap.add_argument("--pitch", default="-4Hz")
    ap.add_argument("--gap", type=float, default=0.6, help="เว้นวรรคระหว่างบรรทัด (วินาที)")
    a = ap.parse_args()

    outdir = HERE / "audio"
    outdir.mkdir(exist_ok=True)
    lines = read_lines()
    asyncio.run(synth_all(lines, a.voice, a.rate, a.pitch, outdir))

    durs, t = [], 0.0
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for i in range(1, len(lines) + 1):
        cmd += ["-i", str(outdir / f"line-{i:02d}.mp3")]
    parts, labels = [], []
    for i in range(len(lines)):
        d = duration(outdir / f"line-{i + 1:02d}.mp3")
        durs.append({"line": i + 1, "start": round(t, 2), "dur": round(d, 2), "text": lines[i]})
        parts.append(f"[{i}:a]aresample=48000,apad=pad_dur={a.gap}[a{i}]")
        labels.append(f"[a{i}]")
        t += d + a.gap
    parts.append(f"{''.join(labels)}concat=n={len(lines)}:v=0:a=1[out]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[out]", str(outdir / "narration.mp3")]
    subprocess.run(cmd, check=True)

    (outdir / "durations.json").write_text(
        json.dumps(durs, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"{len(lines)} บรรทัด รวม {t:.1f} วินาที ({t / 60:.2f} นาที) เสียง {a.voice}")


if __name__ == "__main__":
    main()
