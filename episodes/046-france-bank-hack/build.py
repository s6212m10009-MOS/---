"""สร้าง video/index.html ของตอน 046 (แฮกเกอร์ขโมยเงินธนาคารฝรั่งเศส) — แผนที่โลก ฝรั่งเศส→ไทย + ฉากโมชั่นลอยบนแผนที่ + ชื่อช่อง
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

TAGS = ["ธนาคารฝรั่งเศส <r>ถูกแฮก</r>", "หายไป <r>100 ล้านยูโร</r>", "เงินลูกค้า <r>ปลอดภัย</r>",
        "ยังไม่รู้ <r>วิธีโจมตี</r>", "ไทยเสี่ยง? <r>แอปล่ม</r>", "เตรียมตัว <r>3 ข้อ</r>"]

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
INK = "#1E1E24"
PINS = [("par", 2.35, 48.86, "ฝรั่งเศส", 1), ("tha", 100.5, 13.75, "ไทย", 4)]
CAM = [(4, 46, 4.5, 800), (2.35, 47.5, 9.0, 800), (2.35, 47.5, 9.0, 800), (2.35, 47.5, 9.0, 800), (100.5, 13.75, 7.0, 800), (100.5, 13.75, 7.0, 800)]


def cam_xy(i):
    lon, lat, k, py = CAM[i]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


def txt(x, y, s, size=44, col="#fff", idn="", anchor="middle"):
    t = f'<text x="{x}" y="{y}" font-size="{size}" font-weight="800" fill="{col}" text-anchor="{anchor}" font-family="Kanit" stroke="{INK}" stroke-width="{size*0.28:.1f}" paint-order="stroke" stroke-linejoin="round">{s}</text>'
    return f'<g id="{idn}">{t}</g>' if idn else t


def W(idn, inner):
    return f'<g id="{idn}">{inner}</g>' if idn else inner


def stick(x, y, s=1.0, idn="", col="#fff", head="#fff"):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><circle cx="0" cy="-60" r="26" fill="{head}" stroke="{col}" stroke-width="6"/><path d="M0,-34 V30 M0,-14 L-28,12 M0,-14 L28,12 M0,30 L-20,76 M0,30 L20,76" fill="none" stroke="{col}" stroke-width="8" stroke-linecap="round"/></g>')


def bank(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><path d="M-110,-40 L0,-130 L110,-40Z" fill="#d9a53a" stroke="#fff" stroke-width="6" stroke-linejoin="round"/>'
            + "".join(f'<rect x="{cx-14}" y="-30" width="28" height="100" fill="#f2e6c9" stroke="#fff" stroke-width="5"/>' for cx in (-75, -25, 25, 75))
            + '<rect x="-120" y="70" width="240" height="26" rx="6" fill="#d9a53a" stroke="#fff" stroke-width="6"/></g>')


def coin(x, y, label="€", r=34, fill="#ffd23f"):
    return (f'<g transform="translate({x},{y})"><circle r="{r}" fill="{fill}" stroke="#fff" stroke-width="6"/>'
            f'<text y="{r*0.35:.0f}" font-size="{r*1.1:.0f}" font-weight="800" fill="{INK}" text-anchor="middle" font-family="Kanit">{label}</text></g>')


VIG = {
    1: W("v1b", bank(130, 290, 1.0) + txt(130, 450, "ธนาคาร", 40))
       + W("v1m", f'<rect x="360" y="215" width="240" height="150" rx="16" fill="#12295a" stroke="#fff" stroke-width="6"/>' + txt(480, 280, "แพลตฟอร์ม", 38) + txt(480, 332, "บริษัทภายนอก", 34, "#ffd23f"))
       + W("v1h", stick(830, 300, 1.25, col="#fff", head="#1e1e24") + f'<path d="M800,300 q30,-60 60,0" fill="#1e1e24" stroke="#fff" stroke-width="5"/>' + txt(830, 450, "แฮกเกอร์", 40, "#ff6b6b"))
       + W("v1c", coin(250, 290))
       + W("v1t", txt(480, 80, "100 ล้านยูโร", 78, "#ffd23f") + txt(480, 150, "ใช้บัญชีของธนาคารเอง", 38)),
    2: W("v2s", f'<g transform="translate(260,270)"><path d="M0,-150 L110,-105 Q110,40 0,130 Q-110,40 -110,-105Z" fill="#1f9d55" stroke="#fff" stroke-width="8" stroke-linejoin="round"/><path d="M-48,-5 L-12,35 L54,-45" fill="none" stroke="#fff" stroke-width="18" stroke-linecap="round" stroke-linejoin="round"/></g>')
       + W("v2t", txt(260, 470, "เงินลูกค้าปลอดภัย", 44, "#74c79a"))
       + W("v2h", f'<g transform="translate(700,270)"><path d="M-70,-130 H70 L0,0 L70,130 H-70 L0,0Z" fill="#f2e6c9" stroke="#fff" stroke-width="8" stroke-linejoin="round"/><path d="M-30,-100 H30 L0,-30Z M-45,110 H45 L0,50Z" fill="#d9a53a"/></g>')
       + W("v2u", txt(700, 470, "โอนเงินล่าช้า", 44, "#ffd23f")),
    3: W("v3m", f'<g transform="translate(250,250)"><circle r="95" fill="#12295a" fill-opacity=".6" stroke="#ffd23f" stroke-width="14"/><path d="M68,68 L140,140" stroke="#ffd23f" stroke-width="22" stroke-linecap="round"/></g>')
       + W("v3q", txt(250, 290, "?", 150, "#fff"))
       + W("v3t", txt(480, 70, "ยังไม่เปิดเผยวิธีโจมตี", 50))
       + W("v3c", coin(560, 330, "€") + f'<path d="M610,330 H690" stroke="#fff" stroke-width="8" stroke-linecap="round"/><path d="M670,310 L694,330 L670,350" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>')
       + W("v3b", coin(800, 330, "BTC", 44, "#f7931a") + txt(800, 440, "อาจแปลงเป็นคริปโต", 34, "#ffd23f")),
    4: W("v4p", f'<g transform="translate(220,270)"><rect x="-90" y="-160" width="180" height="320" rx="26" fill="#12295a" stroke="#fff" stroke-width="8"/><path d="M-40,-60 L40,40 M40,-60 L-40,40" stroke="#ff5a5a" stroke-width="20" stroke-linecap="round"/></g>')
       + W("v4s", stick(560, 330, 1.3) + txt(560, 190, "?", 90, "#ffd23f"))
       + W("v4x", txt(480, 60, "แอปใช้ไม่ได้ โอนไม่ได้", 50, "#ff6b6b"))
       + W("v4d", f'<g transform="translate(830,270)"><rect x="-90" y="-100" width="180" height="200" rx="14" fill="#f2e6c9" stroke="#fff" stroke-width="7"/><rect x="-90" y="-100" width="180" height="48" rx="14" fill="#e0243a" stroke="#fff" stroke-width="7"/>' + "".join(f'<circle cx="{-55+(k%4)*37}" cy="{-15+(k//4)*40}" r="9" fill="#1e1e24"/>' for k in range(12)) + '</g>')
       + W("v4t", txt(830, 440, "หลายวัน", 48, "#ffd23f")),
    5: W("v5a", f'<g transform="translate(170,390)"><rect x="-80" y="-45" width="160" height="110" rx="14" fill="#d9a53a" stroke="#fff" stroke-width="7"/><path d="M-30,-45 V-70 Q-30,-90 0,-90 Q30,-90 30,-70 V-45" fill="none" stroke="#fff" stroke-width="9"/><circle cx="0" cy="10" r="22" fill="#1e1e24" stroke="#fff" stroke-width="5"/><text y="20" font-size="30" font-weight="800" fill="#ffd45a" text-anchor="middle" font-family="Kanit">฿</text></g>' + txt(170, 500, "ตู้เซฟเก็บเงินสด", 36))
       + W("v5b", f'<g transform="translate(480,380)"><rect x="-38" y="-95" width="76" height="40" rx="6" fill="#c8ccd6" stroke="#fff" stroke-width="6"/><rect x="-48" y="-60" width="96" height="140" rx="22" fill="#12295a" stroke="#fff" stroke-width="7"/><circle cx="0" cy="-5" r="12" fill="#1e1e24" stroke="#ffd45a" stroke-width="5"/><rect x="-18" y="35" width="36" height="14" rx="7" fill="#ffd45a"/></g>' + txt(480, 500, "กุญแจยืนยันตัวตน", 36))
       + W("v5c", f'<g transform="translate(790,380)"><rect x="-55" y="-90" width="110" height="180" rx="18" fill="#2a2a30" stroke="#fff" stroke-width="7"/>' + "".join(f'<rect x="-30" y="{-60+k*40}" width="60" height="22" rx="5" fill="#31d07a"/>' for k in range(3)) + '<rect x="-14" y="76" width="28" height="9" rx="3" fill="#c8ccd6"/></g>' + txt(790, 500, "พาวเวอร์แบงก์", 36)),
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
