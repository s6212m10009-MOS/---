"""สร้าง video/index.html ของตอน 039 (ไต้หวันถูกปิดล้อม) จาก lines.py + video/timing_gm.json
  python build.py   (PYTHONIOENCODING=utf-8)  ซับผูกกับเสียงด้วยพลังงานเสียง"""
import json, re, subprocess
from pathlib import Path
import numpy as np
from lines import CAPS

HERE = Path(__file__).resolve().parent
V = HERE / "video"
timing = json.loads((V / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL, LINES = timing["total"], timing["lines"]
N = len(LINES)
WORLDLINE = (V / "world-line.txt").read_text()
SR = 16000
INK = "#1E1E24"

# เส้นขอบไต้หวัน (path 9 จุดในแผนที่โลก)
TAIWAN = ""
for sub in re.split(r"(?=M)", WORLDLINE):
    pts = [(float(a), float(b)) for a, b in re.findall(r"(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)", sub)]
    if pts and all(3000 <= x <= 3030 and 645 <= y <= 690 for x, y in pts):
        TAIWAN = sub.strip()
assert TAIWAN


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

TAGS = ["ถ้าจีน<r>ปิดล้อม</r>ไต้หวัน", "จีนซ้อมรบ · <r>เครื่องบิน 49 ลำ</r>", "จีนซ้อมรบ · <r>เรือ 100+ ลำ</r>", "ซ้อมรบ<r>กดดัน</r> · ไม่ใช่ปิดล้อม",
        "ไต้หวัน · <r>TSMC</r> ผลิตชิป", "สมมติ · <r>ปิดล้อมจริง</r>", "ทรัมป์เยือนจีน · <r>18 พ.ย.</r>", "คิดว่า<r>จะเกิดจริง</r>ไหม?"]
assert len(TAGS) == N

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
TWC = (mx(121.0), my(23.7))  # ศูนย์กลางไต้หวัน
HSINCHU = (mx(120.97), my(24.8))
BEIJING = (mx(116.4), my(39.9))


def cam(lon, lat, k, sy):  # ให้จุด (lon,lat) ไปอยู่ที่จอ y = sy
    return [round(540 - mx(lon) * k, 1), round(sy - my(lat) * k, 1), k]


CAM = [cam(121, 23.7, 7, 780), cam(121, 23.7, 7, 780), cam(121, 23.7, 7, 780), cam(116, 28, 2.3, 700), cam(121, 24.5, 9, 700), cam(121, 23.7, 4, 700), cam(116, 32, 2.0, 700), cam(112, 28, 1.9, 700)]
assert len(CAM) == N


# ---------- ไอคอน (พิกัดการ์ด 960x520) ----------
def W(idn, inner):
    return f'<g id="{idn}" class="it">{inner}</g>' if idn else inner


def txt(x, y, s, size=44, col="#fff", idn="", anchor="middle"):
    return W(idn, f'<text x="{x}" y="{y}" font-size="{size}" font-weight="800" fill="{col}" text-anchor="{anchor}" font-family="Kanit">{s}</text>')


PLANE = "M0,-9 L2,-3 L10,2 L10,4.5 L2,2.5 L2,6.5 L5,8.5 L5,10 L0,9 L-5,10 L-5,8.5 L-2,6.5 L-2,2.5 L-10,4.5 L-10,2 L-2,-3Z"
SHIP = "M-10,-3 H10 L7,4 H-7Z M-3,-3 V-8 H4 V-3"
CARRIER = "M-12,-3 H12 L9,5 H-9Z M-12,-4 H12 V-1 H-12Z M5,-4 V-9 H9 V-4"


def plane(x, y, s=1.0, idn="", col="#ff4d4d", rot=0):
    return W(idn, f'<g transform="translate({x},{y}) scale({s}) rotate({rot})"><path d="{PLANE}" fill="{col}" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round"/></g>')


def ship(x, y, s=1.0, idn="", col="#cfd5e1"):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="{SHIP}" fill="{col}" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round"/></g>')


def carrier(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="{CARRIER}" fill="#ff4d4d" stroke="{INK}" stroke-width="1.3" stroke-linejoin="round"/></g>')


def chip(x, y, s=1.0, idn=""):
    pins = "".join(f'<rect x="{-44 + k * 22}" y="-72" width="9" height="20" fill="#cfd5e1" stroke="{INK}" stroke-width="3"/><rect x="{-44 + k * 22}" y="52" width="9" height="20" fill="#cfd5e1" stroke="{INK}" stroke-width="3"/>' for k in range(5)) \
        + "".join(f'<rect x="-72" y="{-44 + k * 22}" width="20" height="9" fill="#cfd5e1" stroke="{INK}" stroke-width="3"/><rect x="52" y="{-44 + k * 22}" width="20" height="9" fill="#cfd5e1" stroke="{INK}" stroke-width="3"/>' for k in range(5))
    return W(idn, f'<g transform="translate({x},{y}) scale({s})">{pins}<rect x="-54" y="-54" width="108" height="108" rx="12" fill="#2b3a67" stroke="{INK}" stroke-width="6"/><rect x="-30" y="-30" width="60" height="60" rx="6" fill="#4f7cff" stroke="#fff" stroke-width="4"/></g>')


def phone(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-38" y="-70" width="76" height="140" rx="14" fill="#cfd5e1" stroke="{INK}" stroke-width="6"/><rect x="-29" y="-54" width="58" height="96" rx="4" fill="#0a1830"/></g>')


def car(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-80,20 V-6 L-52,-8 L-34,-44 H34 L52,-8 L80,-6 V20Z" fill="#e0243a" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><circle cx="-46" cy="24" r="17" fill="#333" stroke="{INK}" stroke-width="5"/><circle cx="46" cy="24" r="17" fill="#333" stroke="{INK}" stroke-width="5"/></g>')


def laptop(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-62" y="-52" width="124" height="82" rx="8" fill="#0a1830" stroke="#cfd5e1" stroke-width="7"/><path d="M-84,40 H84 L72,56 H-72Z" fill="#cfd5e1" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/></g>')


def up(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M0,-30 L26,2 H10 V30 H-10 V2 H-26Z" fill="#e0243a" stroke="#fff" stroke-width="4" stroke-linejoin="round"/></g>')


def xmark(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-44,-44 L44,44 M44,-44 L-44,44" stroke="#e0243a" stroke-width="16" stroke-linecap="round"/></g>')


def tick(x, y, r=34, idn=""):
    return W(idn, f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1f9d55" stroke="#fff" stroke-width="5"/><path d="M{x - r * .45},{y + 2} L{x - r * .1},{y + r * .38} L{x + r * .5},{y - r * .35}" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>')


def flag(code, x, y, w=130, idn=""):
    h = round(w * 2 / 3)
    if code == "us":
        b = "".join(f'<rect x="0" y="{k * h / 7}" width="{w}" height="{h / 7 + .5}" fill="{"#B22234" if k % 2 == 0 else "#fff"}"/>' for k in range(7)) + f'<rect x="0" y="0" width="{w * .45}" height="{h * 4 / 7}" fill="#3C3B6E"/>'
    elif code == "ir":
        b = (f'<rect width="{w}" height="{h / 3 + .5}" fill="#239F40"/><rect y="{h / 3}" width="{w}" height="{h / 3 + .5}" fill="#fff"/><rect y="{2 * h / 3}" width="{w}" height="{h / 3 + .5}" fill="#DA0000"/>'
             f'<circle cx="{w / 2}" cy="{h / 2}" r="{h / 9}" fill="none" stroke="#DA0000" stroke-width="5"/>')
    else:  # cn
        b = f'<rect width="{w}" height="{h}" fill="#DE2910"/><circle cx="{w * .22}" cy="{h * .3}" r="{h * .17}" fill="#FFDE00"/>'
    return W(idn, f'<g transform="translate({x},{y})">{b}<rect width="{w}" height="{h}" fill="none" stroke="#fff" stroke-width="5"/></g>')


def stick(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><circle cx="0" cy="-60" r="26" fill="#0a1830" stroke="#fff" stroke-width="6"/><path d="M0,-34 V30 M0,-14 L-28,12 M0,-14 L28,12 M0,30 L-20,76 M0,30 L20,76" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/></g>')


def calendar(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-80" y="-80" width="160" height="160" rx="16" fill="#fff" stroke="{INK}" stroke-width="7"/><rect x="-80" y="-80" width="160" height="46" rx="16" fill="#e0243a" stroke="{INK}" stroke-width="7"/><text x="0" y="48" font-size="86" font-weight="800" fill="{INK}" text-anchor="middle" font-family="Kanit">18</text></g>')


VG = {
    1: (plane(190, 250, 9, "a1p", "#ff4d4d") + txt(560, 330, "49", 230, "#ffd23f", "a1n") + txt(790, 330, "ลำ", 70, "#fff", "a1u") + txt(560, 430, "ในวันเดียว · สูงสุดของปีนี้", 44, "#fff", "a1t") + txt(480, 68, "ตามรายงานกองทัพไต้หวัน", 38, "#8fd8ee", "a1s")),
    2: (ship(150, 145, 7, "b2a") + txt(470, 185, "100+", 120, "#ffd23f", "b2n") + txt(780, 160, "เรือรบ", 42, "#fff", "b2t") + txt(780, 210, "เรือยามฝั่ง", 42, "#fff", "b2u")
        + carrier(150, 385, 7, "b2c") + txt(430, 425, "2", 120, "#ffd23f", "b2m") + txt(700, 405, "เรือบรรทุก", 42, "#fff", "b2v") + txt(700, 455, "เครื่องบิน", 42, "#fff", "b2w")),
    3: (txt(480, 120, "ซ้อมรบกดดัน", 96, "#ffd23f", "c3a") + tick(120, 100, 34, "c3k") + txt(480, 215, "ไม่ใช่ปิดล้อม", 64, "#fff", "c3b") + xmark(800, 195, .7, "c3x")
        + flag("us", 80, 280, 150, "c3f") + txt(280, 335, "เลือกตั้งกลางเทอม", 44, "#fff", "c3c", "start") + flag("ir", 80, 400, 150, "c3g") + txt(280, 455, "ติดพันสงครามอิหร่าน", 44, "#fff", "c3d", "start")),
    4: (chip(220, 250, 1.9, "d4c") + txt(650, 250, "TSMC", 140, "#ffd23f", "d4t") + txt(650, 340, "ผลิตชิปล้ำสมัย ส่วนใหญ่ของโลก", 42, "#fff", "d4u") + txt(650, 410, "AI · มือถือ · รถยนต์", 40, "#8fd8ee", "d4v")),
    5: (txt(480, 70, "สมมติ", 60, "#ffd23f", "e5t") + ship(120, 200, 6.5, "e5s") + xmark(120, 200, 1.0, "e5x")
        + phone(330, 210, 1.1, "e5p") + car(560, 220, 1.0, "e5q") + laptop(790, 215, 1.0, "e5l")
        + up(330, 340, 1.0, "e5u1") + up(560, 340, 1.0, "e5u2") + up(790, 340, 1.0, "e5u3") + txt(480, 450, "ขาดชิป → ของขาด · ราคาขึ้น", 46, "#fff", "e5v")),
    6: (calendar(190, 220, 1.5, "f6c") + txt(600, 240, "18 พ.ย.", 120, "#ffd23f", "f6n") + txt(600, 320, "ทรัมป์เยือนจีน · เอเปก", 44, "#fff", "f6t")
        + flag("us", 380, 390, 130, "f6u") + txt(560, 450, "?", 80, "#ffd23f", "f6q") + flag("cn", 640, 390, 130, "f6v")),
    7: (stick(480, 320, 1.6, "g7s") + W("g7q", f'<circle cx="480" cy="170" r="70" fill="#ffd23f" stroke="{INK}" stroke-width="7"/><text x="480" y="205" font-size="100" font-weight="800" fill="#111" text-anchor="middle" font-family="Kanit">?</text>') + txt(480, 508, "คอมเมนต์ไว้", 36, "#fff", "g7t")),
}
assert sorted(VG) == list(range(1, N))
card = lambda idn, inner: f'<div id="{idn}" class="vg"><svg viewBox="0 0 960 520" width="960" height="520">{inner}</svg></div>'
ITEMS = {i: re.findall(r'id="([A-Za-z0-9_]+)" class="it"', VG[i]) for i in VG}
VGS = "\n".join(card(f"vg{i}", VG[i]) for i in sorted(VG))
(V / "items.json").write_text(json.dumps({str(k): len(v) for k, v in ITEMS.items()}))
tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))

# ---------- วงโคจรเครื่องบิน/เรือรอบเกาะ (พิกัดแผนที่) ----------
cx, cy = TWC


def orbit(shape_d, R, fill, s, n, start, prefix, face):
    out = []
    for k in range(n):
        th = start + 360 * k / n
        out.append(f'<g id="{prefix}{k}" class="orb" style="opacity:0" transform="translate({cx},{cy}) rotate({th:.1f}) translate(0,-{R}) rotate({face}) scale({s})"><path d="{shape_d}" fill="{fill}" stroke="#1E1E24" stroke-width="1.2" stroke-linejoin="round"/></g>')
    return "".join(out)


NP, NS = 26, 14
planes = orbit(PLANE, 44, "#ff4d4d", .42, NP, 0, "pl", 90)
ships = orbit(SHIP, 27, "#e8eef6", .42, NS, 10, "sh", -90)
carriers = "".join(f'<g id="ca{k}" class="orb" style="opacity:0" transform="translate({cx},{cy}) rotate({th}) translate(0,-18) rotate(-90) scale(.62)"><path d="{CARRIER}" fill="#ffd23f" stroke="#1E1E24" stroke-width="1.2" stroke-linejoin="round"/></g>' for k, th in enumerate([40, 220]))

DATA = dict(SC=SC, SCE=SCE, CAM=CAM, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, ITEMS=ITEMS, NP=NP, NS=NS, CX=cx, CY=cy)
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%TAIWAN%%": TAIWAN, "%%CX%%": str(cx), "%%CY%%": str(cy), "%%PLANES%%": planes, "%%SHIPS%%": ships, "%%CARRIERS%%": carriers,
             "%%HSX%%": str(HSINCHU[0]), "%%HSY%%": str(HSINCHU[1]), "%%BJX%%": str(BEIJING[0]), "%%BJY%%": str(BEIJING[1]),
             "%%VGS%%": VGS, "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "->", SCE[i])
