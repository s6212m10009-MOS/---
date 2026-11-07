"""สร้างเสียงเอฟเฟกต์ (SFX) ของตอน 023 (มังกร) ด้วย numpy ให้ตรงจังหวะกับ timeline ใน template.html
ผลลัพธ์: video/audio_gm/sfx.wav (mono 48kHz ความยาวเท่า timing_gm.json)
  python make_sfx.py
เวลาเหตุการณ์อิง timeline ใน video/index.html (ฉากเริ่ม = เริ่มบรรทัดเสียง - 0.12 วินาที)"""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
timing = json.loads((HERE / "video" / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL = timing["total"]
L = timing["lines"]
SC = [0.0] + [L[i]["start"] - 0.12 for i in range(1, 6)]
SCE = SC[1:] + [TOTAL]
at = lambda i, f: SC[i] + f * (SCE[i] - SC[i])
rng = np.random.default_rng(7)
out = np.zeros(int(SR * (TOTAL + 1)))


def put(t, x, gain=1.0):
    k = int(t * SR)
    if k < 0 or k >= len(out):
        return
    x = x[: len(out) - k]
    out[k:k + len(x)] += x * gain


def env(n, a=0.01, r=0.1):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return y


def whoosh(dur=0.9):
    n = int(SR * dur)
    x = rng.standard_normal(n)
    # กวาดความถี่ขึ้นแล้วลง: ผสมสัญญาณที่กรองต่ำสองระดับ
    lo, hi = lowpass(x, 500), lowpass(x, 3500)
    t = np.linspace(0, 1, n)
    sweep = np.sin(np.pi * t) ** 1.5
    y = lo * (1 - sweep) + hi * sweep
    return y / (np.abs(y).max() + 1e-9) * np.sin(np.pi * t) ** 1.2 * 0.6


def pop(f0=420, f1=900, dur=0.14):
    n = int(SR * dur); t = np.arange(n) / SR
    f = f0 + (f1 - f0) * np.minimum(t / dur * 2, 1)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, dur * 0.7) * 0.7


def thud():
    n = int(SR * 0.45); t = np.arange(n) / SR
    f = 45 + 80 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    click = lowpass(rng.standard_normal(n), 2500) * np.exp(-t * 60) * 0.6
    return (body + click) * 0.9


def splash():
    n = int(SR * 0.6); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 2200) * np.exp(-t * 7) * env(n, 0.01, 0.1) * 0.7


def ding():
    n = int(SR * 0.9); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t)) * np.exp(-t * 5) * 0.5


def tick():
    n = int(SR * 0.05); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 90) * 0.5


def swish():
    return whoosh(0.35) * 0.6


def sparkle():
    y = np.zeros(int(SR * 0.7))
    for k, f in enumerate([1568, 2093, 2637, 3136]):
        n = int(SR * 0.3); t = np.arange(n) / SR
        s = np.sin(2 * np.pi * f * t) * np.exp(-t * 9) * 0.35
        o = int(k * 0.07 * SR); y[o:o + n] += s
    return y



# --- ฮุก: ตัวมังกรพุ่งเข้า ---
put(0.0, whoosh(1.2), 0.9)
put(0.2, pop(350, 800, 0.16), 0.8)
put(0.1, swish(), 0.7); put(0.2, swish(), 0.7)
put(SC[0] + 1.0, pop(), 0.8); put(SC[0] + 2.2, pop(), 0.8)
put(SC[0] + 4.0, thud(), 1.0)             # คำว่า "ทำไม?"
for i in range(1, 6):
    put(SC[i] - 0.1, whoosh(0.9), 0.8)    # ตัดฉาก
    put(SC[i] + 0.2, pop(350, 800, 0.16), 0.8)  # ป้ายบน
put(SC[1] + 0.3, swish(), 0.7); put(SC[1] + 1.6, whoosh(0.7), 0.7)  # ไฟพ่น
put(SC[1] + 1.6, pop(), 0.8); put(SC[1] + 2.8, pop(), 0.8)
put(SC[2] + 0.3, swish(), 0.7); put(SC[2] + 0.6, splash(), 0.35); put(SC[2] + 1.8, splash(), 0.3)
put(SC[2] + 3.4, pop(), 0.8); put(SC[2] + 4.6, sparkle(), 0.9)
put(SC[3] + 0.3, swish(), 0.7); put(SC[3] + 0.5, swish(), 0.7)
put(SC[3] + 1.3, thud(), 1.0)             # เครื่องหมาย ≠
for f in (2.6, 3.4, 4.2, 5.0):
    put(SC[4] + f, pop(350, 700, 0.12), 0.8)
put(SC[4] + 6.0, swish(), 0.8)            # ขีดฆ่าฟอสซิล
put(SC[4] + 6.3, thud(), 0.8)
put(SC[4] + 7.0, ding(), 0.7)             # ยังไม่มีคำตอบเดียว
put(SC[5] + 0.3, swish(), 0.7)
put(SC[5] + 2.6, splash(), 0.3); put(SC[5] + 2.8, pop(), 0.8)
put(SC[5] + 6.2, pop(500, 1100, 0.14), 0.9); put(SC[5] + 6.3, ding(), 0.8)

out = out[: int(SR * TOTAL)]
out = out / max(float(np.abs(out).max()), 1e-9) * 0.6
dest = HERE / "video" / "audio" / "sfx.wav"
with wave.open(str(dest), "wb") as w:
    w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
    w.writeframes((out * 32767).astype("<i2").tobytes())
print("เขียน", dest.name, round(len(out) / SR, 2), "วินาที · peak", round(float(np.abs(out).max()), 2))
