"""สร้าง video/index.html ของ EP.049 What if สงครามโลกครั้งที่ 3 — 5 จังหวัดปลอดภัย (แผนที่โลก 2.5D)
  python build.py   (ต้องมี video/timing_gm.json และ video/audio_gm/NN_t.wav จาก make_voice.py)
เขียน video/sync.json ไว้ให้ make_sfx.py ใช้จับจังหวะด้วย"""
import json, re, subprocess
from pathlib import Path
import numpy as np
from lines import CAPS

HERE = Path(__file__).resolve().parent
V = HERE / "video"
timing = json.loads((V / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL = timing["total"]
LINES = timing["lines"]
N = len(LINES)
WORLD = (V / "world-path.txt").read_text()
OUTL = json.loads((V / "outlines.json").read_text(encoding="utf-8"))
SR = 16000

# ---------- จับเวลาซับจากพลังงานเสียง (วิธีเดียวกับตอน 047) ----------
def envelope(wav):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    x = np.abs(np.frombuffer(raw, dtype="<f4"))
    win = int(SR * 0.03)
    return np.convolve(x, np.ones(win) / win, mode="same")


SPOKEN = {"5": "ห้า", "3": "สาม"}
SYNC = []
for i, chunks in enumerate(CAPS):
    env = envelope(V / "audio_gm" / f"{i:02}_t.wav")
    voiced = np.where(env > env.max() * 0.08)[0]
    t0, t1 = voiced[0] / SR, voiced[-1] / SR
    def plen(s):
        for a, b in SPOKEN.items():
            s = s.replace(a, b)
        return len(re.sub(r"[\s\[\]]", "", s))
    w = [plen(c[0]) for c in chunks]
    cuts, acc = [], 0
    for k in range(len(chunks) - 1):
        acc += w[k]
        t = t0 + (t1 - t0) * acc / sum(w)
        a, b = max(int((t - .4) * SR), int(t0 * SR)), min(int((t + .4) * SR), int(t1 * SR))
        cuts.append((a + int(np.argmin(env[a:b]))) / SR if b > a else t)
    starts = [t0] + cuts
    for k in range(1, len(starts)):
        starts[k] = max(starts[k], starts[k - 1] + .5)
    off = LINES[i]["start"]
    SYNC.append([[round(off + s, 2), round(off + (starts[k + 1] if k + 1 < len(starts) else t1 + .3), 2)] for k, s in enumerate(starts)])

SC = [0.0] + [round(LINES[i]["start"] - 0.2, 3) for i in range(1, N)]
SCE = SC[1:] + [TOTAL]
ck = lambda li, ci: SYNC[li][min(ci, len(SYNC[li]) - 1)][0]


# ---------- เรขาคณิตแผนที่ ----------
mx = lambda lon: round((lon + 180) * 10 if lon > -30 else (lon + 540) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
PW, TILT, PLX, PLY, PERSPY, HORIZ = 1700, 60, -310, 150, 230, 380
CAM0 = [3420, 900, 3300]
CAM = [[3300, 880, 2900],                 # ฮุกจบ: เลื่อนเข้าเอเชีย
       [mx(101.2), my(14.0) + 60, 250],   # 1 เกณฑ์ (โซนอันตราย)
       [mx(99.8), my(18.2) + 55, 150],    # 2 น่าน เลย แม่ฮ่องสอน
       [mx(99.3), my(12.7) + 55, 190],    # 3 อุทัยธานี ระนอง
       [mx(101.0), my(13.2) + 70, 300]]   # 4 CTA


def to_plane(p, c):
    x0, y0 = c[0] - c[2] / 2, c[1] - c[2] / 2
    return round((p[0] - x0) / c[2] * PW, 1), round((p[1] - y0) / c[2] * PW, 1)


land = ""
for dy, col in [(16, "#02060e"), (11, "#061223"), (6, "#0b2238"), (3, "#123553")]:
    land += f'<use href="#wp" y="{dy}" fill="{col}"/><use href="#wp" x="3600" y="{dy}" fill="{col}"/>'
land += ('<use href="#wp" fill="#2a6a8e" stroke="#9fd8ff" stroke-width="1.4" stroke-opacity=".8" vector-effect="non-scaling-stroke"/>'
         '<use href="#wp" x="3600" fill="#2a6a8e" stroke="#9fd8ff" stroke-width="1.4" stroke-opacity=".8" vector-effect="non-scaling-stroke"/>')
grid = "".join(f'<path d="M{x},0 V1800" stroke="#5aa0d8" stroke-opacity=".14" stroke-width="1" vector-effect="non-scaling-stroke"/>' for x in range(1800, 5400, 150))
grid += "".join(f'<path d="M1800,{y} H5400" stroke="#5aa0d8" stroke-opacity=".14" stroke-width="1" vector-effect="non-scaling-stroke"/>' for y in range(300, 1500, 150))
grid += '<path d="M1800,900 H5400" stroke="#ffd23f" stroke-opacity=".35" stroke-width="1.5" stroke-dasharray="10 8" vector-effect="non-scaling-stroke"/>'

# ขีปนาวุธยิงข้ามแผนที่ไปมา + ระเบิด (จุดทั่วโลก ไม่ชี้ประเทศหรือกลุ่มใดโดยเฉพาะ)
MP = [((-100, 40), (8, 48)), ((45, 28), (-60, -10)), ((115, 35), (28, 2)), ((135, -25), (80, 56)), ((8, 48), (-100, 40)), ((-60, -10), (115, 35)),
      ((80, 56), (-3, 38)), ((28, 2), (135, -25)), ((-100, 40), (45, 28)), ((115, 35), (-100, 40)), ((-3, 38), (135, -25)), ((80, 56), (-60, -10)),
      ((45, 28), (115, 35)), ((135, -25), (8, 48)), ((-60, -10), (28, 2)),
      ((28, 2), (-100, 40)), ((-3, 38), (-60, -10)), ((115, 35), (8, 48)), ((135, -25), (-100, 40)), ((-60, -10), (80, 56))]
M_T0, M_STEP, M_FLY = 0.95, 0.22, 0.75
MT = [[round(M_T0 + k * M_STEP, 2), round(M_T0 + k * M_STEP + M_FLY, 2)] for k in range(len(MP))]
WDOTS = ""
for k, (pa, pb) in enumerate(MP):
    x1, y1, x2, y2 = mx(pa[0]), my(pa[1]), mx(pb[0]), my(pb[1])
    dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** .5
    WDOTS += f'<path id="mt{k}" d="M{x1},{y1} Q{(x1 + x2) / 2},{(y1 + y2) / 2 - dist * .32} {x2},{y2}" fill="none" stroke="#ffb84a" stroke-width="15" stroke-linecap="round" opacity="0"/>'
    WDOTS += f'<circle id="mh{k}" cx="{x1}" cy="{y1}" r="36" fill="#fff" stroke="#ff7a1a" stroke-width="14" opacity="0"/>'
    WDOTS += (f'<g id="ex{k}" transform="translate({x2},{y2})"><circle class="eg" r="0" fill="#e0243a" opacity="0"/><circle class="ec" r="0" fill="#ff5a14" opacity="0"/><circle class="ew" r="0" fill="#fff3b0" opacity="0"/>'
              f'<circle class="er" r="0" fill="none" stroke="#ffd23f" stroke-width="14" opacity="0"/></g>')
# โซนเสี่ยง (เมืองหลวง / ฐานทัพ / นิคมฯ) และจังหวัดปลอดภัย
BKK, KORAT, RAYONG = (mx(100.5), my(13.75)), (mx(102.1), my(14.97)), (mx(101.15), my(12.72))
ZONES_P = [BKK, KORAT, RAYONG]
ZONES = "".join(f'<circle id="zr{k}" cx="{p[0]}" cy="{p[1]}" r="0" fill="#e0243a" fill-opacity=".38" stroke="#ff4d5e" stroke-width="3" stroke-dasharray="10 7" vector-effect="non-scaling-stroke" opacity="0"/>' for k, p in enumerate(ZONES_P))
SAFE_LL = {"nan": (100.77, 18.78), "loei": (101.73, 17.49), "mhs": (97.97, 19.30), "uth": (100.03, 15.38), "ran": (98.63, 9.96)}
SAFE_P = {k: (mx(lo), my(la)) for k, (lo, la) in SAFE_LL.items()}
SAFE = "".join(f'<circle id="sf{k}" cx="{p[0]}" cy="{p[1]}" r="0" fill="#2ecc71" fill-opacity=".55" stroke="#fff" stroke-width="3" vector-effect="non-scaling-stroke" opacity="0"/>' for k, p in SAFE_P.items())
TH = (mx(100.9), my(15.6))


# ---------- ป้ายตั้ง ----------
def stand(idn, html, cls="", stem=90):
    return f'<div class="stand" id="{idn}"><div class="sh"></div><div class="up"><div class="an"><div class="lab {cls}">{html}</div><div class="stem" style="height:{stem}px"></div><div class="dot"></div></div></div></div>'


STANDS_HTML = (stand("sZ1", "เมืองหลวง", "red", 60) + stand("sZ2", "ฐานทัพ", "red", 120) + stand("sZ3", "นิคมฯ", "red", 40)
               + stand("sNan", "น่าน", "green", 190) + stand("sLoei", "เลย", "green", 70) + stand("sMhs", "แม่ฮ่องสอน", "green", 110)
               + stand("sUth", "อุทัยธานี", "green", 110) + stand("sRan", "ระนอง", "green", 80))
STANDS = []


def show(idn, p, scene, t_in, t_out):
    for s in STANDS:
        if s["id"] == idn:
            break
    else:
        s = {"id": idn, "show": []}; STANDS.append(s)
    s["show"].append([scene, round(t_in, 2), round(t_out, 2), *to_plane(p, CAM[scene])])


show("sZ1", BKK, 1, ck(1, 1) + 0.1, SCE[1] - 0.3)
show("sZ2", KORAT, 1, ck(1, 2) + 0.1, SCE[1] - 0.3)
show("sZ3", RAYONG, 1, ck(1, 3) + 0.1, SCE[1] - 0.3)
show("sNan", SAFE_P["nan"], 2, ck(2, 1) + 0.1, SCE[2] - 0.3)
show("sLoei", SAFE_P["loei"], 2, ck(2, 3) + 0.1, SCE[2] - 0.3)
show("sMhs", SAFE_P["mhs"], 2, ck(2, 5) + 0.1, SCE[2] - 0.3)
show("sUth", SAFE_P["uth"], 3, ck(3, 1) + 0.1, SCE[3] - 0.3)
show("sRan", SAFE_P["ran"], 3, ck(3, 3) + 0.1, SCE[3] - 0.3)

# ---------- ไดโอรามาไอโซเมตริก (การ์ดล่าง 960x520) ----------
# ---------- ไดโอรามาไอโซเมตริก (การ์ดล่าง 960x520) ----------
ST = "#fff"


def it(k, inner, d=0.0):
    return f'<g class="it" data-k="{k}" data-d="{d}">{inner}</g>'


def txt(x, y, s, size=48, col="#fff"):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="800" fill="{col}" text-anchor="middle" font-family="Kanit">{s}</text>'


def iso(cx, cy, w, d, top, left, right, extra=""):
    hw, hq = w / 2, w / 4
    return (f'<ellipse cx="{cx}" cy="{cy + hq + d + 14}" rx="{hw * .95}" ry="{hq * .5}" fill="#000" opacity=".35"/>'
            f'<polygon points="{cx - hw},{cy} {cx},{cy + hq} {cx},{cy + hq + d} {cx - hw},{cy + d}" fill="{left}" stroke="{ST}" stroke-width="4" stroke-linejoin="round"/>'
            f'<polygon points="{cx},{cy + hq} {cx + hw},{cy} {cx + hw},{cy + d} {cx},{cy + hq + d}" fill="{right}" stroke="{ST}" stroke-width="4" stroke-linejoin="round"/>'
            f'<polygon points="{cx},{cy - hq} {cx + hw},{cy} {cx},{cy + hq} {cx - hw},{cy}" fill="{top}" stroke="{ST}" stroke-width="4" stroke-linejoin="round"/>{extra}')


def isobox(cx, cy, w, h, top, left, right):  # กล่องสูง (ตึก/ถังน้ำ) ฐานอยู่ที่ cy
    hw, hq = w / 2, w / 4
    return (f'<polygon points="{cx - hw},{cy - h} {cx},{cy + hq - h} {cx},{cy + hq} {cx - hw},{cy}" fill="{left}" stroke="{ST}" stroke-width="3"/>'
            f'<polygon points="{cx},{cy + hq - h} {cx + hw},{cy - h} {cx + hw},{cy} {cx},{cy + hq}" fill="{right}" stroke="{ST}" stroke-width="3"/>'
            f'<polygon points="{cx},{cy - hq - h} {cx + hw},{cy - h} {cx},{cy + hq - h} {cx - hw},{cy - h}" fill="{top}" stroke="{ST}" stroke-width="3"/>')


def waves_iso(cx, cy, w, col="#fff", n=3):
    out = ""
    for k in range(n):
        y = cy - w / 8 + k * w / 10
        out += f'<path d="M{cx - w * .3},{y} q{w * .075},-14 {w * .15},0 t{w * .15},0 t{w * .15},0 t{w * .15},0" fill="none" stroke="{col}" stroke-width="5" stroke-linecap="round" opacity=".85"/>'
    return out


def up_arrow(x, y, h=90, col="#e0243a"):
    return (f'<path d="M{x},{y} V{y - h}" stroke="{col}" stroke-width="14" stroke-linecap="round"/>'
            f'<path d="M{x - 26},{y - h + 24} L{x},{y - h - 6} L{x + 26},{y - h + 24}" fill="none" stroke="{col}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>')


def thermo(x, y, h=200, lvl=.85, col="#e0243a"):
    return (f'<rect x="{x - 22}" y="{y - h}" width="44" height="{h}" rx="22" fill="#fff" stroke="{ST}" stroke-width="5"/>'
            f'<rect x="{x - 11}" y="{y - h * lvl}" width="22" height="{h * lvl}" rx="11" fill="{col}"/>'
            f'<circle cx="{x}" cy="{y + 14}" r="38" fill="{col}" stroke="{ST}" stroke-width="5"/>'
            + "".join(f'<path d="M{x + 22},{y - h + 30 + j * 34} h-14" stroke="#1e1e24" stroke-width="4"/>' for j in range(4)))


def sun(x, y, r=56):
    rays = "".join(f'<path d="M{x + np.cos(a) * (r + 14):.0f},{y + np.sin(a) * (r + 14):.0f} L{x + np.cos(a) * (r + 40):.0f},{y + np.sin(a) * (r + 40):.0f}" stroke="#ffb020" stroke-width="10" stroke-linecap="round"/>' for a in np.linspace(0, 2 * np.pi, 12, endpoint=False))
    return rays + f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffd23f" stroke="{ST}" stroke-width="5"/>'


def flame(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M0,-90 Q40,-40 30,-6 Q26,20 0,24 Q-26,20 -30,-6 Q-34,-34 -10,-56 Q-6,-30 6,-30 Q14,-56 0,-90Z" fill="#ff6a1c" stroke="{ST}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M0,-40 Q16,-16 10,4 Q0,14 -10,4 Q-14,-14 0,-40Z" fill="#ffd23f"/></g>')


def person(x, y, s=1.0, col="#fff"):
    return f'<g transform="translate({x},{y}) scale({s})"><circle cx="0" cy="-58" r="18" fill="{col}"/><path d="M-26,0 Q-26,-36 0,-36 Q26,-36 26,0Z" fill="{col}"/></g>'




def tree(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><rect x="-5" y="-14" width="10" height="16" fill="#5a3418" stroke="{ST}" stroke-width="3"/>'
            f'<polygon points="0,-86 28,-14 -28,-14" fill="#1f8a3e" stroke="{ST}" stroke-width="4" stroke-linejoin="round"/></g>')


def mount(x, y, w, h, col="#7a8a6a"):
    return (f'<polygon points="{x - w / 2},{y} {x},{y - h} {x + w / 2},{y}" fill="{col}" stroke="{ST}" stroke-width="4" stroke-linejoin="round"/>'
            f'<polygon points="{x},{y - h} {x + w * .13},{y - h * .72} {x},{y - h * .8} {x - w * .13},{y - h * .72}" fill="#fff"/>')


def noslash(x, y, r=78):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="#e0243a" stroke-width="14"/>'
            f'<path d="M{x - r * .7},{y - r * .7} L{x + r * .7},{y + r * .7}" stroke="#e0243a" stroke-width="14" stroke-linecap="round"/>')


def plane_icon(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M0,-44 L12,-10 L52,12 L52,24 L10,14 L8,40 L24,52 L24,58 L0,52 L-24,58 L-24,52 L-8,40 L-10,14 L-52,24 L-52,12 L-12,-10Z" fill="#cfd6e4" stroke="{ST}" stroke-width="5" stroke-linejoin="round"/></g>')


def drop(x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})"><path d="M0,-70 Q40,-20 36,10 Q32,40 0,40 Q-32,40 -36,10 Q-40,-20 0,-70Z" fill="#4cc3ff" stroke="{ST}" stroke-width="5" stroke-linejoin="round"/></g>'


def barrel(x, y):
    return (f'<rect x="{x - 50}" y="{y - 120}" width="100" height="120" rx="14" fill="#2b3a55" stroke="{ST}" stroke-width="5"/>'
            f'<rect x="{x - 50}" y="{y - 90}" width="100" height="12" fill="#ffd23f"/><rect x="{x - 50}" y="{y - 40}" width="100" height="12" fill="#ffd23f"/>')


def bag(x, y):
    return (f'<path d="M{x - 55},{y} q-8,-80 14,-110 h82 q22,30 14,110Z" fill="#c9a23a" stroke="{ST}" stroke-width="5" stroke-linejoin="round"/>'
            f'<rect x="{x - 36}" y="{y - 120}" width="72" height="16" fill="#8a6a1c" stroke="{ST}" stroke-width="4"/>')


def sail(x, y):
    return (f'<polygon points="{x},{y - 90} {x + 56},{y - 6} {x},{y - 6}" fill="#fff" stroke="{ST}" stroke-width="4" stroke-linejoin="round"/>'
            f'<path d="M{x - 60},{y} h130 l-20,26 h-90Z" fill="#e8553d" stroke="{ST}" stroke-width="4" stroke-linejoin="round"/>')


def zone(cx, obj, name):
    return iso(cx, 340, 200, 30, "#7a2a2a", "#451616", "#5e2020") + obj + noslash(cx, 270) + txt(cx, 120, name, 46, "#ff8a96")


GREEN = ("#3d8f4a", "#1f5a2a", "#2d7338")


def prov(cx, name, sub, extra, wide=250):
    return iso(cx, 350, wide, 40, *GREEN, extra) + txt(cx, 120, name, 60, "#fff") + txt(cx, 478, sub, 34, "#bff0c8")


FAC = ('<rect x="622" y="230" width="22" height="90" fill="#6a6f7e" stroke="#fff" stroke-width="3"/>'
       '<circle cx="636" cy="212" r="18" fill="#aab" opacity=".8"/><circle cx="654" cy="190" r="22" fill="#aab" opacity=".6"/>')
SCENES = {
    1: [it(0, txt(480, 62, "เกณฑ์ความปลอดภัย", 46, "#ffd23f")),
        it(1, zone(130, "".join(isobox(100 + j * 32, 330 - j * 8, 30, 70 + j * 36, "#8a90a0", "#4a4e5a", "#5e6370") for j in range(3)), "เมืองหลวง")),
        it(2, zone(360, plane_icon(360, 296, 1.0), "ฐานทัพ")),
        it(3, zone(590, isobox(580, 330, 90, 80, "#8a90a0", "#4a4e5a", "#5e6370") + FAC, "นิคมฯ")),
        it(4, iso(830, 340, 200, 30, "#1f6a3a", "#124226", "#195633") + drop(800, 300, 0.9)
           + '<path d="M850,330 q-6,-40 -24,-56 M850,330 q4,-44 22,-58 M850,330 q0,-50 2,-66" fill="none" stroke="#e0b53a" stroke-width="7" stroke-linecap="round"/>'
           + txt(830, 120, "น้ำ+อาหาร", 46, "#7dffa6"))],
    2: [it(1, prov(170, "น่าน", "ภูเขา · ป่า", mount(130, 330, 120, 100) + mount(210, 340, 130, 130) + tree(110, 366, .8) + tree(240, 372, .8) + tree(170, 380, .7))),
        it(3, prov(480, "เลย", "ที่สูง · เย็น", mount(430, 332, 150, 120) + mount(520, 340, 130, 100) + tree(470, 378, .8) + tree(560, 372, .7))),
        it(5, prov(790, "แม่ฮ่องสอน", "ไกลที่สุด", mount(740, 334, 140, 140) + mount(830, 340, 120, 110) + tree(790, 380, .8)
                   + '<path d="M690,384 q60,-20 120,-8 t110,-10" fill="none" stroke="#ffd23f" stroke-width="5" stroke-dasharray="12 10"/>'))],
    3: [it(1, iso(250, 350, 330, 50, *GREEN, isobox(250, 336, 190, 54, "#cfd6e4", "#8a90a0", "#a9b0c0") + '<rect x="188" y="300" width="124" height="20" fill="#4cc3ff" opacity=".85"/>' + tree(130, 362, .8) + tree(372, 368, .8))
           + txt(250, 120, "อุทัยธานี", 60, "#fff") + txt(250, 478, "เขื่อน · ป่าใหญ่", 34, "#bff0c8")),
        it(3, iso(710, 350, 330, 50, "#1d6fa8", "#0c3f6a", "#12558a", waves_iso(710, 350, 330) + sail(710, 320))
           + txt(710, 120, "ระนอง", 60, "#fff") + txt(710, 478, "ทะเลอันดามัน", 34, "#9fe0ff")),
        it(5, '<g transform="rotate(-3 480 460)"><rect x="210" y="410" width="540" height="84" rx="18" fill="#ffd23f" stroke="#1e1e24" stroke-width="7"/>' + txt(480, 478, "ห่างศูนย์กลางอำนาจ", 50, "#1e1e24") + '</g>')],
    4: [it(1, barrel(140, 400) + up_arrow(140, 250, 100) + txt(140, 450, "น้ำมัน", 40, "#fff")),
        it(1, bag(360, 400) + up_arrow(360, 250, 100) + txt(360, 450, "อาหาร", 40, "#fff"), 0.35),
        it(3, '<rect x="540" y="130" width="360" height="100" rx="22" fill="#1f9d55" stroke="#fff" stroke-width="7"/>' + txt(720, 205, "5 จังหวัดนี้", 62, "#fff")),
        it(4, '<path d="M560,260 h300 q24,0 24,24 v110 q0,24 -24,24 h-190 l-50,50 v-50 h-60 q-24,0 -24,-24 v-110 q0,-24 24,-24Z" fill="#fff" stroke="#1e1e24" stroke-width="7"/>'
           + '<text x="710" y="360" font-size="54" font-weight="800" fill="#1e1e24" text-anchor="middle" font-family="Kanit" style="stroke:none">คุณอยู่ไหม?</text>')],
}
VGS = "\n".join(f'<div id="vg{i}" class="vg"><svg viewBox="0 0 960 520" width="960" height="520">{"".join(v)}</svg></div>' for i, v in SCENES.items())

TAGS = ["WHAT IF · <r>สงครามโลกครั้งที่ 3</r>", "เกณฑ์ · <r>ห่างเป้าหมาย</r>", "<r>น่าน · เลย · แม่ฮ่องสอน</r>", "<r>อุทัยธานี · ระนอง</r>", "คุณอยู่ใน <r>5 จังหวัดนี้</r>ไหม"]
tags_html = "\n".join(f'<div id="t{i}" class="tag">{t_}</div>' for i, t_ in enumerate(TAGS))

vb0 = f"{CAM0[0] - CAM0[2] / 2} {CAM0[1] - CAM0[2] / 2} {CAM0[2]} {CAM0[2]}"
DATA = dict(SC=SC, SCE=SCE, CAM0=CAM0, CAM=CAM, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, STANDS=STANDS, MT=MT, SAFE=list(SAFE_P))
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLD%%": WORLD, "%%LAND%%": land, "%%GRID%%": grid, "%%TH%%": OUTL["Thailand"], "%%THX%%": str(TH[0]), "%%THY%%": str(TH[1]),
             "%%WDOTS%%": WDOTS, "%%ZONES%%": ZONES, "%%SAFE%%": SAFE, "%%STANDS%%": STANDS_HTML, "%%VGS%%": VGS, "%%TAGS%%": tags_html, "%%VB0%%": vb0, "%%PW%%": str(PW), "%%TILT%%": str(TILT),
             "%%PLX%%": str(PLX), "%%PLY%%": str(PLY), "%%PERSPY%%": str(PERSPY), "%%HORIZ%%": str(HORIZ), "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
(V / "sync.json").write_text(json.dumps({"SC": SC, "SYNC": SYNC, "STANDS": STANDS, "MT": MT}, ensure_ascii=False), encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i, SC[i], "->", SCE[i], [c[0] for c in SYNC[i]])
