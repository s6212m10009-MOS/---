"""สร้าง video/index.html ของตอน 043 (น้ำท่วมทะเลทรายอียิปต์) — แผนที่โลกซูมเข้าไซนาย + ฉากโมชั่นลอยบนแผนที่ (ไม่มีพื้นการ์ด, ไม่มีลายน้ำ)
  python build.py   (ต้องมี video/timing_gm.json และ video/audio_gm/NN_t.wav จาก make_voice_gemini.py)"""
import json, re, subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
V = HERE / "video"
timing = json.loads((V / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL, LINES = timing["total"], timing["lines"]
WORLDLINE = (V / "world-line.txt").read_text()
N = 6

rows = []
for l in (HERE / "script.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\| (\d+) \| [\d–]+ \| (.*?) \| (.*?) \| .*\|$", l)
    if m:
        rows.append(m.group(3))
assert len(rows) == N, len(rows)


def chunk(text, limit=17):
    parts, cur = [], ""
    for w in text.split(" "):
        if cur and len(re.sub(r"[\[\]]", "", cur + " " + w)) > limit:
            parts.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        parts.append(cur)
    return parts


CAPS = [chunk(r) for r in rows]
SR = 16000


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
    w = [len(re.sub(r"[\s\[\]]", "", c)) for c in chunks]
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

TAGS = ["ทะเลทราย <r>น้ำท่วม?!</r>", "27 ต.ค. 2569 · <r>ไซนายใต้ อียิปต์</r>", "ผู้ประสบเหตุ <r>3 คน</r>",
        "ทำไมทะเลทราย <r>ท่วมได้</r>", "ฟ้าใส… แต่ <r>น้ำมา</r>", "ไม่ใช่ครั้งแรก · <r>เลี่ยงหุบเขา</r>"]

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
INK = "#1E1E24"
# id, lon, lat, ป้าย, ฉากที่เปิด
PINS = [("nuw", 34.66, 29.03, "นูเวบา · วาดี วาตีร์", 1), ("ras", 33.1, 28.35, "2016", 5), ("asw", 32.9, 24.1, "อัสวาน 2021", 5)]
# กล้อง: lon, lat, k, y ของหมุดบนวิวพอร์ต
CAM = [(31, 27, 2.3, 800), (34.66, 29.03, 9.0, 800), (34.66, 29.03, 9.0, 800), (34.66, 29.03, 9.0, 800), (34.66, 29.03, 9.0, 800), (33, 26.2, 4.5, 800)]


def cam_xy(i):
    lon, lat, k, py = CAM[i]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


def txt(x, y, s, size=44, col="#fff", idn="", anchor="middle"):
    t = f'<text x="{x}" y="{y}" font-size="{size}" font-weight="800" fill="{col}" text-anchor="{anchor}" font-family="Kanit" stroke="{INK}" stroke-width="{size*0.28:.1f}" paint-order="stroke" stroke-linejoin="round">{s}</text>'
    return f'<g id="{idn}">{t}</g>' if idn else t


def W(idn, inner):
    return f'<g id="{idn}">{inner}</g>' if idn else inner


def stick(x, y, s=1.0, idn="", col="#fff"):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><circle cx="0" cy="-60" r="26" fill="#fff" stroke="{col}" stroke-width="6"/><path d="M0,-34 V30 M0,-14 L-28,12 M0,-14 L28,12 M0,30 L-20,76 M0,30 L20,76" fill="none" stroke="{col}" stroke-width="8" stroke-linecap="round"/></g>')


def truck(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-120" y="-20" width="240" height="46" rx="8" fill="#6d6d75" stroke="#fff" stroke-width="6"/>'
             f'<path d="M-100,-24 L-30,-110 Q30,-130 90,-70 L100,-24Z" fill="#f5a623" stroke="#fff" stroke-width="6" stroke-linejoin="round"/>'
             f'<path d="M-100,-60 L90,-60 M-80,-90 L96,-40" stroke="#fff" stroke-width="4" opacity=".7"/>'
             f'<path d="M100,-24 L130,-24 L130,-70 L100,-70Z" fill="#e0243a" stroke="#fff" stroke-width="6"/>'
             f'<circle cx="-70" cy="34" r="26" fill="#2a2a30" stroke="#fff" stroke-width="6"/><circle cx="60" cy="34" r="26" fill="#2a2a30" stroke="#fff" stroke-width="6"/></g>')


def wave(y, col="#2f9fe0", w=960, n=10):
    d = f"M0,{y}"
    step = w / n
    for _ in range(n):
        d += f" q{step/4},-24 {step/2},0 t{step/2},0"
    return f'<path d="{d} V520 H0Z" fill="{col}" stroke="#fff" stroke-width="6"/>'


def cloud(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-90,30 Q-110,-10 -60,-14 Q-50,-60 0,-50 Q40,-76 70,-34 Q120,-30 100,30Z" fill="#8f98a8" stroke="#fff" stroke-width="6" stroke-linejoin="round"/></g>')


def raindrops(x0, y0, w, h, n, idn=""):
    s = ""
    for k in range(n):
        x = x0 + (k * 37) % w
        y = y0 + (k * 53) % h
        s += f'<path d="M{x},{y} l-8,26" stroke="#9fd8ff" stroke-width="5" stroke-linecap="round"/>'
    return W(idn, s)


VIG = {
    # 1: ฝนบนภูเขา -> น้ำพัดรถผสมปูน
    1: W("v1c", cloud(180, 60, 1.4)) + W("v1r", raindrops(90, 110, 190, 120, 9))
       + W("v1h", f'<path d="M0,420 L120,240 L230,330 L330,200 L440,320 L520,430Z" fill="#a8895a" stroke="#fff" stroke-width="6" stroke-linejoin="round"/>')
       + wave(430) + W("v1t", truck(560, 390, 1.15)) + W("v1w", wave(470, "#1e78c2", 960, 12)),
    # 2: ตัวเลข 1/1/1
    2: W("v2a", txt(165, 280, "1", 230, "#e0243a") + txt(165, 360, "เสียชีวิต", 52)) + W("v2b", txt(480, 280, "1", 230, "#ffd23f") + txt(480, 360, "สูญหาย", 52))
       + W("v2c", txt(795, 280, "1", 230, "#fff") + txt(795, 360, "บาดเจ็บ", 52)) + W("v2d", txt(480, 450, "ทีมกู้ภัยยังค้นหาต่อ", 44, "#ffd23f")),
    # 3: ตัดขวาง ภูเขา -> วาดี ดินแข็งซึมไม่ทัน
    3: W("v3m", f'<path d="M0,500 L0,300 L180,90 L330,250 L450,430 L520,460 L620,430 L760,230 L960,300 V500Z" fill="#c9a05e" stroke="#fff" stroke-width="6" stroke-linejoin="round"/>')
       + W("v3c", cloud(250, 50, 1.3)) + W("v3r", raindrops(150, 90, 200, 110, 10))
       + W("v3f", f'<path d="M270,200 L360,300 L450,420 L520,452 L640,430" fill="none" stroke="#2f9fe0" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="26 18"/>')
       + W("v3w", wave(445, "#2f9fe0", 330, 4).replace("M0,445", "M360,445").replace("H0Z", "H360Z").replace("V520", "V500"))
       + W("v3t1", txt(700, 150, "ดินแข็ง", 54, "#ffd23f") + txt(700, 210, "ซึมไม่ทัน", 54)) + W("v3t2", txt(500, 540, "รวมเป็นกระแสเดียว", 44, "#9fd8ff")),
    # 4: ฟ้าใส ตัวคนยืน น้ำมาจากขอบจอ
    4: W("v4s", f'<circle cx="780" cy="90" r="56" fill="#ffd23f" stroke="#fff" stroke-width="6"/>' + "".join(f'<path d="M780,90 l{int(95*np.cos(a))},{int(95*np.sin(a))}" stroke="#ffd23f" stroke-width="7" stroke-linecap="round" transform="translate(0,0)"/>' for a in np.linspace(0, 6.28, 9)[:-1]))
       + W("v4g", f'<path d="M0,430 H960 V520 H0Z" fill="#e8c986" stroke="#fff" stroke-width="6"/>')
       + stick(520, 380, 1.4) + W("v4c", cloud(110, 80, 0.9) + raindrops(40, 120, 140, 90, 6) + txt(110, 190, "ฝนตกไกลต้นน้ำ", 34, "#9fd8ff"))
       + W("v4w", wave(420, "#1e78c2", 520, 6).replace("M0,420", "M-540,420").replace("H0Z", "H-20Z"))
       + W("v4x", txt(520, 270, "โดยไม่มีสัญญาณ", 50, "#e0243a")),
    # 5: หมุดซีด ป้ายห้าม (ตราอยู่นอก svg)
}
VGS = "\n".join(f'<div id="vg{i}" class="vg"><svg viewBox="0 0 960 520" width="960" height="520">{VIG[i]}</svg></div>' for i in VIG)

pin_html = ""
for pid, lon, lat, label, sc in PINS:
    wlab = len(label) * 24 + 40
    pin_html += (f'<g id="pin_{pid}" transform="translate({mx(lon)},{my(lat)})"><g class="pi" style="opacity:0">'
                 f'<circle class="pdot" r="16" fill="#e0243a" stroke="#fff" stroke-width="5"/>'
                 f'<g class="plab" opacity="0"><rect x="{-wlab/2}" y="-100" width="{wlab}" height="50" rx="25" fill="#fff" stroke="{INK}" stroke-width="5"/>'
                 f'<text y="-64" font-size="30" font-weight="800" fill="{INK}" text-anchor="middle" font-family="Kanit">{label}</text></g></g></g>')

tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))
DATA = dict(SC=SC, SCE=SCE, CAM=[cam_xy(i) for i in range(N)], PINS=[[p[0], p[4]] for p in PINS], CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL)

HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%PINS%%": pin_html, "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์ ·", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "→", SCE[i])
