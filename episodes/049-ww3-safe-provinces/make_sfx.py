"""SFX + เพลงพื้นหลัง EP.049 (What if WW3 5 จังหวัด) ด้วย numpy
  python make_sfx.py  ->  video/audio/sfx.wav, video/audio/music.wav (mono 48kHz)
เวลาเหตุการณ์: ถ้ามี video/timing_gm.json (หลังสร้างเสียงพากย์) จะอิงตามนั้น
ไม่มีก็ใช้เวลาตามบท (script.md) เป็นค่าเริ่มต้น ~52 วินาที"""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUTDIR = HERE / "video" / "audio"
OUTDIR.mkdir(parents=True, exist_ok=True)
SR = 48000

# ต้นฉบับ: เวลาเริ่มของ 5 ฉาก (ฮุก, สาเหตุ, ผลต่อไทย, ฝุ่น, CTA) และความยาวรวม
SC = [0.0, 6.0, 17.0, 35.0, 45.0]
TOTAL = 52.0
tf = HERE / "video" / "timing_gm.json"
if tf.exists():
    tm = json.loads(tf.read_text(encoding="utf-8"))
    TOTAL = tm["total"]
    L = tm["lines"]
    SC = [0.0] + [L[i]["start"] - 0.2 for i in range(1, 5)]

rng = np.random.default_rng(49)
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


def norm(x, g=1.0):
    return x / (np.abs(x).max() + 1e-9) * g


def boom():  # แรงกระแทกตอนขึ้น WHAT IF: ซับต่ำ + แคร็กสูง + หางก้อง
    n = int(SR * 1.6); t = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(32 + 90 * np.exp(-t * 14)) / SR) * np.exp(-t * 2.6)
    crack = lowpass(rng.standard_normal(n), 5000) * np.exp(-t * 55) * 0.9
    rumble = lowpass(rng.standard_normal(n), 180) * np.exp(-t * 2.2) * 1.2
    return norm(sub * 1.2 + crack + rumble, 1.0)


def riser(dur, f0=90, f1=1800, noise=0.5):  # ไรเซอร์: โทนไต่ขึ้น + ลมร้อนไล่สว่าง
    n = int(SR * dur); t = np.arange(n) / SR
    u = (t / dur) ** 2.2
    f = f0 + (f1 - f0) * u
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    z = rng.standard_normal(n)
    air = (lowpass(z, 7000) - lowpass(z, 1200)) * (0.2 + u)
    return norm((tone * 0.5 * u + air * noise) * np.minimum(1, t / 0.3), 0.8)


def whoosh(dur=0.9, up=True):
    n = int(SR * dur)
    x = rng.standard_normal(n)
    lo, hi = lowpass(x, 500), lowpass(x, 3500)
    t = np.linspace(0, 1, n)
    sweep = np.sin(np.pi * t) ** 1.5
    y = lo * (1 - sweep) + hi * sweep
    return norm(y, 1.0) * np.sin(np.pi * t) ** 1.2 * 0.6


def tick(f=1800):
    n = int(SR * 0.05); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t * 90) * 0.5


def pop(f0=420, f1=900, dur=0.14):
    n = int(SR * dur); t = np.arange(n) / SR
    f = f0 + (f1 - f0) * np.minimum(t / dur * 2, 1)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, dur * 0.7) * 0.7


def thud():
    n = int(SR * 0.45); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * np.cumsum(45 + 80 * np.exp(-t * 18)) / SR) * np.exp(-t * 7)
    click = lowpass(rng.standard_normal(n), 2500) * np.exp(-t * 60) * 0.6
    return (body + click) * 0.9


def ding(f=1320, dur=0.9):
    n = int(SR * dur); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t)) * np.exp(-t * 5) * 0.5


def crack():  # ดินแตก: แคร็กแห้งสั้นๆ ถี่ไม่เท่ากัน
    n = int(SR * 0.14); t = np.arange(n) / SR
    z = rng.standard_normal(n)
    return (z - lowpass(z, 1500)) * np.exp(-t * 55) * 0.8


def siren(dur=1.6):  # เตือนภัยฝุ่น
    n = int(SR * dur); t = np.arange(n) / SR
    f = 700 + 180 * np.sin(2 * np.pi * 0.9 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.05, 0.4) * 0.45


def thermo(dur=2.4, f0=300, f1=2200):  # เทอร์โมมิเตอร์พุ่ง: ไถลขึ้นแบบวิทยาศาสตร์
    n = int(SR * dur); t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (t / dur) ** 1.6
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.02, 0.15) * 0.45


def hush(dur=2.0):  # ลมหายใจ/หมอกฝุ่นเลื่อนเข้า
    n = int(SR * dur); t = np.arange(n) / SR
    z = rng.standard_normal(n)
    return norm(lowpass(z, 1800) - lowpass(z, 300), 0.6) * np.sin(np.pi * t / dur) ** 1.4


# ===== ฉาก 0: ฮุก What if (0-6 วิ) =====
put(0.08, boom(), 1.0)                      # WHAT IF? กระแทก
put(0.9, whoosh(0.8), 0.55)
put(1.0, riser(SC[1] - 1.4, 80, 1500), 0.8)
SY = json.loads((HERE / "video" / "sync.json").read_text(encoding="utf-8"))
K = SY["SYNC"]
ck = lambda li, ci: K[li][min(ci, len(K[li]) - 1)][0]
for k, (t0_, t1_) in enumerate(SY["MT"]):  # ขีปนาวุธพุ่ง + ระเบิดตอนตก
    put(t0_, whoosh(0.8), 0.3)
    put(t1_, boom(), 0.32 + 0.1 * (k % 3)); put(t1_, crack(), 0.5)
put(ck(0, 1), boom(), 0.5)                  # ป้าย สงครามโลกครั้งที่ 3
put(ck(0, 3), pop(400, 1200, 0.2), 0.7)     # 5 จังหวัด เด้ง
put(ck(0, 4), thud(), 1.0); put(ck(0, 4), ding(660, 0.9), 0.5)   # ตราประทับ
put(SC[1] - 0.05, whoosh(0.8), 0.6)

# ===== ฉาก 1-4 =====
for st in SY["STANDS"]:                     # ป้ายตั้งบนแผนที่หล่นลง
    for w in st["show"]:
        if w[1] < TOTAL:
            put(w[1] - 0.05, whoosh(0.35), 0.35); put(w[1] + 0.32, thud(), 0.75)
for i in (1, 2, 3, 4):
    put(SC[i] - 0.15, whoosh(1.0), 0.6)     # กล้องเคลื่อน
    for k in range(len(K[i])):
        tt_ = max(ck(i, k), SC[i] + 0.35)
        put(tt_, pop(460 + 70 * k, 980 + 70 * k, 0.14), 0.5)
put(SC[1] + 0.3, hush(2.0), 0.4)
# ฉาก 1: โซนเสี่ยงสีแดง -> น้ำ+อาหารเขียว
for c in (1, 2, 3):
    put(ck(1, c), siren(0.7), 0.3); put(ck(1, c), boom(), 0.4)
put(ck(1, 4), ding(1046, 1.2), 0.6); put(ck(1, 4) + 0.12, ding(1318, 1.2), 0.45)
# ฉาก 2-3: จุดเขียวปลอดภัย: ระฆังไต่ขึ้นทีละจังหวัด
for n_, t_ in enumerate([ck(2, 1), ck(2, 3), ck(2, 5), ck(3, 1), ck(3, 3)]):
    put(t_ + 0.05, ding(784 * (1.122 ** n_), 1.3), 0.6)
put(ck(3, 5), boom(), 0.5)
# ฉาก 4: ของแพง -> 5 จังหวัด -> คอมเมนต์
put(ck(4, 1), riser(1.2, 200, 1200, 0.6), 0.6)
put(ck(4, 3), ding(1046, 1.4), 0.7); put(ck(4, 3) + 0.15, ding(1318, 1.4), 0.5)
for c in range(8):
    put(ck(4, 4) + 0.3 + c * 0.14, pop(700 + c * 60, 1100 + c * 60, 0.1), 0.5)

# เงียบ 0.3 วิ หลังฮุกก่อนเข้าฉาก 2
a, b = int((SC[1] - 0.35) * SR), int((SC[1] - 0.05) * SR)
out[a:b] *= np.linspace(1, 0, b - a) ** 2

out = out[: int(SR * TOTAL)]
out = norm(out, 0.7)
n = len(out); t = np.arange(n) / SR

# เตียงลมร้อนบางๆ ตลอดคลิป (หยุดฮุกวินาทีแรก)
z = rng.standard_normal(n)
bed = lowpass(z, 5000) - lowpass(z, 800)
bed *= 0.5 + 0.3 * np.sin(2 * np.pi * 0.27 * t)
bed *= np.clip((t - 0.9) / 1.0, 0, 1)
out = norm(out + norm(bed, 0.16), 0.75)


def save(name, x):
    with wave.open(str(OUTDIR / name), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((x * 32767).astype("<i2").tobytes())


save("sfx.wav", out)

# เพลง: แพดมืดไต่ความตึงตามความร้อน แล้วคลายตอนปิด
pad = sum(np.sin(2 * np.pi * f * t + p) * a_ for f, p, a_ in [(55, 0, 0.5), (73.4, 1.1, 0.35), (110, 2.0, 0.3), (146.8, 0.4, 0.2)])
pad *= 0.65 + 0.35 * np.sin(2 * np.pi * 0.12 * t)
heat = np.clip(t / SC[3], 0, 1) * (1 - np.clip((t - SC[4]) / 2.0, 0, 1))
pad += heat * (np.sin(2 * np.pi * 233.1 * t) * 0.18 + np.sin(2 * np.pi * 277.2 * t) * 0.14 + np.sin(2 * np.pi * 349.2 * t) * 0.1)
pad += np.clip((t - SC[4]) / 2.5, 0, 1) * (np.sin(2 * np.pi * 261.6 * t) * 0.15 + np.sin(2 * np.pi * 329.6 * t) * 0.12)
pad *= np.minimum(1, t / 1.0) * np.minimum(1, (TOTAL - t) / 2.0)
pad *= np.where((t > SC[1] - 0.35) & (t < SC[1] - 0.05), 0.0, 1.0)
save("music.wav", norm(pad, 0.5))
print("sfx + music", round(TOTAL, 2), "s, peak", round(float(np.abs(out).max()), 2))
