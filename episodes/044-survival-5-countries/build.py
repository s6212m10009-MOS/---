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

TAGS = ["มหันตภัยโลก <r>หนีไปไหน?</r>", "<r>1</r> นิวซีแลนด์", "<r>2</r> ไอซ์แลนด์", "<r>3</r> สวิตเซอร์แลนด์", "<r>4-5</r> นอร์เวย์ · ฟินแลนด์", "ไทย… <r>ไม่อยู่ในลิสต์</r>"]

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
INK = "#1E1E24"
# id, lon, lat, ป้าย, ฉากที่เปิด
PINS = [("nz", 173.0, -41.0, "นิวซีแลนด์", 1), ("is", -19.0, 65.0, "ไอซ์แลนด์", 2), ("ch", 8.2, 46.8, "สวิตเซอร์แลนด์", 3),
        ("no", 9.0, 61.0, "นอร์เวย์", 4), ("fi", 26.0, 62.5, "ฟินแลนด์", 4), ("th", 100.5, 13.7, "ไทย · ไม่อยู่ในลิสต์", 5)]
# กล้อง: lon, lat, k, y ของหมุดบนวิวพอร์ต
CAM = [(70, 20, 0.4, 800), (173, -41, 5.0, 800), (-19, 65, 6.0, 800), (8.2, 46.8, 12.0, 800), (18, 62, 4.2, 800), (100.5, 13.7, 3.5, 800)]


def cam_xy(i):
    lon, lat, k, py = CAM[i]
    if i == 0:  # ฮุค: แผนที่เต็มจอ (k>=1.07 ให้ปิดทั้ง 1920px)
        return [round(540 - mx(25) * 1.1, 1), -30, 1.1]
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
    # 1: นิวซีแลนด์โดดเดี่ยว ห่างออสเตรเลีย 1,000+ ไมล์
    1: W("v1n", '<path d="M40,420 Q70,300 130,330 Q150,260 200,300 Q250,360 230,440 Q140,470 40,420Z" fill="#3fae5a" stroke="#fff" stroke-width="6" stroke-linejoin="round"/>')
       + W("v1a", '<path d="M700,420 Q720,310 820,300 Q930,310 950,400 Q900,470 790,460 Q720,470 700,420Z" fill="#d9a441" stroke="#fff" stroke-width="6" stroke-linejoin="round"/>' + txt(825, 395, "ออสเตรเลีย", 36))
       + W("v1d", '<path d="M270,380 H680" stroke="#ffd23f" stroke-width="10" stroke-dasharray="22 16" stroke-linecap="round"/><path d="M270,380 l26,-18 M270,380 l26,18 M680,380 l-26,-18 M680,380 l-26,18" stroke="#ffd23f" stroke-width="10" stroke-linecap="round"/>')
       + W("v1x", txt(475, 330, "1,000+ ไมล์", 76, "#ffd23f"))
       + W("v1f", txt(480, 120, "ฟาร์มกว้าง · น้ำจืดเยอะ", 52) + txt(480, 190, "เลี้ยงตัวเองได้", 52, "#9fd8ff")),
    # 2: ไอซ์แลนด์ แถบพลังงาน 30/70
    2: W("v2h", txt(480, 90, "พลังงานหมุนเวียน", 56) + txt(480, 230, "~100%", 150, "#ffd23f"))
       + W("v2g", '<rect x="80" y="300" width="240" height="90" rx="14" fill="#ff7a3d" stroke="#fff" stroke-width="6"/>' + txt(200, 450, "ความร้อนใต้พิภพ ~30%", 34))
       + W("v2w", '<rect x="320" y="300" width="560" height="90" rx="14" fill="#2f9fe0" stroke="#fff" stroke-width="6"/>' + txt(600, 450, "ไฟฟ้าพลังน้ำ ~70%", 40)),
    # 3: สวิส หลุมหลบภัย
    3: W("v3m", '<path d="M0,500 L200,200 L280,300 L420,120 L560,320 L650,240 L960,500Z" fill="#8f98a8" stroke="#fff" stroke-width="6" stroke-linejoin="round"/><path d="M420,120 L370,200 L420,180 L470,210Z" fill="#fff"/>')
       + W("v3n", txt(480, 330, "370,000", 150, "#ffd23f") + txt(480, 400, "หลุมหลบภัย", 56))
       + W("v3s", '<path d="M480,430 l60,20 v50 q0,40 -60,60 q-60,-20 -60,-60 v-50Z" fill="#1f9d55" stroke="#fff" stroke-width="6" transform="translate(0,30)"/><path d="M450,540 l22,22 l40,-44" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>')
       + W("v3t", txt(480, 55, "รองรับเกือบทั้งประเทศ", 52, "#9fd8ff")),
    # 4: นอร์เวย์ + ฟินแลนด์
    4: W("v4l", '<ellipse cx="190" cy="230" rx="105" ry="55" fill="#2f9fe0" stroke="#fff" stroke-width="6"/><path d="M290,230 L370,170 L370,290Z" fill="#2f9fe0" stroke="#fff" stroke-width="6" stroke-linejoin="round"/><circle cx="130" cy="218" r="9" fill="#fff"/>' + txt(220, 370, "น้ำจืด · อาหารทะเล", 42) + txt(220, 425, "คนอยู่เบาบาง", 40, "#9fd8ff"))
       + W("v4r", '<path d="M730,120 l140,40 v110 q0,90 -140,130 q-140,-40 -140,-130 v-110Z" fill="#e0243a" stroke="#fff" stroke-width="6" stroke-linejoin="round"/><path d="M730,190 v120 M670,250 h120" stroke="#fff" stroke-width="22" stroke-linecap="round"/>' + txt(730, 455, "เตรียมรับมือภัยพิบัติ", 42) + txt(730, 505, "โครงสร้างพื้นฐานมั่นคง", 36, "#ffd23f")),
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
HOOK0 = [round(540 - mx(25) * 1.8, 1), -450, 1.8]
DATA = dict(HOOK0=HOOK0, SC=SC, SCE=SCE, CAM=[cam_xy(i) for i in range(N)], PINS=[[p[0], p[4]] for p in PINS], CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL)

HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%PINS%%": pin_html, "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์ ·", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "→", SCE[i])
