"""ซาวด์หลอน + SFX ตกใจกลางเรื่อง (สังเคราะห์เองทั้งหมด) -> soundtrack.wav + sfx/*.wav

ถ้ามี timing.json (หลังทำเสียงพากย์ด้วย make_voice_gemini.py) จะวางเสียงตามเวลาจริงของแต่ละซีน
ถ้ายังไม่มี ใช้เวลาประมาณจาก script.md แทน — รันซ้ำหลังมีเสียงพากย์เพื่อให้ตรงจังหวะ
  python tools/make_sound.py
"""

import json
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
# --safe: ไม่ใช้เสียงโทนดนตรี (ระฆัง/ชิม/drone/จิ้งหรีด/เสียงอื้อ) ให้เหลือเฉพาะเสียงลม-noise-เอฟเฟกต์ เพื่อลดโอกาสโดนระบบลิขสิทธิ์จับผิด
SAFE = "--safe" in sys.argv
SR = 48000
rng = np.random.default_rng(2030)

# เวลาเริ่มซีน (วินาที) ตาม script.md ใช้เมื่อยังไม่มี timing.json
DEFAULT = {"hook": 0, "rule": 10, "bet": 28, "enter": 48, "flag": 65, "steps": 85,
           "loop": 105, "whisper": 123, "sorry": 132, "wake": 140, "end": 146, "loopback": 150}
TOTAL = 152.0
START = dict(DEFAULT)
tp = ROOT / "timing.json"
if tp.exists():
    tj = json.loads(tp.read_text(encoding="utf-8"))
    START = {s["id"]: s["start"] for s in tj["scenes"]}
    TOTAL = tj["total"]
    print("ใช้เวลาจาก timing.json")
else:
    print("ไม่พบ timing.json — ใช้เวลาประมาณจาก script.md")

N = int(SR * TOTAL) + 1
mix = np.zeros((2, N))  # ซ้าย/ขวา
(ROOT / "sfx").mkdir(exist_ok=True)


def T(sec):
    return np.arange(int(SR * sec)) / SR


def noise(sec):
    return rng.normal(0, 1, int(SR * sec))


def band(x, lo, hi):
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X = np.fft.rfft(x)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def norm(x):
    m = np.max(np.abs(x))
    return x / m if m > 0 else x


def place(x, t, gain=1.0, pan=0.0):
    """วางเสียงโมโนที่เวลา t วินาที pan -1 ซ้าย .. +1 ขวา"""
    i = int(t * SR)
    if i >= N or i < 0:
        return
    x = x[: N - i]
    l, r = gain * np.sqrt((1 - pan) / 2), gain * np.sqrt((1 + pan) / 2)
    mix[0, i:i + len(x)] += x * l
    mix[1, i:i + len(x)] += x * r


def save(name, x):
    x = norm(x) * 0.9
    with wave.open(str(ROOT / "sfx" / f"{name}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def fade(x, a=.02, b=.05):
    n = len(x)
    x = x.copy()
    ia, ib = int(a * SR), int(b * SR)
    x[:ia] *= np.linspace(0, 1, ia)
    x[-ib:] *= np.linspace(1, 0, ib)
    return x


# ---------- เสียงพื้นฐาน ----------
def drone(sec, f=55):
    t = T(sec)
    x = np.sin(2 * np.pi * f * t) + .6 * np.sin(2 * np.pi * f * 1.5 * t + 1) + .4 * np.sin(2 * np.pi * (f * 2 + 1.7) * t)
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * .13 * t)
    return fade(norm(x), 1.5, 1.5)


def crickets(sec):
    t = T(sec)
    x = np.zeros_like(t)
    for f0, ph in ((4300, 0), (3900, .3), (4700, .7)):
        gate = (np.sin(2 * np.pi * 7 * t + ph) > .3) * (np.sin(2 * np.pi * .9 * t + ph) > -.2)
        x += np.sin(2 * np.pi * f0 * t) * gate * 0.35
    x += band(noise(sec), 300, 900) * 0.05  # น้ำคลองเบาๆ
    return fade(x, .5, .5)


def bell(f=392, sec=4):
    t = T(sec)
    x = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * d)
            for m, a, d in ((1, 1, 1.0), (2.76, .5, 1.6), (5.4, .25, 2.4)))
    return norm(x)


def chime(sec=3):
    return bell(1318, sec) * .6


def creak(sec=1.6):
    t = T(sec)
    f = 180 + 120 * np.sin(2 * np.pi * 3.1 * t) * np.exp(-t) + 60 * t
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sign(np.sin(ph)) * .4 + np.sin(ph)) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t))
    return fade(norm(band(x, 150, 2500)) * np.exp(-t * 1.2), .03, .3)


def step_leaf(): # ใบไม้แห้งถูกเหยียบ "ฟึ่บ"
    t = T(.35)
    env = np.exp(-t * 11) * np.minimum(t * 120, 1)
    return norm(band(noise(.35), 1200, 7000)) * env * (1 + .6 * (rng.random(len(t)) > .93))


def thud():
    t = T(.4)
    return norm(np.sin(2 * np.pi * 60 * t * np.exp(-t * 4))) * np.exp(-t * 9) + .3 * norm(band(noise(.4), 80, 400)) * np.exp(-t * 20)


def heart(sec, bpm=70):
    x = np.zeros(int(SR * sec))
    step = 60 / bpm
    for k in np.arange(0, sec - .4, step):
        for off, a in ((0, 1), (.28, .6)):
            tt = T(.18)
            h = np.sin(2 * np.pi * 52 * tt) * np.exp(-tt * 22)
            i = int((k + off) * SR)
            x[i:i + len(h)] += h[: len(x) - i] * a
    return x


def urn_crack():
    t = T(.9)
    return norm(band(noise(.9), 600, 9000)) * np.exp(-t * 14) + .5 * norm(np.sin(2 * np.pi * 140 * t)) * np.exp(-t * 8)


def whisper(sec=2.4):
    # เสียงลมหายใจกระซิบ (ตัวช่วยบรรยากาศ ใต้เสียงพากย์จริง)
    t = T(sec)
    x = band(noise(sec), 2000, 6500) * (0.5 + 0.5 * np.sin(2 * np.pi * 3.6 * t))
    return fade(norm(x) * np.hanning(len(t)), .2, .5)


def tinnitus(sec=2.5):
    t = T(sec)
    return fade(np.sin(2 * np.pi * 8200 * t) * .25, .3, 1.2)


def jumpscare():
    """เสียงตกใจ: ช่วงเงียบ -> เสียงกรีดสูง + ระเบิดเสียงต่ำ + noise กว้าง"""
    t = T(1.6)
    sweep = np.sin(2 * np.pi * np.cumsum(5200 - 3600 * t) / SR) + .7 * np.sin(2 * np.pi * np.cumsum(3100 - 2000 * t) / SR)
    boom = np.sin(2 * np.pi * 45 * t * np.exp(-t * 1.5)) * 1.4
    burst = band(noise(1.6), 200, 12000)
    x = (sweep * .55 + burst * .8) * np.exp(-t * 2.8) + boom * np.exp(-t * 4.5)
    x = np.tanh(2.2 * x)  # ดันให้แตกนิดๆ
    x[: int(.004 * SR)] *= np.linspace(0, 1, int(.004 * SR))  # attack เกือบทันที
    return norm(x)


# ---------- บันทึก stems ----------
def wind(sec):
    t = T(sec)
    x = band(noise(sec), 70, 420) * (0.55 + 0.45 * np.sin(2 * np.pi * .11 * t + 1.3)) + 0.35 * band(noise(sec), 400, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * .07 * t))
    return fade(norm(x), 1.5, 1.5)


def hiss(sec=2.5):
    return fade(norm(band(noise(sec), 5500, 9500)) * np.hanning(int(SR * sec)) * .5, .3, 1.0)


def soft_boom():  # แทนระฆัง: เสียงตุบนุ่มต่ำ ไม่มีโทน
    t = T(1.5)
    return norm(band(noise(1.5), 60, 300)) * np.exp(-t * 3) * .8


if SAFE:
    stems = {"drone": wind(20), "crickets": wind(20) * .5, "bell": soft_boom(), "chime": soft_boom() * .6, "creak": creak(),
             "step_leaf": step_leaf(), "thud": thud(), "heart": heart(6), "urn_crack": urn_crack(),
             "whisper": whisper(), "tinnitus": hiss(), "jumpscare": jumpscare()}
else:
  stems = {"drone": drone(20), "crickets": crickets(20), "bell": bell(), "chime": chime(), "creak": creak(),
         "step_leaf": step_leaf(), "thud": thud(), "heart": heart(6), "urn_crack": urn_crack(),
         "whisper": whisper(), "tinnitus": tinnitus(), "jumpscare": jumpscare()}
if not SAFE:
    for k, v in stems.items():
        save(k, v)


def S(sid, off=0.0):
    return START[sid] + off


# ---------- วางตามฉาก ----------
# พื้นหลัง drone ทั้งเรื่อง (เบา) + เพิ่มระดับในฉากสูงสุด
d = np.tile(stems["drone"], int(TOTAL // 20) + 2)[:N]
place(d, 0, .22)
place(heart(10, 66), S("hook", 3), .35)

# ฉาก 1 hook: นาฬิกา 3 ติ๊ก แล้วหยุดกึก
for k in range(3):
    place(stems["thud"] * .25, S("hook", .4 + k * .9), .5, pan=-.3)

# ฉาก 2 rule: ambience + ระฆังหนึ่งตี
place(np.tile(stems["crickets"], 3)[: int(SR * (START["flag"] - START["rule"]))], S("rule"), .2)
place(stems["bell"], S("rule", 7.5), .5)

# ฉาก 3 bet: แก้วชน + ตบโต๊ะ
place(stems["thud"], S("bet", 14.5), .55)

# ฉาก 4 enter: ประตูลั่น + ก้าวเดิน + จิ้งหรีดหายทั้งหมด
place(stems["creak"], S("enter", .3), .6, pan=.2)
for k in range(8):
    place(stems["step_leaf"] * .35, S("enter", 2.0 + k * .75), .5, pan=(-1) ** k * .25)

# ฉาก 5 flag: ธงปัก -> เงียบ 1.5 วิ -> *** SFX ตกใจกลางเรื่อง ***
place(stems["thud"], S("flag", 8.0), .9)
SCARE_T = S("steps", .15)           # เสียงตกใจ ตกที่ต้นฉากรอยเท้า (กลางเรื่อง ~1:25)
place(stems["tinnitus"], SCARE_T - 1.6, .12)
place(stems["jumpscare"], SCARE_T, 1.0)
place(heart(40, 78), SCARE_T + 1.0, .45)

# ฉาก 6 steps: ฟึ่บ ฟึ่บ ถี่ขึ้น เข้ามาหูซ้าย
t_ = S("steps", 3.0)
gap = 1.0
for k in range(14):
    place(stems["step_leaf"], t_, .55 + k * .03, pan=-.9 + k * .02)
    t_ += gap
    gap = max(.32, gap * .88)

# ฉาก 7 loop: โกศแตก 3 ครั้ง ทุ้มลงทุกครั้ง
for k in range(3):
    place(stems["urn_crack"] * (.9 - .15 * k), S("loop", 3.5 + k * 4.0), .55, pan=.4)
place(stems["thud"], S("loop", 14.5), .6)  # ไฟฉายดับ

# ฉาก 8 whisper: เงียบ ไม่มีดนตรี มีลมหายใจกระซิบแพนขวา (jumpscare เบาถูกย้ายไปกลางเรื่องแล้ว)
place(stems["whisper"], S("whisper", 1.0), .35, pan=.9)

# ฉาก 9 sorry: ชิม
place(stems["chime"], S("sorry", 5.0), .45)

# ฉาก 10 wake: ระฆังเช้า
place(stems["bell"], S("wake", .2), .4)

# ฉาก 11 end: drone วนกลับต้นเรื่อง + ใจเต้นหนึ่งครั้ง
place(stems["drone"] * 1.0, S("end", 2.0), .35)
place(heart(1.2, 60), S("loopback", 2.2), .6)

# ---------- มาสเตอร์ ----------
peak = np.max(np.abs(mix))
mix = mix / peak * 0.9 if peak > .9 else mix
out = ROOT / ("soundtrack-safe.wav" if SAFE else "soundtrack.wav")
with wave.open(str(out), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix.T * 32767).astype("<i2").tobytes())
print(f"เขียน {out.name} ยาว {TOTAL:.1f}s · ตกใจกลางเรื่องที่ {SCARE_T:.1f}s ({int(SCARE_T // 60)}:{SCARE_T % 60:04.1f})")
