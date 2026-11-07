"""ผูกซับกับคำพูด: หาช่วงที่มีเสียงพูดจริงของแต่ละบรรทัด (จากพลังงานเสียง) แล้วแบ่งท่อนซับตามสัดส่วนตัวอักษร
จากนั้นดึงจุดตัดไปที่ช่วงเว้นจังหวะที่เงียบที่สุดใกล้เคียง (±0.4 วิ) เพราะ Gemini เว้นตามวลี
อ่าน CAPS จาก video_gm/index.html และเขียน var SYNC (เวลาเริ่ม/จบของทุกท่อน) กลับลงไฟล์เดียวกัน
(whisper ภาษาไทยจับคำไม่แม่นพอ จึงไม่ใช้ในขั้นนี้)
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 16000
html_p = HERE / "video" / "index.html"
h = html_p.read_text(encoding="utf-8")
m = re.search(r"var CAPS = (\[.*?\n      \]);", h, re.S)
caps = json.loads(re.sub(r",(\s*[\]\}])", r"\1", m.group(1)))
timing = json.loads((HERE / "video" / "timing_gm.json").read_text(encoding="utf-8"))["lines"]


def envelope(wav):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    x = np.abs(np.frombuffer(raw, dtype="<f4"))
    win = int(SR * 0.03)
    return np.convolve(x, np.ones(win) / win, mode="same")


sync = []
for i, chunks in enumerate(caps):
    env = envelope(HERE / "video" / "audio_gm" / f"{i:02}_t.wav")
    voiced = np.where(env > env.max() * 0.08)[0]
    t0, t1 = voiced[0] / SR, voiced[-1] / SR
    w = [len(re.sub(r"[\s\[\]]", "", c)) for c in chunks]
    cuts, acc = [], 0
    for k in range(len(chunks) - 1):
        acc += w[k]
        t = t0 + (t1 - t0) * acc / sum(w)
        a, b = int((t - 0.4) * SR), int((t + 0.4) * SR)
        a, b = max(a, int(t0 * SR)), min(b, int(t1 * SR))
        cuts.append((a + int(np.argmin(env[a:b]))) / SR if b > a else t)
    starts = [t0] + cuts
    for k in range(1, len(starts)):  # กันท่อนสั้นเกินไป/ลำดับสลับ
        starts[k] = max(starts[k], starts[k - 1] + 0.5)
    off = timing[i]["start"]
    sync.append([[round(off + s, 2), round(off + (starts[k + 1] if k + 1 < len(starts) else t1 + 0.3), 2)] for k, s in enumerate(starts)])
    print(i, f"พูด {off+t0:.2f}-{off+t1:.2f}", sync[-1])
h = re.sub(r"\n      var SYNC = .*?;\n", "\n", h)
h = h.replace("      var capsEl =", "      var SYNC = " + json.dumps(sync) + ";\n      var capsEl =", 1)
html_p.write_text(h, encoding="utf-8")
