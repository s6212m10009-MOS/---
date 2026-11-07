"""สร้าง video/index.html ของตอน 033 (กลางเทอมสหรัฐกับสงครามอิหร่าน) จาก lines.py + video/timing_gm.json
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

TAGS = ["ทรัมป์<r>แพ้</r>เลือกตั้ง?", "<r>กลางเทอม</r> · เลือกสภา", "ทรัมป์อยู่ถึง <r>ม.ค. 2029</r>", "<r>ผลเบื้องต้น</r> · เดโมแครตนำ", "<r>เสียงสะท้อน</r>ต่อสงครามอิหร่าน",
        "<r>มติสงคราม</r> · สภาล่างผ่าน", "วุฒิสภา · <r>ตกไป 1 เสียง</r>", "ถ้าคุมวุฒิสภา · <r>ผ่านง่ายขึ้น</r>", "<r>วีโต้</r> · ต้อง 2 ใน 3", "สภาใหม่ <r>ต้นปีหน้า</r>",
        "<r>ฮอร์มุซ</r> · น้ำมัน · ค่าครองชีพ", "สงคราม<r>จบเร็วขึ้น</r>ไหม?"]
assert len(TAGS) == N

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
DC = (-77.0, 38.9)
IRAN = (53.0, 32.0)
HORMUZ = (56.5, 26.5)


def cam_xy(lon, lat, k, py=None):
    if py is None:
        return [round(540 - mx(lon) * k, 1), round(690 - (my(lat) - 900) * k, 1), k]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


WIDE = cam_xy(-12, 36, 0.72, 500)
CAM = [WIDE, cam_xy(*DC, 3.0, 260), cam_xy(*DC, 3.0, 260), cam_xy(*DC, 3.0, 260), cam_xy(*IRAN, 2.4, 260), cam_xy(*DC, 3.0, 260),
       cam_xy(*DC, 3.0, 260), cam_xy(*DC, 3.0, 260), cam_xy(*DC, 3.0, 260), cam_xy(*DC, 3.0, 260), cam_xy(*HORMUZ, 3.4, 260), WIDE]
assert len(CAM) == N
DRIFT = CAM[10]
GREENLL = []
CITIES = []
OUTL = json.loads((V / "outlines.json").read_text(encoding="utf-8"))
dots_html = (
    f'<path id="outIran" class="it" d="{OUTL["Iran"]}" fill="#ffd23f" fill-opacity=".10" stroke="#ffd23f" stroke-width="3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    f'<g id="usdot" class="it" transform="translate({mx(DC[0])},{my(DC[1])})"><circle r="12" fill="#4a8cff" stroke="#fff" stroke-width="3"/><circle class="ring" r="12" fill="none" stroke="#4a8cff" stroke-width="3"/></g>'
    f'<g id="irdot" class="it" transform="translate({mx(IRAN[0])},{my(IRAN[1])})"><circle r="10" fill="#ffd23f" stroke="#fff" stroke-width="3"/></g>'
    f'<g id="hmdot" class="it" transform="translate({mx(HORMUZ[0])},{my(HORMUZ[1])})"><circle r="8" fill="#e0243a" stroke="#fff" stroke-width="2.5"/></g>'
)
gdots_html = ""
bx, by = mx(DC[0]), my(DC[1])
GRAT = "".join(f"M{mx(lo)},0V1800" for lo in range(-180, 181, 15)) + "".join(f"M0,{my(la)}H3600" for la in range(-90, 91, 15))
ARC = f"M{mx(DC[0])},{my(DC[1])} Q{(mx(DC[0]) + mx(IRAN[0])) / 2},{my(60)} {mx(IRAN[0])},{my(IRAN[1])}"

_stick = stick


def stick(x, y, s=1.0, col=INK, idn="", fill="#fff"):
    return _stick(x, y, s, "#fff", idn, "#0a1830") if col == INK else _stick(x, y, s, col, idn, fill)


def x_mark(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-50,-50 L50,50 M50,-50 L-50,50" stroke="#e0243a" stroke-width="16" stroke-linecap="round"/></g>')


def tick_mark(x, y, r=40, idn=""):
    return W(idn, f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1f9d55" stroke="{INK}" stroke-width="5"/><path d="M{x - r * .45},{y + 2} L{x - r * .1},{y + r * .38} L{x + r * .5},{y - r * .35}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')


def capitol(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-70,-40 Q0,-130 70,-40Z" fill="#e8eef6" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><rect x="-6" y="-120" width="12" height="40" fill="{INK}"/><rect x="-110" y="-40" width="220" height="30" fill="#e8eef6" stroke="{INK}" stroke-width="7"/>' + "".join(f'<rect x="{cx}" y="-10" width="18" height="70" fill="#e8eef6" stroke="{INK}" stroke-width="5"/>' for cx in range(-90, 91, 36)) + f'<rect x="-120" y="60" width="240" height="22" fill="#cfd5e1" stroke="{INK}" stroke-width="7"/></g>')


def ballot(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-90" y="-20" width="180" height="140" rx="12" fill="#4a8cff" stroke="{INK}" stroke-width="8"/><rect x="-55" y="-8" width="110" height="14" rx="7" fill="{INK}"/><rect x="-40" y="-90" width="80" height="100" fill="#fff" stroke="{INK}" stroke-width="6" transform="rotate(-8)"/><path d="M-22,-62 H22 M-22,-42 H22 M-22,-22 H8" stroke="{INK}" stroke-width="6" stroke-linecap="round" transform="rotate(-8)"/></g>')


def bar(x, y, w, h, col, idn=""):
    return W(idn, f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{col}" stroke="{INK}" stroke-width="7"/>')


def barrel(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-55" y="-75" width="110" height="150" rx="18" fill="#2b2f3c" stroke="{INK}" stroke-width="7"/><path d="M-55,-30 H55 M-55,30 H55" stroke="#ffd23f" stroke-width="8"/></g>')


BG = ''
VG = {
    1: (ballot(250, 250, 1.6, "a1b") + txt(690, 200, "เลือกสภา", 80, "#4a8cff", "a1t") + stick(690, 360, 1.0, INK, "a1s") + x_mark(790, 320, 0.9, "a1x") + txt(690, 470, "ไม่ใช่ประธานาธิบดี", 40, "#fff", "a1u"), False),
    2: (bar(80, 140, 190, 130, "#cfd5e1", "b2a") + bar(300, 140, 190, 130, "#ffd23f", "b2b") + bar(520, 140, 190, 130, "#ffd23f", "b2c") + bar(740, 140, 140, 130, "#cfd5e1", "b2d")
        + txt(175, 230, "ปี 1", 54, "#111", "b2e") + txt(395, 230, "ปี 2", 54, "#111", "b2f") + txt(615, 230, "ปี 3", 54, "#111", "b2g") + txt(810, 230, "ปี 4", 54, "#111", "b2h")
        + txt(480, 340, "กลางเทอม = ครึ่งทาง", 48, "#ffd23f", "b2i") + txt(480, 440, "ทรัมป์อยู่ถึง ม.ค. 2029", 46, "#fff", "b2j"), False),
    3: (bar(120, 100, 700, 110, "#4a8cff", "c3a") + txt(470, 180, "สภาล่าง · เดโมแครตนำ", 52, "#fff", "c3b") + bar(120, 250, 700, 110, "#4a8cff", "c3c") + txt(470, 330, "วุฒิสภา · เดโมแครตนำ", 52, "#fff", "c3d")
        + txt(480, 450, "ผลเบื้องต้น · ยังเปลี่ยนได้", 42, "#ffd23f", "c3e"), False),
    4: (capitol(230, 260, 1.5, "d4c") + W("d4b", f'<path d="M520,150 H900 a30,30 0 0 1 30,30 v90 a30,30 0 0 1 -30,30 H640 l-50,45 v-45 H520 a30,30 0 0 1 -30,-30 v-90 a30,30 0 0 1 30,-30Z" fill="#fff" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>') + txt(710, 225, "เสียงต่อ", 46, "#111", "d4t") + txt(710, 275, "สงครามอิหร่าน?", 46, "#e0243a", "d4u")
        + txt(480, 470, "การตีความของสื่อ ไม่ใช่ผลสำรวจ", 34, "#fff", "d4v"), False),
    5: (txt(480, 130, "สภาล่าง · ก.ย.", 54, "#fff", "e5a") + txt(250, 330, "220", 170, "#4a8cff", "e5b") + txt(480, 320, "–", 120, "#fff", "e5c") + txt(710, 330, "204", 170, "#e0243a", "e5d") + tick_mark(480, 440, 36, "e5e") + txt(620, 455, "ผ่านมติ", 44, "#fff", "e5f"), False),
    6: (txt(480, 130, "วุฒิสภา · ก.ย.", 54, "#fff", "f6a") + bar(140, 190, 330, 90, "#4a8cff", "f6b") + bar(500, 190, 330, 90, "#e0243a", "f6c") + txt(480, 400, "ตกไปแค่ 1 เสียง", 80, "#ffd23f", "f6t") + x_mark(480, 470, 0.4, "f6x"), False),
    7: (capitol(260, 260, 1.4, "g7c") + tick_mark(640, 220, 70, "g7t") + txt(690, 360, "ผ่านง่ายขึ้น", 70, "#1f9d55", "g7u") + txt(690, 430, "ถ้าเดโมแครตคุมวุฒิสภา", 34, "#fff", "g7v"), False),
    8: (W("h8s", f'<g transform="translate(300,260) rotate(-12)"><rect x="-170" y="-80" width="340" height="160" rx="16" fill="none" stroke="#e0243a" stroke-width="14"/></g>') + txt(300, 285, "VETO", 120, "#e0243a", "h8t") + txt(720, 240, "2 ใน 3", 110, "#ffd23f", "h8u") + txt(720, 330, "ถึงจะล้มวีโต้", 44, "#fff", "h8v"), False),
    9: (bar(120, 100, 330, 120, "#ffd23f", "i9a") + txt(285, 185, "ต้นปีหน้า", 60, "#111", "i9b") + txt(285, 290, "สภาชุดใหม่เริ่มงาน", 38, "#fff", "i9c") + x_mark(740, 200, 1.4, "i9x") + txt(740, 340, "ไม่จบทันที", 70, "#e0243a", "i9t"), False),
    10: (barrel(190, 260, 1.7, "j10a") + txt(190, 440, "น้ำมัน", 46, "#fff", "j10b") + txt(560, 150, "ช่องแคบฮอร์มุซ", 56, "#ffd23f", "j10c") + txt(560, 260, "ราคาน้ำมัน", 54, "#fff", "j10d") + txt(560, 350, "ค่าขนส่ง · ของกิน", 46, "#fff", "j10e") + txt(560, 440, "ค่าครองชีพ", 54, "#e0243a", "j10f"), False),
    11: (stick(480, 310, 1.6, INK, "k11s") + W("k11q", f'<circle cx="480" cy="170" r="70" fill="#ffd23f" stroke="{INK}" stroke-width="7"/>' + txt(480, 205, "?", 100, "#111")) + txt(480, 508, "คอมเมนต์ไว้", 36, "#fff", "k11t"), False),
}
assert sorted(VG) == list(range(1, N))
CUSTOM = {"c3a", "c3c", "f6b", "f6c", "h8s", "h8t"}
ITEMS = {i: [x for x in re.findall(r'id="([A-Za-z0-9_]+)" class="it"', VG[i][0]) if x not in CUSTOM] for i in VG}
VGS = "\n".join(card(f"vg{i}", VG[i][0], VG[i][1]) for i in sorted(VG))
tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))
(V / "items.json").write_text(json.dumps({str(k): len(v) for k, v in ITEMS.items()}))

DATA = dict(SC=SC, SCE=SCE, CAM=CAM, DRIFT=DRIFT, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, GDOTS=GREENLL, ITEMS=ITEMS, NR=0)
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%DOTS%%": dots_html, "%%GRAT%%": GRAT, "%%ARC%%": ARC, "%%GDOTS%%": gdots_html, "%%BKK%%": f"{bx},{by}", "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "->", SCE[i])
