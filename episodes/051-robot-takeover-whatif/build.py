"""สร้าง video/index.html ของตอน 051 (ถ้าหุ่นยนต์ครองโลก) — แผนที่โลก + ฉากโมชั่นลอยบนแผนที่ + ลายน้ำช่อง
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

TAGS = ["หุ่นยนต์ครองโลก <r>ไทยเจออะไร?</r>", "<r>จีน</r> ผลิตเกือบทั้งหมด", "ด่านแรก: <r>สมองของมัน</r>", "งานที่<r>เสี่ยงก่อน</r>", "พลิกมุม: <r>ไทยขาดคน</r>", "ยึดโลก? <r>ยังไม่มีหลักฐาน</r>"]

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
INK = "#1E1E24"
# id, lon, lat, ป้าย, ฉากที่เปิด
PINS = [("cn", 104.0, 35.0, "จีน", 1), ("th", 100.5, 15.0, "ไทย", 2), ("bk", 100.5, 13.7, "กรุงเทพฯ", 3), ("th2", 100.5, 15.0, "ไทย", 4)]
# กล้อง: lon, lat, k, y ของหมุดบนวิวพอร์ต
CAM = [(70, 20, 0.4, 800), (104, 35, 3.6, 800), (100.5, 15, 7.0, 800), (100.5, 13.7, 12.0, 800), (100.5, 15, 6.0, 800), (100.5, 15, 3.5, 800)]


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


def robot(x, y, s=1.0, idn="", eye="#ff2a2a", body="#aeb6c4"):
    arm = lambda c, w: f'<path d="M-52,-155 L-82,-72 M52,-155 L82,-72 M-24,-55 V0 M24,-55 V0" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round"/>'
    return W(idn, f'<g transform="translate({x},{y}) scale({s})">' + arm("#fff", 32) + arm(body, 20)
             + f'<path d="M0,-250 V-282" stroke="#fff" stroke-width="8"/><circle cy="-288" r="11" fill="{eye}" stroke="#fff" stroke-width="4"/>'
             + f'<rect x="-54" y="-172" width="108" height="122" rx="16" fill="{body}" stroke="#fff" stroke-width="7"/><circle cy="-112" r="20" fill="{eye}" stroke="#fff" stroke-width="5"/>'
             + f'<rect x="-46" y="-252" width="92" height="74" rx="15" fill="#2a2d36" stroke="#fff" stroke-width="7"/>'
             + f'<circle cx="-20" cy="-216" r="11" fill="{eye}"/><circle cx="20" cy="-216" r="11" fill="{eye}"/></g>')


def job(x, label, idn):
    return W(idn, f'<rect x="{x}" y="250" width="280" height="130" rx="16" fill="#fff" stroke="{INK}" stroke-width="7"/>'
             f'<text x="{x+140}" y="330" font-size="42" font-weight="800" fill="{INK}" text-anchor="middle" font-family="Kanit">{label}</text>'
             f'<path d="M{x+36},276 L{x+244},356 M{x+244},276 L{x+36},356" stroke="#e0243a" stroke-width="15" stroke-linecap="round"/>')


VIG = {
    1: W("v1h", txt(480, 70, "ส่งมอบทั่วโลก ครึ่งแรกปี 2569", 46) + txt(480, 215, "~19,100 ตัว", 135, "#ffd23f"))
       + W("v1g", txt(480, 295, "โตเกือบ 4 เท่า", 56, "#ff8a75"))
       + W("v1b", f'<rect x="60" y="335" width="840" height="84" rx="16" fill="#31343d" stroke="#fff" stroke-width="6"/><rect id="v1fill" x="60" y="335" width="815" height="84" rx="16" fill="#e0243a" stroke="#fff" stroke-width="6"/>' + txt(470, 395, "ผู้ผลิตจีน กว่า 97%", 54))
       + "".join(robot(180 + k * 150, 660, 0.58, f"v1r{k}") for k in range(5)),
    2: W("v2h", txt(480, 70, "AI อาจกระทบแรงงานไทย", 52) + txt(480, 225, "8.7 ล้านคน", 150, "#ffd23f"))
       + "".join(stick(160 + k * 160, 370, 1.05, f"v2p{k}", "#ff4b3a" if k == 2 else "#fff") for k in range(5))
       + W("v2t", txt(480, 510, "ราว 1 ใน 5 ของแรงงานทั้งประเทศ", 44, "#9fd8ff")),
    3: W("v3h", txt(480, 70, "อาจถูกแทนที่", 56) + txt(480, 215, "2.2 ล้านคน", 145, "#ffd23f"))
       + job(20, "เสมียน", "v3a") + job(340, "บริการลูกค้า", "v3b") + job(660, "บัญชี", "v3c")
       + W("v3k", txt(480, 470, "กว่าครึ่งอยู่กรุงเทพ-ปริมณฑล", 50, "#9fd8ff")),
    4: W("v4h", txt(480, 70, "อีกราว 10 ปี · อายุ 60+", 52) + txt(480, 225, "เกิน 30%", 150, "#ffd23f"))
       + W("v4e", stick(250, 400, 1.3, "", "#fff") + '<path d="M292,395 q24,-16 30,10 V505" fill="none" stroke="#f5a623" stroke-width="10" stroke-linecap="round"/>')
       + robot(690, 505, 0.85, "v4r", "#25d0ff")
       + W("v4l", '<path d="M360,420 H540" stroke="#ffd23f" stroke-width="10" stroke-dasharray="20 14" stroke-linecap="round"/><path d="M360,420 l24,-16 M360,420 l24,16" stroke="#ffd23f" stroke-width="10" stroke-linecap="round"/>' + txt(460, 365, "งานหนักขาดคน", 46)),
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

ROBOTS = "".join(f'<g id="m{k+1}">{robot(0, 0, s, eye="#ff1f1f", body="#8f97a6")}</g>' for k, s in enumerate((1.3, 1.3, 1.9)))
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%ROBOTS%%": ROBOTS, "%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%PINS%%": pin_html, "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์ ·", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "→", SCE[i])
