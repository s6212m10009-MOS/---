"""สร้าง video/index.html ของตอน 030 (What If แอปธนาคารล่ม 24 ชั่วโมง) จาก lines.py + video/timing_gm.json
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

bag = ns["bag"]
TAGS = ["What If · <r>แอปล่ม 24 ชม.</r>", "<r>เคยเกิดจริง</r> · พร้อมเพย์", "<r>สแกนจ่ายไม่ได้</r> · เงินสดเท่านั้น", "ขั้น 1 · <r>รายจ่ายต่อวัน</r>", "ขั้น 2 · <r>เงินสดต่อวัน</r>",
        "ขั้น 3 · <r>เผื่อ 3 วัน</r>", "<r>แบงก์ย่อย</r> · เงินทอน", "<r>แบ่งเก็บ</r>หลายที่", "<r>บัตรสำรอง</r> · ไม่พึ่งแอปเดียว", "<r>เบอร์ธนาคาร</r> · แหล่งทางการ",
        "<r>เงินยังอยู่</r> · ไม่ต้องแห่ถอน", "<r>ไม่ตื่นตระหนก</r>", "<r>เงินสด</r>ติดบ้านเท่าไร?"]
assert len(TAGS) == N

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
BKK = (100.5, 13.75)


def cam_xy(lon, lat, k, py=None):
    if py is None:
        return [round(540 - mx(lon) * k, 1), round(690 - (my(lat) - 900) * k, 1), k]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


A, B, C, Dd, E = cam_xy(100.5, 14.5, 2.2, 260), cam_xy(*BKK, 2.6, 260), cam_xy(*BKK, 3.0, 260), cam_xy(100.5, 16, 2.2, 260), cam_xy(101, 13, 3.0, 260)
CAM = [cam_xy(100.5, 15, 1.9, 500), A, A, B, B, B, C, C, C, Dd, Dd, Dd, E]
assert len(CAM) == N
DRIFT = CAM[11]

CITIES = [(100.5, 13.75), (98.99, 18.79), (98.4, 7.88), (102.83, 16.43), (100.47, 7.0), (101.3, 12.7), (99.9, 15.1), (104.8, 15.2), (100.0, 17.6), (102.1, 14.0), (98.98, 12.9), (100.9, 16.8)]
GREENLL = CITIES
OUTL = json.loads((V / "outlines.json").read_text(encoding="utf-8"))
bx, by = mx(BKK[0]), my(BKK[1])
dots_html = (
    f'<path id="outTh" class="it" d="{OUTL["Thailand"]}" fill="#2fe07a" fill-opacity=".10" stroke="#2fe07a" stroke-width="3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    + "".join(f'<g class="rdot it" id="rd{k}" transform="translate({mx(lo)},{my(la)})"><circle r="9" fill="#e0243a" stroke="#fff" stroke-width="2.5"/></g>' for k, (lo, la) in enumerate(CITIES))
)
gdots_html = "".join(f'<g id="gd{k}" class="gdot" transform="translate({mx(lo)},{my(la)})"><circle r="8" fill="#2fe07a" stroke="#fff" stroke-width="2.5"/></g>' for k, (lo, la) in enumerate(GREENLL))

_stick = stick


def stick(x, y, s=1.0, col=INK, idn="", fill="#fff"):
    return _stick(x, y, s, "#fff", idn, "#0a1830") if col == INK else _stick(x, y, s, col, idn, fill)


def x_mark(x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})"><path d="M-50,-50 L50,50 M50,-50 L-50,50" stroke="#e0243a" stroke-width="16" stroke-linecap="round"/></g>'


def tick_mark(x, y, r=40, idn=""):
    return W(idn, f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1f9d55" stroke="{INK}" stroke-width="5"/><path d="M{x - r * .45},{y + 2} L{x - r * .1},{y + r * .38} L{x + r * .5},{y - r * .35}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')


def phone(x, y, s=1.0, label="", idn=""):
    inner = f'<g transform="translate({x},{y}) scale({s})"><rect x="-90" y="-170" width="180" height="340" rx="30" fill="#2a2d3a" stroke="{INK}" stroke-width="7"/><rect x="-74" y="-130" width="148" height="250" rx="8" fill="#cfe8d4"/></g>'
    return W(idn, inner + (txt(x, y + 8 * s, label, int(60 * s), "#111") if label else ""))


def banknote(x, y, val, col, rot=0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) rotate({rot})"><rect x="-110" y="-60" width="220" height="120" rx="10" fill="{col}" stroke="{INK}" stroke-width="6"/><circle cx="0" cy="0" r="38" fill="none" stroke="#fff" stroke-width="5" opacity=".7"/></g>' + txt(x, y + 22, val, 64, "#111"))


BG = ''
VG = {
    1: (phone(300, 270, 1.0, "ล่ม", "a1p") + W("a1x", x_mark(300, 250, 1.3))
        + W("a1c", f'<circle cx="680" cy="250" r="110" fill="#fff" stroke="{INK}" stroke-width="8"/><path d="M680,250 V170 M680,250 L735,285" stroke="{INK}" stroke-width="10" stroke-linecap="round"/><circle cx="680" cy="250" r="9" fill="{INK}"/>')
        + txt(680, 420, "นานหลายชั่วโมง", 42, "#fff", "a1t"), False),
    2: (W("b2q", f'<rect x="90" y="100" width="260" height="260" rx="16" fill="#fff" stroke="{INK}" stroke-width="8"/><rect x="115" y="125" width="70" height="70" fill="{INK}"/><rect x="255" y="125" width="70" height="70" fill="{INK}"/><rect x="115" y="265" width="70" height="70" fill="{INK}"/><rect x="215" y="225" width="35" height="35" fill="{INK}"/><rect x="270" y="280" width="40" height="40" fill="{INK}"/><rect x="215" y="140" width="25" height="25" fill="{INK}"/>')
        + W("b2x", x_mark(220, 230, 1.8))
        + W("b2s", f'<rect x="520" y="130" width="340" height="230" rx="20" fill="#ffd23f" stroke="{INK}" stroke-width="8"/>' + txt(690, 245, "เงินสด", 82, "#111") + txt(690, 325, "เท่านั้น", 52, "#111"))
        + txt(220, 450, "สแกนจ่าย", 38, "#fff", "b2t"), False),
    3: (W("c3a", f'<path d="M80,240 H220 Q220,340 150,340 Q80,340 80,240Z" fill="#fff" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><path d="M110,215 q10,-30 20,0 M150,210 q10,-34 20,0" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round"/>') + txt(150, 420, "อาหาร", 34, "#fff", "c3l1")
        + W("c3b", f'<rect x="270" y="190" width="200" height="130" rx="18" fill="#f08a1c" stroke="{INK}" stroke-width="7"/><rect x="290" y="210" width="60" height="45" fill="#cfe8d4"/><rect x="370" y="210" width="80" height="45" fill="#cfe8d4"/><circle cx="320" cy="330" r="18" fill="{INK}"/><circle cx="430" cy="330" r="18" fill="{INK}"/>') + txt(370, 420, "เดินทาง", 34, "#fff", "c3l2")
        + W("c3c", f'<g transform="translate(590,250) scale(0.9)"><rect x="-50" y="-80" width="100" height="160" rx="14" fill="#e0243a" stroke="{INK}" stroke-width="6"/><rect x="-34" y="-62" width="68" height="40" rx="6" fill="#cfe8d4" stroke="{INK}" stroke-width="4"/><path d="M50,-40 Q90,-40 90,0 V50" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/></g>') + txt(590, 420, "น้ำมัน", 34, "#fff", "c3l3")
        + W("c3d", f'<rect x="760" y="215" width="130" height="62" rx="31" fill="#fff" stroke="{INK}" stroke-width="7" transform="rotate(-30 825 246)"/><path d="M825,215 L825,277" stroke="{INK}" stroke-width="6" transform="rotate(-30 825 246)"/>') + txt(825, 420, "ยา", 34, "#fff", "c3l4"), False),
    4: (txt(480, 70, "บาท ต่อวัน", 40, "#fff", "d4u")
        + stick(230, 250, 1.3, INK, "d4a") + txt(230, 410, "คนเดียว", 36, "#fff", "d4l1") + txt(230, 480, "500–1,000", 60, "#ffd23f", "d4n1")
        + stick(600, 270, 0.8, INK, "d4b1") + stick(670, 270, 0.8, INK, "d4b2") + stick(740, 270, 0.8, INK, "d4b3") + stick(810, 270, 0.8, INK, "d4b4")
        + txt(705, 400, "ครอบครัว 4 คน", 36, "#fff", "d4l2") + txt(705, 480, "2,000–3,000", 60, "#ffd23f", "d4n2"), False),
    5: (W("e5c", f'<rect x="120" y="140" width="320" height="290" rx="22" fill="#fff" stroke="{INK}" stroke-width="8"/><rect x="120" y="140" width="320" height="75" rx="22" fill="#e0243a" stroke="{INK}" stroke-width="8"/>') + txt(280, 355, "3 วัน", 110, "#111", "e5d")
        + txt(660, 300, "×3", 190, "#ffd23f", "e5x") + txt(660, 410, "เผื่อสามวัน", 42, "#fff", "e5u"), False),
    6: (banknote(190, 250, "20", "#8fd19e", -8, "f6a") + banknote(480, 230, "50", "#7fb6ee", 4, "f6b") + banknote(770, 250, "100", "#ee8c8c", -5, "f6c")
        + txt(480, 90, "แบงก์ย่อย", 70, "#ffd23f", "f6t") + txt(480, 430, "ร้านค้าอาจไม่มีเงินทอน", 40, "#fff", "f6u"), False),
    7: (W("g7a", f'<path d="M80,260 L220,150 L360,260 V400 H80Z" fill="#c4883a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><rect x="190" y="310" width="60" height="90" fill="#6d4a1f" stroke="{INK}" stroke-width="5"/>') + txt(220, 460, "ที่บ้าน", 34, "#fff", "g7l1")
        + W("g7b", f'<rect x="420" y="240" width="190" height="130" rx="22" fill="#6d4a1f" stroke="{INK}" stroke-width="7"/><rect x="540" y="285" width="70" height="40" rx="14" fill="#c4883a" stroke="{INK}" stroke-width="5"/>') + txt(515, 430, "กระเป๋าตัง", 34, "#fff", "g7l2")
        + bag(780, 270, 0.9, "g7c") + txt(780, 430, "ติดตัว", 34, "#fff", "g7l3") + txt(480, 70, "แบ่งเก็บหลายที่", 52, "#ffd23f", "g7t"), False),
    8: (W("h8a", f'<rect x="90" y="180" width="330" height="200" rx="22" fill="#2a5fb0" stroke="{INK}" stroke-width="8"/><rect x="90" y="220" width="330" height="48" fill="{INK}"/><rect x="120" y="310" width="110" height="26" rx="6" fill="#fff"/>') + txt(255, 440, "บัตรสำรอง", 36, "#fff", "h8l")
        + phone(700, 260, 0.9, "", "h8b") + W("h8x", x_mark(700, 250, 1.1)) + tick_mark(420, 170, 40, "h8c"), False),
    9: (W("i9a", f'<path d="M100,340 q0,-130 90,-160 l40,70 l-44,28 q30,60 70,86 l36,-46 l70,40 q-20,100 -120,70 q-120,-30 -142,-88Z" fill="#fff" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>') + txt(250, 450, "ศูนย์บริการ", 36, "#fff", "i9l")
        + W("i9b", f'<rect x="560" y="110" width="280" height="320" rx="14" fill="#ffd23f" stroke="{INK}" stroke-width="7"/><path d="M590,180 H810 M590,240 H810 M590,300 H810 M590,360 H760" stroke="{INK}" stroke-width="5"/>') + txt(700, 90, "จดเบอร์ไว้", 44, "#ffd23f", "i9t"), False),
    10: (W("j10a", f'<path d="M180,190 L330,100 L480,190Z" fill="#c4883a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><rect x="200" y="200" width="260" height="30" fill="#e8eef6" stroke="{INK}" stroke-width="5"/><rect x="215" y="235" width="36" height="120" fill="#e8eef6" stroke="{INK}" stroke-width="5"/><rect x="290" y="235" width="36" height="120" fill="#e8eef6" stroke="{INK}" stroke-width="5"/><rect x="365" y="235" width="36" height="120" fill="#e8eef6" stroke="{INK}" stroke-width="5"/><rect x="190" y="360" width="280" height="30" fill="#e8eef6" stroke="{INK}" stroke-width="5"/>')
         + tick_mark(640, 180, 70, "j10c") + txt(640, 330, "เงินยังอยู่", 66, "#1f9d55", "j10t") + txt(640, 410, "แค่ใช้ผ่านระบบไม่ได้ชั่วคราว", 34, "#fff", "j10u"), False),
    11: (stick(300, 330, 1.7, INK, "k11s") + W("k11a", f'<path d="M300,276 L250,200 M300,276 L350,200" stroke="#fff" stroke-width="12" stroke-linecap="round"/>') + tick_mark(660, 200, 70, "k11c")
         + txt(660, 340, "เตรียมแค่พอใช้", 56, "#1f9d55", "k11t") + txt(660, 420, "ไม่ตื่นตระหนก", 44, "#fff", "k11u"), False),
    12: (stick(480, 310, 1.6, INK, "l12s") + W("l12q", f'<circle cx="480" cy="170" r="70" fill="#ffd23f" stroke="{INK}" stroke-width="7"/>' + txt(480, 205, "?", 100, "#111")) + txt(480, 508, "พิมพ์ตอบในคอมเมนต์", 36, "#fff", "l12t"), False),
}
assert sorted(VG) == list(range(1, N))
ITEMS = {i: re.findall(r'id="([A-Za-z0-9_]+)" class="it"', VG[i][0]) for i in VG}
VGS = "\n".join(card(f"vg{i}", VG[i][0], VG[i][1]) for i in sorted(VG))
tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))
(V / "items.json").write_text(json.dumps({str(k): len(v) for k, v in ITEMS.items()}))

DATA = dict(SC=SC, SCE=SCE, CAM=CAM, DRIFT=DRIFT, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, GDOTS=GREENLL, ITEMS=ITEMS, NR=len(CITIES))
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%DOTS%%": dots_html, "%%GDOTS%%": gdots_html, "%%BKK%%": f"{bx},{by}", "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "->", SCE[i])
