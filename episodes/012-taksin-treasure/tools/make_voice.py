"""เสียงพากย์ Edge TTS ทีละซีน + เวลาของแต่ละคำ -> audio/NN.mp3, audio/NN.json, timing.json, narration.wav

ความยาวซีนคำนวณจากเสียงจริง (ไม่ต้องกำหนดเอง)
  python -I tools/make_voice.py            # สร้างเฉพาะไฟล์ที่ยังไม่มี
  python -I tools/make_voice.py --fresh    # สร้างเสียงใหม่ทั้งหมด
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
STORY = json.loads((ROOT / "story.json").read_text(encoding="utf-8"))
VOICE, RATE = "th-TH-NiwatNeural", "+12%"
SR = 48000
LEAD = 0.15      # เงียบก่อนเริ่มพูดในแต่ละซีน
TAIL = 0.3      # เผื่อหลังพูดจบ
END_HOLD = 3.2   # ซีนปิดค้างไว้นานขึ้น


async def synth(text, mp3, js):
    comm = edge_tts.Communicate(text, VOICE, rate=RATE, boundary="WordBoundary")
    words = []
    with open(mp3, "wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({"t": chunk["offset"] / 1e7, "d": chunk["duration"] / 1e7, "w": chunk["text"]})
    js.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")


def decode(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-af",
                                   "loudnorm=I=-16:TP=-1.5:LRA=8", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def chunk_times(parts, words):
    """เวลาเริ่มของแต่ละท่อนซับ = เวลาคำแรกที่อยู่ในท่อนนั้น (จับคู่ตามตำแหน่งตัวอักษรในข้อความพากย์)"""
    voice = " ".join(v for _, v in parts)
    starts, pos = [], 0
    for _, v in parts:
        starts.append(voice.index(v, pos))
        pos = starts[-1] + len(v)
    # วางคำของ TTS ลงบนข้อความเพื่อหาตำแหน่งตัวอักษร
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
    fresh = "--fresh" in sys.argv
    (ROOT / "audio").mkdir(exist_ok=True)
    for i, s in enumerate(STORY):
        mp3, js = ROOT / "audio" / f"{i:02}.mp3", ROOT / "audio" / f"{i:02}.json"
        if fresh or not (mp3.exists() and js.exists()):
            text = " ".join(v for _, v in s["parts"])
            print("TTS", i, s["id"], text, flush=True)
            asyncio.run(asyncio.wait_for(synth(text, mp3, js), 60))

    timing, clips, start = [], [], 0.0
    for i, s in enumerate(STORY):
        a = decode(ROOT / "audio" / f"{i:02}.mp3")
        words = json.loads((ROOT / "audio" / f"{i:02}.json").read_text(encoding="utf-8"))
        vdur = len(a) / SR
        dur = round(LEAD + vdur + (END_HOLD if s["id"] == "end" else TAIL), 2)
        cts = chunk_times(s["parts"], words)
        timing.append({
            "id": s["id"], "start": round(start, 3), "duration": dur, "voice": round(vdur, 3),
            "chunks": [{"text": c, "t": round(start + LEAD + t, 3)} for (c, _), t in zip(s["parts"], cts)],
        })
        clips.append((start + LEAD, a))
        print(f"{i:2} {s['id']:9} start {start:6.2f} dur {dur:5.2f} words {len(words)}", flush=True)
        start += dur

    total = round(start, 2)
    n = int(SR * total) + 1
    speech = np.zeros(n)
    for at, a in clips:
        k = int(at * SR)
        speech[k:k + len(a)] += a[: n - k]
    with wave.open(str(ROOT / "narration.wav"), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((np.clip(speech, -.98, .98) * 32767).astype("<i2").tobytes())
    (ROOT / "timing.json").write_text(json.dumps({"total": total, "scenes": timing}, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "narration-th.txt").write_text("\n".join(" ".join(v for _, v in s["parts"]) for s in STORY), encoding="utf-8")
    print("total", total)


if __name__ == "__main__":
    main()
