"""สร้างเสียงเอฟเฟกต์ (SFX) ของตอน 040 (ฟ้าฝ่า) ด้วย numpy ให้ตรงจังหวะกับ timeline ใน template.html
ผลลัพธ์: video/audio_gm/sfx.wav (mono 48kHz ความยาวเท่า timing_gm.json)
  python make_sfx.py
เวลาของเหตุการณ์คำนวณจาก timing_gm.json แบบเดียวกับ build.py (ฉากเริ่ม = เริ่มบรรทัดเสียง - 0.2 วินาที)"""
import json, sys, wave
from pathlib import Path
import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
SR = 48000
timing = json.loads((HERE / "video" / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL = timing["total"]
L = timing["lines"]
NEW = [0.0] + [round(L[i]["start"] - 0.2, 2) for i in range(1, 7)] + [TOTAL]
OLD = [0, 5, 15, 25, 33, 41, 50, 56]


def M(t):  # เวลาตามตารางเดิมใน script.md -> เวลาตามเสียงพากย์จริง (เหมือน build.py)
    for i in range(7):
        if t <= OLD[i + 1] or i == 6:
            return NEW[i] + (t - OLD[i]) * (NEW[i + 1] - NEW[i]) / (OLD[i + 1] - OLD[i])


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


def crack(dur=2.2):  # ฟ้าผ่าใกล้: สแนปแหลม + ตูมต่ำ + ซับ + ก้อง อัดจนหนัก (soft clip)
    n = int(SR * dur); t = np.arange(n) / SR
    snap = rng.standard_normal(n) * np.exp(-t * 70)
    crackle = rng.standard_normal(n) * (rng.random(n) > 0.985) * np.exp(-t * 6) * 3
    boom = lowpass(rng.standard_normal(n), 260) * np.exp(-t * 2.2) * 3.0
    sub = np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-t * 9)) / SR) * np.exp(-t * 2.6) * 1.6
    y = (snap * 1.3 + crackle + boom + sub) * env(n, 0.0005, 0.5)
    return np.tanh(y * 1.6) * 0.95


def rumble(dur=3.0):  # ฟ้าร้องไกลๆ
    n = int(SR * dur); t = np.arange(n) / SR
    return lowpass(rng.standard_normal(n), 140) * 3.2 * np.sin(np.pi * t / dur) ** 1.5 * (1 + 0.4 * np.sin(2 * np.pi * 3.1 * t))


def zap(dur=0.45):  # ไฟฟ้าช็อต
    n = int(SR * dur); t = np.arange(n) / SR
    x = rng.standard_normal(n) * (np.sin(2 * np.pi * 70 * t) > 0)
    return lowpass(x, 5000) * np.exp(-t * 6) * 0.8


def buzzer(dur=0.5):
    n = int(SR * dur); t = np.arange(n) / SR
    return np.sign(np.sin(2 * np.pi * 110 * t)) * 0.35 * env(n, 0.005, 0.05)


def ringing(dur=1.6):  # หูอื้อหลังฟ้าผ่า
    n = int(SR * dur); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 6200 * t) * 0.25 * np.exp(-t * 1.6) * env(n, 0.05, 0.3)


def slam():
    return thud() * 0.9 + lowpass(rng.standard_normal(int(SR * 0.45)), 1800) * np.exp(-np.arange(int(SR * 0.45)) / SR * 40) * 0.5


def phone():
    y = np.zeros(int(SR * 2.4))
    for k in range(3):
        n = int(SR * 0.4); t = np.arange(n) / SR
        o = int(k * 0.8 * SR)
        y[o:o + n] += (np.sin(2 * np.pi * 480 * t) + np.sin(2 * np.pi * 620 * t)) * 0.3 * env(n, 0.01, 0.05)
    return y


def heartbeat(beats=6, gap=0.55):
    y = np.zeros(int(SR * (beats * gap + 0.4)))
    for k in range(beats):
        for j, d in enumerate((0.0, 0.18)):
            n = int(SR * 0.16); t = np.arange(n) / SR
            o = int((k * gap + d) * SR)
            y[o:o + n] += np.sin(2 * np.pi * 55 * t) * np.exp(-t * 20) * (1.0 if j == 0 else 0.6)
    return y


# --- ซีน 1: ฮุกแบบ Ep39 -- กระแทกตั้งแต่เฟรมแรก แล้วเรียงชั้นเสียงถึงวินาทีที่ 5 ---
put(0.0, crack(2.4), 1.0)                    # ฟ้าผ่าแรก ตูมทันที
put(0.0, zap(0.6), 0.9)
put(M(0.15), thud(), 1.0); put(M(0.65), thud(), 0.9)   # ตัวหนังสือตบจอ 2 ครั้ง
put(M(0.3), rumble(3.4), 0.7)                    # ฟ้าร้องก้องต่อ
put(M(1.3), crack(1.4), 0.7); put(M(1.3), zap(0.4), 0.7)   # ฟ้าแลบซ้ำ
put(M(1.4), whoosh(1.6), 0.8)                    # ซูมเข้ากรุงเทพ
put(M(2.4), rumble(2.4), 0.55)
put(M(3.3), crack(1.4), 0.8); put(M(3.3), zap(0.5), 0.8)
put(M(3.8), whoosh(1.0), 0.7)
put(M(4.7), crack(2.6), 1.0)                  # ฟ้าผ่าห่าง 10 เมตร (ใหญ่สุด)
put(M(4.7), zap(0.7), 1.0)
put(M(4.7) + 0.5, ringing(), 0.6)             # หูอื้อ
# --- ซีน 2: ตัวเลข + กระแสวิ่งตามพื้น ---
put(M(5.0), swish(), 0.7); put(M(5.3), pop(300, 700, 0.18), 0.8)
put(M(6.0), crack(1.0), 0.8)
put(M(7.5), zap(0.6), 0.7); put(M(8.2), zap(0.5), 0.6); put(M(9.0), zap(0.5), 0.5)
put(M(11.0), tick(), 0.8)
# --- ซีน 3: เข้าที่กำบัง ---
put(M(15.0) - 0.1, whoosh(1.2), 0.8)
put(M(16.0), rumble(2.6), 0.4)
put(M(17.0), slam(), 0.9)                    # ปิดประตูรถ
put(M(18.0), ding(), 0.8)                    # หมุดเขียว
put(M(20.0), crack(1.0), 0.6); put(M(20.0), zap(0.5), 0.8)
# --- ซีน 4: ต้นไม้ ---
put(M(25.0) - 0.1, whoosh(1.0), 0.8)
put(M(27.0), crack(1.4), 0.9); put(M(27.3), zap(0.5), 0.9)
put(M(28.4), buzzer(), 0.8)
# --- ซีน 5: ย่อ ห้ามนอน ---
put(M(33.0) - 0.1, whoosh(1.0), 0.8)
put(M(35.2), ding(), 0.8)
put(M(38.6), buzzer(), 0.8); put(M(38.0), zap(0.6), 0.6)
# --- ซีน 6: ช่วยคน ---
put(M(41.0) - 0.1, whoosh(1.2), 0.8)
put(M(44.0), phone(), 0.7)
put(M(46.5), heartbeat(6), 0.9)
# --- ซีน 7: ปิด ---
put(M(50.0) - 0.1, whoosh(1.2), 0.7)
put(M(52.5), ding(), 0.8)
put(M(53.5), rumble(2.4), 0.3)

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
