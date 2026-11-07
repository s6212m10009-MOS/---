"""สร้าง video/index.html ของตอน 028 (What If ถ้าสหรัฐใช้นิวเคลียร์กับอิหร่าน) จาก lines.py + video/timing_gm.json
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

TAGS = ["WHAT IF · <r>สมมติ</r>", "<r>ครั้งแรก</r> ตั้งแต่ 1945", "กัมมันตรังสี · <r>รอบอิหร่าน</r>", "<r>ทูต</r> · ตอบโต้ · แข่งอาวุธ", "ฮอร์มุซ · <r>น้ำมันพุ่ง</r>",
        "ไทย · <r>ความเสี่ยงต่ำ</r>", "ผลที่<r>หนักกว่า</r> · เศรษฐกิจ", "เตรียม · <r>เงินสำรอง</r>", "ข่าว · <r>ทางการ</r>", "<r>ตื่นตัว</r> ไม่ตื่นตระหนก"]

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
BKK = (100.5, 13.75)
IRAN = (53, 32)
HORMUZ = (56.3, 26.5)


def cam_xy(lon, lat, k, py=None):
    if py is None:
        return [round(540 - mx(lon) * k, 1), round(690 - (my(lat) - 900) * k, 1), k]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


WORLD = cam_xy(20, 15, 0.55)
CAM = [cam_xy(*IRAN, 2.0, 500)] + [cam_xy(*IRAN, 2.2, 260)] * 4 + [cam_xy(77, 24, 1.8, 300)] + [cam_xy(*BKK, 2.4, 260)] * 3 + [cam_xy(101, 13, 3.0, 260)]
DRIFT = cam_xy(*BKK, 2.7, 260)

GREENLL = [(100.5, 13.75), (98.99, 18.79), (98.4, 7.88), (102.83, 16.43), (100.47, 7.0), (101.3, 12.7), (99.9, 15.1), (104.8, 15.2), (100.0, 17.6), (102.1, 14.0), (98.98, 12.9), (100.9, 16.8)]
OUTL = json.loads((V / "outlines.json").read_text(encoding="utf-8"))
ix, iy, hx, hy, bx, by = mx(IRAN[0]), my(IRAN[1]), mx(HORMUZ[0]), my(HORMUZ[1]), mx(BKK[0]), my(BKK[1])
dots_html = (
    f'<g transform="translate({ix},{iy})"><circle id="ring3" class="it" r="20" fill="#e0243a" fill-opacity=".12" stroke="#e0243a" stroke-width="3" vector-effect="non-scaling-stroke" stroke-dasharray="14 10"/>'
    f'<circle id="ring2" class="it" r="20" fill="#e0243a" fill-opacity=".16" stroke="#e0243a" stroke-width="3" vector-effect="non-scaling-stroke"/>'
    f'<circle id="iran" class="it" r="16" fill="#e0243a" stroke="#fff" stroke-width="5"/></g>'
    f'<g transform="translate({hx},{hy})"><circle id="horm" class="it" r="12" fill="#ffd23f" stroke="#1e1e24" stroke-width="4"/></g>'
    f'<path id="outIran" class="it" d="{OUTL["Iran"]}" fill="#ffd23f" fill-opacity=".08" stroke="#ffd23f" stroke-width="3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    f'<path id="outTh" class="it" d="{OUTL["Thailand"]}" fill="#2fe07a" fill-opacity=".10" stroke="#2fe07a" stroke-width="3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    f'<path id="dist" class="it" d="M{ix},{iy} L{bx},{by}" pathLength="1" fill="none" stroke="#ffd23f" stroke-width="5" stroke-dasharray="1" stroke-dashoffset="1" vector-effect="non-scaling-stroke"/>'
)
gdots_html = "".join(f'<g id="gd{k}" class="gdot" transform="translate({mx(lo)},{my(la)})"><circle r="8" fill="#2fe07a" stroke="#fff" stroke-width="2.5"/></g>' for k, (lo, la) in enumerate(GREENLL))


_stick = stick


def stick(x, y, s=1.0, col=INK, idn="", fill="#fff"):
    return _stick(x, y, s, "#fff", idn, "#0a1830") if col == INK else _stick(x, y, s, col, idn, fill)


def x_mark(x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})"><path d="M-50,-50 L50,50 M50,-50 L-50,50" stroke="#e0243a" stroke-width="16" stroke-linecap="round"/></g>'


def tick_mark(x, y, r=40, idn=""):
    return W(idn, f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1f9d55" stroke="{INK}" stroke-width="5"/><path d="M{x - r * .45},{y + 2} L{x - r * .1},{y + r * .38} L{x + r * .5},{y - r * .35}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')


def pill(x, y, w, label, col="#fff", fg=INK, idn=""):
    return W(idn, f'<rect x="{x - w / 2}" y="{y - 36}" width="{w}" height="72" rx="36" fill="{col}" stroke="{INK}" stroke-width="6"/>' + txt(x, y + 16, label, 40, fg))


BG = ''
DK = ''
VG = {
    1: (DK + txt(480, 330, "1945", 230, "#ffd23f", "v1t") + txt(480, 100, "ครั้งสุดท้ายที่ใช้ในสงคราม", 42, "#fff", "v1u") + txt(480, 460, "แล้ว 2026 ?", 66, "#e0243a", "v1w") + W("v1l", '<path d="M200,375 H760" stroke="#fff" stroke-width="6" stroke-dasharray="14 10"/>'), True),
    2: (DK
        + txt(480, 78, "กัมมันตรังสีอาจกระจาย", 48, "#ffd23f", "v2t")
        + "".join(stick(x, y, 0.8, "#7a7f99", f"v2p{k}", "#0d1226") for k, (x, y) in enumerate([(150, 330), (810, 330), (200, 160), (760, 150)])), True),
    3: (BG + pill(190, 90, 280, "รัสเซีย", "#0a1830", INK, "v3a") + pill(770, 90, 280, "จีน", "#0a1830", INK, "v3b")
        + W("v3c", f'<path d="M190,140 L430,230 M770,140 L530,230" stroke="#fff" stroke-width="7" stroke-linecap="round"/>') + txt(480, 262, "ตอบโต้ทางการทูต", 44, "#e0243a", "v3d")
        + "".join(W(f"v3g{k}", f'<rect x="{150 + k * 170}" y="{430 - 25 * (k + 1)}" width="110" height="{25 * (k + 1)}" fill="#e0243a" stroke="{INK}" stroke-width="5"/>') for k in range(4))
        + txt(480, 500, "ประเทศที่อยากมีอาวุธ ↑", 30, "#555", "v3e"), False),
    4: (BG + W("v4b", f'<rect x="60" y="150" width="170" height="230" rx="26" fill="#5a4a42" stroke="{INK}" stroke-width="7"/><path d="M60,210 H230 M60,320 H230" stroke="{INK}" stroke-width="6"/>' + txt(145, 285, "น้ำมัน", 40, "#fff"))
        + W("v4c", f'<path d="M330,380 L430,340 L500,360 L600,250 L680,270 L850,110" fill="none" stroke="#e0243a" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/><path d="M820,100 L860,100 L860,140" fill="none" stroke="#e0243a" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>')
        + txt(560, 70, "ราคาน้ำมัน พุ่ง", 46, "#e0243a", "v4t") + txt(480, 450, "ฮอร์มุซ ~1 ใน 4 ของน้ำมันโลก", 36, "#555", "v4u"), False),
    5: (BG + W("v5a", '<circle cx="150" cy="200" r="34" fill="#e0243a" stroke="#1e1e24" stroke-width="6"/>') + txt(150, 290, "อิหร่าน", 36)
        + W("v5b", '<circle cx="810" cy="200" r="34" fill="#1f9d55" stroke="#1e1e24" stroke-width="6"/>') + txt(810, 290, "ไทย", 36)
        + W("v5l", f'<path d="M200,200 H760" stroke="#fff" stroke-width="8" stroke-dasharray="18 14"/>') + txt(480, 170, "ไกล", 64, "#1f9d55", "v5t")
        + W("v5x", f'<rect x="360" y="360" width="240" height="90" rx="18" fill="#c9ced6" stroke="{INK}" stroke-width="6"/>' + x_mark(480, 405, 0.9)) + txt(480, 490, "ไม่ต้องสร้างหลุมหลบภัย", 34, "#555", "v5u"), False),
    6: (BG + "".join(W(f"v6i{k}", f'<rect x="{x - 80}" y="100" width="160" height="200" rx="26" fill="{c}" stroke="{INK}" stroke-width="7"/>' + txt(x, 230, g, 84, "#fff")) + txt(x, 380, lab, 32, "#555", f"v6l{k}")
                for k, (x, c, g, lab) in enumerate([(120, "#e0243a", "⛽", "น้ำมันแพง"), (360, "#f08a1c", "↑", "ค่าครองชีพ"), (600, "#2d6ae0", "฿", "บาทผันผวน"), (840, "#37b3a6", "✈", "ท่องเที่ยวชะลอ")])), False),
    7: (BG + cash(150, 330, 1.2, "v7a") + cash(150, 270, 1.2, "v7b") + cash(150, 210, 1.2, "v7c") + txt(150, 440, "เงินสำรอง", 36, "#555", "v7l")
        + W("v7m", f'<rect x="330" y="120" width="190" height="190" rx="22" fill="#fff" stroke="{INK}" stroke-width="7"/><rect x="330" y="120" width="190" height="55" rx="22" fill="#e0243a" stroke="{INK}" stroke-width="7"/>' + txt(425, 270, "3-6", 80, "#111")) + txt(425, 350, "เดือน", 40, "#555", "v7n")
        + stick(700, 340, 1.0, INK, "v7s") + W("v7k", f'<rect x="760" y="260" width="120" height="80" rx="10" fill="#c9ced6" stroke="{INK}" stroke-width="6"/><circle cx="785" cy="365" r="12" fill="{INK}"/><circle cx="855" cy="365" r="12" fill="{INK}"/>') + W("v7x", x_mark(780, 220, 0.9)) + txt(780, 440, "ไม่แห่ตุน", 36, "#e0243a", "v7t"), False),
    8: (BG + W("v8p", f'<rect x="90" y="90" width="200" height="330" rx="34" fill="#2a2d3a" stroke="{INK}" stroke-width="7"/><rect x="108" y="130" width="164" height="240" rx="10" fill="#cfe8d4"/>' + txt(190, 220, "ข่าว", 40, "#111") + txt(190, 270, "ทางการ", 34, "#111"))
        + tick_mark(290, 110, 36, "v8c") + idcard(560, 230, 1.7, "v8i") + txt(560, 370, "ประกาศ กต.", 36, "#555", "v8j") + txt(190, 460, "แหล่งทางการ", 32, "#555", "v8k")
        + stick(810, 340, 1.2, INK, "v8s") + txt(810, 460, "ญาติอยู่แถวนั้น", 30, "#555", "v8l"), False),
    9: (BG + stick(300, 330, 1.7, INK, "v9s") + W("v9a", f'<path d="M300,276 L250,200 M300,276 L350,200" stroke="#fff" stroke-width="12" stroke-linecap="round"/>') + tick_mark(660, 200, 70, "v9c")
        + txt(660, 340, "ตื่นตัว", 64, "#1f9d55", "v9t") + txt(660, 420, "ไม่ตื่นตระหนก", 44, "#555", "v9u"), False),
}
VGS = "\n".join(card(f"vg{i}", VG[i][0], VG[i][1]) for i in sorted(VG))
tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))

DATA = dict(SC=SC, SCE=SCE, CAM=CAM, DRIFT=DRIFT, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, GDOTS=GREENLL)
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE,  "%%DOTS%%": dots_html, "%%GDOTS%%": gdots_html, "%%BKK%%": f"{bx},{by}", "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "->", SCE[i])
