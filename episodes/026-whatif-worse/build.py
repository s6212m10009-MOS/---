"""สร้าง video/index.html ของตอน 026 (What If ถ้าสถานการณ์แย่ลง) จาก lines.py + video/timing_gm.json
  python build.py   (ตั้ง PYTHONIOENCODING=utf-8 ถ้าคอนโซลเป็น cp874)
ยืมฟังก์ชันวาด (W/txt/stick/bag/radio/...) จาก ../025-whatif-world-war/build.py แล้วเพิ่มฉากของตอนนี้
ซับผูกกับเสียงด้วยพลังงานเสียง ไทย + อังกฤษตัวเล็ก"""
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
WORLDLINE = (V / "world-line.txt").read_text()
SR = 16000

REF = (HERE.parent / "025-whatif-world-war" / "build.py").read_text(encoding="utf-8")
ns = {"INK": "#1E1E24"}
exec(REF[REF.index("def W("):REF.index("BAGX, BAGY")], ns)
W, txt, stick, bottle, radio, power, card, skyline = (ns[k] for k in ("W", "txt", "stick", "bottle", "radio", "power", "card", "skyline"))
INK = ns["INK"]


def envelope(wav):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    x = np.abs(np.frombuffer(raw, dtype="<f4"))
    win = int(SR * 0.03)
    return np.convolve(x, np.ones(win) / win, mode="same")


SYNC = []
for i, chunks in enumerate(CAPS):
    env = envelope(V / "audio_gm" / f"{i:02}_t.wav")
    voiced = np.where(env > env.max() * 0.08)[0]
    t0, t1 = voiced[0] / SR, voiced[-1] / SR
    w = [len(re.sub(r"[\s\[\]]", "", c[0])) for c in chunks]
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

TAGS = ["WHAT IF · <r>ถ้าแย่ลง</r>", "กรุงเทพฯ · <r>ไฟดับ</r>", "<r>วุ่นวาย</r> · ตื่นตระหนก", "ตั้งสติ · <r>เตรียมไว้</r>", "ข้อ 1 · <r>ข่าว + นัดพบ</r>",
        "ข้อ 2 · <r>น้ำ + อาหาร</r>", "ข้อ 3 · <r>พลังงานสำรอง</r>", "ข้อ 4 · <r>รับมือร้อน</r>", "ข้อ 5 · <r>ช่วยกัน</r>", "ไฟ<r>กลับมา</r>แล้ว"]

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
BKK = (100.5, 13.75)


def cam_xy(lon, lat, k, py=None):
    if py is None:
        return [round(540 - mx(lon) * k, 1), round(690 - (my(lat) - 900) * k, 1), k]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


WORLD = cam_xy(20, 15, 0.55)
CAM = [cam_xy(101, 14, 1.7, 620)] + [cam_xy(*BKK, 3.0, 860)] * 8 + [WORLD]
DRIFT = cam_xy(*BKK, 3.4, 860)

DOTLL = [(-100, 40), (-60, -10), (-3, 50), (20, 5), (37, 50), (60, 45), (78, 22), (115, 35), (135, 36), (150, -25), (-75, 5), (30, -28), (-120, 55), (90, 60), (-45, 70),
         (-90, 20), (10, 30), (50, 20), (70, 55), (100, 50), (125, 10), (-55, -35), (25, 60), (140, -5), (-110, 30)]
GREENLL = [(-100, 40), (-3, 50), (37, 50), (78, 22), (135, 36), (-60, -10), (20, 5), (150, -25), (115, 35), (100.5, 13.75), (60, 45), (-75, 5)]
dots_html = "".join(f'<g id="dot{k}" class="dotg" transform="translate({mx(lo)},{my(la)})"><circle r="38" fill="#e0243a" stroke="#fff" stroke-width="6"/><circle class="ring" r="38" fill="none" stroke="#e0243a" stroke-width="8"/></g>'
                    for k, (lo, la) in enumerate(DOTLL))
gdots_html = "".join(f'<g id="gd{k}" class="gdot" transform="translate({mx(lo)},{my(la)})"><circle r="30" fill="#2fe07a" stroke="#fff" stroke-width="5"/></g>' for k, (lo, la) in enumerate(GREENLL))


def gen(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-56" y="-38" width="112" height="76" rx="12" fill="#f08a1c" stroke="{INK}" stroke-width="6"/><rect x="-30" y="-24" width="60" height="26" rx="6" fill="#444"/><circle cx="-34" cy="44" r="12" fill="#444" stroke="{INK}" stroke-width="4"/><circle cx="34" cy="44" r="12" fill="#444" stroke="{INK}" stroke-width="4"/><path d="M40,-38 V-62 H56" fill="none" stroke="{INK}" stroke-width="6"/></g>')


def house(x, y, s=1.0, idn="", inner=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-110" y="-70" width="220" height="140" fill="#f7e6c4" stroke="{INK}" stroke-width="6"/><path d="M-130,-70 L0,-150 L130,-70Z" fill="#c4533a" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>{inner}</g>')


def x_mark(x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})"><path d="M-50,-50 L50,50 M50,-50 L-50,50" stroke="#e0243a" stroke-width="16" stroke-linecap="round"/></g>'


BG = '<rect width="960" height="520" fill="#fff"/>'
RUN = [(400, 380), (500, 400), (600, 370), (700, 395), (800, 375), (890, 400)]
VG = {
    1: (skyline() + txt(480, 150, "ไฟดับทั้งเมือง", 70, "#ffd23f", "v1t") + txt(480, 490, "วันที่ 4 ขึ้นไป · ร้านปิด", 36, "#fff", "v1u"), True),
    2: ('<rect width="960" height="520" fill="#2a0d14"/>'
        + "".join(f'<rect x="40" y="{y}" width="300" height="12" fill="#6c4a3a" stroke="{INK}" stroke-width="3"/>' for y in (170, 280, 390))
        + '<rect x="70" y="140" width="34" height="30" fill="#8a5a4a"/><rect x="250" y="360" width="40" height="30" fill="#8a5a4a"/>'
        + W("v2s", '<rect x="520" y="26" width="400" height="76" rx="20" fill="#000" stroke="#e0243a" stroke-width="6"/>' + txt(720, 80, "ไม่มีสัญญาณ", 44, "#fff"))
        + "".join(stick(x, y, 1.05, "#fff", f"v2p{k}", "#2a0d14") for k, (x, y) in enumerate(RUN))
        + txt(560, 200, "!", 110, "#e0243a", "v2e") + txt(820, 230, "!", 90, "#ffd23f", "v2f"), True),
    3: ('<rect width="960" height="520" fill="#0d1226"/>'
        + W("v3crowd", "".join(stick(x, 400, 1.0, "#7a7f99", "", "#0d1226") for x in (110, 220, 740, 850, 910)))
        + W("v3r", '<circle cx="480" cy="260" r="150" fill="none" stroke="#37b3a6" stroke-width="10" opacity=".8"/>')
        + stick(480, 340, 1.8, "#fff", "v3c", "#0d1226") + txt(480, 495, "ตั้งสติ", 52, "#ffd23f", "v3t"), True),
    4: (BG + radio(150, 250, 1.5, "v4r")
        + W("v4p", f'<rect x="300" y="110" width="210" height="270" rx="10" fill="#fff8c8" stroke="{INK}" stroke-width="6"/>' + "".join(f'<path d="M324,{170 + k * 50} H486" stroke="#999" stroke-width="5"/>' for k in range(4)) + txt(405, 158, "เบอร์โทร", 34))
        + W("v4m", f'<rect x="590" y="110" width="320" height="270" rx="22" fill="#cfe8d4" stroke="{INK}" stroke-width="6"/><path d="M590,250 H910 M720,110 V380" stroke="#fff" stroke-width="14"/><circle cx="780" cy="240" r="26" fill="#e0243a" stroke="{INK}" stroke-width="5"/>' + txt(750, 330, "จุดนัดพบ", 34))
        + txt(150, 440, "วิทยุถ่าน", 34, "#555") + txt(405, 440, "เขียนไว้", 34, "#555") + txt(750, 440, "ครอบครัว", 34, "#555"), False),
    5: (BG + W("v5j", f'<rect x="80" y="130" width="150" height="220" rx="30" fill="#5ab8ee" stroke="{INK}" stroke-width="7"/><rect x="125" y="100" width="60" height="36" rx="8" fill="#fff" stroke="{INK}" stroke-width="6"/>' + txt(155, 255, "21", 70, "#fff") + txt(155, 305, "ลิตร", 34, "#fff"))
        + W("v5p", f'<path d="M340,200 V320 Q340,350 370,350 H530 Q560,350 560,320 V200Z" fill="#c9ced6" stroke="{INK}" stroke-width="7"/><path d="M320,200 H580" stroke="{INK}" stroke-width="9"/><path d="M400,170 Q380,140 400,115 M450,170 Q430,140 450,115 M500,170 Q480,140 500,115" fill="none" stroke="#aaa" stroke-width="7" stroke-linecap="round"/>' + txt(450, 280, "1 นาที", 44, "#e0243a"))
        + W("v5f", f'<rect x="700" y="100" width="170" height="270" rx="18" fill="#e8eef6" stroke="{INK}" stroke-width="7"/><path d="M700,210 H870" stroke="{INK}" stroke-width="6"/><path d="M845,140 V180 M845,240 V300" stroke="{INK}" stroke-width="8" stroke-linecap="round"/>' + txt(785, 175, "4 ชม.", 30, "#e0243a") + txt(785, 295, "ก่อนเสีย", 28, "#555"))
        + txt(155, 440, "น้ำสำรอง", 34, "#555") + txt(450, 440, "ต้มเดือด", 34, "#555") + txt(785, 440, "กินของในตู้เย็นก่อน", 30, "#555"), False),
    6: (BG + txt(480, 70, "กลางแจ้งเท่านั้น", 56, "#e0243a", "v6t")
        + house(240, 270, 1.0, "v6a", f'<g transform="translate(0,20)"><rect x="-50" y="-30" width="100" height="70" rx="10" fill="#f08a1c" stroke="{INK}" stroke-width="5"/></g>' + x_mark(0, 10, 1.2))
        + W("v6o", f'<path d="M520,330 H900" stroke="{INK}" stroke-width="6"/>') + gen(700, 280, 1.3, "v6b")
        + W("v6k", '<circle cx="860" cy="160" r="40" fill="#1f9d55" stroke="#1e1e24" stroke-width="5"/><path d="M842,162 L856,176 L882,146" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')
        + power(480, 280, 0.9, "v6p") + txt(240, 460, "ในบ้าน: ห้าม", 34, "#e0243a") + txt(700, 460, "ก๊าซ CO", 34, "#555"), False),
    7: (BG + W("v7s", f'<circle cx="160" cy="150" r="64" fill="#ffd23f" stroke="{INK}" stroke-width="7"/>' + "".join(f'<path d="M160,150 m{int(math_c * 82)},{int(math_s * 82)} l{int(math_c * 36)},{int(math_s * 36)}" stroke="{INK}" stroke-width="7" stroke-linecap="round"/>' for math_c, math_s in [(1, 0), (0.7, 0.7), (0, 1), (-0.7, 0.7), (-1, 0), (-0.7, -0.7), (0, -1), (0.7, -0.7)]))
        + bottle(480, 260, 1.7, "v7b")
        + W("v7c", f'<path d="M690,180 Q760,150 830,180 V330 Q760,360 690,330Z" fill="#8fd8ee" stroke="{INK}" stroke-width="7"/><path d="M730,380 q6,12 0,20 q-6,-8 0,-20 M790,390 q6,12 0,20 q-6,-8 0,-20" fill="#37b3a6"/>')
        + txt(160, 440, "ร้อนชื้น", 34, "#555") + txt(480, 440, "ดื่มน้ำเยอะ", 34, "#555") + txt(760, 440, "ผ้าเปียกเช็ดตัว", 34, "#555"), False),
    8: (BG + house(200, 280, 0.95, "v8a") + house(760, 280, 0.95, "v8b") + stick(200, 330, 0.9, INK, "v8x") + stick(760, 330, 0.9, INK, "v8y")
        + bottle(480, 260, 1.2, "v8w") + txt(480, 90, "แบ่งน้ำ อาหาร", 52, "#1f9d55", "v8t"), False),
    9: (BG + W("v9s", f'<rect x="580" y="170" width="190" height="180" rx="22" fill="#e8eef6" stroke="{INK}" stroke-width="7"/><rect x="620" y="220" width="16" height="50" fill="{INK}"/><rect x="700" y="220" width="16" height="50" fill="{INK}"/>')
        + W("v9p", f'<path d="M180,260 H340" stroke="{INK}" stroke-width="9" stroke-linecap="round"/><rect x="340" y="215" width="120" height="90" rx="16" fill="#f4f4f4" stroke="{INK}" stroke-width="7"/><rect x="460" y="228" width="60" height="14" fill="#888"/><rect x="460" y="278" width="60" height="14" fill="#888"/>')
        + W("v9z", '<path d="M470,110 L430,200 H470 L440,290 L520,170 H478Z" fill="#ffd23f" stroke="#1e1e24" stroke-width="6" stroke-linejoin="round"/>')
        + txt(480, 440, "ถอดปลั๊กกันไฟกระชาก", 40, "#555"), False),
}
VGS = "\n".join(card(f"vg{i}", VG[i][0], VG[i][1]) for i in sorted(VG))
tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))

DATA = dict(SC=SC, SCE=SCE, CAM=CAM, DRIFT=DRIFT, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, DOTS=DOTLL, GDOTS=GREENLL, RUN=len(RUN))
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%DOTS%%": dots_html, "%%GDOTS%%": gdots_html, "%%BKK%%": f"{mx(BKK[0])},{my(BKK[1])}", "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "->", SCE[i])
