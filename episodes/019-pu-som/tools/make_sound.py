"""ดนตรี + ซาวด์เอฟเฟกต์ประกอบแต่ละฉาก (สังเคราะห์เองทั้งหมด ไม่มีเพลงลิขสิทธิ์) -> soundtrack.wav

อ่านเวลาจาก timing.json แล้ววางเสียงตามท่อนที่พากย์
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
N = int(SR * TOTAL) + 1
rng = np.random.default_rng(2500)
SC = {s["id"]: s for s in TIMING["scenes"]}


def at(sid, k=0):
    """เวลาเริ่มของท่อนซับที่ k ในซีน sid"""
    return SC[sid]["chunks"][k]["t"]


def start(sid):
    return SC[sid]["start"]


def end(sid):
    return SC[sid]["start"] + SC[sid]["duration"]


def T(sec):
    return np.arange(int(SR * sec)) / SR


def band(x, lo, hi):
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X = np.fft.rfft(x)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def noise(sec):
    return rng.normal(0, 1, int(SR * sec))


def norm(x):
    m = np.max(np.abs(x))
    return x / m if m > 0 else x


# ---------- เสียงพื้นฐาน ----------
def chug_burst():
    t = T(.22)
    return norm(band(noise(.22), 150, 2200)) * np.exp(-t * 22) * np.minimum(t * 300, 1)


def whistle(sec=1.8, base=520):
    t = T(sec)
    vib = 1 + .006 * np.sin(2 * np.pi * 5.5 * t)
    env = np.minimum(t / .12, 1) * np.minimum((sec - t) / .5, 1)
    tone = sum(np.sin(2 * np.pi * base * r * vib * t) * g for r, g in [(1, 1), (1.26, .8), (1.5, .6), (2, .2)])
    breath = band(noise(sec), base * .9, base * 3.2) * .25
    return norm(tone + breath) * env


def boom(sec=2.5, lo=30):
    t = T(sec)
    sweep = np.sin(2 * np.pi * np.cumsum(70 * np.exp(-t * 2) + lo) / SR)
    rumble = norm(band(noise(sec), 20, 160))
    return norm(sweep * .8 + rumble) * np.exp(-t * 2.2) * np.minimum(t * 200, 1)


def explosion():
    t = T(3.5)
    debris = norm(band(noise(3.5), 300, 7000)) * np.exp(-t * 3.5) * .45
    crack = norm(band(noise(3.5), 800, 9000)) * np.exp(-t * 40) * .8
    return norm(boom(3.5, 28) + debris + crack)


def clink(pitch=1.0):
    t = T(.6)
    parts = [(2140, 1, 18), (3410, .6, 24), (5230, .35, 30), (7400, .2, 45)]
    tone = sum(np.sin(2 * np.pi * f * pitch * t) * g * np.exp(-t * d) for f, g, d in parts)
    click = band(noise(.6), 1500, 9000) * np.exp(-t * 160)
    thud = band(noise(.6), 60, 400) * np.exp(-t * 35) * 1.5
    return norm(tone + click * .7 + thud)


def ping():
    t = T(2.4)
    p = np.sin(2 * np.pi * 1180 * t) * np.exp(-t * 2.6) * np.minimum(t * 300, 1)
    out = p.copy()
    for d, g in [(.42, .35), (.84, .15)]:
        k = int(d * SR)
        out[k:] += p[:-k] * g
    return norm(out)


def pop(f=880):
    t = T(.18)
    return np.sin(2 * np.pi * (f + 900 * t) * t) * np.exp(-t * 28) * np.minimum(t * 600, 1)


def tick():
    t = T(.05)
    return norm(np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 120) + band(noise(.05), 2000, 8000) * np.exp(-t * 200))


def stamp():
    t = T(.8)
    return norm(band(noise(.8), 40, 500) * np.exp(-t * 14) * 1.6 + band(noise(.8), 800, 5000) * np.exp(-t * 60))


def whoosh(sec=1.0):
    t = T(sec)
    env = np.sin(np.pi * t / sec) ** 2
    lowp = band(noise(sec), 200, 1200)
    hip = band(noise(sec), 1200, 5000)
    mix = lowp * (1 - t / sec) + hip * (t / sec) * .6
    return norm(mix) * env


def heartbeat():
    t = T(.9)
    lub = np.sin(2 * np.pi * 52 * t) * np.exp(-t * 18)
    k = int(.24 * SR)
    dub = np.zeros_like(t)
    dub[k:] = np.sin(2 * np.pi * 46 * t[:-k]) * np.exp(-t[:-k] * 22) * .7
    return norm(lub + dub)


def bell(f, sec=3.0):
    t = T(sec)
    return (np.sin(2 * np.pi * f * t) + .45 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3)
            + .2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6)) * np.exp(-t * 1.6) * np.minimum(t * 500, 1)


def piano(f, sec=3.5):
    t = T(sec)
    h = sum(np.sin(2 * np.pi * f * n * t) * g * np.exp(-t * (1.2 + n)) for n, g in [(1, 1), (2, .45), (3, .2), (4, .1)])
    return h * np.minimum(t * 800, 1)


# ---------- บัสเสียง (สเตอริโอ) ----------
music = np.zeros((N, 2))
fx = np.zeros((N, 2))
amb = np.zeros((N, 2))


def put(bus, t0, sound, gain, pan=0.0):
    k = int(round(t0 * SR))
    if k >= N:
        return
    m = min(len(sound), N - k)
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[k:k + m, 0] += sound[:m] * gain * l * 1.41
    bus[k:k + m, 1] += sound[:m] * gain * r * 1.41


def bed(bus, t0, t1, sound_fn, gain, fade=1.0, pan=0.0):
    """เสียงบรรยากาศต่อเนื่องช่วง t0–t1 พร้อม fade เข้า/ออก"""
    sec = t1 - t0
    s = sound_fn(sec)
    t = T(sec)[: len(s)]
    env = np.minimum(t / fade, 1) * np.minimum((sec - t) / fade, 1)
    put(bus, t0, s * env, gain, pan)


def chug_bed(sec, rate=3.2, accel=0.0):
    out = np.zeros(int(SR * sec) + SR)
    b = chug_burst()
    t, i = 0.0, 0
    while t < sec:
        g = 1.0 if i % 4 == 0 else .55
        k = int(t * SR)
        out[k:k + len(b)] += b * g
        t += 1 / (rate + accel * t)
        i += 1
    return out[: int(SR * sec)]


def waves(sec):
    t = T(sec)
    swell = .35 + .65 * np.sin(np.pi * t / 5.5) ** 2
    return norm(band(noise(sec), 90, 1400)) * swell


def insects(sec):
    t = T(sec)
    chirp = norm(band(noise(sec), 4200, 6200)) * (.5 + .5 * np.sin(2 * np.pi * 34 * t)) ** 2
    pulse = .55 + .45 * np.sin(2 * np.pi * .23 * t)
    night = norm(band(noise(sec), 2400, 3000)) * (.5 + .5 * np.sin(2 * np.pi * 9 * t)) ** 3 * .5
    return (chirp * pulse + night)


def fire(sec):
    t = T(sec)
    roar = norm(band(noise(sec), 70, 450)) * (.7 + .3 * np.sin(2 * np.pi * .7 * t))
    crackle = np.zeros_like(t)
    for k in rng.integers(0, len(t) - 2000, int(sec * 14)):
        L = int(rng.integers(150, 900))
        crackle[k:k + L] += rng.normal(0, 1, L) * np.exp(-np.arange(L) / (L / 5)) * rng.uniform(.3, 1)
    return roar * .55 + band(crackle, 900, 7000) * 1.2


def plane(sec):
    t = T(sec)
    tone = sum(np.sign(np.sin(2 * np.pi * f * t)) * g for f, g in [(88, 1), (91.5, .8), (176, .3)])
    return norm(band(tone, 40, 900)) * np.minimum(t / sec, 1) ** 1.5


def mosquito(sec):
    t = T(sec)
    f = 560 + 40 * np.sin(2 * np.pi * 3 * t)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR))
    return norm(band(s, 400, 3000)) * np.sin(np.pi * t / sec)


# ---------- ดนตรี: แพดตึงเครียดในคีย์ C minor ----------

# ---------- เสียงเฉพาะตอนนี้ ----------
def quake(sec=2.6):
    """แผ่นดินไหว: เสียงครืนต่ำ + ของสั่นกระทบกัน"""
    t = T(sec)
    env = np.minimum(t / .25, 1) * np.exp(-np.maximum(t - .6, 0) * 1.6)
    rumble = norm(band(noise(sec), 18, 120)) * (1 + .4 * np.sin(2 * np.pi * 7 * t))
    rattle = norm(band(noise(sec), 900, 5000)) * (.5 + .5 * np.sign(np.sin(2 * np.pi * 13 * t))) * .25
    return norm(rumble + rattle) * env


def crack():
    t = T(.9)
    snap = norm(band(noise(.9), 1200, 9000)) * np.exp(-t * 30)
    groan = np.sin(2 * np.pi * (90 - 40 * t) * t) * np.exp(-t * 4) * .6
    return norm(snap + groan)


def crumble(sec=2.0):
    out = np.zeros(int(SR * sec) + SR)
    for j in range(26):
        k = int(rng.uniform(0, sec * .8) * SR)
        L = int(rng.uniform(.05, .25) * SR)
        n = norm(band(rng.normal(0, 1, L), 150, 3000))
        out[k:k + L] += n * np.exp(-np.arange(L) / (L / 4)) * rng.uniform(.3, 1)
    return norm(out[: int(SR * sec)] + band(noise(sec), 30, 200) * np.exp(-T(sec) * 2) * 2)


def siren(sec=3.0, f0=620, f1=920, rate=.9):
    t = T(sec)
    f = f0 + (f1 - f0) * (.5 + .5 * np.sin(2 * np.pi * rate * t))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    env = np.minimum(t / .2, 1) * np.minimum((sec - t) / .4, 1)
    return norm(s + .3 * np.sin(2 * np.pi * 2 * np.cumsum(f) / SR)) * env


def alarm_beeps(n=3):
    out = np.zeros(int(SR * (n * .5 + .3)))
    for j in range(n):
        t = T(.32)
        b = np.sign(np.sin(2 * np.pi * 1050 * t)) * .5 * np.minimum(t * 200, 1) * np.minimum((.32 - t) * 200, 1)
        k = int(j * .5 * SR)
        out[k:k + len(b)] += band(b, 300, 4000)
    return norm(out)


def engine(sec, f=48):
    t = T(sec)
    s = np.sign(np.sin(2 * np.pi * f * t)) + .5 * np.sign(np.sin(2 * np.pi * f * 2.01 * t))
    return norm(band(s, 30, 600)) * (.8 + .2 * np.sin(2 * np.pi * 3 * t))


def train(sec):
    t = T(sec)
    hum = norm(band(noise(sec), 200, 2400)) * .6 + np.sin(2 * np.pi * 110 * t) * .2
    clack = chug_bed(sec, 2.2) * .5
    return norm(hum + clack)


def brakes():
    t = T(1.4)
    f = 2400 - 600 * t
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) + band(noise(1.4), 2000, 6000) * .4) * np.exp(-t * 1.8)


def chime_up():
    out = np.zeros(int(SR * 2.2))
    for j, f in enumerate([523.25, 659.25, 783.99, 1046.5]):
        b = bell(f, 1.6)
        k = int(j * .12 * SR)
        out[k:k + len(b)] += b[: len(out) - k]
    return norm(out)


def clock_tick(sec):
    out = np.zeros(int(SR * sec) + SR)
    for j in range(int(sec)):
        tk = tick()
        k = int(j * SR)
        out[k:k + len(tk)] += tk * (1 if j % 2 else .7)
    return out[: int(SR * sec)]




# ---------- ดนตรี: แพดลึกลับในคีย์ D minor + โน้ตระนาดห้าเสียง ----------
CHORDS = [[73.42, 146.83, 174.61, 220.0], [58.27, 116.54, 146.83, 174.61],
          [65.41, 130.81, 164.81, 196.0], [55.0, 110.0, 138.59, 164.81]]  # Dm Bb C A
STEP = 4.0


def pad(chord, sec):
    t = T(sec)
    env = np.minimum(t / 1.2, 1) * np.minimum((sec - t) / 1.2, 1)
    s = sum(np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 1.004 * t + 1) for f in chord)
    return s * env * (.8 + .2 * np.sin(2 * np.pi * .25 * t))


def ranat(f, sec=1.2):
    """เสียงตีไม้คล้ายระนาด: สั้น ใส มีฮาร์มอนิกไม่ลงตัว"""
    t = T(sec)
    h = (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 3.93 * t) * np.exp(-t * 9)
         + .25 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t * 20))
    return h * np.exp(-t * 4.5) * np.minimum(t * 900, 1)


def drum_bed(sec, bpm=84, f=62.0):
    out = np.zeros(int(SR * sec) + SR)
    b = 60 / bpm
    k = 0
    while k * b < sec:
        t = T(.45)
        hit = np.sin(2 * np.pi * (f + 50 * np.exp(-t * 30)) * t) * np.exp(-t * 8)
        i = int(k * b * SR)
        out[i:i + len(hit)] += hit * (1 if k % 4 == 0 else .5 if k % 2 == 0 else .3)
        k += 1
    return out[: int(SR * sec)]


# ---------- ดนตรีผจญภัย: แพดเดิม + กลองจังหวะเร่ง + ระนาดห้าเสียง ----------
QUIET = [(start("scholar"), end("proof"))]
k = 0
while k * STEP < TOTAL:
    t0 = k * STEP
    g = .016 if any(a - 1 < t0 < b for a, b in QUIET) else .026
    put(music, t0, pad(CHORDS[k % 4], STEP + 1.5), g)
    k += 1
put(music, 0, np.sin(2 * np.pi * 36.7 * T(TOTAL)) * .5, .03)
for sid, bpm, gain in [("hook", 96, .07), ("heist", 104, .1), ("curse", 92, .08), ("prince", 100, .09)]:
    bed(music, start(sid), end(sid), lambda s, b=bpm: drum_bed(s, bpm=b), gain, fade=.6)
SCALE = [293.66, 349.23, 392.0, 440.0, 523.25, 587.33]  # D F G A C D ห้าเสียง
PATTERN = [0, 2, 3, 2, 4, 3, 1, 0, 5, 4, 3, 1]
for sid, gain, step in [("what", .035, .42), ("heist", .05, .3), ("curse", .04, .36), ("prince", .045, .32), ("proof", .035, .42)]:
    for i, t0 in enumerate(np.arange(start(sid) + .1, end(sid) - .2, step)):
        put(music, t0, ranat(SCALE[PATTERN[i % 12]]), gain, -.3 + .6 * (i % 2))

# ---------- เสียงเฉพาะตอนนี้ ----------
def rip(sec=.8):
    """แผ่นทองถูกฉีก: เสียงโลหะบางยับ + แตกร้าว"""
    t = T(sec)
    crinkle = np.zeros_like(t)
    for kk in rng.integers(0, len(t) - 800, 60):
        L = int(rng.integers(80, 500))
        crinkle[kk:kk + L] += rng.normal(0, 1, L) * np.exp(-np.arange(L) / (L / 4))
    metal = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in [(1830, 9), (2710, 12), (4150, 16)]) * .25
    return norm(band(crinkle, 1500, 9000) + metal) * np.minimum(t * 300, 1) * np.exp(-t * 2.5)


def shimmer(sec=1.6):
    out = np.zeros(int(SR * sec) + SR)
    for j, f in enumerate([1318.5, 1567.98, 1760.0, 2093.0, 2349.3, 2637.0]):
        b = bell(f, 1.2)
        kk = int(j * .09 * SR)
        out[kk:kk + len(b)] += b * (.8 - .08 * j)
    return norm(out[: int(SR * sec)] + band(noise(sec), 5000, 11000) * np.exp(-T(sec) * 2.5) * .3)


def dig(sec):
    """จอบเสียมกระทบอิฐ เป็นจังหวะ"""
    out = np.zeros(int(SR * sec) + SR)
    t, i = 0.0, 0
    while t < sec:
        tt = T(.3)
        hit = norm(band(noise(.3), 300, 3500)) * np.exp(-tt * 30) + np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 25) * .6
        kk = int(t * SR)
        out[kk:kk + len(hit)] += hit * (1 if i % 2 == 0 else .6)
        t += .62 + .08 * np.sin(i)
        i += 1
    return out[: int(SR * sec)]


def blowout():
    t = T(.5)
    return norm(band(noise(.5), 200, 2500)) * np.sin(np.pi * np.minimum(t / .5, 1)) ** 2 * np.exp(-t * 4)


def footsteps(sec, rate=6.0):
    out = np.zeros(int(SR * sec) + SR)
    j = 0
    while j / rate < sec:
        tt = T(.12)
        s = norm(band(noise(.12), 80, 1200)) * np.exp(-tt * 45)
        kk = int(j / rate * SR)
        out[kk:kk + len(s)] += s * (.6 + .4 * rng.uniform())
        j += 1
    return out[: int(SR * sec)]


def trumpet_elephant():
    """เสียงช้างร้อง (สังเคราะห์) สูงขึ้นแล้วสั่น"""
    t = T(1.4)
    f = 380 + 280 * np.minimum(t / .3, 1) + 25 * np.sin(2 * np.pi * 11 * t)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .6 + np.sin(2 * np.pi * np.cumsum(f) * 2 / SR) * .4
    return norm(band(s, 300, 4000)) * np.minimum(t / .08, 1) * np.exp(-np.maximum(t - .6, 0) * 4)


def whistle_police():
    t = T(1.0)
    f = 2900 + 260 * np.sign(np.sin(2 * np.pi * 26 * t))
    return norm(np.sin(2 * np.pi * np.cumsum(f) / SR) + band(noise(1.0), 2500, 4500) * .3) * np.minimum(t / .03, 1) * np.minimum((1 - t) / .1, 1)


def drip(f=420):
    t = T(.5)
    return np.sin(2 * np.pi * (f + 900 * np.exp(-t * 30)) * t) * np.exp(-t * 14)


def cuffs():
    return norm(clink(1.3) + np.roll(clink(1.6), int(.07 * SR)) * .7)


def fuse_hiss(sec):
    t = T(sec)
    return norm(band(noise(sec), 2500, 9000)) * (.7 + .3 * np.sin(2 * np.pi * 23 * t))


def coin_rain(n=8, gap=.11):
    out = np.zeros(int(SR * (n * gap + .7)))
    for j in range(n):
        c = clink(.9 + .08 * (j % 4))
        kk = int(j * gap * SR)
        out[kk:kk + len(c)] += c[: len(out) - kk] * (.6 + .4 * rng.uniform())
    return norm(out)


def gong(f=98.0, sec=4.0):
    t = T(sec)
    return norm(sum(np.sin(2 * np.pi * f * r * t) * g * np.exp(-t * d) for r, g, d in [(1, 1, .9), (2.01, .5, 1.4), (2.76, .35, 2.2), (5.1, .15, 4)])) * np.minimum(t * 300, 1)


def crowd(sec):
    t = T(sec)
    return norm(band(noise(sec), 180, 900)) * (.6 + .4 * np.sin(2 * np.pi * 1.7 * t) ** 2)


# hook: เสียงเตือนจากใต้ดิน
put(fx, 0, boom(2.2, 34), .35)
put(fx, .1, shimmer(), .2)
bed(amb, 0, at("hook", 2), insects, .05, fade=.4)
put(fx, at("hook", 1) - .1, whoosh(.8), .18)
put(fx, at("hook", 1) + .6, crack(), .3, -.3)
put(fx, at("hook", 2) + .2, coin_rain(5), .16)
put(fx, at("hook", 3) - .3, heartbeat(), .3)
put(fx, at("hook", 3), gong(73.4), .3)
# what: ถ้ำ เงา เสียงหยด
bed(amb, start("what"), end("what"), insects, .07, fade=.5)
put(fx, at("what", 0) - .1, whoosh(.8), .15)
for j in range(3):
    put(fx, at("what", 1) + .3 + j * 1.1, drip(380 + 60 * j), .14, -.4 + .4 * j)
put(fx, at("what", 2), bell(110.0, 4), .16)
put(fx, at("what", 2) + .4, heartbeat(), .25)
# heist: ขุดกรุ
put(fx, at("heist", 0) - .1, whoosh(1.0), .18)
bed(fx, at("heist", 1), at("heist", 4), dig, .3, fade=.2)
bed(fx, at("heist", 1) - .2, at("heist", 2), lambda s: footsteps(s, 5.0), .18, fade=.2)
put(fx, at("heist", 3) + .2, stamp(), .25)
put(fx, at("heist", 4) - .1, shimmer(), .25)
put(fx, at("heist", 4), coin_rain(8), .2)
put(fx, at("heist", 5), whoosh(.9), .15)
put(fx, at("heist", 5) + .5, pop(520), .18, .3)
# curse: คำสาป
put(fx, at("curse", 0) - .1, boom(1.6, 40), .25)
put(fx, at("curse", 1), shimmer(), .3)
put(fx, at("curse", 1) + .3, bell(293.66, 3), .12)
put(fx, at("curse", 2) - .2, heartbeat(), .3)
put(fx, at("curse", 2) + .8, heartbeat(), .25)
put(fx, at("curse", 3), crack(), .3, .2)
put(fx, at("curse", 3) + .3, crumble(1.4), .2)
# prince: วัดกุฎีดาว กลางคืน
bed(amb, start("prince"), end("prince"), insects, .06, fade=.5)
put(fx, at("prince", 0), stamp(), .25)
bed(fx, at("prince", 1), at("prince", 2), dig, .22, fade=.2)
put(fx, at("prince", 2) - .1, boom(1.8, 36), .35)
put(fx, at("prince", 2), gong(65.4), .3)
put(fx, at("prince", 2) + .3, quake(1.8), .2)
put(fx, at("prince", 3) - .1, heartbeat(), .28)
put(fx, at("prince", 3) + .9, cuffs(), .12)
put(fx, at("prince", 4), bell(110.0, 4), .15)
# scholar: ตรวจหลักฐาน
put(fx, at("scholar", 1) - .1, pop(760), .2)
put(fx, at("scholar", 2) - .1, pop(660), .2, .3)
put(fx, at("scholar", 3) - .1, stamp(), .4)
# proof
put(fx, at("proof", 1) - .1, pop(880), .2)
put(fx, at("proof", 1) + 1.5, clink(1.1), .15)
put(fx, at("proof", 2) - .1, stamp(), .45)
put(fx, at("proof", 3), bell(98.0, 3), .12)
# ask
put(fx, at("ask", 0), bell(110.0, 3), .12)
put(fx, at("ask", 2) - .1, pop(880), .22, -.3)
put(fx, at("ask", 3) - .1, pop(660), .22, .3)
put(fx, at("ask", 4), chime_up(), .1)
# end
for j, f in enumerate([523.25, 659.25, 783.99, 1046.5]):
    put(fx, start("end") + .2 + j * .16, bell(f, 2.5), .07)
put(fx, TOTAL - 1.4, whoosh(1.2), .2)

# ห้องเสียงเล็กน้อยให้ fx กลมกลืน
ir = rng.normal(0, 1, int(SR * 1.4)) * np.exp(-T(1.4) * 4.5)
ir /= np.sqrt(np.sum(ir ** 2))
for c in range(2):
    L = N + len(ir)
    wet = np.fft.irfft(np.fft.rfft(fx[:, c], L) * np.fft.rfft(ir, L), L)[:N]
    fx[:, c] += wet * .18

# ---------- มิกซ์ ----------
with wave.open(str(ROOT / "narration.wav")) as w:
    speech = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").astype(np.float64) / 32767
speech = np.pad(speech, (0, max(0, N - len(speech))))[:N]
env = np.convolve(np.abs(speech), np.ones(SR // 8) / (SR // 8), mode="same")
duck = 1 - .5 * np.clip(env / .05, 0, 1)
t = np.arange(N) / SR
fade = np.minimum(t / .4, 1) * np.minimum((TOTAL - t) / 1.5, 1)
FX_LEVEL, AMB_LEVEL = .85, .8  # ระดับเอฟเฟกต์/บรรยากาศเทียบเสียงพากย์
# ใต้เสียงพากย์ เอฟเฟกต์ถูกกดลงอีกเล็กน้อย
under = (1 - .25 * np.clip(env / .05, 0, 1))[:, None]
mix = (music * duck[:, None] + amb * AMB_LEVEL * under + fx * FX_LEVEL * under + speech[:, None] * .95) * fade[:, None]
peak = np.max(np.abs(mix))
if peak > .97:
    mix *= .97 / peak
with wave.open(str(ROOT / "soundtrack.wav"), "wb") as w:
    w.setparams((2, 2, SR, 0, "NONE", "not compressed"))
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("soundtrack ready", TOTAL, "s, peak", round(peak, 3))
