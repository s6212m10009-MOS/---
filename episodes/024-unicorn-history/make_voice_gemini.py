"""พากย์ script.md ด้วย Gemini TTS ในคำขอเดียว แล้วตัดแบ่งเป็นบรรทัดด้วย whisper
ใช้ฟังก์ชันจาก ../../make_voice_gemini.py ต้องตั้ง GEMINI_API_KEY
ผลลัพธ์: video/audio_gm/NN.wav, video/audio_gm/vo.wav, video/timing_gm.json
  python make_voice_gemini.py [--voice Sadaltager]
"""
import argparse, json, os, subprocess, sys, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
import make_voice_gemini as G  # noqa: E402

AUD = HERE / "video" / "audio_gm"
GAP, LEAD, TAIL = 0.3, 0.25, 1.6

ap = argparse.ArgumentParser()
ap.add_argument("--voice", default=G.VOICE)
ap.add_argument("--style", default=G.STYLE)
ap.add_argument("--tempo", type=float, default=1.0, help="เร่งเสียง เช่น 1.25")
a = ap.parse_args()
sys.stdout.reconfigure(encoding="utf-8")

body = (HERE / "script.md").read_text(encoding="utf-8").split("## เสียงพากย์ทั้งเรื่อง", 1)[1].split("## ช่องโหว่", 1)[0]
texts = [l[2:].strip() for l in body.splitlines() if l.startswith("> ")]
AUD.mkdir(parents=True, exist_ok=True)
if not os.environ.get("GEMINI_API_KEY"):
    sys.exit("ยังไม่ได้ตั้ง GEMINI_API_KEY")

from google import genai
client = genai.Client()
tmp = AUD / "batch.wav"
if not tmp.exists():
    print("TTS", len(texts), "บรรทัด", sum(len(t) for t in texts), "ตัวอักษร", flush=True)
    G.synth(client, "\n".join(texts), tmp, a.voice, a.style)
def split_by_silence(batch, texts, out_dir):
    """แบ่งบรรทัดจากช่วงเงียบ: ตำแหน่งคาดหวังตามสัดส่วนตัวอักษร แล้วดึงไปที่ช่วงเงียบยาวสุดใกล้เคียง (whisper ไทยจับคำไม่แม่น)"""
    SR16 = 16000
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(batch), "-f", "f32le", "-ac", "1", "-ar", str(SR16), "-"])
    x = np.abs(np.frombuffer(raw, dtype="<f4"))
    win = int(SR16 * 0.03)
    env = np.convolve(x, np.ones(win) / win, mode="same")
    voiced = np.where(env > env.max() * 0.04)[0]
    v0, v1 = voiced[0] / SR16, voiced[-1] / SR16
    quiet, runs, i, n = env < env.max() * 0.04, [], 0, len(env)
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]:
                j += 1
            if (j - i) / SR16 >= 0.3:
                runs.append(((i + j) / 2 / SR16, (j - i) / SR16))
            i = j
        else:
            i += 1
    w = [len(t.replace(" ", "")) for t in texts]
    cuts, acc = [], 0
    for k in range(len(texts) - 1):
        acc += w[k]
        t = v0 + (v1 - v0) * acc / sum(w)
        cand = [(d - 0.25 * abs(m - t), m) for m, d in runs if abs(m - t) <= 2.0 and (not cuts or m > cuts[-1] + 2.0)]
        cuts.append(max(cand)[1] if cand else t)
    cj = Path(__file__).resolve().parent / "cuts.json"
    if cj.exists():  # แก้จุดตัดด้วยมือหลังตรวจฟัง/ถอดเสียง
        cuts = json.loads(cj.read_text())
    edges = [max(v0 - 0.15, 0)] + cuts + [v1 + 0.2]
    out_dir.mkdir(parents=True, exist_ok=True)
    for k in range(len(texts)):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(batch), "-ss", f"{edges[k]:.3f}", "-to", f"{edges[k + 1]:.3f}",
                        "-ac", "1", "-ar", str(G.SR), str(out_dir / f"{k:02}.wav")], check=True)
    print("จุดตัด", [round(c, 2) for c in cuts])


split_by_silence(tmp, texts, AUD)

t, timing, clips = LEAD, [], []
for i, text in enumerate(texts):
    src = AUD / f"{i:02}.wav"
    if a.tempo != 1.0:
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
