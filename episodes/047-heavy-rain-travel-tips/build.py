"""สร้าง video/index.html ของตอน 047 (ฝนตกหนักทั้งคืน เดินทางยังไง) ด้วยสไตล์ตอน 028: แผนที่ดาวเทียมมืด + แท็กบน + ซับเหลือง/แดง + ฉากลอย
  python build.py   (ต้องมี video/timing_gm.json และ video/audio_gm/NN_t.wav จาก make_voice.py)"""
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
txt, card = ns["txt"], ns["card"]
INK = "#1E1E24"


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

TAGS = ["ฝนตก<r>หนัก</r> ทั้งคืน", "ถนนที่ลุ่ม · <r>น้ำขัง</r>", "<r>รถติด</r> · ถนนลื่น", "ใกล้ภูเขา · <r>น้ำหลาก</r>", "ก่อนออก · <r>เช็กพยากรณ์</r>",
        "เผื่อเวลา · <r>ลดความเร็ว</r>", "ไฟหน้า · <r>จอดให้ปลอดภัย</r>", "อย่า<r>ฝ่าน้ำ</r> ไม่รู้ลึก", "พื้นที่คุณ · <r>ฝนหนักไหม?</r>"]

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
BKK = (100.5, 13.75)
NORTH = (98.99, 18.79)


def cam_xy(lon, lat, k, py=260):
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


CAM = [cam_xy(101, 14, 2.4), cam_xy(100.5, 13.75, 4.0), cam_xy(100.5, 14.5, 3.4), cam_xy(99.8, 16.4, 3.6), cam_xy(101, 13.5, 2.9),
       cam_xy(101, 13.5, 2.9), cam_xy(101, 13.5, 2.9), cam_xy(100.5, 13.75, 3.6), cam_xy(101, 13, 3.0)]

GREENLL = [(100.5, 13.75), (98.99, 18.79), (98.4, 7.88), (102.83, 16.43), (100.47, 7.0), (101.3, 12.7), (99.9, 15.1), (104.8, 15.2), (100.0, 17.6), (102.1, 14.0), (98.98, 12.9), (100.9, 16.8)]
OUTL = json.loads((V / "outlines.json").read_text(encoding="utf-8"))
bx, by, nx, ny = mx(BKK[0]), my(BKK[1]), mx(NORTH[0]), my(NORTH[1])
BLUE = "#4cc3ff"
dots_html = (
    f'<path id="outTh" class="it" d="{OUTL["Thailand"]}" fill="{BLUE}" fill-opacity=".10" stroke="{BLUE}" stroke-width="3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>'
    f'<g transform="translate({bx},{by})"><circle id="rc0" class="it" r="42" fill="{BLUE}" fill-opacity=".25" stroke="{BLUE}" stroke-width="3" vector-effect="non-scaling-stroke" stroke-dasharray="12 8"/></g>'
    f'<g transform="translate({nx},{ny})"><circle id="rc1" class="it" r="52" fill="{BLUE}" fill-opacity=".25" stroke="{BLUE}" stroke-width="3" vector-effect="non-scaling-stroke" stroke-dasharray="12 8"/></g>'
    f'<path id="flow" class="it" d="M{nx},{ny + 6} Q{nx + 18},{(ny + by) / 2} {bx - 10},{by - 10}" pathLength="1" fill="none" stroke="{BLUE}" stroke-width="6" stroke-linecap="round" stroke-dasharray="1" stroke-dashoffset="1" vector-effect="non-scaling-stroke"/>'
)
gdots_html = "".join(f'<g id="gd{k}" class="gdot" transform="translate({mx(lo)},{my(la)})"><circle r="8" fill="{BLUE}" stroke="#fff" stroke-width="2.5"/></g>' for k, (lo, la) in enumerate(GREENLL))
pins_html = (
    f'<g id="pin_bkk" transform="translate({bx},{by})"><g class="pi" style="opacity:0"><circle r="16" fill="#e0243a" stroke="#1e1e24" stroke-width="5"/><g class="plab"><rect x="-110" y="-100" width="220" height="50" rx="25" fill="#fff" stroke="#1e1e24" stroke-width="5"/><text y="-64" font-size="32" font-weight="800" fill="#1e1e24" text-anchor="middle" font-family="Kanit">กรุงเทพฯ</text></g></g></g>'
    f'<g id="pin_north" transform="translate({nx},{ny})"><g class="pi" style="opacity:0"><circle r="16" fill="#e0243a" stroke="#1e1e24" stroke-width="5"/><g class="plab"><rect x="-110" y="-100" width="220" height="50" rx="25" fill="#fff" stroke="#1e1e24" stroke-width="5"/><text y="-64" font-size="32" font-weight="800" fill="#1e1e24" text-anchor="middle" font-family="Kanit">ภาคเหนือ</text></g></g></g>'
)

# ---------- ตัวช่วยวาด ----------
ST = '#fff'


def g(inner):  # องค์ประกอบระดับบนสุดของฉาก: อนิเมชันเข้าทีละชิ้นตามลำดับ
    return f'<g class="it">{inner}</g>'


def t(x, y, s, size=48, col="#fff"):
    return g(txt(x, y, s, size, col))


def car(x, y, s=1.0, col="#e0243a", brake=True):
    b = '<rect x="-118" y="-22" width="12" height="16" fill="#ff5d6c" stroke="#fff" stroke-width="3"/>' if brake else ""
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M-110,0 L-92,-32 Q-60,-64 -10,-64 L44,-64 Q80,-62 94,-30 L112,-24 Q122,-20 122,0Z" fill="{col}" stroke="{ST}" stroke-width="6" stroke-linejoin="round"/>'
            f'<path d="M-76,-32 Q-52,-54 -10,-54 L20,-54 L20,-32Z M32,-54 L52,-54 Q76,-52 82,-32 L32,-32Z" fill="#cfe8ff" stroke="{ST}" stroke-width="3"/>'
            f'{b}<circle cx="-62" cy="4" r="24" fill="#2a2a30" stroke="{ST}" stroke-width="6"/><circle cx="68" cy="4" r="24" fill="#2a2a30" stroke="{ST}" stroke-width="6"/></g>')


def wave(y, x0=0, x1=960, col="#2f9fe0", n=10, bottom=520):
    step = (x1 - x0) / n
    d = f"M{x0},{y}" + "".join(f" q{step / 4},-24 {step / 2},0 t{step / 2},0" for _ in range(n))
    return f'<path d="{d} V{bottom} H{x0}Z" fill="{col}" stroke="{ST}" stroke-width="6"/>'


def cloud(x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})"><path d="M-90,30 Q-110,-10 -60,-14 Q-50,-60 0,-50 Q40,-76 70,-34 Q120,-30 100,30Z" fill="#8f98a8" stroke="{ST}" stroke-width="6" stroke-linejoin="round"/></g>'


def drops(x0, y0, w, h, n):
    return "".join(f'<path d="M{x0 + (k * 37) % w},{y0 + (k * 53) % h} l-8,26" stroke="#9fd8ff" stroke-width="5" stroke-linecap="round"/>' for k in range(n))


def xmark(x, y, s=1.0):
    return f'<g transform="translate({x},{y}) scale({s})"><path d="M-50,-50 L50,50 M50,-50 L-50,50" stroke="#e0243a" stroke-width="18" stroke-linecap="round"/></g>'


def tick(x, y, r=40):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1f9d55" stroke="{ST}" stroke-width="5"/>'
            f'<path d="M{x - r * .45},{y + 2} L{x - r * .1},{y + r * .38} L{x + r * .5},{y - r * .35}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')


def phone(x, y, w=190, h=340):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="34" fill="#2a2d3a" stroke="{ST}" stroke-width="6"/>'
            f'<rect x="{x + 16}" y="{y + 40}" width="{w - 32}" height="{h - 80}" rx="10" fill="#cfe8ff"/>')


SCENES = {
    # 1 ถนนที่ลุ่ม น้ำขัง
    1: [g(f'<path d="M40,500 L350,210 L610,210 L920,500Z" fill="#3a3d48" stroke="{ST}" stroke-width="6" stroke-linejoin="round"/><path d="M480,500 L480,220" stroke="#fff" stroke-width="7" stroke-dasharray="26 22"/>'),
        g(f'<ellipse cx="470" cy="392" rx="270" ry="58" fill="#2f9fe0" fill-opacity=".9" stroke="{ST}" stroke-width="6"/><ellipse cx="470" cy="392" rx="150" ry="28" fill="none" stroke="#fff" stroke-width="4" opacity=".7"/>'),
        g(f'<rect x="790" y="230" width="26" height="230" rx="8" fill="#e8e8ee" stroke="{ST}" stroke-width="5"/>' + "".join(f'<path d="M790,{260 + 40 * k} h26" stroke="#e0243a" stroke-width="5"/>' for k in range(5))),
        t(803, 215, "?", 90, "#e0243a"), t(480, 110, "น้ำขัง", 84, BLUE), t(480, 170, "ลึกกว่าที่เห็น", 50, "#ffd23f")],
    # 2 รถติด ถนนลื่น
    2: [g(car(140, 330, .9, "#2d6ae0")), g(car(360, 330, .9, "#f08a1c")), g(car(580, 330, .9, "#37b3a6")), g(car(800, 330, .9, "#e0243a")),
        t(480, 130, "รถติดยาว", 84, "#e0243a"),
        g('<path d="M60,450 q60,-34 120,0 t120,0 t120,0 t120,0 t120,0 t120,0 t120,0" fill="none" stroke="#ffd23f" stroke-width="9" stroke-linecap="round"/>'),
        t(480, 505, "ถนนลื่น · มองไม่ชัด", 48, "#fff")],
    # 3 ภูเขา น้ำไหลหลาก
    3: [g(f'<path d="M0,440 L170,190 L300,310 L470,100 L640,310 L770,210 L960,440Z" fill="#6e7d4a" stroke="{ST}" stroke-width="6" stroke-linejoin="round"/>'),
        g(cloud(150, 60, .95) + drops(80, 100, 190, 100, 8)),
        g(f'<path d="M470,150 L500,260 L430,350 L510,420" fill="none" stroke="#2f9fe0" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="26 18"/>'),
        g(f'<rect x="760" y="360" width="90" height="70" fill="#f7f0df" stroke="{ST}" stroke-width="5"/><path d="M748,364 L805,308 L862,364Z" fill="#e0243a" stroke="{ST}" stroke-width="5" stroke-linejoin="round"/>'),
        t(480, 500, "น้ำไหลหลาก", 72, "#e0243a")],
    # 4 เช็กพยากรณ์ + เส้นทาง
    4: [g(phone(130, 60)), g(cloud(225, 200, .7) + drops(165, 225, 120, 40, 4)), g(tick(330, 90, 38)), t(225, 340, "ฝนตก", 46, "#111"),
        g(f'<path d="M500,420 Q580,300 660,360 T830,190" fill="none" stroke="#fff" stroke-width="9" stroke-dasharray="20 14" stroke-linecap="round"/><circle cx="500" cy="420" r="20" fill="#1f9d55" stroke="{ST}" stroke-width="5"/><circle cx="830" cy="190" r="22" fill="#e0243a" stroke="{ST}" stroke-width="5"/>'),
        t(660, 480, "เช็กเส้นทาง", 48, "#ffd23f"), t(660, 110, "พยากรณ์อากาศ", 46, "#fff")],
    # 5 เผื่อเวลา / ลดความเร็ว / เว้นระยะ
    5: [g(f'<circle cx="170" cy="230" r="86" fill="#fff" stroke="{ST}" stroke-width="7"/><path d="M170,230 V170 M170,230 L214,252" stroke="{INK}" stroke-width="9" stroke-linecap="round"/><circle cx="250" cy="150" r="32" fill="#1f9d55" stroke="{ST}" stroke-width="5"/><path d="M250,134 V166 M234,150 H266" stroke="#fff" stroke-width="8" stroke-linecap="round"/>'),
        t(170, 380, "เผื่อเวลา", 42, "#ffd23f"),
        g(f'<path d="M390,300 A90,90 0 0 1 570,300Z" fill="#2a2d3a" stroke="{ST}" stroke-width="7"/><path d="M480,300 L430,240" stroke="#e0243a" stroke-width="9" stroke-linecap="round"/><path d="M480,130 V200 M450,172 L480,204 L510,172" fill="none" stroke="#e0243a" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>'),
        t(480, 380, "ลดความเร็ว", 42, "#e0243a"),
        g(car(700, 250, .5, "#37b3a6") + car(870, 250, .5, "#2d6ae0", False) + '<path d="M755,170 H820 M772,152 L750,170 L772,188 M803,152 L825,170 L803,188" fill="none" stroke="#ffd23f" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'),
        t(790, 380, "เว้นระยะ", 42, "#fff")],
    # 6 ไฟหน้า / ไม่จอดริมคลอง ใต้ต้นไม้ใหญ่
    6: [g('<path d="M345,290 L690,200 L690,380Z" fill="#ffd23f" fill-opacity=".38"/>'), g(car(230, 330, 1.3, "#2d6ae0", False)),
        t(260, 120, "เปิดไฟหน้า", 56, "#ffd23f"),
        g(f'<rect x="770" y="300" width="26" height="120" fill="#8a5a2e" stroke="{ST}" stroke-width="5"/><circle cx="783" cy="250" r="78" fill="#2f9d55" stroke="{ST}" stroke-width="6"/>' + wave(452, 640, 960, "#2f9fe0", 4, 500)),
        g(xmark(790, 330, 1.3)), t(790, 120, "ห้ามจอด", 56, "#e0243a"), t(790, 505, "ริมคลอง · ใต้ต้นไม้ใหญ่", 30, "#fff")],
    # 7 อย่าฝ่าน้ำ
    7: [g(car(480, 330, 1.7, "#e0243a", False)), g(wave(350, 0, 960, "#1e78c2", 12, 520)), g(wave(402, 0, 960, "#2f9fe0", 12, 520)),
        g(xmark(480, 262, 1.6)), t(480, 90, "น้ำลึกเท่าไหร่?", 70, "#ffd23f"), t(480, 500, "เครื่องดับ · รถลอย", 56, "#e0243a")],
    # 8 ประกาศเตือน
    8: [t(480, 90, "ฝนตกหนักไหม?", 84, "#ffd23f"),
        g(phone(110, 130, 180, 330)), g(f'<path d="M200,230 q-46,0 -46,56 v24 l-18,28 h128 l-18,-28 v-24 q0,-56 -46,-56Z" fill="#ffd23f" stroke="{ST}" stroke-width="6" stroke-linejoin="round"/><circle cx="200" cy="360" r="14" fill="#ffd23f" stroke="{ST}" stroke-width="5"/><circle cx="252" cy="236" r="16" fill="#e0243a" stroke="#fff" stroke-width="4"/>'),
        t(620, 290, "เช็ก", 56, "#fff"), t(620, 360, "ประกาศเตือน", 60, BLUE), t(620, 430, "ในพื้นที่คุณ", 50, "#fff")],
}
SCENES_NS = {i: len(v) for i, v in SCENES.items()}
VGS = "\n".join(card(f"vg{i}", "".join(v), True) for i, v in SCENES.items())
(V / "items.json").write_text(json.dumps(SCENES_NS), encoding="utf-8")

# ฝนเต็มจอ
rng = np.random.default_rng(5)
RAIN = [dict(x=int(rng.integers(-40, 1100)), dur=round(float(rng.uniform(.5, .85)), 2), delay=round(float(rng.uniform(0, .8)), 2), len=int(rng.integers(40, 80))) for _ in range(60)]
rain_html = "".join(f'<path id="rn{k}" d="M{r["x"]},-100 l-{r["len"] // 3},{r["len"]}" stroke="#bfe6ff" stroke-width="{3 + k % 3}" stroke-linecap="round" opacity="{.35 + (k % 4) * .1:.2f}"/>' for k, r in enumerate(RAIN))
tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t_}</div>' for i, t_ in enumerate(TAGS))

DATA = dict(SC=SC, SCE=SCE, CAM=CAM, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, GDOTS=GREENLL, RAIN=RAIN, NITEMS=SCENES_NS)
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%DOTS%%": dots_html, "%%GDOTS%%": gdots_html, "%%PINS%%": pins_html,
             "%%RAIN%%": rain_html, "%%VGS%%": VGS, "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "->", SCE[i])
