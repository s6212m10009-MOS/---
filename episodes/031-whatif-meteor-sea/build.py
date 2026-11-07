"""สร้าง video/index.html ของตอน 031 (What If อุกกาบาตตกทะเลอันดามัน) จาก lines.py + video/timing_gm.json
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

TAGS = ["What If · <r>อุกกาบาตตกทะเล</r>", "<r>ก้อนเล็ก</r> · ไหม้หมด", "<r>ก้อนใหญ่</r> · เจาะน้ำ", "<r>คลื่นยักษ์</r> · แผ่ทุกทิศ", "ปัจจัย · <r>ขนาด ความเร็ว ความลึก</r>",
        "วิทยาศาสตร์ · <r>ยังถกเถียง</r>", "ไทย · <r>ชายฝั่ง 3,000 กม.</r>", "บทเรียน · <r>สึนามิ 2547</r>", "<r>หอเตือนภัย</r> · เส้นทางอพยพ", "รู้จัก<r>ที่สูง</r>ใกล้ตัว",
        "สัญญาณดัง · <r>หนีขึ้นที่สูง</r>", "<r>นาซา</r> · ภารกิจ DART", "ที่พักสูง<r>กี่เมตร?</r>"]
assert len(TAGS) == N

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
IMP = (93.0, 8.0)
ix, iy = mx(IMP[0]), my(IMP[1])


def cam_xy(lon, lat, k, py=None):
    if py is None:
        return [round(540 - mx(lon) * k, 1), round(690 - (my(lat) - 900) * k, 1), k]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


CAM = [cam_xy(93, 8, 2.4, 500), cam_xy(93, 8, 2.0, 260), cam_xy(93, 8, 2.4, 260), cam_xy(95, 8.5, 2.2, 260), cam_xy(95, 8.5, 2.2, 260), cam_xy(95, 8.5, 2.2, 260),
       cam_xy(99, 9, 2.6, 260), cam_xy(98.4, 8, 3.0, 260), cam_xy(100, 11, 2.4, 260), cam_xy(100, 11, 2.4, 260), cam_xy(100, 11, 2.4, 260), cam_xy(100.5, 13.75, 2.0, 260), cam_xy(101, 13, 3.0, 260)]
assert len(CAM) == N
DRIFT = CAM[11]

CITIES = [(100.5, 13.75), (98.99, 18.79), (98.4, 7.88), (102.83, 16.43), (100.47, 7.0), (101.3, 12.7), (99.9, 15.1), (104.8, 15.2), (100.0, 17.6), (102.1, 14.0), (98.98, 12.9), (100.9, 16.8)]
GREENLL = CITIES
OUTL = json.loads((V / "outlines.json").read_text(encoding="utf-8"))
bx, by = mx(100.5), my(13.75)
dots_html = (
    f'<path id="outTh" class="it" d="{OUTL["Thailand"]}" fill="#2fe07a" fill-opacity=".10" stroke="#2fe07a" stroke-width="3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    f'<g transform="translate({ix},{iy})">'
    + "".join(f'<circle id="w{j}" class="it" r="5" fill="none" stroke="#8fd8ee" stroke-width="{4 - j}" vector-effect="non-scaling-stroke"/>' for j in range(3))
    + '<circle id="fl" class="it" r="4" fill="#fff"/><circle id="crt" class="it" r="6" fill="#ffd23f" fill-opacity=".35" stroke="#ff7a1a" stroke-width="3" vector-effect="non-scaling-stroke"/>'
    '<g id="rockg" class="it"><g transform="scale(1.9)"><path d="M0,0 L-70,-62 L-58,-30Z" fill="#ff9a2a" opacity=".85"/><path d="M0,0 L-46,-52 L-30,-22Z" fill="#fff3b0" opacity=".9"/><circle r="9" fill="#8a5a2b" stroke="#ff7a1a" stroke-width="3"/></g></g></g>'
)
gdots_html = "".join(f'<g id="gd{k}" class="gdot" transform="translate({mx(lo)},{my(la)})"><circle r="8" fill="#2fe07a" stroke="#fff" stroke-width="2.5"/></g>' for k, (lo, la) in enumerate(GREENLL))

_stick = stick


def stick(x, y, s=1.0, col=INK, idn="", fill="#fff"):
    return _stick(x, y, s, "#fff", idn, "#0a1830") if col == INK else _stick(x, y, s, col, idn, fill)


def x_mark(x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})"><path d="M-50,-50 L50,50 M50,-50 L-50,50" stroke="#e0243a" stroke-width="16" stroke-linecap="round"/></g>'


def tick_mark(x, y, r=40, idn=""):
    return W(idn, f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1f9d55" stroke="{INK}" stroke-width="5"/><path d="M{x - r * .45},{y + 2} L{x - r * .1},{y + r * .38} L{x + r * .5},{y - r * .35}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')


def rock(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-60,-10 L-30,-55 L25,-60 L62,-18 L50,38 L5,58 L-45,35Z" fill="#8a5a2b" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><circle cx="-12" cy="-12" r="12" fill="#6d4720"/><circle cx="26" cy="14" r="9" fill="#6d4720"/></g>')


SEA = '<path d="M0,420 q60,-24 120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 V520 H0Z" fill="#2a6fb0" stroke="#8fd8ee" stroke-width="6"/>'
BG = ''
VG = {
    1: (rock(260, 230, 1.0, "a1r") + W("a1f", '<path d="M300,170 q60,-40 110,-60 q-30,50 -20,90 q-40,10 -90,-30Z" fill="#ff9a2a" stroke="#ffd23f" stroke-width="5"/>')
        + txt(690, 220, "ไหม้หมด", 90, "#ffd23f", "a1t") + txt(690, 310, "ในบรรยากาศ", 44, "#fff", "a1u"), False),
    2: (rock(300, 170, 1.9, "b2r") + W("b2a", '<path d="M300,290 V380" stroke="#ffd23f" stroke-width="12" stroke-linecap="round"/><path d="M270,350 L300,395 L330,350" fill="none" stroke="#ffd23f" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>')
        + W("b2w", SEA) + txt(730, 190, "ก้อนใหญ่", 84, "#ffd23f", "b2t") + txt(730, 280, "เจาะน้ำ", 56, "#fff", "b2u"), False),
    3: (W("c3w", '<path d="M0,430 q80,-150 160,0 q80,-250 160,0 q80,-150 160,0 q80,-250 160,0 q80,-150 160,0 q80,-100 160,0 V520 H0Z" fill="#2a6fb0" stroke="#8fd8ee" stroke-width="7"/>')
        + txt(480, 120, "คลื่นยักษ์", 110, "#ffd23f", "c3t") + txt(480, 200, "แผ่ออกทุกทิศ", 50, "#fff", "c3u"), False),
    4: (W("d4a", f'<circle cx="170" cy="230" r="28" fill="#8a5a2b" stroke="{INK}" stroke-width="6"/><circle cx="260" cy="210" r="62" fill="#8a5a2b" stroke="{INK}" stroke-width="7"/>') + txt(215, 400, "ขนาด", 44, "#fff", "d4l1")
        + W("d4b", '<path d="M410,250 H600" stroke="#ffd23f" stroke-width="14" stroke-linecap="round"/><path d="M565,205 L620,250 L565,295" fill="none" stroke="#ffd23f" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>') + txt(510, 400, "ความเร็ว", 44, "#fff", "d4l2")
        + W("d4c", f'<rect x="720" y="150" width="150" height="200" fill="#2a6fb0" stroke="{INK}" stroke-width="7"/><path d="M885,150 V350 M870,150 H900 M870,350 H900" stroke="#fff" stroke-width="6"/>') + txt(795, 400, "ความลึก", 44, "#fff", "d4l3"), False),
    5: (stick(250, 320, 1.5, INK, "e5s") + W("e5q", f'<circle cx="250" cy="150" r="64" fill="#ffd23f" stroke="{INK}" stroke-width="7"/>' + txt(250, 182, "?", 90, "#111"))
        + txt(670, 230, "ยังถกเถียง", 80, "#ffd23f", "e5t") + txt(670, 320, "ว่าแรงแค่ไหน", 52, "#fff", "e5u"), False),
    6: (W("f6c", f'<path d="M0,300 q120,-70 240,-10 q100,60 200,-10 q110,-80 230,-10 q140,70 290,-10 V520 H0Z" fill="#c4883a" stroke="{INK}" stroke-width="7"/><path d="M0,420 q120,-30 240,0 t240,0 t240,0 t240,0 V520 H0Z" fill="#2a6fb0"/>')
        + txt(480, 130, "~3,000 กม.", 110, "#ffd23f", "f6t") + txt(480, 215, "ชายฝั่งไทย", 50, "#fff", "f6u"), False),
    7: (txt(480, 150, "2547", 150, "#ffd23f", "g7y") + txt(480, 330, "5,000+", 130, "#e0243a", "g7n") + txt(480, 440, "คนไทยเสียชีวิต", 50, "#fff", "g7u"), False),
    8: (W("h8a", f'<rect x="150" y="190" width="46" height="250" fill="#e8eef6" stroke="{INK}" stroke-width="6"/><rect x="120" y="140" width="106" height="60" rx="14" fill="#e0243a" stroke="{INK}" stroke-width="6"/><path d="M100,150 Q80,170 100,190 M246,150 Q266,170 246,190" fill="none" stroke="#ffd23f" stroke-width="7" stroke-linecap="round"/>') + txt(175, 490, "หอเตือนภัย", 36, "#fff", "h8l")
        + W("h8b", f'<rect x="460" y="150" width="400" height="230" rx="18" fill="#1f6fd0" stroke="#fff" stroke-width="8"/><path d="M520,300 H760 M720,250 L770,300 L720,350" fill="none" stroke="#fff" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>') + txt(660, 440, "เส้นทางอพยพ", 40, "#fff", "h8t"), False),
    9: (W("i9a", f'<path d="M60,430 Q300,420 420,280 Q520,140 640,170 Q760,200 900,430Z" fill="#3f8a4a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
        + W("i9b", f'<path d="M560,170 L610,120 L660,170Z M570,170 H650 V215 H570Z" fill="#c4883a" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/>') + txt(250, 160, "ที่สูง", 90, "#ffd23f", "i9t")
        + W("i9w", '<path d="M0,470 q60,-20 120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0 V520 H0Z" fill="#2a6fb0"/>'), False),
    10: (stick(250, 330, 1.5, INK, "j10s") + W("j10a", '<path d="M330,260 L470,170 M440,160 L475,168 L462,203" fill="none" stroke="#ffd23f" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>')
         + W("j10w", '<path d="M590,430 q60,-90 120,0 q60,-90 120,0 V500 H590Z" fill="#2a6fb0" stroke="#8fd8ee" stroke-width="5"/>') + W("j10x", x_mark(710, 300, 1.2))
         + txt(710, 90, "อย่าไปดูคลื่น", 54, "#e0243a", "j10t") + txt(300, 90, "หนีขึ้นที่สูง", 54, "#ffd23f", "j10u"), False),
    11: (W("k11p", f'<rect x="90" y="230" width="110" height="50" rx="8" fill="#e8eef6" stroke="{INK}" stroke-width="6"/><rect x="60" y="215" width="30" height="80" fill="#ffd23f" stroke="{INK}" stroke-width="5"/>') + rock(600, 250, 1.1, "k11r")
         + W("k11a", '<path d="M210,255 H450" stroke="#ffd23f" stroke-width="10" stroke-dasharray="16 12" stroke-linecap="round"/><path d="M640,330 Q720,420 820,400" fill="none" stroke="#2fe07a" stroke-width="10" stroke-linecap="round"/>')
         + txt(480, 100, "DART", 100, "#ffd23f", "k11t") + txt(480, 470, "ชนเปลี่ยนวงโคจรได้", 46, "#fff", "k11u"), False),
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
