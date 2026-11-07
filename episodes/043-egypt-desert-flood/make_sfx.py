"""SFX + music ตอน 043 (น้ำท่วมทะเลทรายอียิปต์) ด้วย numpy ให้ตรงกับ timeline ใน build.py
  python make_sfx.py  -> video/audio_gm/sfx.wav, music.wav"""
import json, sys, wave
from pathlib import Path
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
SR = 48000
timing = json.loads((HERE / "video" / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL = timing["total"]
L = timing["lines"]
SC = [0.0] + [L[i]["start"] - 0.2 for i in range(1, 6)]
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



def siren(dur=1.6):
    n = int(SR * dur); t = np.arange(n) / SR
    f = 700 + 300 * np.sin(2 * np.pi * 1.2 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.05, 0.3) * 0.35


def rush(dur=1.5, peak=0.8):
    n = int(SR * dur); t = np.linspace(0, 1, n)
    x = lowpass(rng.standard_normal(n), 900) * (t ** 1.5) * 0.9
    return x * env(n, 0.05, 0.25) * peak


def rain(dur=2.0):
    n = int(SR * dur)
    x = rng.standard_normal(n) - lowpass(rng.standard_normal(n), 3000)
    return x * 0.12 * env(n, 0.2, 0.4)


def buzz():
    n = int(SR * 0.4); t = np.arange(n) / SR
    return np.sign(np.sin(2 * np.pi * 150 * t)) * env(n, 0.005, 0.1) * 0.35


# --- ฮุก ---
put(0.0, whoosh(3.2), 1.0)
put(0.12, thud(), 1.0)
put(0.55, thud(), 1.0)
put(0.9, rush(2.0, 0.9), 0.9)
put(0.55, pop(300, 1200, 0.2), 0.6)
# --- กล้อง/การ์ด ---
for i in range(1, 6):
    put(SC[i] - 0.1, whoosh(1.0), 0.8)
for i in range(0, 6):
    put(SC[i] + (3.5 if i == 0 else 0.3), pop(300, 700, 0.18), 0.8)
    put(SCE[i] - 0.3, swish(), 0.5)
# ซีน 1: ฝน+น้ำพัดรถ
put(SC[1] + 0.3, rain(5.0), 1.0)
put(SC[1] + 0.9, siren(2.0), 0.7)
put(at(1, 0.45), rush(2.2, 1.0), 1.0)
put(at(1, 0.75), thud(), 1.0)
# ซีน 2: ตัวเลข
for f in (0.2, 0.45, 0.7):
    put(at(2, f), thud(), 0.9); put(at(2, f), ding(), 0.5)
# ซีน 3: ฝนตกบนภูเขา น้ำรวมตัว
put(SC[3] + 0.2, rain(6.0), 1.0)
put(at(3, 0.45), rush(3.0, 0.8), 0.9)
put(at(3, 0.7), pop(500, 1100, 0.12), 0.7)
# ซีน 4: น้ำไกลดังขึ้น ปะทะ
put(at(4, 0.2), rush(4.5, 1.0), 0.7)
put(at(4, 0.75), thud(), 1.0)
put(at(4, 0.75), splash(), 1.0)
put(at(4, 0.78), buzz(), 0.6)
# ซีน 5: ตราประทับ
for k, f in enumerate((0.3, 0.45, 0.6)):
    put(at(5, f), thud(), 1.0)
    put(at(5, f) + 0.05, buzz() if k < 2 else ding(), 0.8)
put(at(5, 0.85), ding(), 0.9)

out = out[: int(SR * TOTAL)]
n = len(out); t = np.arange(n) / SR
drone = np.sin(2 * np.pi * 55 * t) * 0.35 + np.sin(2 * np.pi * 82.4 * t) * 0.22 + np.sin(2 * np.pi * 110.5 * t) * 0.12
drone *= 0.65 + 0.35 * np.sin(2 * np.pi * 0.12 * t)
beat = np.zeros(n)
for bt in np.arange(0.4, TOTAL, 1.0):
    k = int(bt * SR); m = int(0.25 * SR); tt = np.arange(m) / SR
    beat[k:k + m] += (np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 14))[: n - k] * 0.5
music = (drone + beat) * np.minimum(1, np.minimum(t / 0.5, (TOTAL - t) / 1.2))


def save(name, x, peak):
    x = x / max(float(np.abs(x).max()), 1e-9) * peak
    with wave.open(str(HERE / "video" / "audio_gm" / name), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((np.clip(x, -.98, .98) * 32767).astype("<i2").tobytes())


save("sfx.wav", out, 0.9)
save("music.wav", music, 0.7)
print("sfx/music OK", round(TOTAL, 2), "s")
