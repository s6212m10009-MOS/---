"""เสียงพากย์คลิปทดลองสไตล์ตะเกียง -> narration.wav + timing.json
  python tools/make_voice.py
"""

import asyncio
import json
import subprocess
import wave
from pathlib import Path

import edge_tts
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
VOICE, RATE = "th-TH-NiwatNeural", "+8%"
SR = 48000
LINES = [
    "ใต้ดินกรุงเก่า ยังมีสมบัติที่ไม่มีเจ้าของ",
    "หลังสงคราม ผู้คนแห่กันมาขุดหาทรัพย์ เรื่องนี้มีบันทึกจริง",
    "แต่ที่ว่าพระเจ้าตากกู้เงินจีนหกหมื่นตำลึง ยังเป็นแค่เรื่องเล่า",
]
LEAD, GAP, TAIL = 1.2, 0.55, 2.2   # เปิดตะเกียงก่อนพูด / เว้นระหว่างประโยค / ปิดรูกุญแจ


async def synth(text, mp3):
    await edge_tts.Communicate(text, VOICE, rate=RATE).save(str(mp3))


def decode(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-af",
                                   "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                                   "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                                   "loudnorm=I=-16:TP=-1.5:LRA=8",
                                   "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def main():
    clips = []
    for i, text in enumerate(LINES):
        mp3 = ROOT / "audio" / f"{i:02}.mp3"
        if not mp3.exists():
            asyncio.run(synth(text, mp3))
        clips.append(decode(mp3))

    t, lines, parts = LEAD, [], [np.zeros(int(SR * LEAD))]
    for text, a in zip(LINES, clips):
        d = len(a) / SR
        lines.append({"text": text, "start": round(t, 3), "duration": round(d, 3)})
        parts += [a, np.zeros(int(SR * GAP))]
        t += d + GAP
    total = round(t - GAP + TAIL, 3)
    mix = np.concatenate(parts)
    mix = np.pad(mix, (0, max(0, int(SR * total) - len(mix))))[: int(SR * total)]

    with wave.open(str(ROOT / "narration.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
    (ROOT / "timing.json").write_text(json.dumps({"total": total, "lines": lines}, ensure_ascii=False, indent=1),
                                      encoding="utf-8")
    print(json.dumps({"total": total, "lines": lines}, ensure_ascii=False))


main()
