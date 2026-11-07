"""พากย์ตอน 036 ด้วย Gemini TTS (รวดเดียวทุกบรรทัด) -> video/audio_gm/NN_t.wav, vo.wav, video/timing_gm.json
ยืมฟังก์ชัน synth/transcribe/split_batch จาก ../../make_voice_gemini.py (ต้องตั้ง GEMINI_API_KEY)
  python make_voice_gemini.py [--tempo 1.25] [--voice Sadaltager]"""
import argparse, json, os, subprocess, sys, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
import make_voice_gemini as mg
from lines import TTS

AUD = HERE / "video" / "audio_gm"
SR, GAP, LEAD, TAIL = 48000, 0.3, 0.25, 2.2

ap = argparse.ArgumentParser()
ap.add_argument("--tempo", type=float, default=1.25)
ap.add_argument("--voice", default=mg.VOICE)
ap.add_argument("--style", default=mg.STYLE)
ap.add_argument("--reuse", action="store_true", help="ใช้ gemini_raw.wav ที่มีอยู่ ไม่เรียก API ซ้ำ")
a = ap.parse_args()
sys.stdout.reconfigure(encoding="utf-8")

AUD.mkdir(parents=True, exist_ok=True)
raw = AUD / "gemini_raw.wav"
fast = AUD / "gemini_fast.wav"
# ตัดเสียงรวม gemini_fast.wav ตามช่วงเงียบที่ตรวจด้วย silencedetect (whisper แบ่งผิดบรรทัด 036)
CUTS = [0, 4.29, 9.86, 14.68, 18.81, 22.17, 28.40, 31.99, 34.88, 38.15, 40.84, 99]
tmp = AUD / "split"
tmp.mkdir(exist_ok=True)
for i in range(len(TTS)):
    subprocess.check_call(["ffmpeg", "-v", "error", "-y", "-ss", str(CUTS[i]), "-to", str(CUTS[i + 1]), "-i", str(fast), "-af",
        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse", "-ar", "48000", "-ac", "1", str(tmp / f"{i:02}.wav")])

t, timing, clips = LEAD, [], []
for i, text in enumerate(TTS):
    x = mg.decode(tmp / f"{i:02}.wav")
    wav = AUD / f"{i:02}_t.wav"
    with wave.open(str(wav), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((np.clip(x, -.98, .98) * 32767).astype("<i2").tobytes())
    d = len(x) / SR
    timing.append({"n": i + 1, "text": text, "start": round(t, 3), "end": round(t + d, 3)})
    clips.append((t, x))
    t += d + GAP
total = round(timing[-1]["end"] + TAIL, 2)
n = int(SR * total) + 1
sp = np.zeros(n)
for at, x in clips:
    k = int(at * SR)
    sp[k:k + len(x)] += x[: n - k]
sp = sp / max(float(np.abs(sp).max()), 1e-9) * 0.9
with wave.open(str(AUD / "vo.wav"), "wb") as w:
    w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
    w.writeframes((np.clip(sp, -.98, .98) * 32767).astype("<i2").tobytes())
(HERE / "video" / "timing_gm.json").write_text(json.dumps({"total": total, "lines": timing}, ensure_ascii=False, indent=1), encoding="utf-8")
for e in timing:
    print(f"{e['n']}: {e['start']:6.2f}-{e['end']:6.2f}")
print("total", total)
