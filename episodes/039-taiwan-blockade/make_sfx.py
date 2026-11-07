"""SFX + เพลงพื้นหลังของตอน 039 (ไต้หวัน) ด้วย numpy ให้ตรงจังหวะกับ timeline ใน template.html
  python make_sfx.py  ->  video/audio_gm/sfx.wav, video/audio_gm/music.wav (mono 48kHz)
ฮุก 0-5 วิ: เครื่องบินเจ็ตบินผ่านวนรอบเกาะ + แตรเรือ + ไซเรน"""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
timing = json.loads((HERE / "video" / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL = timing["total"]
L = timing["lines"]
ITEMS = json.loads((HERE / "video" / "items.json").read_text())
SC = [0.0] + [L[i]["start"] - 0.2 for i in range(1, len(L))]
rng = np.random.default_rng(39)
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
    a = float(np.exp(-2 * np.pi * fc / SR))
    # one-pole lowpass via FFT-free recursion in blocks (vectorised with cumulative trick)
    n = len(x)
    y = np.empty(n)
    s_ = 0.0
    B = 2048
    k = np.arange(B)
    w = (1 - a) * a ** k
    for i in range(0, n, B):
        blk = x[i:i + B]
        m = len(blk)
        conv = np.convolve(blk, w[:m])[:m]
        y[i:i + m] = conv + s_ * a ** (k[:m] + 1)
        s_ = y[i + m - 1]
    return y


def whoosh(dur=0.9):
    n = int(SR * dur)
    x = rng.standard_normal(n)
    lo, hi = lowpass(x, 500), lowpass(x, 3500)
    t = np.linspace(0, 1, n)
    sweep = np.sin(np.pi * t) ** 1.5
    y = lo * (1 - sweep) + hi * sweep
    return y / (np.abs(y).max() + 1e-9) * np.sin(np.pi * t) ** 1.2 * 0.6


def jet(dur=1.5):  # เจ็ตบินผ่าน: ลมหวีด + ไถลความถี่ (โดปเปลอร์)
    n = int(SR * dur); t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    band = lowpass(noise, 2600) - lowpass(noise, 500)
    f = 520 * (1.6 - 1.1 * t ** 0.8)  # โทนสูงตกลงตอนผ่าน
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    amp = np.sin(np.pi * t) ** 2
    y = (band / (np.abs(band).max() + 1e-9) * 0.8 + tone) * amp
    return y * 0.8


def horn(dur=1.6, f=98):  # แตรเรือ: โทนต่ำสองความถี่
    n = int(SR * dur); t = np.arange(n) / SR
    y = np.sign(np.sin(2 * np.pi * f * t)) * 0.18 + np.sin(2 * np.pi * f * t) * 0.4 + np.sin(2 * np.pi * f * 1.5 * t) * 0.25
    y = lowpass(y, 900)
    return y * env(n, 0.12, 0.5) * 1.1


def siren(dur=2.0):
    n = int(SR * dur); t = np.arange(n) / SR
    f = 700 + 180 * np.sin(2 * np.pi * 0.9 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.05, 0.4) * 0.35


def pop(f0=420, f1=900, dur=0.14):
    n = int(SR * dur); t = np.arange(n) / SR
    f = f0 + (f1 - f0) * np.minimum(t / dur * 2, 1)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, dur * 0.7) * 0.6


def tick():
    n = int(SR * 0.05); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 90) * 0.4


def stamp():
    n = int(SR * 0.6); tt = np.arange(n) / SR
    body = np.sin(2 * np.pi * np.cumsum(70 + 160 * np.exp(-tt * 25)) / SR) * np.exp(-tt * 6)
    crack = rng.standard_normal(n) * np.exp(-tt * 55) * 0.9
    return (body + crack) * 0.9


def ping(f=1250, dur=1.1):
    n = int(SR * dur); tt = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 7)
    echo = np.zeros(n); k = int(0.28 * SR); echo[k:] = y[:n - k] * 0.45
    return (y + echo) * 0.5


def buzz(dur=0.5):
    n = int(SR * dur); tt = np.arange(n) / SR
    y = np.sign(np.sin(2 * np.pi * 110 * tt)) * 0.35 + np.sin(2 * np.pi * 165 * tt) * 0.2
    return y * env(n, 0.01, 0.15)


def ding():
    n = int(SR * 0.9); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t)) * np.exp(-t * 5) * 0.4


def impact():
    n = int(SR * 0.9); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-t * 14)) / SR) * np.exp(-t * 4)
    return (body + lowpass(rng.standard_normal(n), 1800) * np.exp(-t * 14) * 0.6) * 0.9


# ----- ฮุก 0-5 วิ -----
put(0.0, impact(), 0.9)
for t0, g in [(0.25, 0.9), (1.35, 0.9), (2.5, 0.9), (3.6, 0.8)]:
    put(t0, jet(1.6), g)
put(0.5, horn(1.8, 98), 0.8)
put(2.9, horn(1.8, 82), 0.8)
put(1.0, siren(2.6), 0.5)
for k in range(6):  # ซอนาร์
    put(0.8 + k * 0.7, ping(1250 if k % 2 == 0 else 1000, 0.8), 0.25)

# ----- เปลี่ยนฉาก + ไอเท็มในการ์ด -----
for i in range(1, len(SC)):
    put(SC[i] - 0.05, whoosh(0.7), 0.8)
    for k in range(ITEMS[str(i)]):
        put(SC[i] + 0.4 + 0.2 * k, pop(400 + 40 * (k % 4), 850 + 40 * (k % 4)), 0.7)
# นับเลข 49 / 100+
for k in range(14):
    put(SC[1] + 0.5 + k * 0.085, tick(), 0.8)
for k in range(14):
    put(SC[2] + 0.5 + k * 0.085, tick(), 0.8)
put(SC[1] + 0.25, jet(1.2), 0.5)
put(SC[2] + 0.3, horn(1.4, 110), 0.55)
put(SC[3] + 0.9, stamp(), 0.9)          # ซ้อมรบ ไม่ใช่ปิดล้อม
put(SC[4] + 0.5, ding(), 0.8)           # TSMC pin
put(SC[5] + 0.5, buzz(0.6), 0.9)        # สมมติ: เรือเข้าไม่ได้
put(SC[5] + 1.4, siren(2.0), 0.35)
for k in range(3):
    put(SC[5] + 2.0 + k * 0.25, pop(500, 1100), 0.5)
put(SC[6] + 0.4, ping(1000, 1.2), 0.7)  # ปักกิ่ง
put(SC[7] + 0.9, ding(), 0.9)

# ----- เพลง: ดรอนต่ำตึงเครียด + ชีพจรช้าๆ -----
n = len(out)
t = np.arange(n) / SR
drone = np.sin(2 * np.pi * 55 * t) * 0.35 + np.sin(2 * np.pi * 82.4 * t) * 0.22 + np.sin(2 * np.pi * 110.5 * t) * 0.12
drone *= 0.65 + 0.35 * np.sin(2 * np.pi * 0.12 * t)
beat = np.zeros(n)
for b in np.arange(0.4, TOTAL, 1.0):
    k = int(b * SR)
    m = int(0.25 * SR)
    tt = np.arange(m) / SR
    beat[k:k + m] += (np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 14))[: n - k] * 0.5
music = drone + beat
fade = np.minimum(1, np.minimum(t / 0.5, (TOTAL + 1 - t) / 1.2))
music = music * fade


def save(name, x, peak):
    x = x / max(float(np.abs(x).max()), 1e-9) * peak
    with wave.open(str(HERE / "video" / "audio_gm" / name), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((np.clip(x, -.98, .98) * 32767).astype("<i2").tobytes())


save("sfx.wav", out, 0.9)
save("music.wav", music, 0.7)
print("sfx/music OK", round(TOTAL, 2), "s")
