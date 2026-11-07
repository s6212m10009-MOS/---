"""เสียงบรรยากาศ (สังเคราะห์เองทั้งหมด) + เสียงพากย์ -> <variant>/soundtrack.wav
  python tools/make_sound.py 916
"""

import json
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / sys.argv[1]
TIMING = json.loads((OUT / "timing.json").read_text(encoding="utf-8"))
SR = 48000
TOTAL = TIMING["total"]
N = int(SR * TOTAL)
rng = np.random.default_rng(4813)
t = np.arange(N) / SR
BELL = {"ok": 660, "half": 587, "guess": 523, "open": 440, "myth": 392}


def env(n, a, d):
    e = np.ones(n)
    ka, kd = max(1, int(SR * a)), max(1, int(SR * d))
    e[:ka] = np.linspace(0, 1, ka)
    e[-kd:] *= np.linspace(1, 0, kd)
    return e


def lowpass(x, cutoff):
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X = np.fft.rfft(x)
    X[f > cutoff] = 0
    return np.fft.irfft(X, len(x))


def smooth(x, sec):
    """ค่าเฉลี่ยเคลื่อนที่แบบ cumsum (เร็วกว่า np.convolve มากกับเสียงยาว)"""
    k = max(1, int(SR * sec))
    c = np.cumsum(np.concatenate([np.zeros(k), x]))
    y = (c[k:] - c[:-k]) / k
    return np.roll(y, -k // 2)


def put(buf, at, sig, gain=1.0):
    i = max(0, int(at * SR))
    j = min(len(buf), i + len(sig))
    if j > i:
        buf[i:j] += sig[: j - i] * gain


def bell(freq, dur=2.0):
    tt = np.arange(int(SR * dur)) / SR
    s = sum(a * np.sin(2 * np.pi * freq * r * tt) * np.exp(-tt * k)
            for r, a, k in [(1, 1, 2.2), (2.76, .45, 3.5), (5.4, .25, 5), (8.9, .12, 7)])
    return s * env(len(tt), .003, .3)


def tick():
    n = int(SR * .05)
    return rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 120) * .8


def thud():
    tt = np.arange(int(SR * .35)) / SR
    return np.sin(2 * np.pi * (70 - 30 * tt) * tt) * np.exp(-tt * 14) + lowpass(rng.standard_normal(len(tt)), 900) * np.exp(-tt * 25) * .6


def swish(dur=.6):
    n = int(SR * dur)
    return lowpass(rng.standard_normal(n), 2500) * np.sin(np.linspace(0, np.pi, n)) ** 2


mix = np.zeros(N)

# โดรนต่ำ: เปลี่ยนคอร์ดเบา ๆ ทุกซีน
roots = [55, 49, 58.27, 52]
drone = np.zeros(N)
for i, sc in enumerate(TIMING["scenes"]):
    a, b = int(sc["start"] * SR), min(N, int((sc["start"] + sc["duration"]) * SR))
    f = roots[i % len(roots)]
    seg = t[a:b]
    drone[a:b] = np.sin(2 * np.pi * f * seg) * .5 + np.sin(2 * np.pi * f * 1.498 * seg) * .28 + np.sin(2 * np.pi * f * 2.003 * seg) * .1
drone = smooth(drone, .08)
drone *= .75 + .25 * np.sin(2 * np.pi * .21 * t)
mix += drone * np.clip((t - .45) / 1.5, 0, 1) * np.clip((TOTAL - t) / 1.5, 0, 1) * .14

crackle = lowpass(rng.standard_normal(N), 4000) * .022
for k in range(int(TOTAL * 2.5)):
    put(crackle, rng.uniform(.5, TOTAL - 1), tick(), rng.uniform(.03, .1))
mix += crackle * np.clip((t - .45) / .4, 0, 1) * np.clip((TOTAL - t) / 1.0, 0, 1)

put(mix, .4, swish(1.0), .35)
for i, sc in enumerate(TIMING["scenes"]):
    s0 = sc["start"]
    if i:
        put(mix, s0 - .2, swish(.55), .22)
    for c in sc["chunks"]:
        if c.get("v"):
            for j in range(5):
                put(mix, c["t"] - .5 + j * .1, tick(), .1)
            put(mix, c["t"], bell(BELL[c["v"]]), .2)
        if c.get("cue", "").startswith("t") or c.get("cue") == "knot":
            put(mix, c["t"], swish(.5), .2)
    if sc["id"] == "threads":
        put(mix, s0 - .05, thud(), .5)
        put(mix, s0 + .3, swish(.7), .25)
    if sc["id"] == "end":
        put(mix, s0 + 1.0, thud(), .7)
        put(mix, s0 + 1.05, bell(988, 2.4), .15)

with wave.open(str(OUT / "narration.wav")) as w:
    voice = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32767
voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]
duck = smooth((np.abs(voice) > .02).astype(float), .25)
mix = mix * (1 - .45 * np.clip(duck, 0, 1)) + voice
mix /= max(1e-9, np.abs(mix).max() / .95)
with wave.open(str(OUT / "soundtrack.wav"), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("soundtrack.wav", round(TOTAL, 2), "s")
