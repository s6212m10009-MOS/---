TAGS = ["What If · <r>ต้องอพยพวันนี้</r>", "เตรียมของ · <r>แต่ไม่รู้ที่พักพิง</r>", "ข้อ 1 · <r>ถามที่หลบภัย</r>", "<r>ศูนย์พักพิง</r> · เปิด 24 ชม.", "ข้อ 2 · <r>เส้นทาง + สำรอง</r>",
        "ข้อ 3 · <r>แอปเตือนภัย</r>", "<r>สายด่วน 1784</r> · ปภ.", "ข้อ 4 · <r>กระเป๋า 6 หมวด</r>", "<r>น้ำ 3 ลิตร</r> · 3 วัน", "ข้อ 5 · <r>ซ้อมกับครอบครัว</r>",
        "<r>ประกาศอพยพ</r> · ไปทันที", "<r>เช็ก</r>กับหน่วยงานในพื้นที่", "ที่หลบภัย<r>อยู่ไหน?</r>"]
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
    + "".join(f'<g class="rdot it" id="rd{k}" transform="translate({mx(lo)},{my(la)})"><circle r="9" fill="#ffd23f" stroke="#fff" stroke-width="2.5"/></g>' for k, (lo, la) in enumerate(CITIES))
)
gdots_html = "".join(f'<g id="gd{k}" class="gdot" transform="translate({mx(lo)},{my(la)})"><circle r="8" fill="#2fe07a" stroke="#fff" stroke-width="2.5"/></g>' for k, (lo, la) in enumerate(GREENLL))

_stick = stick


def stick(x, y, s=1.0, col=INK, idn="", fill="#fff"):
    return _stick(x, y, s, "#fff", idn, "#0a1830") if col == INK else _stick(x, y, s, col, idn, fill)


def x_mark(x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})"><path d="M-50,-50 L50,50 M50,-50 L-50,50" stroke="#e0243a" stroke-width="16" stroke-linecap="round"/></g>'


def tick_mark(x, y, r=40, idn=""):
    return W(idn, f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1f9d55" stroke="{INK}" stroke-width="5"/><path d="M{x - r * .45},{y + 2} L{x - r * .1},{y + r * .38} L{x + r * .5},{y - r * .35}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')


def house(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-90,0 L0,-85 L90,0Z" fill="#c4883a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><rect x="-70" y="0" width="140" height="95" fill="#e8d7b0" stroke="{INK}" stroke-width="7"/><rect x="-18" y="35" width="36" height="60" fill="#6d4a1f" stroke="{INK}" stroke-width="5"/></g>')


def tent(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-110,95 L0,-70 L110,95Z" fill="#2fa66a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><path d="M0,-70 L-32,95 H32Z" fill="#1c6b44" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><path d="M0,-70 V-110 L38,-95 L0,-82" fill="#e0243a" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/></g>')


def office(x, y, label, idn=""):
    return W(idn, f'<rect x="{x - 90}" y="{y - 60}" width="180" height="140" fill="#e8eef6" stroke="{INK}" stroke-width="7"/><path d="M{x - 105},{y - 60} L{x},{y - 120} L{x + 105},{y - 60}Z" fill="#c4883a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><rect x="{x - 20}" y="{y + 20}" width="40" height="60" fill="#6d4a1f" stroke="{INK}" stroke-width="5"/>') + txt(x, y + 140, label, 34, "#fff", "")


def tile(x, y, label, col, idn=""):
    return W(idn, f'<rect x="{x - 130}" y="{y - 50}" width="260" height="100" rx="20" fill="{col}" stroke="{INK}" stroke-width="7"/>' + txt(x, y + 20, label, 54, "#111"))


BG = ''
VG = {
    1: (house(240, 270, 1.5, "a1h") + txt(700, 330, "?", 380, "#ffd23f", "a1q") + txt(700, 440, "ที่พักพิงอยู่ไหน", 44, "#fff", "a1t"), False),
    2: (W("b2a", office(170, 230, "ปภ.จังหวัด")) + W("b2b", office(480, 230, "เทศบาล")) + W("b2c", office(790, 230, "อำเภอ")) + txt(480, 70, "ถามที่ไหน?", 50, "#ffd23f", "b2t"), False),
    3: (tent(300, 270, 1.6, "c3a") + W("c3k", f'<circle cx="700" cy="250" r="105" fill="#fff" stroke="{INK}" stroke-width="8"/><path d="M700,250 V175 M700,250 L752,282" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>') + txt(700, 420, "24 ชม.", 60, "#ffd23f", "c3t"), False),
    4: (house(130, 250, 0.9, "d4h") + W("d4r", '<path d="M240,250 H690" stroke="#ffd23f" stroke-width="12" stroke-dasharray="22 14" stroke-linecap="round"/><path d="M650,215 L700,250 L650,285" fill="none" stroke="#ffd23f" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>')
        + W("d4s", '<path d="M240,300 Q420,420 690,310" fill="none" stroke="#8fd8ee" stroke-width="10" stroke-dasharray="14 12" stroke-linecap="round"/>') + tent(820, 250, 0.9, "d4t") + txt(470, 480, "เส้นทางหลัก + สำรอง", 40, "#fff", "d4u"), False),
    5: (W("e5p", f'<rect x="330" y="60" width="200" height="390" rx="36" fill="#2a2d3a" stroke="{INK}" stroke-width="8"/><rect x="348" y="105" width="164" height="290" rx="10" fill="#cfe8d4"/>')
        + W("e5b", f'<path d="M430,170 q-50,0 -50,60 v50 h100 v-50 q0,-60 -50,-60Z" fill="#ffd23f" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><circle cx="430" cy="300" r="14" fill="{INK}"/>')
        + txt(700, 210, "แอป", 70, "#ffd23f", "e5t") + txt(700, 290, "Thai Disaster", 44, "#fff", "e5u") + txt(700, 340, "Alert", 44, "#fff", "e5v"), False),
    6: (txt(480, 230, "1784", 230, "#ffd23f", "f6n") + txt(480, 350, "สายด่วน ปภ.", 64, "#fff", "f6t") + txt(480, 440, "เปิดตลอด 24 ชม.", 44, "#fff", "f6u"), False),
    7: (tile(250, 130, "น้ำ", "#7fb6ee", "g7a") + tile(480, 130, "อาหาร", "#f0c04a", "g7b") + tile(710, 130, "ไฟฉาย", "#ffd23f", "g7c")
        + tile(250, 290, "ยา", "#ee8c8c", "g7d") + tile(480, 290, "เอกสาร", "#cfd5e1", "g7e") + tile(710, 290, "ของใช้", "#8fd19e", "g7f") + txt(480, 440, "6 หมวด", 54, "#ffd23f", "g7t"), False),
    8: (W("h8a", f'<rect x="100" y="150" width="90" height="200" rx="20" fill="#7fb6ee" stroke="{INK}" stroke-width="7"/><rect x="125" y="115" width="40" height="40" fill="#cfe8f6" stroke="{INK}" stroke-width="5"/>')
        + W("h8b", f'<rect x="210" y="150" width="90" height="200" rx="20" fill="#7fb6ee" stroke="{INK}" stroke-width="7"/><rect x="235" y="115" width="40" height="40" fill="#cfe8f6" stroke="{INK}" stroke-width="5"/>')
        + W("h8c", f'<rect x="320" y="150" width="90" height="200" rx="20" fill="#7fb6ee" stroke="{INK}" stroke-width="7"/><rect x="345" y="115" width="40" height="40" fill="#cfe8f6" stroke="{INK}" stroke-width="5"/>')
        + txt(255, 420, "3 ลิตร/คน/วัน", 40, "#fff", "h8l")
        + W("h8d", f'<rect x="560" y="150" width="300" height="250" rx="20" fill="#fff" stroke="{INK}" stroke-width="8"/><rect x="560" y="150" width="300" height="70" rx="20" fill="#e0243a" stroke="{INK}" stroke-width="8"/>') + txt(710, 340, "3 วัน", 100, "#111", "h8e"), False),
    9: (stick(190, 300, 1.0, INK, "i9a") + stick(300, 300, 1.0, INK, "i9b") + stick(410, 300, 1.0, INK, "i9c")
        + W("i9f", f'<path d="M700,100 V420" stroke="{INK}" stroke-width="10" stroke-linecap="round"/><path d="M700,100 L840,150 L700,200Z" fill="#e0243a" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/>')
        + txt(700, 480, "จุดนัดพบ", 48, "#ffd23f", "i9t") + txt(300, 150, "ซ้อมด้วยกัน", 44, "#fff", "i9u"), False),
    10: (stick(250, 330, 1.5, INK, "j10s") + W("j10a", '<path d="M350,260 H650" stroke="#ffd23f" stroke-width="14" stroke-linecap="round"/><path d="M610,220 L660,260 L610,300" fill="none" stroke="#ffd23f" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>')
         + tent(790, 280, 0.9, "j10t") + txt(480, 90, "ไปตามเจ้าหน้าที่", 56, "#ffd23f", "j10u") + txt(480, 470, "อย่ารอจนสาย", 44, "#fff", "j10v"), False),
    11: (office(250, 250, "หน่วยงานในพื้นที่", "k11a") + tick_mark(640, 220, 70, "k11c") + txt(640, 360, "เช็กก่อน", 70, "#1f9d55", "k11t") + txt(640, 430, "แต่ละพื้นที่ไม่เหมือนกัน", 36, "#fff", "k11u"), False),
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
