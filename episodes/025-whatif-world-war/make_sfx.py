"""SFX + เพลงพื้นหลังของตอน 025 ด้วย numpy ให้ตรงจังหวะกับ timeline ใน template.html
  python make_sfx.py  ->  video/audio_gm/sfx.wav, video/audio_gm/music.wav (mono 48kHz ยาวเท่า timing_gm.json)
เวลาของเหตุการณ์คำนวณจาก timing_gm.json แบบเดียวกับ build.py (ฉากเริ่ม = เริ่มบรรทัดเสียง - 0.2 วินาที)"""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
timing = json.loads((HERE / "video" / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL = timing["total"]
L = timing["lines"]
SC = [0.0] + [L[i]["start"] - 0.2 for i in range(1, 12)]
SCE = SC[1:] + [TOTAL]
at = lambda i, f: SC[i] + f * (SCE[i] - SC[i])
rng = np.random.default_rng(11)
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


def plop():  # ของตกลงกระเป๋า: ตุ้บนุ่มๆ + กริ๊กเบาๆ
    n = int(SR * 0.3); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * np.cumsum(140 + 120 * np.exp(-t * 25)) / SR) * np.exp(-t * 14)
    tick = lowpass(rng.standard_normal(n), 3000) * np.exp(-t * 90) * 0.5
    return (body + tick) * 0.9


def tick():
    n = int(SR * 0.05); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 90) * 0.5


def ding():
    n = int(SR * 0.9); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t)) * np.exp(-t * 5) * 0.5


def siren(dur=2.0):  # ไซเรนเตือนภัย: โทนวนขึ้นลง 520-880 Hz
    n = int(SR * dur); t = np.arange(n) / SR
    f = 700 + 180 * np.sin(2 * np.pi * 0.9 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.05, 0.4) * 0.45


def powerdown(dur=1.4):  # ไฟตก: โทนไถลลง + ฮัมหาย
    n = int(SR * dur); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 2.6) + 50
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * 0.6


def zipper(dur=0.6):  # ซิป: คลิกถี่ๆ
    y = np.zeros(int(SR * dur))
    for k in range(int(dur / 0.025)):
        o = int(k * 0.025 * SR)
        n = int(SR * 0.012)
        y[o:o + n] += lowpass(rng.standard_normal(n), 4500) * np.exp(-np.arange(n) / SR * 400) * 0.6
    return y



# ---- ฮุก: ไซเรน + ตัวหนังสือตบจอ + จุดแดงทยอยขึ้น ----
put(0.0, whoosh(1.2), 0.9)
put(0.12, thud(), 1.0)
put(0.5, thud(), 0.9)
put(0.2, siren(max(SCE[1] - 0.2, 2.0)), 0.8)
for k in range(15):
    put(0.3 + k * 0.09, pop(500 + k * 20, 1000 + k * 20, 0.08), 0.35)
put(SC[1] + 0.1, powerdown(SCE[1] - SC[1] - 0.1), 0.9)
put(SC[2] - 0.1, whoosh(1.5), 0.9)         # ซูมลงกรุงเทพฯ
swish = whoosh(0.35) * 0.6
put(at(2, 0.3), swish, 0.6)
put(at(2, 0.55), pop(600, 1000), 0.8)
put(at(3, 0.15), tick(), 0.7)
for k in range(8):
    put(at(3, 0.2) + k * 0.4, tick(), 0.5)
put(at(3, 0.55), thud(), 1.0)              # 72 ชม. ตบจอ
put(SC[4] - 0.1, whoosh(0.8), 0.6)
put(at(4, 0.15), swish, 0.7); put(at(4, 0.3), pop(), 0.8); put(at(4, 0.55), pop(600, 1000), 0.8)
put(at(4, 0.8), zipper(0.5), 0.8)          # เปิดซิป

# ---- เก็บของใส่กระเป๋า: popIn ของกระเป๋า + ของตกทีละชิ้น ----
DROPS = {5: (0.15, 0.32, 0.5), 6: (0.15, 0.4, 0.65), 7: (0.12, 0.3, 0.5, 0.7), 8: (0.12, 0.32, 0.6), 9: (0.12, 0.4, 0.68), 10: (0.15, 0.5)}
for i, fr in DROPS.items():
    put(SC[i] - 0.1, whoosh(0.6), 0.5)
    put(at(i, 0.05), pop(300, 700, 0.18), 0.7)
    for f in fr:
        put(at(i, f) + 0.3, plop(), 0.9)   # เด้งแตะพื้นช่วงท้ายของ tween ตก
put(at(5, 0.7), pop(500, 1100), 0.8)
for f in (0.2, 0.3, 0.4, 0.5):
    put(at(7, f), tick(), 0.6)  # ไฟฉายกะพริบ
put(at(8, 0.5), zipper(0.35), 0.5)         # ซองกันน้ำ

# ---- ปิด: ปิดซิป + เช็กลิสต์ติ๊ก + ding ----
put(SC[11] - 0.1, whoosh(1.2), 0.8)
put(at(11, 0.05), pop(300, 700, 0.18), 0.8)
for c in range(6):
    put(at(11, 0.1 + c * 0.09), pop(700 + c * 80, 1100 + c * 80, 0.1), 0.7)
put(at(11, 0.55), zipper(0.6), 0.9)
put(at(11, 0.62), thud(), 1.0)
put(at(11, 0.7), ding(), 0.9)

out = out[: int(SR * TOTAL)]
out = out / max(float(np.abs(out).max()), 1e-9) * 0.6


def save(name, x):
    with wave.open(str(HERE / "video" / "audio_gm" / name), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((x * 32767).astype("<i2").tobytes())


save("sfx.wav", out)

# ---- เพลงพื้นหลัง: พาดมืดตึงเครียด (ฮัมต่ำ) แล้วสว่างขึ้นตอนเก็บกระเป๋า ----
n = int(SR * TOTAL); t = np.arange(n) / SR
pad = sum(np.sin(2 * np.pi * f * t + p) * a for f, p, a in [(55, 0, 0.5), (82.4, 1.1, 0.35), (110, 2.0, 0.3), (164.8, 0.4, 0.15)])
pad *= 0.65 + 0.35 * np.sin(2 * np.pi * 0.12 * t)
bright = np.clip((t - SC[4]) / 3.0, 0, 1)
pad += bright * (np.sin(2 * np.pi * 220 * t) * 0.15 + np.sin(2 * np.pi * 277.2 * t) * 0.1 + np.sin(2 * np.pi * 329.6 * t) * 0.1)
pad *= np.minimum(1, t / 1.5) * np.minimum(1, (TOTAL - t) / 2.0)
pad = pad / np.abs(pad).max() * 0.5
save("music.wav", pad)
print("sfx + music", round(TOTAL, 2), "วินาที")
