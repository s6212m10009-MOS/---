"""สร้าง video/index.html ของตอน 034 (ค่าไฟกับสงครามอิหร่าน) จาก lines.py + video/timing_gm.json
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
W, txt, stick, cash, idcard, card = (ns[k] for k in ("W", "txt", "stick", "cash", "idcard", "card"))
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

TAGS = ["สงครามอิหร่าน · <r>ค่าไฟ</r>แพงขึ้นไหม?", "ไฟฟ้าไทย · <r>พึ่งก๊าซ</r>", "LNG <r>28%</r> · กาตาร์+โอมาน", "สงครามเริ่ม · LNG <r>พุ่ง ×2</r>", "ค่าไฟ ก.ย.–ธ.ค. · <r>ตรึง 3.95</r>",
        "<r>เงินสำรอง</r> · ช่วยอุ้ม", "ตัวเลือกสูงสุด <r>4.73</r>", "ย้อน 2022 · <r>4.03 → 4.72</r>", "<r>งวดหน้า</r> · ยังไม่ประกาศ", "<r>3 วิธี</r> · ประหยัดไฟ", "บ้านคุณจ่าย<r>กี่บาท?</r>"]
assert len(TAGS) == N

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
BKK = (100.5, 13.75)
QATAR = (51.2, 25.3)
OMAN = (57.5, 21.5)
GULF = (54.0, 24.0)


def cam_xy(lon, lat, k, py=None):
    if py is None:
        return [round(540 - mx(lon) * k, 1), round(690 - (my(lat) - 900) * k, 1), k]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


WIDE = cam_xy(76, 20, 1.45, 500)
CAM = [WIDE, cam_xy(*BKK, 3.0, 260), cam_xy(*GULF, 3.2, 260), cam_xy(*GULF, 3.2, 260), cam_xy(*BKK, 3.0, 260), cam_xy(*BKK, 3.0, 260), cam_xy(*BKK, 3.0, 260),
       cam_xy(*BKK, 3.0, 260), cam_xy(*BKK, 3.0, 260), cam_xy(*BKK, 3.0, 260), WIDE]
assert len(CAM) == N
DRIFT = CAM[9]
GREENLL = []
CITIES = []
OUTL = json.loads((V / "outlines.json").read_text(encoding="utf-8"))
dots_html = (
    f'<path id="outTh" class="it" d="{OUTL["Thailand"]}" fill="#2fe07a" fill-opacity=".22" stroke="#2fe07a" stroke-width="3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    f'<path id="outIran" class="it" d="{OUTL["Iran"]}" fill="#ffd23f" fill-opacity=".18" stroke="#ffd23f" stroke-width="3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    f'<g id="qdot" class="it" transform="translate({mx(QATAR[0])},{my(QATAR[1])})"><circle r="9" fill="#ffd23f" stroke="#fff" stroke-width="3"/></g>'
    f'<g id="odot" class="it" transform="translate({mx(OMAN[0])},{my(OMAN[1])})"><circle r="9" fill="#ffd23f" stroke="#fff" stroke-width="3"/></g>'
    f'<g id="bdot" class="it" transform="translate({mx(BKK[0])},{my(BKK[1])})"><circle r="11" fill="#e0243a" stroke="#fff" stroke-width="3"/></g>'
)
gdots_html = ""
bx, by = mx(BKK[0]), my(BKK[1])
GRAT = "".join(f"M{mx(lo)},0V1800" for lo in range(-180, 181, 15)) + "".join(f"M0,{my(la)}H3600" for la in range(-90, 91, 15))
ARC = f"M{mx(GULF[0])},{my(GULF[1])} Q{(mx(GULF[0]) + mx(BKK[0])) / 2},{my(-2)} {mx(BKK[0])},{my(BKK[1])}"

_stick = stick


def stick(x, y, s=1.0, col=INK, idn="", fill="#fff"):
    return _stick(x, y, s, "#fff", idn, "#0a1830") if col == INK else _stick(x, y, s, col, idn, fill)


def x_mark(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-50,-50 L50,50 M50,-50 L-50,50" stroke="#e0243a" stroke-width="16" stroke-linecap="round"/></g>')


def tick_mark(x, y, r=40, idn=""):
    return W(idn, f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1f9d55" stroke="{INK}" stroke-width="5"/><path d="M{x - r * .45},{y + 2} L{x - r * .1},{y + r * .38} L{x + r * .5},{y - r * .35}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')


def bill(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-90" y="-120" width="180" height="240" rx="10" fill="#fff" stroke="{INK}" stroke-width="7"/><path d="M-60,-80 H60 M-60,-50 H60 M-60,-20 H30 M-60,10 H60 M-60,40 H20" stroke="#9aa3b5" stroke-width="7" stroke-linecap="round"/><rect x="-60" y="68" width="120" height="34" rx="8" fill="#ffd23f" stroke="{INK}" stroke-width="5"/></g>')


def plant(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-110" y="-10" width="220" height="110" fill="#cfd5e1" stroke="{INK}" stroke-width="7"/><rect x="-80" y="-90" width="42" height="80" fill="#9aa3b5" stroke="{INK}" stroke-width="6"/><rect x="-10" y="-120" width="42" height="110" fill="#9aa3b5" stroke="{INK}" stroke-width="6"/><path d="M60,-10 C40,-60 80,-70 62,-120 C110,-80 100,-40 60,-10Z" fill="#ff8a1f" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><rect x="-30" y="40" width="60" height="60" fill="#6d93c9" stroke="{INK}" stroke-width="5"/></g>')


def bar(x, y, w, h, col, idn=""):
    return W(idn, f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{col}" stroke="{INK}" stroke-width="7"/>')


def coin(x, y, r=34, idn=""):
    return W(idn, f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffd23f" stroke="{INK}" stroke-width="6"/><text x="{x}" y="{y + r * .35}" font-size="{r * 1.1}" font-weight="800" fill="{INK}" text-anchor="middle" font-family="Kanit">฿</text>')


def plug(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-45" y="-50" width="90" height="80" rx="16" fill="#e8eef6" stroke="{INK}" stroke-width="7"/><rect x="-26" y="-85" width="14" height="40" fill="{INK}"/><rect x="12" y="-85" width="14" height="40" fill="{INK}"/><path d="M0,30 V90" stroke="{INK}" stroke-width="10" stroke-linecap="round"/></g>')


def ac(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-120" y="-45" width="240" height="90" rx="22" fill="#e8eef6" stroke="{INK}" stroke-width="7"/><path d="M-90,25 H90" stroke="#9aa3b5" stroke-width="8" stroke-linecap="round"/><path d="M-60,70 q20,30 0,55 M0,70 q20,30 0,55 M60,70 q20,30 0,55" fill="none" stroke="#8fd8ee" stroke-width="8" stroke-linecap="round"/></g>')


BG = ''
VG = {
    1: (plant(280, 260, 1.7, "b2p") + txt(700, 190, "ก๊าซธรรมชาติ", 64, "#ffd23f", "b2t") + txt(700, 280, "ผลิตไฟฟ้าหลัก", 56, "#fff", "b2u") + txt(700, 380, "ต้องนำเข้า LNG", 46, "#fff", "b2v"), False),
    2: (txt(480, 230, "28%", 240, "#ffd23f", "c3n") + txt(480, 340, "ของ LNG ที่นำเข้า", 54, "#fff", "c3t") + txt(480, 420, "มาจากกาตาร์ + โอมาน", 50, "#8fd8ee", "c3u") + txt(480, 490, "ข้อมูลปี 2025", 34, "#fff", "c3v"), False),
    3: (bar(260, 300, 140, 130, "#7fb6ee", "d4a") + bar(560, 70, 140, 360, "#e0243a", "d4b") + txt(330, 480, "ก่อน", 40, "#fff", "d4c") + txt(630, 480, "หลังสงครามเริ่ม", 40, "#fff", "d4d") + txt(630, 50, "×2 ขึ้นไป", 60, "#ffd23f", "d4e"), False),
    4: (txt(480, 230, "3.95", 250, "#ffd23f", "e5n") + txt(480, 330, "บาท/หน่วย", 64, "#fff", "e5t") + txt(480, 410, "ค่าไฟเฉลี่ย ก.ย.–ธ.ค.", 44, "#8fd8ee", "e5u") + txt(480, 480, "กกพ. ตรึงไว้", 44, "#fff", "e5v"), False),
    5: (coin(180, 330, 60, "f6a") + coin(300, 300, 60, "f6b") + coin(420, 330, 60, "f6c") + coin(240, 410, 60, "f6d") + coin(360, 420, 60, "f6e") + txt(700, 220, "เงินสำรอง", 64, "#fff", "f6t") + txt(700, 320, "~16,000", 90, "#ffd23f", "f6n") + txt(700, 400, "ล้านบาท", 52, "#fff", "f6u"), False),
    6: (bar(220, 260, 170, 150, "#7fb6ee", "g7a") + bar(520, 150, 170, 260, "#e0243a", "g7b") + txt(305, 235, "3.95", 56, "#fff", "g7c") + txt(605, 125, "4.73", 56, "#ffd23f", "g7d") + txt(305, 470, "ที่จ่ายจริง", 40, "#fff", "g7e") + txt(605, 470, "ตัวเลือกสูงสุด", 40, "#fff", "g7f"), False),
    7: (txt(480, 120, "สงครามรัสเซีย–ยูเครน · 2022", 44, "#fff", "h8a") + txt(220, 300, "4.03", 120, "#7fb6ee", "h8b") + W("h8c", '<path d="M370,270 H570" stroke="#ffd23f" stroke-width="14" stroke-linecap="round"/><path d="M530,230 L580,270 L530,310" fill="none" stroke="#ffd23f" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>') + txt(740, 300, "4.72", 120, "#e0243a", "h8d") + txt(480, 440, "บาท/หน่วย", 46, "#fff", "h8e"), False),
    8: (bar(240, 90, 480, 220, "#ffd23f", "i9a") + txt(480, 220, "งวดหน้า ?", 100, "#111", "i9b") + txt(480, 370, "ยังไม่ประกาศ", 60, "#fff", "i9c") + txt(480, 450, "ค่าไฟอาจขยับ", 52, "#e0243a", "i9d"), False),
    9: (plug(190, 250, 1.3, "j10p") + txt(190, 440, "ถอดปลั๊ก", 44, "#fff", "j10a") + ac(480, 240, 1.0, "j10c") + txt(480, 440, "แอร์พอดี", 44, "#fff", "j10b") + bill(770, 250, 0.9, "j10d") + txt(770, 440, "เช็กบิล", 44, "#fff", "j10e"), False),
}
assert sorted(VG) == list(range(1, N - 1))
VG[N - 1] = (stick(480, 310, 1.6, INK, "k11s") + W("k11q", f'<circle cx="480" cy="170" r="70" fill="#ffd23f" stroke="{INK}" stroke-width="7"/>' + txt(480, 205, "?", 100, "#111")) + txt(480, 508, "คอมเมนต์ไว้", 36, "#fff", "k11t"), False)
assert sorted(VG) == list(range(1, N))
CUSTOM = {"d4a", "d4b", "g7a", "g7b"}
ITEMS = {i: [x for x in re.findall(r'id="([A-Za-z0-9_]+)" class="it"', VG[i][0]) if x not in CUSTOM] for i in VG}
VGS = "\n".join(card(f"vg{i}", VG[i][0], VG[i][1]) for i in sorted(VG))
tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))
(V / "items.json").write_text(json.dumps({str(k): len(v) for k, v in ITEMS.items()}))

DATA = dict(SC=SC, SCE=SCE, CAM=CAM, DRIFT=DRIFT, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, GDOTS=GREENLL, ITEMS=ITEMS, NR=0)
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%DOTS%%": dots_html, "%%ARC%%": ARC, "%%GDOTS%%": gdots_html, "%%BKK%%": f"{bx},{by}", "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "->", SCE[i])
