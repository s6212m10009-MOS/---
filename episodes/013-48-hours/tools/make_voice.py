"""เสียงพากย์ Edge TTS ทีละซีน + เวลาของแต่ละท่อน -> <variant>/audio/*, timing.json, narration.wav

  python tools/make_voice.py 916          # Shorts 9:16 (ข้ามท่อน only=L)
  python tools/make_voice.py 169 --fresh  # 16:9 ฉบับเต็ม สร้างเสียงใหม่ทั้งหมด
"""

import asyncio
import json
import subprocess
import sys
import wave
from pathlib import Path

import edge_tts
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
VOICE = "th-TH-NiwatNeural"
RATE = {"916": "+18%", "169": "+12%"}
SR = 48000
FIRST_LEAD = 1.5   # ให้ตะเกียงติดก่อนพูดคำแรก
LEAD, TAIL = 0.45, 0.4
END_HOLD = 3.6


def parts_for(scene, variant):
    out = []
    for p in scene["parts"]:
        opt = p[2] if len(p) > 2 else {}
        if opt.get("only") == "L" and variant != "169":
            continue
        out.append((p[0], p[1], opt))
    return out


async def synth(text, mp3, js, rate):
    comm = edge_tts.Communicate(text, VOICE, rate=rate, boundary="WordBoundary")
    words = []
    with open(mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({"t": chunk["offset"] / 1e7, "d": chunk["duration"] / 1e7, "w": chunk["text"]})
    js.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")


def decode(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-af", "loudnorm=I=-16:TP=-1.5:LRA=8",
                                   "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def chunk_times(spoken, words):
    """เวลาเริ่มของแต่ละท่อน = เวลาคำแรกของ TTS ที่ตกอยู่ในท่อนนั้น"""
    voice = " ".join(spoken)
    starts, pos = [], 0
    for v in spoken:
        starts.append(voice.index(v, pos))
        pos = starts[-1] + len(v)
    cursor, placed = 0, []
    for w in words:
        k = voice.find(w["w"], cursor)
        if k < 0:
            continue
        placed.append((k, w["t"]))
        cursor = k + len(w["w"])
    out = []
    for s in starts:
        hit = [t for k, t in placed if k >= s]
        out.append(hit[0] if hit else (out[-1] if out else 0.0))
    return out


def main():
    variant = sys.argv[1]
    fresh = "--fresh" in sys.argv
    out = ROOT / variant
    (out / "audio").mkdir(parents=True, exist_ok=True)
    story = json.loads((ROOT / "story.json").read_text(encoding="utf-8"))

    timing, clips, start = [], [], 0.0
    for i, s in enumerate(story):
        parts = parts_for(s, variant)
        mp3, js = out / "audio" / f"{i:02}.mp3", out / "audio" / f"{i:02}.json"
        text = " ".join(p[1] for p in parts)
        if fresh or not (mp3.exists() and js.exists()) or json.loads(js.read_text(encoding="utf-8")) == []:
            print("TTS", i, s["id"], flush=True)
            asyncio.run(asyncio.wait_for(synth(text, mp3, js, RATE[variant]), 90))
        a = decode(mp3)
        words = json.loads(js.read_text(encoding="utf-8"))
        lead = FIRST_LEAD if i == 0 else LEAD
        vdur = len(a) / SR
        dur = round(lead + vdur + (END_HOLD if s["id"] == "end" else TAIL), 3)
        cts = chunk_times([p[1] for p in parts], words)
        timing.append({"id": s["id"], "start": round(start, 3), "duration": dur,
                       "chunks": [{"text": p[0], "t": round(start + lead + t, 3), **p[2]} for p, t in zip(parts, cts)]})
        clips.append((start + lead, a))
        print(f"{i:2} {s['id']:8} start {start:6.2f} dur {dur:5.2f}", flush=True)
        start += dur

    total = round(start, 3)
    n = int(SR * total) + 1
    speech = np.zeros(n)
    for at, a in clips:
        k = int(at * SR)
        speech[k:k + len(a)] += a[: n - k]
    with wave.open(str(out / "narration.wav"), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((np.clip(speech, -.98, .98) * 32767).astype("<i2").tobytes())
    (out / "timing.json").write_text(json.dumps({"total": total, "scenes": timing}, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
    (out / "narration-th.txt").write_text("\n".join(" ".join(p[1] for p in parts_for(s, variant)) for s in story),
                                          encoding="utf-8")
    print("total", total)


if __name__ == "__main__":
    main()
