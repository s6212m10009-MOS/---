"""เสียงบรรยากาศคลิปทดลอง (สังเคราะห์เองทั้งหมด) + เสียงพากย์ -> soundtrack.wav
  python tools/make_sound.py
"""

import json
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
TIMING = json.loads((ROOT / "timing.json").read_text(encoding="utf-8"))
SR = 48000
TOTAL = TIMING["total"]
N = int(SR * TOTAL)
rng = np.random.default_rng(2569)
t = np.arange(N) / SR

# จังหวะเหตุการณ์ ต้องตรงกับ index.html
LIGHT_ON = 0.45
RISE = [4.2, 4.4, 7.5, 7.9]
DIG = [5.05, 5.85, 6.65, 5.45, 6.25]
NEEDLE = [6.1, 10.05]
KEY_CLOSE = 11.75


def env(n, a, d):
    e = np.ones(n)
    ka, kd = int(SR * a), int(SR * d)
    e[:ka] = np.linspace(0, 1, ka)
    e[-kd:] *= np.linspace(1, 0, kd)
    return e


def lowpass(x, cutoff):
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X = np.fft.rfft(x)
    X[f > cutoff] = 0
    return np.fft.irfft(X, len(x))


def put(buf, at, sig, gain=1.0):
    i = int(at * SR)
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def bell(freq, dur=2.2):
    tt = np.arange(int(SR * dur)) / SR
    s = sum(a * np.sin(2 * np.pi * freq * r * tt) * np.exp(-tt * k)
            for r, a, k in [(1, 1, 2.2), (2.76, .45, 3.5), (5.4, .25, 5), (8.9, .12, 7)])
    return s * env(len(tt), .003, .3)


def tick():
    n = int(SR * .05)
    return rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 120) * .8


def thud():
    tt = np.arange(int(SR * .35)) / SR
    return (np.sin(2 * np.pi * (70 - 30 * tt) * tt) * np.exp(-tt * 14)
            + lowpass(rng.standard_normal(len(tt)), 900) * np.exp(-tt * 25) * .6)


def swish(dur=.6):
    n = int(SR * dur)
    s = lowpass(rng.standard_normal(n), 2500)
    return s * np.sin(np.linspace(0, np.pi, n)) ** 2


mix = np.zeros(N)

# โดรนต่ำ เปิดพร้อมตะเกียง หรี่ช่วงตำนาน
drone = (np.sin(2 * np.pi * 55 * t) * .5 + np.sin(2 * np.pi * 82.4 * t) * .3 + np.sin(2 * np.pi * 110.3 * t) * .12)
drone *= .75 + .25 * np.sin(2 * np.pi * .23 * t)
dr_env = np.clip((t - LIGHT_ON) / 1.5, 0, 1) * np.clip((TOTAL - t) / 1.2, 0, 1)
mix += drone * dr_env * .16

# เปลวไฟ: เสียงซ่าเบา ๆ + ปะทุเป็นจุด
crackle = lowpass(rng.standard_normal(N), 4000) * .025
for k in range(40):
    put(crackle, rng.uniform(LIGHT_ON, TOTAL - 1), tick(), rng.uniform(.04, .12))
mix += crackle * np.clip((t - LIGHT_ON) / .4, 0, 1) * np.clip((TOTAL - t) / 1.0, 0, 1)

put(mix, LIGHT_ON - .05, swish(1.0), .35)          # ตะเกียงติด
for r in RISE:
    put(mix, r, swish(.55), .22)                   # หุ่นเงาโผล่จากล่าง
for d in DIG:
    put(mix, d, thud(), .35)
for k, n in enumerate(NEEDLE):
    for j in range(5):
        put(mix, n - .5 + j * .1, tick(), .12)     # เข็มหมุน
    put(mix, n, bell(660 if k == 0 else 494), .22)
put(mix, KEY_CLOSE, thud(), .7)
put(mix, KEY_CLOSE + .05, bell(988, 2.4), .16)

# เสียงพากย์ + ลดเสียงพื้นตอนพูด
with wave.open(str(ROOT / "narration.wav")) as w:
    voice = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32767
voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
duck = np.convolve((np.abs(voice) > .02).astype(float), np.ones(int(SR * .25)) / (SR * .25), "same")
mix = mix * (1 - .45 * np.clip(duck, 0, 1)) + voice

mix /= max(1e-9, np.abs(mix).max() / .95)
with wave.open(str(ROOT / "soundtrack.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("soundtrack.wav", round(TOTAL, 2), "s")
