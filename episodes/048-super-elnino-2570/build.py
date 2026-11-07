"""สร้าง video/index.html ของ EP.048 What if ซูเปอร์เอลนีโญ — แผนที่โลก 2.5D (พื้นแผนที่เอียง ทวีปนูน ป้ายตั้ง + ไดโอรามาไอโซเมตริก)
  python build.py   (ต้องมี video/timing_gm.json และ video/audio_gm/NN_t.wav จาก make_voice.py)
เขียน video/sync.json ไว้ให้ make_sfx.py ใช้จับจังหวะด้วย"""
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
WORLD = (V / "world-path.txt").read_text()
OUTL = json.loads((V / "outlines.json").read_text(encoding="utf-8"))
SR = 16000

# ---------- จับเวลาซับจากพลังงานเสียง (วิธีเดียวกับตอน 047) ----------
def envelope(wav):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    x = np.abs(np.frombuffer(raw, dtype="<f4"))
    win = int(SR * 0.03)
    return np.convolve(x, np.ones(win) / win, mode="same")


SPOKEN = {"PM2.5": "พีเอ็มสองจุดห้า", "40": "สี่สิบ", "16": "สิบหก", "4": "สี่", "มี.ค.": "มีนาคม", "เม.ย.": "เมษายน"}
SYNC = []
for i, chunks in enumerate(CAPS):
    env = envelope(V / "audio_gm" / f"{i:02}_t.wav")
    voiced = np.where(env > env.max() * 0.08)[0]
    t0, t1 = voiced[0] / SR, voiced[-1] / SR
    def plen(s):
        for a, b in SPOKEN.items():
            s = s.replace(a, b)
        return len(re.sub(r"[\s\[\]]", "", s))
    w = [plen(c[0]) for c in chunks]
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
ck = lambda li, ci: SYNC[li][min(ci, len(SYNC[li]) - 1)][0]

# ---------- เรขาคณิตแผนที่ ----------
mx = lambda lon: round((lon + 180) * 10 if lon > -30 else (lon + 540) * 10, 1)   # แปซิฟิกตะวันออกต่อทางขวา (โลกสองแผ่น)
my = lambda lat: round((90 - lat) * 10, 1)
PW, TILT, PLX, PLY, PERSPY, HORIZ = 1700, 60, -310, 150, 230, 380
TH = (mx(100.9), my(15.6))
CAM0 = [3420, 900, 3300]                                  # ฮุกเริ่ม: เอเชีย-แปซิฟิกกว้าง
CAM = [[3250, 880, 2500],                                 # ฮุกจบ
       [3760, 900, 1900],                                 # 1 แปซิฟิก
       [TH[0] + 5, TH[1] + 25, 640],                      # 2 ไทย
       [TH[0] + 5, TH[1] + 10, 600],                      # 3 ฝุ่น
       [3050, 820, 1500]]                                 # 4 CTA ถอยกล้อง


def to_plane(p, c):
    x0, y0 = c[0] - c[2] / 2, c[1] - c[2] / 2
    return round((p[0] - x0) / c[2] * PW, 1), round((p[1] - y0) / c[2] * PW, 1)


# ทวีปนูน: ชั้นเงาซ้อนลงด้านล่าง + ผิวบน (โลกสองแผ่นต่อกัน)
land = ""
for dy, col in [(16, "#02060e"), (11, "#061223"), (6, "#0b2238"), (3, "#123553")]:
    land += f'<use href="#wp" y="{dy}" fill="{col}"/><use href="#wp" x="3600" y="{dy}" fill="{col}"/>'
land += ('<use href="#wp" fill="#2a6a8e" stroke="#9fd8ff" stroke-width="1.4" stroke-opacity=".8" vector-effect="non-scaling-stroke"/>'
         '<use href="#wp" x="3600" fill="#2a6a8e" stroke="#9fd8ff" stroke-width="1.4" stroke-opacity=".8" vector-effect="non-scaling-stroke"/>')
grid = "".join(f'<path d="M{x},0 V1800" stroke="#5aa0d8" stroke-opacity=".14" stroke-width="1" vector-effect="non-scaling-stroke"/>' for x in range(1800, 5400, 150))
grid += "".join(f'<path d="M1800,{y} H5400" stroke="#5aa0d8" stroke-opacity=".14" stroke-width="1" vector-effect="non-scaling-stroke"/>' for y in range(300, 1500, 150))
grid += f'<path d="M1800,900 H5400" stroke="#ffd23f" stroke-opacity=".35" stroke-width="1.5" stroke-dasharray="10 8" vector-effect="non-scaling-stroke"/>'

DOTLL = [(98.99, 18.79), (99.83, 19.91), (97.97, 19.3), (100.77, 18.78), (99.5, 18.29), (100.14, 18.14), (99.13, 16.88), (100.26, 16.82),
         (102.79, 17.41), (102.83, 16.43), (104.86, 15.24), (102.1, 14.97), (100.52, 13.86), (100.5, 13.75)]
dots = "".join(f'<circle id="pd{k}" class="pd" cx="{mx(lo)}" cy="{my(la)}" r="0" fill="#ff8a1c" stroke="#fff" stroke-width="2.5" vector-effect="non-scaling-stroke" opacity="0"/>' for k, (lo, la) in enumerate(DOTLL))
DOT_T0 = round(ck(3, 3) - 0.1, 2)

# ---------- ป้ายตั้ง ----------
PAC = (mx(-150), my(0))
NORTH, NE, BKK = (mx(99.2), my(18.8)), (mx(103.2), my(16.2)), (mx(100.5), my(13.75))


def stand(idn, html, cls="", stem=90):
    return f'<div class="stand" id="{idn}"><div class="sh"></div><div class="up"><div class="an"><div class="lab {cls}">{html}</div><div class="stem" style="height:{stem}px"></div><div class="dot"></div></div></div></div>'


STANDS_HTML = (stand("sTH", "ไทย", "red") + stand("sPAC", "แปซิฟิก อุ่นผิดปกติ", "hot") + stand("sTH2", "ร้อน · แล้ง", "hot")
               + stand("sN", "ภาคเหนือ", "", 160) + stand("sBKK", "กทม.", "", 30) + stand("sTH4", "ไทย", "red"))
STANDS = []


def show(idn, p, scene, t_in, t_out):
    for s in STANDS:
        if s["id"] == idn:
            break
    else:
        s = {"id": idn, "show": []}; STANDS.append(s)
    s["show"].append([scene, round(t_in, 2), round(t_out, 2), *to_plane(p, CAM[scene])])


show("sTH", TH, 0, ck(0, 5) + 0.1, SC[1] - 0.15)
show("sPAC", PAC, 1, SC[1] + 1.5, SCE[1] - 0.3)
show("sTH", TH, 1, ck(1, 4), SCE[1] - 0.3)
show("sTH2", TH, 2, SC[2] + 1.5, SCE[2] - 0.3)
show("sN", NORTH, 3, ck(3, 3) + 0.1, SCE[3] - 0.3)
show("sBKK", BKK, 3, ck(3, 3) + 0.6, SCE[3] - 0.3)
show("sTH4", TH, 4, SC[4] + 1.5, TOTAL + 1)

# ---------- ไดโอรามาไอโซเมตริก (การ์ดล่าง 960x520) ----------
ST = "#fff"


def it(k, inner, d=0.0):
    return f'<g class="it" data-k="{k}" data-d="{d}">{inner}</g>'


def txt(x, y, s, size=48, col="#fff"):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="800" fill="{col}" text-anchor="middle" font-family="Kanit">{s}</text>'


def iso(cx, cy, w, d, top, left, right, extra=""):
    hw, hq = w / 2, w / 4
    return (f'<ellipse cx="{cx}" cy="{cy + hq + d + 14}" rx="{hw * .95}" ry="{hq * .5}" fill="#000" opacity=".35"/>'
            f'<polygon points="{cx - hw},{cy} {cx},{cy + hq} {cx},{cy + hq + d} {cx - hw},{cy + d}" fill="{left}" stroke="{ST}" stroke-width="4" stroke-linejoin="round"/>'
            f'<polygon points="{cx},{cy + hq} {cx + hw},{cy} {cx + hw},{cy + d} {cx},{cy + hq + d}" fill="{right}" stroke="{ST}" stroke-width="4" stroke-linejoin="round"/>'
            f'<polygon points="{cx},{cy - hq} {cx + hw},{cy} {cx},{cy + hq} {cx - hw},{cy}" fill="{top}" stroke="{ST}" stroke-width="4" stroke-linejoin="round"/>{extra}')


def isobox(cx, cy, w, h, top, left, right):  # กล่องสูง (ตึก/ถังน้ำ) ฐานอยู่ที่ cy
    hw, hq = w / 2, w / 4
    return (f'<polygon points="{cx - hw},{cy - h} {cx},{cy + hq - h} {cx},{cy + hq} {cx - hw},{cy}" fill="{left}" stroke="{ST}" stroke-width="3"/>'
            f'<polygon points="{cx},{cy + hq - h} {cx + hw},{cy - h} {cx + hw},{cy} {cx},{cy + hq}" fill="{right}" stroke="{ST}" stroke-width="3"/>'
            f'<polygon points="{cx},{cy - hq - h} {cx + hw},{cy - h} {cx},{cy + hq - h} {cx - hw},{cy - h}" fill="{top}" stroke="{ST}" stroke-width="3"/>')


def waves_iso(cx, cy, w, col="#fff", n=3):
    out = ""
    for k in range(n):
        y = cy - w / 8 + k * w / 10
        out += f'<path d="M{cx - w * .3},{y} q{w * .075},-14 {w * .15},0 t{w * .15},0 t{w * .15},0 t{w * .15},0" fill="none" stroke="{col}" stroke-width="5" stroke-linecap="round" opacity=".85"/>'
    return out


def up_arrow(x, y, h=90, col="#e0243a"):
    return (f'<path d="M{x},{y} V{y - h}" stroke="{col}" stroke-width="14" stroke-linecap="round"/>'
            f'<path d="M{x - 26},{y - h + 24} L{x},{y - h - 6} L{x + 26},{y - h + 24}" fill="none" stroke="{col}" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>')


def thermo(x, y, h=200, lvl=.85, col="#e0243a"):
    return (f'<rect x="{x - 22}" y="{y - h}" width="44" height="{h}" rx="22" fill="#fff" stroke="{ST}" stroke-width="5"/>'
            f'<rect x="{x - 11}" y="{y - h * lvl}" width="22" height="{h * lvl}" rx="11" fill="{col}"/>'
            f'<circle cx="{x}" cy="{y + 14}" r="38" fill="{col}" stroke="{ST}" stroke-width="5"/>'
            + "".join(f'<path d="M{x + 22},{y - h + 30 + j * 34} h-14" stroke="#1e1e24" stroke-width="4"/>' for j in range(4)))


def sun(x, y, r=56):
    rays = "".join(f'<path d="M{x + np.cos(a) * (r + 14):.0f},{y + np.sin(a) * (r + 14):.0f} L{x + np.cos(a) * (r + 40):.0f},{y + np.sin(a) * (r + 40):.0f}" stroke="#ffb020" stroke-width="10" stroke-linecap="round"/>' for a in np.linspace(0, 2 * np.pi, 12, endpoint=False))
    return rays + f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffd23f" stroke="{ST}" stroke-width="5"/>'


def flame(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M0,-90 Q40,-40 30,-6 Q26,20 0,24 Q-26,20 -30,-6 Q-34,-34 -10,-56 Q-6,-30 6,-30 Q14,-56 0,-90Z" fill="#ff6a1c" stroke="{ST}" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M0,-40 Q16,-16 10,4 Q0,14 -10,4 Q-14,-14 0,-40Z" fill="#ffd23f"/></g>')


def person(x, y, s=1.0, col="#fff"):
    return f'<g transform="translate({x},{y}) scale({s})"><circle cx="0" cy="-58" r="18" fill="{col}"/><path d="M-26,0 Q-26,-36 0,-36 Q26,-36 26,0Z" fill="{col}"/></g>'


cracks = "".join(f'<path d="{d}" fill="none" stroke="#5a3418" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>' for d in
                 ["M340,320 l40,14 l22,-16 l36,20", "M480,286 l-20,26 l26,18 l-12,30", "M560,330 l40,-10 l26,18", "M420,368 l40,8 l18,22", "M600,300 l-24,-14"])
rice = "".join(f'<path d="M{x},{y} q-6,-40 -24,-56 M{x},{y} q4,-44 22,-58 M{x},{y} q0,-50 2,-66" fill="none" stroke="#c9a23a" stroke-width="6" stroke-linecap="round"/>' for x, y in [(400, 336), (460, 352), (520, 340), (580, 326)])
SCENES = {
    1: [it(0, iso(250, 330, 380, 56, "#e8553d", "#a32d2d", "#c4402e", waves_iso(250, 330, 380)) + txt(250, 128, "ซูเปอร์เอลนีโญ", 52, "#ffd23f")),
        it(1, txt(250, 190, "แปซิฟิกอุ่นผิดปกติ", 38, "#fff")),
        it(3, f'<g transform="rotate(-6 250 330)"><rect x="140" y="280" width="220" height="96" rx="20" fill="#ffd23f" stroke="#1e1e24" stroke-width="7"/>{txt(250, 352, "≈ +4°C", 66, "#e0243a")}</g>'),
        it(4, iso(710, 360, 360, 70, "#1d4f88", "#0c2f5a", "#123f73", "".join(f'<path d="M{560 + j * 10},{372 + j * 22} h{300 - j * 20}" stroke="#ff6a2a" stroke-width="5" opacity=".7"/>' for j in range(3))) + txt(710, 128, "ความร้อนสะสม", 52, "#ffd23f")),
        it(5, up_arrow(640, 330, 110) + up_arrow(710, 300, 140) + up_arrow(780, 330, 110) + txt(710, 128 + 70, "ปล่อยสู่อากาศ", 38, "#fff"))],
    2: [it(0, iso(480, 330, 520, 60, "#c98a4a", "#7a4a22", "#9a5e2e", cracks)),
        it(1, sun(130, 120)),
        it(1, thermo(820, 330, 230, .9), 0.3),
        it(3, isobox(110, 400, 120, 100, "#4cc3ff", "#1d5e8a", "#2a78ad") + txt(110, 272, "น้ำต้นทุนตึง", 34, "#4cc3ff")),
        it(4, rice + txt(490, 200, "ข้าว · มันสำปะหลัง", 42, "#fff")),
        it(5, f'<g transform="rotate(-4 480 470)"><rect x="250" y="430" width="460" height="80" rx="16" fill="#e0243a" stroke="#fff" stroke-width="6"/>{txt(480, 488, "เสียหาย หลายหมื่นล้าน ฿", 46, "#fff")}</g>')],
    3: [it(0, iso(250, 340, 340, 56, "#6e7d4a", "#3e4a26", "#55633a", f'<path d="M150,340 L230,250 L280,300 L330,240 L380,330" fill="#55633a" stroke="#fff" stroke-width="4" stroke-linejoin="round"/>') + flame(240, 300, 0.9) + flame(300, 296, 0.7) + txt(250, 178, "ไฟป่า", 54, "#ff8a1c")),
        it(1, iso(710, 360, 340, 50, "#5a5f6e", "#30333d", "#41444f",
                  isobox(650, 360, 70, 120, "#8a90a0", "#4a4e5a", "#5e6370") + isobox(730, 350, 80, 170, "#8a90a0", "#4a4e5a", "#5e6370") + isobox(800, 380, 60, 90, "#8a90a0", "#4a4e5a", "#5e6370"))
           + '<ellipse cx="720" cy="300" rx="230" ry="120" fill="#b08a5a" opacity=".55"/>' + txt(710, 178, "PM2.5", 60, "#ffd23f")),
        it(3, f'<rect x="300" y="18" width="360" height="104" rx="22" fill="#e0243a" stroke="#fff" stroke-width="7"/>' + txt(480, 94, "40 จังหวัด", 70, "#fff")),
        it(5, "".join(person(330 + j * 60, 500, .9) for j in range(6)) + txt(780, 492, "16 ล้านคน", 52, "#ffd23f"))],
    4: [it(0, f'<circle cx="160" cy="130" r="56" fill="#1f9d55" stroke="#fff" stroke-width="6"/><path d="M132,132 L152,154 L192,108" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>' + txt(560, 150, "ตระหนัก ไม่ตระหนก", 62, "#fff")),
        it(1, iso(300, 360, 340, 50, "#3a7fc0", "#1d4f88", "#2a63a0", waves_iso(300, 360, 340)) + f'<g transform="translate(300,330)">{up_arrow(0, -110, 90, "#4cc3ff").replace("M-26", "M-26").replace("V-200", "V-200")}</g>'),
        it(2, txt(300, 260, "เอลนีโญอาจอ่อนลง", 40, "#4cc3ff") + txt(300, 506, "มี.ค. – เม.ย.", 40, "#fff")),
        it(3, '<path d="M560,240 h300 q24,0 24,24 v130 q0,24 -24,24 h-210 l-50,50 v-50 h-40 q-24,0 -24,-24 v-130 q0,-24 24,-24Z" fill="#fff" stroke="#1e1e24" stroke-width="7"/>'
           + '<text x="710" y="350" font-size="54" font-weight="800" fill="#1e1e24" text-anchor="middle" font-family="Kanit" style="stroke:none">จังหวัดคุณ?</text>')],
}
VGS = "\n".join(f'<div id="vg{i}" class="vg"><svg viewBox="0 0 960 520" width="960" height="520">{"".join(v)}</svg></div>' for i, v in SCENES.items())
# ลูกศรฉาก 4 ให้ชี้ลง (คลายร้อน)
VGS = VGS.replace('<g transform="translate(300,330)">', '<g transform="translate(300,170) rotate(180)">')

TAGS = ["WHAT IF · <r>ร้อนที่สุด</r>ในประวัติศาสตร์", "ต้นเหตุ · <r>ซูเปอร์เอลนีโญ</r>", "ไทย · <r>ร้อน แล้ง</r>", "<r>PM2.5</r> · 40 จังหวัดเสี่ยง", "ตระหนัก · <r>ไม่ตระหนก</r>"]
tags_html = "\n".join(f'<div id="t{i}" class="tag">{t_}</div>' for i, t_ in enumerate(TAGS))

vb0 = f"{CAM0[0] - CAM0[2] / 2} {CAM0[1] - CAM0[2] / 2} {CAM0[2]} {CAM0[2]}"
DATA = dict(SC=SC, SCE=SCE, CAM0=CAM0, CAM=CAM, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, STANDS=STANDS, DOTS=DOTLL, DOT_T0=DOT_T0)
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLD%%": WORLD, "%%LAND%%": land, "%%GRID%%": grid, "%%TH%%": OUTL["Thailand"], "%%THX%%": str(TH[0]), "%%THY%%": str(TH[1]),
             "%%DOTS%%": dots, "%%STANDS%%": STANDS_HTML, "%%VGS%%": VGS, "%%TAGS%%": tags_html, "%%VB0%%": vb0, "%%PW%%": str(PW), "%%TILT%%": str(TILT),
             "%%PLX%%": str(PLX), "%%PLY%%": str(PLY), "%%PERSPY%%": str(PERSPY), "%%HORIZ%%": str(HORIZ), "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
(V / "sync.json").write_text(json.dumps({"SC": SC, "SYNC": SYNC, "DOT_T0": DOT_T0, "STANDS": STANDS}, ensure_ascii=False), encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i, SC[i], "->", SCE[i], [c[0] for c in SYNC[i]])
