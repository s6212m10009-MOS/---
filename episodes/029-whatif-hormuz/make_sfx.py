"""SFX + เพลงพื้นหลังของตอน 028 ด้วย numpy ให้ตรงจังหวะกับ timeline ใน template.html
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
SC = [0.0] + [L[i]["start"] - 0.2 for i in range(1, 15)]
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
    for k in range(int(dur / 0.026)):
        o = int(k * 0.026 * SR)
        n = int(SR * 0.012)
        y[o:o + n] += lowpass(rng.standard_normal(n), 4500) * np.exp(-np.arange(n) / SR * 400) * 0.6
    return y



# ---- ฮุก ----
put(0.0, whoosh(1.2), 0.9)
put(0.12, thud(), 1.0)
put(0.5, thud(), 0.9)
put(0.9, pop(400, 800, 0.15), 0.8)
put(1.0, siren(2.0), 0.35)
# ฉากต่อฉาก: เปลี่ยนกล้อง (whoosh) + ไอคอนตก (plop) + ป้ายเด้ง (pop)
DROPS = {1: (0.05, 0.2, 0.55), 2: (0.05, 0.4, 0.6, 0.8), 3: (0.1, 0.2, 0.3, 0.5), 4: (0.05, 0.1, 0.2, 0.3), 5: (0.05, 0.1, 0.2, 0.3, 0.5),
         6: (0.05, 0.15, 0.35, 0.55), 7: (0.05, 0.1, 0.4, 0.6),
         8: (0.05, 0.2, 0.3, 0.4, 0.7), 9: (0.05, 0.12, 0.2, 0.4, 0.7), 10: (0.05, 0.12, 0.2, 0.25, 0.55),
         11: (0.05, 0.35), 12: (0.05, 0.25, 0.45, 0.6), 13: (0.05, 0.25, 0.3), 14: (0.05, 0.2)}
for i, fr in DROPS.items():
    put(SC[i] - 0.1, whoosh(0.7 if i not in (1, 11) else 1.6), 0.6)
    for f in fr:
        put(at(i, f) + 0.3, plop(), 0.8)
    put(at(i, 0.02), tick(), 0.4)
# เรือ: ฮอร์นเรือตอนออกเดินทาง และตอนถึง
def horn(dur=1.3):
    n = int(SR * dur); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 110 * t) + 0.6 * np.sin(2 * np.pi * 138 * t)) * env(n, 0.08, 0.5) * 0.5
put(SC[3] + 0.3, horn(), 0.7)
put(SC[6] + 2.8, horn(1.0), 0.6)
put(at(7, 0.4) + 0.3, thud(), 0.8)
put(at(8, 0.7) + 0.3, ding(), 0.7)
put(at(13, 0.25) + 0.3, ding(), 0.8)
for c in range(12):
    put(SC[14] + 1.2 + c * 0.16, pop(700 + c * 60, 1100 + c * 60, 0.1), 0.6)
put(at(14, 0.72), ding(), 0.9)

out = out[: int(SR * TOTAL)]
out = out / max(float(np.abs(out).max()), 1e-9) * 0.6


def save(name, x):
    with wave.open(str(HERE / "video" / "audio_gm" / name), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((x * 32767).astype("<i2").tobytes())


save("sfx.wav", out)
n = int(SR * TOTAL); t = np.arange(n) / SR
pad = sum(np.sin(2 * np.pi * f * t + p) * a for f, p, a in [(55, 0, 0.5), (82.4, 1.1, 0.35), (110, 2.0, 0.3), (164.8, 0.4, 0.15)])
pad *= 0.65 + 0.35 * np.sin(2 * np.pi * 0.12 * t)
bright = np.clip((t - SC[10]) / 3.0, 0, 1)
pad += bright * (np.sin(2 * np.pi * 220 * t) * 0.15 + np.sin(2 * np.pi * 277.2 * t) * 0.1 + np.sin(2 * np.pi * 329.6 * t) * 0.1)
pad *= np.minimum(1, t / 1.5) * np.minimum(1, (TOTAL - t) / 2.0)
save("music.wav", pad / np.abs(pad).max() * 0.5)
print("sfx + music", round(TOTAL, 2), "s")
