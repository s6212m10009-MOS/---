"""SFX + ดนตรีสยอง EP.050 ด้วย numpy
  python make_sfx.py  ->  video/audio/sfx.wav, video/audio/music.wav (mono 48kHz)
ต้องมี video/sync.json และ video/timing_gm.json"""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "video" / "audio"
OUT.mkdir(parents=True, exist_ok=True)
SR = 48000
TOTAL = json.loads((HERE / "video" / "timing_gm.json").read_text(encoding="utf-8"))["total"]
sync = json.loads((HERE / "video" / "sync.json").read_text(encoding="utf-8"))
SC, SYNC = sync["SC"], sync["SYNC"]
ck = lambda l, k: SYNC[l][min(k, len(SYNC[l]) - 1)][0]
rng = np.random.default_rng(50)
out = np.zeros(int(SR * (TOTAL + 2)))


def put(t, x, g=1.0):
    k = int(t * SR)
    if 0 <= k < len(out):
        x = x[: len(out) - k]
        out[k:k + len(x)] += x * g


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x); s = 0.0
    for i, v in enumerate(x):
        s = (1 - a) * v + a * s; y[i] = s
    return y


def norm(x, g=1.0):
    return x / (np.abs(x).max() + 1e-9) * g


def tt(d):
    return np.arange(int(SR * d)) / SR


def chew_one():  # เสียงเคี้ยวเปียก ๆ หนึ่งคำ
    t = tt(0.17); z = rng.standard_normal(len(t))
    wet = (lowpass(z, 1700) - lowpass(z, 220)) * np.exp(-t * 26) * (1 + 0.8 * np.sin(2 * np.pi * (70 + rng.random() * 50) * t))
    crunch = (z - lowpass(z, 2600)) * np.exp(-t * 80) * (0.25 + rng.random() * 0.35)
    return norm(wet + crunch, 1.0)


def chewing(a, b, g=1.0, rise=False):
    t = a
    while t < b:
        put(t, chew_one(), g * (0.7 + rng.random() * 0.3) * (0.5 + 0.5 * (t - a) / (b - a) if rise else 1))
        t += 0.2 + rng.random() * 0.1


def beat(g=1.0):
    t = tt(0.5)
    y = lambda o: np.sin(2 * np.pi * np.cumsum(55 + 40 * np.exp(-np.maximum(t - o, 0) * 28)) / SR) * np.exp(-np.maximum(t - o, 0) * 11) * (t >= o)
    return (y(0) + 0.7 * y(0.19)) * g


def heart(a, b, g=1.0, bpm=78):
    t = a
    while t < b:
        put(t, beat(), g); t += 60 / bpm


def stab(d=1.8):  # สติงเกอร์ตกใจ: คลัสเตอร์เสียงไม่ประสาน + แรงกระแทก
    t = tt(d)
    tone = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate([233, 247, 311, 466, 494, 622]))
    tone = norm(tone) * np.exp(-t * 2.2) * np.minimum(1, t / 0.01)
    z = rng.standard_normal(len(t))
    hit = lowpass(z, 200) * np.exp(-t * 5) * 2.5 + (z - lowpass(z, 3000)) * np.exp(-t * 14) * 0.35
    sub = np.sin(2 * np.pi * np.cumsum(30 + 80 * np.exp(-t * 12)) / SR) * np.exp(-t * 2.4)
    return norm(tone * 0.8 + hit * 0.5 + sub * 1.1, 1.0)


def riser(d, f0=80, f1=900):
    t = tt(d); u = (t / d) ** 2.2
    f = f0 + (f1 - f0) * u
    z = rng.standard_normal(len(t))
    return norm((np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 + np.sin(2 * np.pi * np.cumsum(f * 1.06) / SR) * 0.5) * u + (lowpass(z, 5000) - lowpass(z, 900)) * u * 0.4, 0.8)


def creak():  # ไม้ลั่น
    t = tt(0.32)
    f = 190 + 150 * np.sin(2 * np.pi * 3 * t) + 60 * rng.random()
    saw = ((np.cumsum(f) / SR * 34) % 1) * 2 - 1  # แรงเสียดสีเป็นจังหวะถี่
    tone = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (saw > 0.2)
    return norm(lowpass(tone, 1500), 0.5) * np.sin(np.pi * t / 0.32)


def step():
    t = tt(0.16)
    return (np.sin(2 * np.pi * 95 * t) * np.exp(-t * 34) + lowpass(rng.standard_normal(len(t)), 900) * np.exp(-t * 50) * 0.5)


def chirp(f0, f1, d=0.09, g=0.6):
    t = tt(d); f = np.linspace(f0, f1, len(t))
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 18) * g * 0.5 + np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 18) * g * 0.5


def ding(f=1046, d=1.1):
    t = tt(d)
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 4.5) * 0.6


def boot():
    y = np.zeros(int(SR * 1.2))
    for i, (a, b) in enumerate([(300, 500), (500, 760), (760, 1040), (1040, 1560)]):
        c = chirp(a, b, 0.14); k = int(i * 0.13 * SR); y[k:k + len(c)] += c
    d = ding(1568, 0.6); k = int(0.52 * SR); y[k:k + len(d)] += d[: len(y) - k]
    return y


def ping():
    t = tt(0.7)
    return np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 7) * 0.7 + np.sin(2 * np.pi * 660 * t) * np.exp(-t * 11) * 0.3


def alarm():
    t = tt(0.18)
    return np.sign(np.sin(2 * np.pi * 880 * t)) * np.minimum(1, (0.18 - t) * 60) * 0.4


def rooster():
    t = tt(1.5); u = t / 1.5
    f = 520 + 340 * np.sin(np.pi * np.minimum(u * 1.3, 1)) - 150 * u
    x = sum(np.sin(2 * np.pi * k * np.cumsum(f) / SR) / k for k in (1, 2, 3))
    return norm(lowpass(x, 3000), 0.5) * np.sin(np.pi * u) ** 0.5


# ---------- วางเสียงตามเรื่อง ----------
chewing(0.9, SC[1], 0.5, rise=True)
for k in range(5):
    put(ck(0, 2) + 0.1 + k * 0.56, step(), 0.42)
    if k % 2 == 0:
        put(ck(0, 2) + 0.14 + k * 0.56, creak(), 0.22)
chewing(SC[1], ck(1, 2), 0.85)
heart(SC[1], ck(1, 3), 0.75, 92)
for k in range(4):
    put(SC[1] + 0.2 + k * 0.6, step(), 0.28)
put(ck(1, 2) - 0.1, creak(), 0.34)                     # ย่าหันมา = เงียบเคี้ยว + ไม้ลั่น
put(ck(1, 3), stab(), 1.0)
put(ck(2, 1) - 0.8, riser(0.8, 70, 500), 0.5)
put(ck(2, 1), stab(2.2), 0.95)
put(SC[3], boot(), 0.75)
put(ck(3, 1), ding(1318, 0.9), 0.5)
put(ck(3, 3), chirp(800, 1200, 0.1), 0.5)
for k in range(4):
    put(ck(3, 3) + 0.5 + k * 0.5, chirp(1400, 1400, 0.05), 0.3)
put(SC[4], rooster(), 0.34)
put(ck(4, 2), stab(1.2), 0.5)
for k in range(3):
    put(ck(4, 3) + 0.35 + k * 0.4, ping(), 0.65)
for i, c in enumerate([SC[5] + 0.1, ck(5, 2), ck(5, 4)]):
    put(c, chirp(620, 980, 0.11), 0.55); put(c, beat(), 0.7)
put(SC[6] - 0.25, riser(0.3, 300, 1500), 0.3)
put(SC[6] + 0.2, ding(1568, 1.4), 0.5); put(SC[6] + 0.32, ding(2093, 1.4), 0.34)
put(ck(6, 4), chirp(300, 180, 0.2), 0.6)
put(ck(6, 5), stab(1.5), 0.7)
heart(SC[7], SC[8] - 0.2, 0.9, 88)
chewing(SC[7] + 0.9, SC[8] - 0.1, 0.8, rise=True)
put(ck(7, 2), stab(1.6), 0.9)
a = ck(7, 2) + 0.15
while a < SC[8] - 0.3:
    put(a, alarm(), 0.3); a += 0.5
for k in range(1, 4):
    put(ck(8, k), chirp(700 + 120 * k, 1000 + 120 * k, 0.12), 0.55); put(ck(8, k), beat(), 0.5)
put(ck(8, 5), ding(1046, 0.8), 0.4)
put(ck(8, 6), ding(1318, 0.9), 0.5); put(ck(8, 6) + 0.12, ding(1760, 0.9), 0.4)
put(TOTAL - 1.6, chew_one(), 0.9); put(TOTAL - 1.3, chew_one(), 0.9)   # ปิดด้วยเสียงเคี้ยวสองคำ

out = out[: int(SR * TOTAL)]
n = len(out); t = np.arange(n) / SR
# เบดกลางคืน: จิ้งหรีด + ลม
z = rng.standard_normal(n)
wind = (lowpass(z, 900) - lowpass(z, 120)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t))
cr = np.sin(2 * np.pi * 4300 * t) * (np.sin(2 * np.pi * 26 * t) > 0.2) * (np.sin(2 * np.pi * 1.4 * t) > 0)
day = (t >= SC[4]) & (t < ck(4, 3))
cr = cr * np.where(day, 0, 1)
out = norm(out, 0.8) + norm(wind, 0.11) + cr * 0.012
a, b = int((ck(1, 3) - 0.28) * SR), int((ck(1, 3) - 0.02) * SR)     # เงียบก่อนสติงเกอร์ปากแดง
out[a:b] *= 0.12


def save(name, x):
    with wave.open(str(OUT / name), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())


save("sfx.wav", norm(out, 0.82))

# ดนตรี: โดรนต่ำไม่ประสาน ไต่ขึ้นตามความตึง เงียบตอนฮุกหลังซับปาก และเงียบก่อนเฉลยโหวต
dr = sum(np.sin(2 * np.pi * f * t + p) * a_ for f, p, a_ in [(49, 0, .5), (51.9, 1.1, .4), (98, 2, .25), (146.8, .4, .16), (155.6, 1.7, .14)])
dr *= 0.7 + 0.3 * np.sin(2 * np.pi * 0.09 * t)
sys_on = ((t >= SC[3]) & (t < SC[4])) | ((t >= SC[6]) & (t < ck(6, 5)))
pulse = np.sin(2 * np.pi * 220 * t) * (((t * 4) % 1) < .18) * 0.1 * sys_on
tension = np.clip(t / SC[3], 0, 1) * 0.35 + np.clip((t - SC[7]) / (SC[8] - SC[7]), 0, 1) * 0.5
high = (np.sin(2 * np.pi * 622 * t) + np.sin(2 * np.pi * 659 * t)) * 0.05 * tension
mus = (dr + high) * (0.75 + tension) + pulse
mus *= np.minimum(1, t / 1.0) * np.minimum(1, (TOTAL - t) / 1.5)
save("music.wav", norm(mus, 0.5))
print("sfx + music", TOTAL)
