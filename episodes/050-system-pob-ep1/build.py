"""สร้าง video/index.html ของ EP.050 ระบบล่าปอบ ตอน 1 (Three.js 2.5D)
  python build.py   (ต้องมี video/timing_gm.json และ video/audio_gm/NN_t.wav จาก make_voice.py)
เขียน video/sync.json ให้ make_sfx.py ใช้จับจังหวะด้วย"""
import json, re, subprocess
from pathlib import Path
import numpy as np
from lines import CAPS

HERE = Path(__file__).resolve().parent
V = HERE / "video"
timing = json.loads((V / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL = timing["total"]
LINES = timing["lines"]
N = len(LINES)
SR = 16000


def envelope(wav):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    x = np.abs(np.frombuffer(raw, dtype="<f4"))
    win = int(SR * 0.03)
    return np.convolve(x, np.ones(win) / win, mode="same")


SPOKEN = {"A": "เอ", "B": "บี", "C": "ซี", "...": ""}


def plen(s):
    for a, b in SPOKEN.items():
        s = s.replace(a, b)
    return len(re.sub(r"[\s\[\]{}]", "", s))


SYNC = []
for i, chunks in enumerate(CAPS):
    env = envelope(V / "audio_gm" / f"{i:02}_t.wav")
    voiced = np.where(env > env.max() * 0.08)[0]
    t0, t1 = voiced[0] / SR, voiced[-1] / SR
    w = [plen(c[0]) for c in chunks]
    cuts, acc = [], 0
    for k in range(len(chunks) - 1):
        acc += w[k]
        t = t0 + (t1 - t0) * acc / sum(w)
        a, b = max(int((t - .4) * SR), int(t0 * SR)), min(int((t + .4) * SR), int(t1 * SR))
        cuts.append((a + int(np.argmin(env[a:b]))) / SR if b > a else t)
    starts = [t0] + cuts
    for k in range(1, len(starts)):
        starts[k] = max(starts[k], starts[k - 1] + .5)
    off = LINES[i]["start"]
    SYNC.append([[round(off + s, 2), round(off + (starts[k + 1] if k + 1 < len(starts) else t1 + .3), 2)] for k, s in enumerate(starts)])

SC = [0.0] + [round(LINES[i]["start"] - 0.2, 3) for i in range(1, N)]
DATA = dict(SC=SC, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL)
HTML = (HERE / "template.html").read_text(encoding="utf-8")
HTML = HTML.replace("%%TOTAL%%", f"{TOTAL}").replace("%%DATA%%", json.dumps(DATA, ensure_ascii=False))
(V / "index.html").write_text(HTML, encoding="utf-8")
(V / "sync.json").write_text(json.dumps({"SC": SC, "SYNC": SYNC}, ensure_ascii=False), encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i, SC[i], [c[0] for c in SYNC[i]])
