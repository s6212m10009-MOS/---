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
SC = [0.0] + [L[i]["start"] - 0.2 for i in range(1, 10)]
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



# ---- ฮุก: เครื่องบินบินผ่าน ทิ้งระเบิด ตูม ----
def jet(dur=1.9):  # เสียงเครื่องบินผ่าน: ลมหอน + เครื่องยนต์ต่ำ
    n = int(SR * dur); t = np.arange(n) / SR
    x = lowpass(rng.standard_normal(n), 900) * np.sin(np.pi * t / dur) ** 1.5
    x += np.sin(2 * np.pi * (95 + 25 * np.sin(2 * np.pi * 0.7 * t)) * t) * 0.25 * np.sin(np.pi * t / dur)
    return x / (np.abs(x).max() + 1e-9) * 0.7


def bomb_whistle(dur=0.9):  # ระเบิดตก: โทนหวีดไถลลง
    n = int(SR * dur); t = np.arange(n) / SR
    f = 2200 - 1500 * (t / dur) ** 0.8
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.05, 0.05) * 0.35


def boom(dur=2.6):  # ระเบิดตูม: เสียงต่ำกระแทก + สัญญาณรบกวน + กังวานท้าย
    n = int(SR * dur); t = np.arange(n) / SR
    low = np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-t * 9)) / SR) * np.exp(-t * 1.8)
    noise = lowpass(rng.standard_normal(n), 1400) * np.exp(-t * 3.2)
    crack = rng.standard_normal(n) * np.exp(-t * 55) * 0.8
    rumble = lowpass(rng.standard_normal(n), 120) * np.exp(-t * 1.1) * 1.4
    y = low * 1.0 + noise * 0.8 + crack + rumble
    return y / (np.abs(y).max() + 1e-9)


put(0.2, jet(1.9), 0.8)
put(0.95, bomb_whistle(0.9), 0.7)
put(0.12, thud(), 0.6)
put(1.85, boom(), 1.4)
put(2.3, pop(300, 800, 0.15), 0.4)
for k in range(4):
    put(2.6 + k * 1.0, tick(), 0.3)
# ฉาก 1: 1945
put(SC[1] - 0.1, whoosh(1.7), 0.9)
put(at(1, 0.15) + 0.3, thud(), 1.0)
put(at(1, 0.6) + 0.3, pop(500, 900), 0.8)
# ฉาก 2: กัมมันตรังสีแผ่เป็นวง
put(SC[2] - 0.1, whoosh(0.8), 0.6)
put(at(2, 0.05) + 0.3, powerdown(1.4), 0.5)
for k in range(4):
    put(at(2, 0.4 + k * 0.1) + 0.3, pop(300 + k * 50, 700, 0.12), 0.6)
# ฉาก 3: ทูตตอบโต้ + แท่งกราฟขึ้น
put(SC[3] - 0.1, whoosh(0.6), 0.5)
put(at(3, 0.05) + 0.3, plop(), 0.8)
put(at(3, 0.1) + 0.3, plop(), 0.8)
put(at(3, 0.3) + 0.3, pop(400, 800), 0.8)
for k in range(4):
    put(at(3, 0.5 + k * 0.1) + 0.3, pop(400 + k * 120, 800 + k * 120, 0.1), 0.6)
# ฉาก 4: น้ำมันพุ่ง
put(SC[4] - 0.1, whoosh(1.6), 0.7)
put(at(4, 0.05) + 0.3, plop(), 0.9)
put(at(4, 0.25) + 0.3, whoosh(1.2), 0.6)
put(at(4, 0.2) + 0.3, pop(500, 1000), 0.8)
# ฉาก 5: ไกล ไม่ต้องหลุมหลบภัย
put(SC[5] - 0.1, whoosh(1.6), 0.7)
put(at(5, 0.05) + 0.3, pop(400, 800), 0.8)
put(at(5, 0.15) + 0.3, pop(500, 900), 0.8)
put(at(5, 0.1), whoosh(1.8), 0.4)
put(at(5, 0.35) + 0.3, ding() * 0.6, 0.7)
put(at(5, 0.65) + 0.3, plop(), 0.9)
# ฉาก 6: 4 ผลกระทบเศรษฐกิจ
put(SC[6] - 0.1, whoosh(0.6), 0.5)
for q in range(4):
    put(at(6, 0.05 + q * 0.12) + 0.3, plop(), 0.9)
# ฉาก 7: เงินสำรอง
put(SC[7] - 0.1, whoosh(0.6), 0.5)
for f in (0.05, 0.12, 0.2):
    put(at(7, f) + 0.3, plop(), 0.8)
put(at(7, 0.3) + 0.3, pop(500, 900), 0.8)
put(at(7, 0.7) + 0.3, thud() * 0.6, 0.7)
# ฉาก 8: ข่าวทางการ
put(SC[8] - 0.1, whoosh(0.6), 0.5)
put(at(8, 0.05) + 0.3, plop(), 0.9)
put(at(8, 0.3) + 0.3, ding(), 0.7)
put(at(8, 0.4) + 0.3, plop(), 0.9)
# ฉาก 9: ตั้งสติ ไฟเขียวทั่วโลก
put(SC[9] - 0.1, whoosh(1.5), 0.8)
put(at(9, 0.05) + 0.3, pop(300, 700, 0.18), 0.8)
put(at(9, 0.25) + 0.3, ding(), 0.8)
for c in range(12):
    put(SC[9] + 1.2 + c * 0.16, pop(700 + c * 60, 1100 + c * 60, 0.1), 0.6)
put(at(9, 0.72), ding(), 0.9)

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
bright = np.clip((t - SC[5]) / 3.0, 0, 1)
pad += bright * (np.sin(2 * np.pi * 220 * t) * 0.15 + np.sin(2 * np.pi * 277.2 * t) * 0.1 + np.sin(2 * np.pi * 329.6 * t) * 0.1)
pad *= np.minimum(1, t / 1.5) * np.minimum(1, (TOTAL - t) / 2.0)
save("music.wav", pad / np.abs(pad).max() * 0.5)
print("sfx + music", round(TOTAL, 2), "s")
