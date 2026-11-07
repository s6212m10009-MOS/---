"""พากย์ตอน 049 ด้วย Gemini TTS (เร่ง 1.25 เท่า ตามที่เคยตั้งไว้) -> video/audio_gm/NN.wav, NN_t.wav, vo.wav, timing_gm.json
ใช้ฟังก์ชันจาก ../../make_voice_gemini.py ต้องตั้ง GEMINI_API_KEY
  python make_voice.py [--voice Sadaltager] [--tempo 1.25]"""
import argparse, json, os, subprocess, sys, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
sys.path.insert(0, str(HERE))
import make_voice_gemini as G  # noqa: E402
from lines import TTS  # noqa: E402

AUD = HERE / "video" / "audio_gm"
GAP, LEAD, TAIL = 0.3, 0.25, 2.2

ap = argparse.ArgumentParser()
ap.add_argument("--voice", default=G.VOICE)
ap.add_argument("--style", default=G.STYLE)
ap.add_argument("--tempo", type=float, default=1.25)
a = ap.parse_args()
sys.stdout.reconfigure(encoding="utf-8")
AUD.mkdir(parents=True, exist_ok=True)
if not os.environ.get("GEMINI_API_KEY"):
    sys.exit("ยังไม่ได้ตั้ง GEMINI_API_KEY")

from google import genai
from faster_whisper import WhisperModel
client = genai.Client()
BATCHES = [range(0, 5)]
model = WhisperModel(G.WHISPER, device="cpu", compute_type="int8")
for bi, idx in enumerate(BATCHES):
    idx = list(idx)
    tmp = AUD / f"batch{bi}.wav"
    bt = [TTS[i] for i in idx]
    if not tmp.exists():
        print("TTS ชุด", bi, sum(len(t) for t in bt), "ตัวอักษร", flush=True)
        G.synth(client, chr(10).join(bt), tmp, a.voice, a.style)
    if not os.environ.get("SKIPSPLIT"):
        words = G.transcribe(model, tmp, " ".join(bt))
        G.split_batch(tmp, idx, bt, words, AUD)

t, timing, clips = LEAD, [], []
for i, text in enumerate(TTS):
    src = AUD / f"{i:02}_t.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(AUD / f"{i:02}.wav"), "-af", f"atempo={a.tempo}", str(src)], check=True)
    x = G.decode(src)
    d = len(x) / G.SR
    timing.append({"n": i + 1, "text": text, "start": round(t, 3), "end": round(t + d, 3)})
    clips.append((t, x))
    t += d + GAP
total = round(timing[-1]["end"] + TAIL, 2)
n = int(G.SR * total) + 1
sp = np.zeros(n)
for at, x in clips:
    k = int(at * G.SR)
    sp[k:k + len(x)] += x[: n - k]
with wave.open(str(AUD / "vo.wav"), "wb") as w:
    w.setparams((1, 2, G.SR, 0, "NONE", "not compressed"))
    w.writeframes((np.clip(sp, -.98, .98) * 32767).astype("<i2").tobytes())
(HERE / "video" / "timing_gm.json").write_text(json.dumps({"total": total, "lines": timing}, ensure_ascii=False, indent=1), encoding="utf-8")
for e in timing:
    print(f"{e['n']}: {e['start']:6.2f}-{e['end']:6.2f}")
print("total", total)
