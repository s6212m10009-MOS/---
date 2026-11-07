"""สร้าง video/index.html ของตอน 025 (What If ถ้าเกิดสงครามโลก) จาก lines.py + video/timing_gm.json
  python build.py
ซับผูกกับเสียงด้วยพลังงานเสียง (วิธีเดียวกับ ../022-mermaid-map/build.py) แต่ละท่อนมีซับไทย + อังกฤษตัวเล็ก"""
import json, re, subprocess
from pathlib import Path
import numpy as np
from lines import CAPS

HERE = Path(__file__).resolve().parent
V = HERE / "video"
timing = json.loads((V / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL = timing["total"]
LINES = timing["lines"]
WORLD = (V / "world-path.txt").read_text()
WORLDLINE = (V / "world-line.txt").read_text()
SR = 16000


def envelope(wav):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    x = np.abs(np.frombuffer(raw, dtype="<f4"))
    win = int(SR * 0.03)
    return np.convolve(x, np.ones(win) / win, mode="same")


# ---- ผูกซับกับเสียง ----
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

SC = [0.0] + [round(LINES[i]["start"] - 0.2, 3) for i in range(1, 12)]
SCE = SC[1:] + [TOTAL]

TAGS = ["WHAT IF · <r>สงครามโลก</r>", "<r>ไฟดับ</r> ทั้งโลก", "กรุงเทพฯ · <r>ของพอไหม?</r>", "กรม ปภ. · <r>อย่างน้อย 72 ชม.</r>", "เตรียม<r>กระเป๋า</r>ฉุกเฉิน",
        "<r>น้ำ</r> · 3 ลิตร/คน/วัน", "<r>อาหารแห้ง</r> + ที่เปิดกระป๋อง", "<r>ไฟ</r> + <r>การสื่อสาร</r>", "<r>เอกสาร</r> + เงินสด", "<r>ยา</r> + สุขอนามัย", "<r>ผ้าห่ม</r> + เสื้อกันฝน", "กระเป๋า<r>พร้อม</r>แล้ว"]

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
BKK = (100.5, 13.75)


def cam_xy(lon, lat, k, py=None):
    if py is None:
        return [round(540 - mx(lon) * k, 1), round(690 - (my(lat) - 900) * k, 1), k]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


CAM = [cam_xy(20, 15, 0.55), cam_xy(20, 15, 0.55)] + [cam_xy(*BKK, 3.0, 860)] * 9 + [cam_xy(20, 15, 0.55)]
DRIFT = cam_xy(*BKK, 3.4, 860)

# จุดแดงกระจายทั่วโลก (ไม่ชี้ประเทศหรือกลุ่มใดโดยเฉพาะ)
DOTLL = [(-100, 40), (-60, -10), (-3, 50), (20, 5), (37, 50), (60, 45), (78, 22), (115, 35), (135, 36), (150, -25), (-75, 5), (30, -28), (-120, 55), (90, 60), (-45, 70)]
dots_html = "".join(f'<g id="dot{k}" class="dotg" transform="translate({mx(lo)},{my(la)})"><circle r="38" fill="#e0243a" stroke="#fff" stroke-width="6"/><circle class="ring" r="38" fill="none" stroke="#e0243a" stroke-width="8"/></g>'
                    for k, (lo, la) in enumerate(DOTLL))

INK = "#1E1E24"


def W(idn, inner):
    return f'<g id="{idn}" class="it">{inner}</g>' if idn else inner


def txt(x, y, s, size=44, col=INK, idn="", anchor="middle"):
    return W(idn, f'<text x="{x}" y="{y}" font-size="{size}" font-weight="800" fill="{col}" text-anchor="{anchor}" font-family="Kanit">{s}</text>')


def stick(x, y, s=1.0, col=INK, idn="", fill="#fff"):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><circle cx="0" cy="-60" r="26" fill="{fill}" stroke="{col}" stroke-width="6"/><path d="M0,-34 V30 M0,-14 L-28,12 M0,-14 L28,12 M0,30 L-20,76 M0,30 L20,76" fill="none" stroke="{col}" stroke-width="7" stroke-linecap="round"/></g>')


def bag(x, y, s=1.3, idn="", zipped=False):
    z = f'<path d="M-62,-58 H62" stroke="{INK}" stroke-width="5" stroke-dasharray="8 6"/>' if zipped else ""
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-30,-108 Q0,-150 30,-108" fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round"/><rect x="-82" y="-112" width="164" height="206" rx="42" fill="#d6262f" stroke="{INK}" stroke-width="7"/><rect x="-60" y="14" width="120" height="66" rx="16" fill="#b81c24" stroke="{INK}" stroke-width="5"/><path d="M-62,-58 H62" stroke="{INK}" stroke-width="4"/>{z}<rect x="-8" y="-46" width="16" height="40" fill="#fff"/><rect x="-20" y="-34" width="40" height="16" fill="#fff"/></g>')


def bottle(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-22" y="-60" width="44" height="120" rx="14" fill="#5ab8ee" stroke="{INK}" stroke-width="6"/><rect x="-12" y="-82" width="24" height="26" rx="6" fill="#fff" stroke="{INK}" stroke-width="5"/><rect x="-22" y="-14" width="44" height="30" fill="#fff" opacity=".7"/></g>')


def can(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-44" y="-48" width="88" height="96" rx="10" fill="#c9ced6" stroke="{INK}" stroke-width="6"/><rect x="-44" y="-14" width="88" height="34" fill="#e0243a" stroke="{INK}" stroke-width="5"/><ellipse cx="0" cy="-48" rx="44" ry="12" fill="#e4e8ee" stroke="{INK}" stroke-width="5"/></g>')


def noodle(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-54,-40 H54 L38,56 H-38Z" fill="#ffd23f" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><path d="M-56,-40 H56" stroke="{INK}" stroke-width="9"/><path d="M-24,-12 Q0,6 24,-12" fill="none" stroke="#e0243a" stroke-width="7"/></g>')


def opener(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-50,40 L40,-30" stroke="{INK}" stroke-width="14" stroke-linecap="round"/><circle cx="46" cy="-34" r="22" fill="#fff" stroke="{INK}" stroke-width="7"/><path d="M-50,40 L-20,30 L-36,10Z" fill="#c9ced6" stroke="{INK}" stroke-width="5"/></g>')


def flash(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-26" y="-20" width="52" height="96" rx="12" fill="#444" stroke="{INK}" stroke-width="6"/><path d="M-26,-20 L-42,-58 H42 L26,-20Z" fill="#ffd23f" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/></g>')


def power(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-34" y="-56" width="68" height="112" rx="14" fill="#1f9d55" stroke="{INK}" stroke-width="6"/><path d="M6,-30 L-12,4 H2 L-6,32 L14,-6 H0Z" fill="#fff"/></g>')


def radio(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M30,-50 L60,-100" stroke="{INK}" stroke-width="6" stroke-linecap="round"/><rect x="-60" y="-50" width="120" height="96" rx="14" fill="#2a2d3a" stroke="{INK}" stroke-width="6"/><circle cx="-24" cy="0" r="26" fill="#6c747d" stroke="{INK}" stroke-width="5"/><rect x="12" y="-30" width="34" height="16" fill="#8fe3a0"/><circle cx="30" cy="14" r="8" fill="#e0243a"/></g>')


def whistle(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><circle cx="-10" cy="10" r="30" fill="#e0243a" stroke="{INK}" stroke-width="6"/><rect x="10" y="-14" width="46" height="26" rx="8" fill="#e0243a" stroke="{INK}" stroke-width="6"/><circle cx="-10" cy="10" r="8" fill="#fff"/></g>')


def idcard(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-70" y="-46" width="140" height="92" rx="10" fill="#fff" stroke="{INK}" stroke-width="6"/><circle cx="-34" cy="-6" r="16" fill="#b5835a" stroke="{INK}" stroke-width="4"/><path d="M-6,-18 H52 M-6,0 H52 M-6,18 H40" stroke="{INK}" stroke-width="6"/></g>')


def pouch(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-84" y="-62" width="168" height="124" rx="16" fill="#bfe2f2" opacity=".55" stroke="#3a6fd8" stroke-width="7"/><path d="M-84,-40 H84" stroke="#3a6fd8" stroke-width="5"/></g>')


def cash(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-68" y="-40" width="136" height="80" rx="8" fill="#8fd19e" stroke="{INK}" stroke-width="6"/><circle cx="0" cy="0" r="24" fill="#d8f2dc" stroke="{INK}" stroke-width="4"/><text x="0" y="12" font-size="34" font-weight="800" text-anchor="middle" fill="{INK}" font-family="Kanit">฿</text></g>')


def pills(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-60" y="-34" width="120" height="68" rx="34" transform="rotate(-25)" fill="#fff" stroke="{INK}" stroke-width="6"/><path d="M0,-52 L0,52" transform="rotate(-25)" stroke="{INK}" stroke-width="5"/><rect x="-60" y="-34" width="60" height="68" rx="34" transform="rotate(-25)" fill="#e0243a" stroke="{INK}" stroke-width="6"/></g>')


def firstaid(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-64" y="-46" width="128" height="96" rx="14" fill="#fff" stroke="{INK}" stroke-width="6"/><rect x="-10" y="-30" width="20" height="64" fill="#e0243a"/><rect x="-32" y="-8" width="64" height="20" fill="#e0243a"/><path d="M-24,-46 V-62 H24 V-46" fill="none" stroke="{INK}" stroke-width="6"/></g>')


def wipes(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-48" y="-52" width="96" height="104" rx="14" fill="#8fd8ee" stroke="{INK}" stroke-width="6"/><circle cx="0" cy="-8" r="22" fill="#fff"/><path d="M-12,-8 H12 M0,-20 V4" stroke="#37b3a6" stroke-width="6"/></g>')


def blanket(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-90" y="-36" width="180" height="76" rx="38" fill="#7a8ea6" stroke="{INK}" stroke-width="6"/><path d="M-50,-36 V40 M-10,-36 V40 M30,-36 V40" stroke="{INK}" stroke-width="4" opacity=".6"/><ellipse cx="84" cy="2" rx="22" ry="38" fill="#9db0c6" stroke="{INK}" stroke-width="6"/></g>')


def raincoat(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-70,-30 L-34,-70 H34 L70,-30 L50,10 L40,0 V70 H-40 V0 L-50,10Z" fill="#ffd23f" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><path d="M0,-70 V70" stroke="{INK}" stroke-width="5"/><circle cx="-12" cy="-10" r="4" fill="{INK}"/><circle cx="-12" cy="20" r="4" fill="{INK}"/></g>')


def skyline():
    s = f'<rect width="960" height="520" fill="#0d1226"/>'
    xs = [(40, 150, 160), (210, 90, 230), (310, 140, 140), (470, 100, 260), (590, 130, 190), (730, 110, 240), (850, 90, 170)]
    win = ""
    for bx, bw, bh in xs:
        s += f'<rect x="{bx}" y="{440 - bh}" width="{bw}" height="{bh + 80}" fill="#1a2040"/>'
        for wy in range(440 - bh + 20, 420, 44):
            for wx in range(bx + 14, bx + bw - 20, 30):
                win += f'<rect x="{wx}" y="{wy}" width="14" height="20" fill="#ffd23f"/>'
    return s + f'<g id="v2w">{win}</g>'


def card(idn, inner, dark=False):
    return f'<div id="{idn}" class="vg{" dark" if dark else ""}"><svg viewBox="0 0 960 520" width="960" height="520">{inner}</svg></div>'


BAGX, BAGY = 740, 270
VG = {
    2: (skyline() + stick(480, 330, 1.7, "#fff", "v2m", "#0d1226") + txt(640, 160, "?", 150, "#ffd23f", "v2q") + txt(480, 490, "ไฟดับทั้งเมือง · ร้านปิด", 36, "#fff"), True),
    3: (f'<rect width="960" height="520" fill="#fff"/>' + W("v3b", f'<circle cx="480" cy="260" r="170" fill="#fff" stroke="{INK}" stroke-width="12"/>' + "".join(f'<path d="M480,{260 - 150} V{260 - 130}" stroke="{INK}" stroke-width="8" transform="rotate({a} 480 260)"/>' for a in range(0, 360, 30)) + txt(480, 330, "72 ชม.", 64, "#e0243a") + txt(480, 400, "= 3 วัน", 40, "#555"))
        + f'<g id="v3h" class="it"><path d="M480,260 V130" stroke="{INK}" stroke-width="12" stroke-linecap="round"/><path d="M480,260 V390" stroke="none" stroke-width="12"/><circle cx="480" cy="260" r="14" fill="#e0243a"/></g>', False),
    4: (f'<rect width="960" height="520" fill="#fff"/>' + stick(220, 330, 1.6, INK, "v4s") + bag(BAGX, BAGY, 1.4, "v4b") + txt(610, 140, "?", 120, "#e0243a", "v4q"), False),
    5: (f'<rect width="960" height="520" fill="#fff"/>' + bag(BAGX, BAGY, 1.4, "v5b") + bottle(120, 230, 1.5, "v5a") + bottle(250, 230, 1.5, "v5b2") + bottle(380, 230, 1.5, "v5c")
        + txt(250, 430, "3 ลิตร × 7 วัน = 21 ลิตร", 40, "#e0243a", "v5t"), False),
    6: (f'<rect width="960" height="520" fill="#fff"/>' + bag(BAGX, BAGY, 1.4, "v6b") + can(130, 230, 1.5, "v6a") + noodle(300, 230, 1.5, "v6n") + opener(450, 240, 1.4, "v6o") + txt(300, 440, "กินได้โดยไม่ต้องใช้ไฟ", 36, "#555"), False),
    7: (f'<rect width="960" height="520" fill="#fff"/>' + bag(BAGX, BAGY, 1.4, "v7b") + flash(100, 240, 1.3, "v7a") + power(210, 240, 1.3, "v7p") + radio(330, 250, 1.1, "v7r") + whistle(470, 260, 1.3, "v7w")
        + f'<path id="v7beam" d="M100,190 L20,40 L180,40Z" fill="#ffd23f" opacity="0" style="opacity:0"/>' + txt(280, 440, "เผื่อสัญญาณมือถือล่ม", 36, "#555"), False),
    8: (f'<rect width="960" height="520" fill="#fff"/>' + bag(BAGX, BAGY, 1.4, "v8b") + idcard(150, 240, 1.4, "v8i") + pouch(150, 240, 1.45, "v8z") + cash(380, 250, 1.4, "v8c") + txt(260, 440, "ซองกันน้ำ + เงินสดย่อย", 36, "#555"), False),
    9: (f'<rect width="960" height="520" fill="#fff"/>' + bag(BAGX, BAGY, 1.4, "v9b") + pills(110, 250, 1.4, "v9p") + firstaid(260, 250, 1.4, "v9k") + wipes(410, 250, 1.4, "v9w") + txt(260, 440, "ยาสำรอง 7–14 วัน", 36, "#555"), False),
    10: (f'<rect width="960" height="520" fill="#fff"/>' + bag(BAGX, BAGY, 1.4, "v10b") + blanket(190, 250, 1.5, "v10a") + raincoat(410, 240, 1.4, "v10c") + txt(300, 440, "กันหนาว กันฝน", 36, "#555"), False),
}
rows = ["น้ำ", "อาหาร", "ไฟ + วิทยุ", "เอกสาร + เงิน", "ยา", "ผ้าห่ม"]
chk = "".join(W(f"v11c{k}", f'<circle cx="560" cy="{90 + k * 66}" r="22" fill="#1f9d55" stroke="{INK}" stroke-width="5"/><path d="M549,{91 + k * 66} L557,{99 + k * 66} L572,{81 + k * 66}" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>' + txt(610, 102 + k * 66, rows[k], 38, INK, "", "start")) for k in range(6))
VG[11] = (f'<rect width="960" height="520" fill="#fff"/>' + bag(230, 280, 1.7, "v11b", True) + chk + f'<g id="v11z" style="opacity:0"><text x="230" y="500" font-size="40" font-weight="800" fill="#1f9d55" text-anchor="middle" font-family="Kanit">พร้อมแล้ว!</text></g>', False)
VGS = "\n".join(card(f"vg{i}", VG[i][0], VG[i][1]) for i in sorted(VG))
tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))

DATA = dict(SC=SC, SCE=SCE, CAM=CAM, DRIFT=DRIFT, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, DOTS=DOTLL)
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%DOTS%%": dots_html, "%%BKK%%": f"{mx(BKK[0])},{my(BKK[1])}", "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(12):
    print(i + 1, SC[i], "→", SCE[i])
