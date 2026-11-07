"""สร้าง video/index.html ของตอน 029 (What If ช่องแคบฮอร์มุซถูกปิด) จาก lines.py + video/timing_gm.json
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

TAGS = ["What If · <r>ฮอร์มุซปิด</r>", "<r>ฮอร์มุซ</r> · ทางผ่านน้ำมัน", "ไทย · <r>นำเข้าพลังงาน 70%</r>",
        "เส้นทาง · <r>เรือน้ำมัน</r>", "<r>ทะเลอาหรับ</r> · อ้อมอินเดีย", "<r>ช่องแคบมะละกา</r> · คอขวด", "<r>~2 สัปดาห์</r> · ถึงไทย", "ฮอร์มุซปิด · <r>เรือไม่มา</r>",
        "ผลกระทบ · <r>ลูกโซ่</r>", "ตั้งรับ · <r>เงินสำรอง</r>", "ตั้งรับ · <r>กระจายความเสี่ยง</r>", "เช็ก · <r>ก่อนเดินทาง</r>", "ข่าว · <r>แหล่งทางการ</r>", "<r>ไม่ตื่นตระหนก</r>", "<r>ปรับตัว</r>ยังไง?"]

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
BKK = (100.5, 13.75)
IRAN = (53, 32)
HORMUZ = (56.3, 26.5)


def cam_xy(lon, lat, k, py=None):
    if py is None:
        return [round(540 - mx(lon) * k, 1), round(690 - (my(lat) - 900) * k, 1), k]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


SEG_LL = [  # เส้นทางเรือ แยกตามฉาก (ลอง, ลาต)
    [(56.3, 26.5), (57.6, 25.6), (60.5, 23.4), (64, 19.5), (66, 17)],
    [(66, 17), (70, 12.5), (74, 7.3), (77.6, 6.2), (80.8, 5.2), (86, 6.0)],
    [(86, 6.0), (92, 6.6), (95.4, 6.4), (98.2, 5.0), (100.8, 3.0), (103.5, 1.3)],
    [(103.5, 1.3), (104.7, 3.0), (104.6, 5.6), (103, 8.2), (101.6, 10.6), (100.9, 12.8)],
]
CAM = ([cam_xy(*IRAN, 2.0, 500), cam_xy(*HORMUZ, 3.2, 260), cam_xy(*BKK, 2.4, 260),
        cam_xy(60.5, 22.0, 2.4, 260), cam_xy(76, 10.5, 2.2, 260), cam_xy(97, 4.5, 3.0, 260), cam_xy(102, 7.5, 3.0, 260), cam_xy(78, 20, 2.0, 260)]
       + [cam_xy(*BKK, 2.4, 260)] * 3 + [cam_xy(*IRAN, 2.2, 260)] + [cam_xy(*BKK, 2.4, 260)] * 2 + [cam_xy(101, 13, 3.0, 260)])
DRIFT = CAM[13]

GREENLL = [(100.5, 13.75), (98.99, 18.79), (98.4, 7.88), (102.83, 16.43), (100.47, 7.0), (101.3, 12.7), (99.9, 15.1), (104.8, 15.2), (100.0, 17.6), (102.1, 14.0), (98.98, 12.9), (100.9, 16.8)]
OUTL = json.loads((V / "outlines.json").read_text(encoding="utf-8"))
ix, iy, hx, hy, bx, by = mx(IRAN[0]), my(IRAN[1]), mx(HORMUZ[0]), my(HORMUZ[1]), mx(BKK[0]), my(BKK[1])
dots_html = (
    f'<g transform="translate({ix},{iy})"><circle id="iran" class="it" r="16" fill="#e0243a" stroke="#fff" stroke-width="5"/></g>'
    f'<g transform="translate({hx},{hy})"><circle id="hormR" class="it" r="40" fill="#ffd23f" fill-opacity=".18" stroke="#ffd23f" stroke-width="3" vector-effect="non-scaling-stroke"/><circle id="horm" class="it" r="10" fill="#ffd23f" stroke="#1e1e24" stroke-width="3"/></g>'
    f'<path id="outIran" class="it" d="{OUTL["Iran"]}" fill="#ffd23f" fill-opacity=".08" stroke="#ffd23f" stroke-width="3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    f'<path id="outTh" class="it" d="{OUTL["Thailand"]}" fill="#2fe07a" fill-opacity=".10" stroke="#2fe07a" stroke-width="3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
)
SEG = [[[mx(lo), my(la)] for lo, la in seg] for seg in SEG_LL]
ROUTE_D = "M" + "L".join(f"{p[0]} {p[1]}" for p in [q for sg in SEG for q in sg])
dots_html += (
    f'<path id="route" class="it" d="{ROUTE_D}" fill="none" stroke="#ffd23f" stroke-width="4" stroke-dasharray="14 10" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    f'<g transform="translate({hx},{hy})"><g id="hx" class="it"><path d="M-9,-9 L9,9 M9,-9 L-9,9" stroke="#e0243a" stroke-width="7" stroke-linecap="round" vector-effect="non-scaling-stroke"/></g></g>'
    '<g id="shipm" class="it"><g transform="scale(0.9)"><path d="M-22,0 H22 L17,9 H-17Z" fill="#3b4150" stroke="#fff" stroke-width="2"/><rect x="-16" y="-7" width="24" height="7" fill="#e0243a" stroke="#fff" stroke-width="1.5"/><rect x="10" y="-12" width="9" height="12" fill="#e8eef6" stroke="#fff" stroke-width="1.5"/></g></g>'
)
gdots_html = "".join(f'<g id="gd{k}" class="gdot" transform="translate({mx(lo)},{my(la)})"><circle r="8" fill="#2fe07a" stroke="#fff" stroke-width="2.5"/></g>' for k, (lo, la) in enumerate(GREENLL))

_stick = stick


def stick(x, y, s=1.0, col=INK, idn="", fill="#fff"):
    return _stick(x, y, s, "#fff", idn, "#0a1830") if col == INK else _stick(x, y, s, col, idn, fill)


def x_mark(x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})"><path d="M-50,-50 L50,50 M50,-50 L-50,50" stroke="#e0243a" stroke-width="16" stroke-linecap="round"/></g>'


def tick_mark(x, y, r=40, idn=""):
    return W(idn, f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1f9d55" stroke="{INK}" stroke-width="5"/><path d="M{x - r * .45},{y + 2} L{x - r * .1},{y + r * .38} L{x + r * .5},{y - r * .35}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')


def pump(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-50" y="-80" width="100" height="160" rx="14" fill="#e0243a" stroke="{INK}" stroke-width="6"/><rect x="-34" y="-62" width="68" height="40" rx="6" fill="#cfe8d4" stroke="{INK}" stroke-width="4"/><path d="M50,-40 Q90,-40 90,0 V50" fill="none" stroke="{INK}" stroke-width="8" stroke-linecap="round"/></g>')


BG = ''
DK = ''
VG = {
    1: (W("v1s", f'<path d="M150,300 H810 L760,370 H210Z" fill="#3b4150" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><rect x="620" y="220" width="100" height="80" fill="#e8eef6" stroke="{INK}" stroke-width="6"/><rect x="240" y="262" width="340" height="40" rx="8" fill="#e0243a" stroke="{INK}" stroke-width="5"/><path d="M120,395 q60,-20 120,0 t120,0 t120,0 t120,0 t120,0 t120,0" fill="none" stroke="#8fd8ee" stroke-width="8"/>')
        + txt(480, 130, "~1 ใน 5", 120, "#ffd23f", "v1t") + W("v1x", x_mark(480, 300, 1.7)) + txt(480, 470, "ของน้ำมันโลกผ่านทางนี้", 40, "#fff", "v1u"), True),
    2: (txt(480, 150, "70%+", 150, "#ffd23f", "v2t") + txt(480, 230, "ไทยนำเข้าพลังงาน", 44, "#fff", "v2u")
        + pump(140, 360, 0.8, "v2a") + W("v2b", f'<path d="M240,360 H320" stroke="#fff" stroke-width="8" stroke-linecap="round"/><path d="M300,340 L330,360 L300,380" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>')
        + W("v2c", f'<rect x="360" y="320" width="150" height="80" rx="10" fill="#f08a1c" stroke="{INK}" stroke-width="6"/><rect x="510" y="345" width="70" height="55" rx="8" fill="#e8eef6" stroke="{INK}" stroke-width="6"/><circle cx="410" cy="410" r="16" fill="{INK}"/><circle cx="545" cy="410" r="16" fill="{INK}"/>')
        + txt(470, 470, "ขนส่ง", 32, "#fff", "v2d") + W("v2e", f'<path d="M620,360 H680" stroke="#fff" stroke-width="8" stroke-linecap="round"/>')
        + W("v2f", f'<path d="M720,330 H860 L840,400 H740Z" fill="#ffd23f" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><circle cx="760" cy="320" r="18" fill="#e0243a" stroke="{INK}" stroke-width="4"/><circle cx="800" cy="312" r="18" fill="#8fd19e" stroke="{INK}" stroke-width="4"/>')
        + txt(790, 470, "ของกิน", 32, "#fff", "v2g"), True),
    3: (pump(240, 280, 1.5, "v3p") + stick(560, 340, 1.0, INK, "v3s1") + stick(650, 350, 1.0, INK, "v3s2") + stick(740, 340, 1.0, INK, "v3s3")
        + W("v3x", x_mark(480, 160, 1.3)) + txt(480, 70, "แห่ตุน", 56, "#e0243a", "v3t") + tick_mark(850, 120, 40, "v3c") + txt(850, 190, "สำรองพอ", 30, "#fff", "v3u"), False),
    4: (cash(130, 330, 1.2, "v4a") + cash(130, 270, 1.2, "v4b") + cash(130, 210, 1.2, "v4c") + txt(130, 440, "เงินสำรอง", 36, "#fff", "v4l")
        + W("v4m", f'<rect x="310" y="120" width="190" height="190" rx="22" fill="#fff" stroke="{INK}" stroke-width="7"/><rect x="310" y="120" width="190" height="55" rx="22" fill="#e0243a" stroke="{INK}" stroke-width="7"/>' + txt(405, 270, "3-6", 80, "#111")) + txt(405, 350, "เดือน", 40, "#fff", "v4n")
        + W("v4d", f'<rect x="620" y="170" width="260" height="140" rx="20" fill="#3b4150" stroke="{INK}" stroke-width="7"/>' + txt(750, 255, "หนี้ดอกสูง", 44, "#fff") + x_mark(750, 240, 1.2)) + txt(750, 370, "เลี่ยง", 40, "#e0243a", "v4e"), False),
    5: (W("v5a", f'<path d="M100,330 H300 L280,420 H120Z" fill="#c4883a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><circle cx="150" cy="320" r="26" fill="#ffd23f" stroke="{INK}" stroke-width="5"/><circle cx="210" cy="312" r="26" fill="#8fd19e" stroke="{INK}" stroke-width="5"/><circle cx="265" cy="320" r="26" fill="#5ab8ee" stroke="{INK}" stroke-width="5"/>')
        + W("v5b", f'<path d="M380,330 H580 L560,420 H400Z" fill="#c4883a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><circle cx="440" cy="318" r="26" fill="#e0243a" stroke="{INK}" stroke-width="5"/><circle cx="510" cy="318" r="26" fill="#ffd23f" stroke="{INK}" stroke-width="5"/>')
        + W("v5c", f'<path d="M660,330 H860 L840,420 H680Z" fill="#c4883a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><circle cx="740" cy="318" r="26" fill="#8fd19e" stroke="{INK}" stroke-width="5"/><circle cx="800" cy="318" r="26" fill="#5ab8ee" stroke="{INK}" stroke-width="5"/>')
        + txt(480, 120, "กระจายความเสี่ยง", 60, "#ffd23f", "v5t") + tick_mark(480, 230, 44, "v5k") + txt(480, 490, "อย่าเทหมดหน้าตัก", 38, "#fff", "v5u"), False),
    6: (idcard(250, 250, 2.0, "v6i") + txt(250, 400, "ประกาศเตือน กต.", 38, "#fff", "v6j")
        + W("v6w", f'<path d="M700,130 L820,330 H580Z" fill="#ffd23f" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>' + txt(700, 300, "!", 120, "#111")) + txt(700, 410, "ตะวันออกกลาง", 38, "#fff", "v6k"), False),
    7: (W("v7p", f'<rect x="90" y="90" width="200" height="330" rx="34" fill="#2a2d3a" stroke="{INK}" stroke-width="7"/><rect x="108" y="130" width="164" height="240" rx="10" fill="#cfe8d4"/>' + txt(190, 220, "ข่าว", 40, "#111") + txt(190, 270, "ทางการ", 34, "#111"))
        + tick_mark(290, 110, 36, "v7c") + txt(190, 460, "แหล่งทางการ", 32, "#fff", "v7k")
        + W("v7b", f'<path d="M520,120 H860 Q890,120 890,150 V250 Q890,280 860,280 H640 L590,330 V280 H550 Q520,280 520,250Z" fill="#fff" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>' + txt(705, 220, "ข่าวลือ!", 56, "#111")) + W("v7x", x_mark(705, 200, 1.4)) + txt(705, 400, "ไม่แชร์", 40, "#e0243a", "v7t"), False),
    8: (stick(300, 330, 1.7, INK, "v8s") + W("v8a", f'<path d="M300,276 L250,200 M300,276 L350,200" stroke="#fff" stroke-width="12" stroke-linecap="round"/>') + tick_mark(660, 200, 70, "v8c")
        + txt(660, 340, "เตรียมตัว", 60, "#1f9d55", "v8t") + txt(660, 420, "ไม่ตื่นตระหนก", 44, "#fff", "v8u"), False),
    9: (stick(480, 310, 1.6, INK, "v9s") + W("v9q", f'<circle cx="480" cy="170" r="70" fill="#ffd23f" stroke="{INK}" stroke-width="7"/>' + txt(480, 205, "?", 100, "#111")) + txt(480, 508, "พิมพ์ตอบในคอมเมนต์", 36, "#fff", "v9t"), False),
}
def tanker(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-260,40 H260 L220,120 H-220Z" fill="#3b4150" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/><rect x="110" y="-50" width="110" height="90" fill="#e8eef6" stroke="{INK}" stroke-width="7"/><rect x="-200" y="-12" width="300" height="52" rx="8" fill="#e0243a" stroke="{INK}" stroke-width="6"/></g>')


WAVE = '<path d="M60,430 q60,-20 120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0" fill="none" stroke="#8fd8ee" stroke-width="8"/>'
NEWVG = {
    3: (txt(480, 130, "หลายพัน กม.", 100, "#ffd23f", "n3t") + tanker(480, 290, 0.9, "n3s") + W("n3w", WAVE) + txt(480, 500, "เรือบรรทุกน้ำมันยักษ์", 38, "#fff", "n3u"), False),
    4: (W("n4a", f'<path d="M70,130 H420 L330,320 Q300,380 270,320Z" fill="#c4883a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>') + txt(250, 230, "อินเดีย", 40, "#111", "n4i")
        + W("n4b", f'<ellipse cx="450" cy="400" rx="34" ry="44" fill="#c4883a" stroke="{INK}" stroke-width="6"/>') + txt(450, 490, "ศรีลังกา", 32, "#fff", "n4j")
        + W("n4c", '<path d="M130,420 Q320,480 560,440 T880,330" fill="none" stroke="#ffd23f" stroke-width="10" stroke-dasharray="18 14" stroke-linecap="round"/><path d="M850,300 L890,325 L850,355" fill="none" stroke="#ffd23f" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>')
        + txt(700, 190, "อ้อมอินเดีย", 60, "#ffd23f", "n4t"), False),
    5: (W("n5a", f'<path d="M60,90 H420 L470,270 L430,430 H60Z" fill="#c4883a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>') + txt(210, 270, "สุมาตรา", 38, "#111", "n5i")
        + W("n5b", f'<path d="M900,90 H570 L520,270 L560,430 H900Z" fill="#c4883a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>') + txt(740, 270, "มาเลเซีย", 38, "#111", "n5j")
        + tanker(495, 255, 0.12, "n5s") + txt(480, 70, "คอขวด", 70, "#ffd23f", "n5t") + txt(480, 495, "ช่องแคบมะละกา", 44, "#fff", "n5u"), False),
    6: (W("n6c", f'<rect x="90" y="150" width="270" height="250" rx="20" fill="#fff" stroke="{INK}" stroke-width="7"/><rect x="90" y="150" width="270" height="62" rx="20" fill="#e0243a" stroke="{INK}" stroke-width="7"/>') + txt(225, 340, "~14", 110, "#111", "n6d") + txt(225, 450, "วัน", 40, "#fff", "n6e")
        + W("n6f", f'<rect x="520" y="260" width="340" height="140" fill="#8a93a6" stroke="{INK}" stroke-width="7"/><rect x="560" y="150" width="46" height="110" fill="#6d7587" stroke="{INK}" stroke-width="6"/><rect x="650" y="170" width="46" height="90" fill="#6d7587" stroke="{INK}" stroke-width="6"/><rect x="740" y="140" width="46" height="120" fill="#6d7587" stroke="{INK}" stroke-width="6"/><circle cx="585" cy="110" r="22" fill="#cfd5e1"/><circle cx="765" cy="96" r="26" fill="#cfd5e1"/>')
        + txt(690, 455, "โรงกลั่น", 40, "#fff", "n6g"), False),
    7: (txt(480, 120, "เรือไม่มา", 100, "#e0243a", "n7t") + tanker(480, 310, 0.8, "n7s") + W("n7x", x_mark(480, 280, 1.9)) + txt(480, 500, "ไกลกว่า · แพงกว่า · ช้ากว่า", 40, "#fff", "n7u"), False),
}
VG = {**{k: v for k, v in VG.items() if k <= 2}, **{k + 5: v for k, v in VG.items() if k >= 3}, **NEWVG}

VGS = "\n".join(card(f"vg{i}", VG[i][0], VG[i][1]) for i in sorted(VG))
tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))

DATA = dict(SEG=SEG, SC=SC, SCE=SCE, CAM=CAM, DRIFT=DRIFT, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, GDOTS=GREENLL)
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%DOTS%%": dots_html, "%%GDOTS%%": gdots_html, "%%BKK%%": f"{bx},{by}", "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "->", SCE[i])
