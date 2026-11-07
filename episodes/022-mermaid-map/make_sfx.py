"""สร้างเสียงเอฟเฟกต์ (SFX) ของตอน 022 ด้วย numpy ให้ตรงจังหวะกับ timeline ใน template.html
ผลลัพธ์: video/audio_gm/sfx.wav (mono 48kHz ความยาวเท่า timing_gm.json)
  python make_sfx.py
เวลาของเหตุการณ์คำนวณจาก timing_gm.json แบบเดียวกับ build.py (ฉากเริ่ม = เริ่มบรรทัดเสียง - 0.2 วินาที)"""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
timing = json.loads((HERE / "video" / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL = timing["total"]
L = timing["lines"]
SC = [0.0] + [L[i]["start"] - 0.2 for i in range(1, 13)]
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


# --- กล้องบินข้ามแผนที่ ---
for i in (1, 2, 3, 4, 5, 7, 8, 9, 11, 12):
    put(SC[i] - 0.1, whoosh(1.0), 0.8)
put(at(0, 0.45), swish(), 0.6)
for f in (0.62, 0.7, 0.78):
    put(at(0, f), pop(350, 600, 0.12), 0.8)
# --- แผนที่เปิดฉาก: จุดเทาไล่ปรากฏ ---
put(0.0, whoosh(3.2), 1.0)       # ฮุก: พุ่งเข้าจากอวกาศ
put(0.12, thud(), 1.0)            # ตัวหนังสือบรรทัดแรกตบจอ
put(0.55, thud(), 1.0)            # บรรทัดที่สอง
put(0.55, pop(300, 1200, 0.2), 0.6)
# --- การ์ดโมชั่นเข้า/ออก ---
for i in range(0, 12):
    put(SC[i] + (3.5 if i == 0 else 0.3), pop(300, 700, 0.18), 0.8)
    put(SCE[i] - 0.3, swish(), 0.5)
# --- หมุดเปลี่ยนเป็นแดง ---
for sc in (1, 2, 3, 3, 5, 7, 8):
    put(SC[sc] + 0.9 + (0.0 if sc != 3 else 0.0), pop(500, 1100, 0.12), 0.7)
# --- ฉากเฉพาะ ---
put(at(1, 0.28), splash(), 0.9)            # เงือกโผล่
put(at(2, 0.05), swish(), 0.6)             # เรือแล่น
put(at(2, 0.4), splash(), 0.8)
put(at(2, 0.62), pop(600, 1000), 0.8)      # ฟองคำถาม
put(at(3, 0.08), swish(), 0.7); put(at(3, 0.5), swish(), 0.7)
for f in (0.1, 0.3, 0.7):
    put(at(4, f), pop(), 0.8)
put(at(5, 0.05), swish(), 0.5)
for f in (0.4, 0.55, 0.7):
    put(at(5, f), pop(350, 600, 0.12), 0.8)
put(at(6, 0.1), pop(), 0.8); put(at(6, 0.3), pop(), 0.8); put(at(6, 0.5), tick(), 0.8)
put(at(7, 0.08), swish(), 0.6); put(at(7, 0.28), swish(), 0.6); put(at(7, 0.6), pop(500, 1200), 0.9)
put(at(8, 0.4), thud(), 1.0)               # ตรา "นิยาย"
put(at(8, 0.65), tick(), 0.8)
put(at(9, 0.15), swish(), 0.9)             # ขีดฆ่านางเงือก
put(at(9, 0.28), splash(), 0.7)
put(at(10, 0.1), thud(), 0.7); put(at(10, 0.45), thud(), 0.7)
put(at(11, 0.15), pop(400, 1000), 0.9)
put(SC[9] + 1.0, sparkle(), 0.9)           # พะยูนแทนหมุด
for k in range(3):                          # ตราประทับท้ายคลิป
    put(SC[12] + 0.2 + k * (SCE[12] - SC[12]) * 0.2, thud(), 1.0)
put(SC[12] + (SCE[12] - SC[12]) * 0.78, ding(), 0.9)

out = out[: int(SR * TOTAL)]
out = out / max(float(np.abs(out).max()), 1e-9) * 0.6   # ปรับยอดเสียงไม่ให้แตก (เสียงพากย์ต้องเด่นกว่า)
dest = HERE / "video" / "audio_gm" / "sfx.wav"
with wave.open(str(dest), "wb") as w:
    w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
    w.writeframes((out * 32767).astype("<i2").tobytes())
print("เขียน", dest.name, round(len(out) / SR, 2), "วินาที · peak", round(float(np.abs(out).max()), 2))
