"""SFX + เพลงพื้นหลังของตอน 035 ด้วย numpy ให้ตรงจังหวะกับ timeline ใน template.html
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
SC = [0.0] + [L[i]["start"] - 0.2 for i in range(1, len(L))]
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



def rise(dur=0.6, f0=300, f1=900):  # แท่งยืด: โทนไต่ขึ้น
    n = int(SR * dur); tt = np.arange(n) / SR
    f = f0 + (f1 - f0) * (tt / dur) ** 1.5
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.02, 0.25) * 0.5


def stamp():  # ตราประทับวีโต้: ตุ้บหนัก + แตกกรอบ
    n = int(SR * 0.6); tt = np.arange(n) / SR
    body = np.sin(2 * np.pi * np.cumsum(70 + 160 * np.exp(-tt * 25)) / SR) * np.exp(-tt * 6)
    crack = rng.standard_normal(n) * np.exp(-tt * 55) * 0.9
    return (body + crack) * 0.95


def ping(f=1250, dur=1.1):  # เรดาร์: ปิงพร้อมเสียงสะท้อน
    n = int(SR * dur); tt = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 7)
    echo = np.zeros(n)
    k = int(0.28 * SR)
    echo[k:] = y[:n - k] * 0.45
    return (y + echo) * 0.5


def buzz(dur=0.45):  # ผิดพลาด/ไม่จบ: บัซเซอร์ต่ำ
    n = int(SR * dur); tt = np.arange(n) / SR
    y = np.sign(np.sin(2 * np.pi * 110 * tt)) * 0.35 + np.sin(2 * np.pi * 165 * tt) * 0.2
    return y * env(n, 0.01, 0.15)


def chime():  # สำเร็จ: สองโน้ตไต่ขึ้น
    a, b = ding(), ding()
    y = np.zeros(int(SR * 1.3))
    y[:len(a)] += a * 0.7
    k = int(0.14 * SR)
    y[k:k + len(b)] += np.roll(b, 0) * 0.9
    return y


def zap(dur=0.5):  # ฟ้าผ่า: ซ่าไฮสูง + แตกกรอบ
    n = int(SR * dur); tt = np.arange(n) / SR
    hi = (rng.standard_normal(n) - lowpass(rng.standard_normal(n), 3000)) * np.exp(-tt * 9)
    crack = rng.standard_normal(n) * np.exp(-tt * 70) * 1.2
    buzz_ = np.sin(2 * np.pi * 180 * tt) * np.exp(-tt * 14) * 0.6
    y = hi + crack + buzz_
    return y / (np.abs(y).max() + 1e-9) * 0.9


def riser(dur=0.85):  # ไต่เสียงก่อนฟ้าผ่า
    n = int(SR * dur); tt = np.arange(n) / SR
    f = 120 + 1900 * (tt / dur) ** 2.2
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + lowpass(rng.standard_normal(n), 2500) * (tt / dur) * 0.5
    return y * env(n, 0.02, 0.02)


def boom(dur=2.6):  # ตูม: ต่ำกระแทก + กังวานท้าย
    n = int(SR * dur); tt = np.arange(n) / SR
    low = np.sin(2 * np.pi * np.cumsum(38 + 90 * np.exp(-tt * 9)) / SR) * np.exp(-tt * 1.8)
    noise = lowpass(rng.standard_normal(n), 1400) * np.exp(-tt * 3.2)
    crack = rng.standard_normal(n) * np.exp(-tt * 55) * 0.8
    rumble = lowpass(rng.standard_normal(n), 120) * np.exp(-tt * 1.1) * 1.4
    y = low + noise * 0.8 + crack + rumble
    return y / (np.abs(y).max() + 1e-9)


# ---- ฮุก: จอ CRT เปิด + แผนที่สแกน + พิมพ์ล็อก + มัลแวร์กลิตช์ ----
def datachirp(dur=0.5, base=900):  # ข้อมูลบิ๊บถี่ๆ แบบโมเด็ม/สแกน
    n = int(SR * dur)
    y = np.zeros(n)
    k = 0
    while k < n:
        L = int(SR * rng.uniform(0.012, 0.04))
        f = base * rng.choice([0.5, 0.75, 1, 1.5, 2, 3])
        tt = np.arange(min(L, n - k)) / SR
        y[k:k + len(tt)] += np.sign(np.sin(2 * np.pi * f * tt)) * 0.25 * np.hanning(len(tt))
        k += L + int(SR * rng.uniform(0.0, 0.02))
    return y


def keyclack(n_keys=8, span=0.8):  # พิมพ์คีย์บอร์ดกลไก
    y = np.zeros(int(SR * (span + 0.1)))
    for _ in range(n_keys):
        o = int(rng.uniform(0, span) * SR)
        n = int(SR * 0.03)
        y[o:o + n] += lowpass(rng.standard_normal(n), 5000) * np.exp(-np.arange(n) / SR * 150) * 0.7
    return y


def glitchhit(dur=0.35):  # กลิตช์: นอยส์ขาดๆ
    n = int(SR * dur)
    y = np.zeros(n)
    k = 0
    while k < n:
        L = int(SR * rng.uniform(0.01, 0.05))
        seg = rng.standard_normal(min(L, n - k)) * rng.choice([0.2, 0.7])
        y[k:k + len(seg)] += seg
        k += L
    return y / (np.abs(y).max() + 1e-9) * np.exp(-np.arange(n) / SR * 5) * 0.8


def alarm_lo(dur=0.9):  # เตือนมัลแวร์: โทนต่ำสองจังหวะ
    n = int(SR * dur); tt = np.arange(n) / SR
    f = np.where((tt * 4) % 1 < 0.5, 220, 165)
    return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 * env(n, 0.01, 0.2)


def degauss():  # จอ CRT เปิด: ตุ้บ + ฮัมไต่ลง
    n = int(SR * 0.9); tt = np.arange(n) / SR
    hum = np.sin(2 * np.pi * np.cumsum(240 * np.exp(-tt * 3) + 60) / SR) * np.exp(-tt * 3.5)
    thump = np.sin(2 * np.pi * np.cumsum(60 + 120 * np.exp(-tt * 40)) / SR) * np.exp(-tt * 12) * 1.2
    return (hum * 0.7 + thump) * 0.9


put(0.02, degauss(), 1.0)
put(0.1, datachirp(1.1, 700), 0.5)                          # กวาดสแกนแผนที่ทีละแถว
for r in range(10):
    put(0.12 + r * 0.11, tick(), 0.35)
for tt_ in (1.25, 1.85, 2.55):                              # หมุดโผล่บนแผนที่
    put(tt_, ping(1100, 0.6), 0.5)
for tt_ in (0.65, 1.3, 1.95, 2.6):                          # พิมพ์ล็อกทีละบรรทัด
    put(tt_ - 0.02, keyclack(18, 0.45), 0.8)
    put(tt_ + 0.5, tick(), 0.5)
put(1.3, datachirp(0.6, 1200), 0.4)
put(1.95, datachirp(0.6, 900), 0.4)
put(2.6, buzz(0.35), 0.55)
put(3.3, glitchhit(0.5), 1.0)                               # MALWARE โผล่
put(3.3, thud(), 1.0)
put(3.35, alarm_lo(1.2), 0.7)
for g in (3.55, 3.78, 4.02, 4.2):
    put(g, glitchhit(0.12), 0.8)
put(4.5, whoosh(0.6), 0.5)
ITEMS = json.loads((HERE / "video" / "items.json").read_text())
NS = len(L)
for i in range(1, NS):
    put(SC[i] - 0.1, whoosh(0.7), 0.5)
    put(SC[i] + 0.02, tick(), 0.4)
    for k in range(ITEMS[str(i)]):
        put(SC[i] + 0.4 + 0.2 * k + 0.1, plop() if k % 2 == 0 else pop(500, 900, 0.12), 0.7)
put(at(NS - 1, 0.72), ding(), 0.9)

# ---- เสียงเฉพาะฉากของตอน 035 ----
put(SC[1] + 0.2, ping(900, 0.9), 0.5)                      # หมุดฝรั่งเศส
put(SC[1] + 1.0, buzz(0.5), 0.5)                           # ตู้เย็นถูกแฮก
put(SC[2] + 0.6, rise(0.8, 200, 900), 0.5)                 # อุณหภูมิพุ่ง
put(SC[2] + 2.4, chime(), 0.5)                             # จับได้ทัน
put(SC[3] + 0.2, ping(1250, 1.1), 0.6)                     # อิหร่าน
for c in range(18):                                        # นับ 60+
    put(SC[3] + 0.4 + c * 0.06, tick(), 0.4 + 0.01 * c)
put(SC[4] + 0.5, ping(900, 1.0), 0.5)                      # ไทย
put(SC[4] + 1.5, chime(), 0.5)
put(SC[5] + 0.3, powerdown(1.4), 0.8)                      # ไฟดับ
put(SC[5] + 1.6, buzz(0.5), 0.5)
put(SC[6] + 0.4, siren(1.6), 0.35)                         # สัญญาณหาย
put(SC[7] + 0.4, powerdown(1.2), 0.6)
put(SC[7] + 1.6, buzz(0.6), 0.5)
put(SC[8] + 0.3, chime(), 0.5)
put(SC[9] + 0.3, chime(), 0.5)


# LOGSFX: ทุกฉาก พิมพ์ล็อก + ข้อมูลรัว + กลิตช์ตอนเปลี่ยนฉาก
LOGN = {1: 3, 2: 4, 3: 3, 4: 2, 5: 3, 6: 2, 7: 2, 8: 2, 9: 2, 10: 2}
for i_, n_ in LOGN.items():
    put(SC[i_] - 0.02, glitchhit(0.12), 0.6)
    put(SC[i_] + 0.1, glitchhit(0.1), 0.4)
    put(SC[i_] + 0.25, datachirp(0.3, 900), 0.4)
    for k_ in range(n_):
        put(SC[i_] + 0.5 + k_ * 0.55 - 0.02, keyclack(14, 0.4), 0.7)
        put(SC[i_] + 0.5 + k_ * 0.55 + 0.45, tick(), 0.45)

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
bright = np.clip((t - SC[9]) / 3.0, 0, 1)
pad += bright * (np.sin(2 * np.pi * 220 * t) * 0.15 + np.sin(2 * np.pi * 277.2 * t) * 0.1 + np.sin(2 * np.pi * 329.6 * t) * 0.1)
pad *= np.minimum(1, t / 1.5) * np.minimum(1, (TOTAL - t) / 2.0)
save("music.wav", pad / np.abs(pad).max() * 0.5)
print("sfx + music", round(TOTAL, 2), "s")
