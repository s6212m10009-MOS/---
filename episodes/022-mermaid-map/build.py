"""สร้าง video/index.html ของตอน 022 (แผนที่โลก + ฉากโมชั่น) จาก script.md + video/timing_gm.json
  python build.py
ซับผูกกับเสียงด้วยพลังงานเสียง (วิธีเดียวกับ ../021-naga-3-levels/sync_captions.py)
ตัวสร้างตัวละครไม้จิ้มฟันยืมมาจาก ../021-naga-3-levels/video_gm/index.html"""
import json, re, subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
V = HERE / "video"
timing = json.loads((V / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL = timing["total"]
LINES = timing["lines"]
WORLD = (V / "world-path.txt").read_text()
WORLDLINE = (V / "world-line.txt").read_text()
REF = (HERE.parent / "021-naga-3-levels" / "video_gm" / "index.html").read_text(encoding="utf-8")

# ---- บทพูดพร้อมวงเล็บเน้นสี จากตารางใน script.md ----
rows = []
for l in (HERE / "script.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\| (\d+) \| [\d–]+ \| (.*?) \| .*\|$", l)
    if m and 1 <= int(m.group(1)) <= 13:
        rows.append(re.sub(r"[✅⚠❓️]\s*", "", m.group(2)))
assert len(rows) == 13, len(rows)


def chunk(text, limit=17):
    parts, cur = [], ""
    for w in text.split(" "):
        if cur and len(re.sub(r"[\[\]]", "", cur + " " + w)) > limit:
            parts.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        parts.append(cur)
    return parts


CAPS = [chunk(r) for r in rows]

# ---- ผูกซับกับเสียง ----
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

SC = [0.0] + [round(LINES[i]["start"] - 0.2, 3) for i in range(1, 13)]
SCE = SC[1:] + [TOTAL]

TAGS = ["นางเงือก <r>มีจริงไหม?</r>", "ซีเรียโบราณ · <r>เทพีอตาร์กาติส</r>", "กรีก · <r>น้องสาวอเล็กซานเดอร์</r>",
        "ญี่ปุ่น <r>นิงเงียว</r> · ไทย <r>สุวรรณมัจฉา</r>", "ไทย · <r>พระอภัยมณี</r>", "ปี 1493 · <r>โคลัมบัส</r>",
        "<r>“ไม่งามเท่าที่วาดกัน”</r>", "ปี 1842 · <r>นางเงือกฟีจี</r>", "ปี 2012 · <r>รายการนิยายวิทยาศาสตร์</r>",
        "แต่... สิ่งที่เห็นคือ <r>พะยูน</r>", "ชื่อ <r>Sirenia</r> มาจาก “ไซเรน”", "พะยูนไทย <r>เหลือน้อย</r>", "สรุป: <r>ตำนาน</r> กับ <r>ความจริง</r>"]
PART = [1] * 5 + [2] * 4 + [3] * 4
PARTTXT = {1: "ภาค 1/3 · ตำนานทั่วโลก", 2: "ภาค 2/3 · ผู้เห็นกับของปลอม", 3: "ภาค 3/3 · ความจริง"}

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)

# id, lon, lat, ป้าย, ฉากที่เปิดใช้งาน
PINS = [("syr", 36.2, 36.5, "ซีเรีย", 1), ("gre", 22.5, 39.0, "กรีซ", 2), ("jpn", 138, 36, "ญี่ปุ่น", 3), ("tha", 101, 15, "ไทย", 3),
        ("hisp", -70.5, 19, "ฮิสปานิโอลา", 5), ("nyc", -74, 40.7, "นิวยอร์ก", 7), ("usa", -77, 38.9, "สหรัฐ", 8)]
ROUTES = [("syr", "gre", 2), ("jpn", "tha", 3)]
# กล้อง: lon, lat, k, y ของหมุดบนวิวพอร์ต (None = มองทั้งโลก)
CAM = [(-70.5, 19, 2.4, 800), (36, 36.5, 1.7, 800), (28, 38.5, 1.7, 800), (118, 26, 1.0, 790), (101, 15, 2.4, 800),
       (-70.5, 19, 2.0, 800), (-70.5, 19, 2.0, 800), (-74, 40.7, 2.4, 800), (-77, 38.9, 2.4, 800),
       (20, 15, 0.5, None), (20, 15, 0.5, None), (99.6, 8, 3.0, 800), (20, 15, 0.5, None)]
POSE = [("norm", "smile", "point", 0, 0), ("shock", "o", "up", 0, 0), ("norm", "smile", "chin", 0, 0), ("happy", "smile", "point", 1, 0),
        ("norm", "smile", "chin", 0, 0), ("norm", "flat", "scratch", 0, 0), ("sad", "frown", "shrug", 0, 1), ("shock", "o", "up", 0, 0),
        ("norm", "flat", "shrug", 0, 1), ("happy", "grin", "up", 1, 0), ("norm", "smile", "point", 0, 0), ("sad", "frown", "down", 0, 0),
        ("happy", "smile", "up", 1, 0)]


def cam_xy(i):
    lon, lat, k, py = CAM[i]
    if py is None:
        return [round(540 - mx(lon) * k, 1), round(960 - my(lat) * k, 1), k]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


# ---- ฉากโมชั่น (svg 960x520) ----
INK = "#1E1E24"


def W(idn, inner):  # ห่อให้ gsap ขยับได้โดยไม่ชนกับ transform ภายใน
    return f'<g id="{idn}">{inner}</g>' if idn else inner


def mermaid(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-26,-76 Q0,-112 26,-76 Q32,-40 22,-20 L-22,-20 Q-32,-40 -26,-76Z" fill="#8a4fbf" stroke="{INK}" stroke-width="5"/><circle cx="0" cy="-68" r="24" fill="#fff" stroke="{INK}" stroke-width="6"/><circle cx="-8" cy="-70" r="3.5" fill="{INK}"/><circle cx="8" cy="-70" r="3.5" fill="{INK}"/><path d="M-7,-58 Q0,-52 7,-58" fill="none" stroke="{INK}" stroke-width="3"/><path d="M-16,-40 L16,-40 L12,0 Q40,40 20,90 L0,70 L-20,90 Q-40,40 -12,0Z" fill="#37b3a6" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><path d="M-20,90 L-42,122 L0,100 L42,122 L20,90Z" fill="#37b3a6" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/></g>')


def waves(y, w=960, n=12, col="#6bbce6"):
    d = f"M0,{y}"
    step = w / n
    for _ in range(n):
        d += f" q{step / 4},-22 {step / 2},0 t{step / 2},0"
    return f'<path d="{d} V520 H0Z" fill="{col}" stroke="{INK}" stroke-width="5"/>'


def stick(x, y, s):
    return f'<g transform="translate({x},{y}) scale({s})"><circle cx="0" cy="-60" r="26" fill="#fff" stroke="{INK}" stroke-width="6"/><path d="M0,-34 V30 M0,-14 L-28,12 M0,-14 L28,12 M0,30 L-20,76 M0,30 L20,76" fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round"/></g>'


def ship(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-90,0 H90 L65,45 H-65Z" fill="#a8693a" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><path d="M0,0 V-150" stroke="{INK}" stroke-width="7"/><path d="M6,-145 Q80,-90 6,-20Z" fill="#fff" stroke="{INK}" stroke-width="6"/><path d="M-6,-120 Q-60,-80 -6,-30Z" fill="#fff" stroke="{INK}" stroke-width="6"/></g>')


def fish_tail(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M0,0 Q70,-30 120,0 L160,-40 L160,40 L120,0 Q70,30 0,0Z" fill="#37b3a6" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><circle cx="20" cy="-4" r="5" fill="{INK}"/></g>')


def monkey(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><circle cx="0" cy="0" r="52" fill="#b5835a" stroke="{INK}" stroke-width="6"/><ellipse cx="0" cy="12" rx="32" ry="26" fill="#f2cfa5" stroke="{INK}" stroke-width="4"/><circle cx="-16" cy="-8" r="6" fill="{INK}"/><circle cx="16" cy="-8" r="6" fill="{INK}"/><path d="M-12,22 Q0,32 12,22" fill="none" stroke="{INK}" stroke-width="4"/><circle cx="-56" cy="0" r="16" fill="#b5835a" stroke="{INK}" stroke-width="5"/><circle cx="56" cy="0" r="16" fill="#b5835a" stroke="{INK}" stroke-width="5"/><path d="M-40,52 L40,52 L30,110 L-30,110Z" fill="#b5835a" stroke="{INK}" stroke-width="6"/></g>')


def manatee(x, y, s=1.0, idn="", baby=True):
    b = f'<ellipse cx="-40" cy="46" rx="42" ry="22" fill="#b4bcc5" stroke="{INK}" stroke-width="5"/><circle cx="-68" cy="40" r="4" fill="{INK}"/>' if baby else ""
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><ellipse cx="0" cy="0" rx="150" ry="70" fill="#9aa3ad" stroke="{INK}" stroke-width="7"/><path d="M130,-10 Q190,-60 230,-20 Q200,10 230,40 Q180,50 130,20Z" fill="#9aa3ad" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/><circle cx="-110" cy="-18" r="8" fill="{INK}"/><ellipse cx="-142" cy="6" rx="14" ry="10" fill="#6c747d"/>{b}<path d="M-30,40 Q-10,84 24,66" fill="none" stroke="{INK}" stroke-width="9" stroke-linecap="round"/></g>')


def txt(x, y, s, size=44, col=INK, idn=""):
    return W(idn, f'<text x="{x}" y="{y}" font-size="{size}" font-weight="800" fill="{col}" text-anchor="middle" font-family="Kanit">{s}</text>')


def tv(x, y):
    return f'<g transform="translate({x},{y})"><rect x="-230" y="-140" width="460" height="280" rx="24" fill="#2a2d3a" stroke="{INK}" stroke-width="8"/><rect x="-206" y="-116" width="412" height="232" rx="14" fill="#16213e"/>' + txt(0, -20, "นางเงือก", 56, "#ffd23f") + txt(0, 46, "พบซากแล้ว", 56, "#fff") + "</g>"


VIG = {
    0: waves(340) + ship(260, 310, 1.5, "v0s") + W("v0a", f'<ellipse cx="610" cy="378" rx="46" ry="20" fill="#9aa3ad" stroke="{INK}" stroke-width="5"/>' + txt(610, 326, "?", 56, "#e0243a"))
       + W("v0b", f'<ellipse cx="730" cy="392" rx="46" ry="20" fill="#9aa3ad" stroke="{INK}" stroke-width="5"/>' + txt(730, 340, "?", 56, "#e0243a"))
       + W("v0c", f'<ellipse cx="850" cy="378" rx="46" ry="20" fill="#9aa3ad" stroke="{INK}" stroke-width="5"/>' + txt(850, 326, "?", 56, "#e0243a"))
       + W("v0t", txt(480, 90, "“ไม่สวยเลย!”", 64, "#e0243a")),
    1: waves(380) + mermaid(300, 300, 1.5, "v1m") + txt(700, 300, "เล่ากันว่า", 40) + txt(700, 350, "ทรงกระโดดลงสระ", 40, "#e0243a"),
    2: waves(330) + ship(300, 300, 1.6, "v2s") + mermaid(740, 330, 1.1, "v2m")
       + W("v2b", f'<rect x="500" y="40" width="420" height="120" rx="30" fill="#fff" stroke="{INK}" stroke-width="6"/><path d="M700,160 L730,215 L745,160Z" fill="#fff" stroke="{INK}" stroke-width="6"/>' + txt(710, 90, "“พระเจ้าอเล็กซานเดอร์", 32) + txt(710, 134, "ยังมีชีวิตอยู่ไหม?”", 32, "#e0243a")),
    3: W("v3a", f'<rect x="40" y="110" width="410" height="290" rx="30" fill="#fff" stroke="{INK}" stroke-width="7"/>' + txt(245, 200, "ญี่ปุ่น", 44, "#e0243a") + txt(245, 280, "นิงเงียว", 70) + txt(245, 350, "กินเนื้อแล้วอายุยืน", 32, "#555"))
       + W("v3b", f'<rect x="510" y="110" width="410" height="290" rx="30" fill="#fff" stroke="{INK}" stroke-width="7"/>' + txt(715, 200, "ไทย · รามเกียรติ์", 40, "#e0243a") + txt(715, 280, "สุวรรณมัจฉา", 62) + txt(715, 350, "ธิดาทศกัณฐ์ แปลงเป็นปลา", 30, "#555")),
    4: W("v4a", f'<circle cx="170" cy="190" r="46" fill="#fff" stroke="{INK}" stroke-width="7"/><path d="M124,256 H216 V300 Q170,280 124,300Z" fill="#3a6fd8" stroke="{INK}" stroke-width="6"/><circle cx="155" cy="184" r="5" fill="{INK}"/><circle cx="185" cy="184" r="5" fill="{INK}"/>' + txt(170, 380, "พระอภัยมณี", 34)) + W("v4b", mermaid(500, 250, 1.0) + txt(500, 420, "นางเงือก", 34))
       + W("v4l", f'<path d="M230,215 H440 M335,215 V330 M500,300 V330 H335 M335,330 H640" fill="none" stroke="{INK}" stroke-width="6" stroke-dasharray="14 10"/>')
       + W("v4c", f'<circle cx="780" cy="230" r="46" fill="#fff" stroke="{INK}" stroke-width="7"/><path d="M734,296 H826 V340 Q780,320 734,340Z" fill="#f5b83d" stroke="{INK}" stroke-width="6"/><circle cx="765" cy="224" r="5" fill="{INK}"/><circle cx="795" cy="224" r="5" fill="{INK}"/>' + txt(780, 430, "สินสมุทร", 34, "#e0243a")),
    5: waves(360) + ship(220, 330, 1.4, "v5s") + W("v5a", f'<ellipse cx="620" cy="378" rx="46" ry="20" fill="#9aa3ad" stroke="{INK}" stroke-width="5"/>' + txt(620, 330, "?", 56, "#e0243a"))
       + W("v5b", f'<ellipse cx="730" cy="392" rx="46" ry="20" fill="#9aa3ad" stroke="{INK}" stroke-width="5"/>' + txt(730, 344, "?", 56, "#e0243a"))
       + W("v5c", f'<ellipse cx="840" cy="378" rx="46" ry="20" fill="#9aa3ad" stroke="{INK}" stroke-width="5"/>' + txt(840, 330, "?", 56, "#e0243a")) + txt(480, 70, "8 มกราคม 1493", 44),
    6: W("v6a", mermaid(200, 270, 1.5) + txt(200, 480, "ที่วาดกัน", 36, "#37b3a6")) + txt(480, 260, "vs", 48, "#999")
       + W("v6b", manatee(720, 260, 1.0, "", False) + txt(720, 440, "ที่เห็นจริง", 36, "#e0243a")),
    7: W("v7m", monkey(170, 200, 1.2)) + txt(320, 230, "+", 80) + W("v7f", fish_tail(370, 210, 1.1)) + txt(620, 230, "=", 80)
       + W("v7r", mermaid(780, 250, 1.1) + txt(780, 440, "“นางเงือกฟีจี”", 34, "#e0243a")) + txt(480, 490, "ลิงเย็บติดหางปลา", 36, "#555"),
    8: tv(480, 250) + W("v8st", f'<g transform="translate(600,370) rotate(-10)"><rect x="-190" y="-44" width="380" height="88" rx="14" fill="#fff" stroke="#e0243a" stroke-width="8"/>' + txt(0, 18, "นิยายวิทยาศาสตร์", 48, "#e0243a") + "</g>")
       + W("v8n", txt(480, 495, "NOAA: ไม่เคยพบหลักฐานมนุษย์ครึ่งปลา", 30)),
    9: W("v9m", mermaid(260, 260, 1.5)) + W("v9x", f'<path d="M110,100 L410,440 M410,100 L110,440" stroke="#e0243a" stroke-width="16" stroke-linecap="round"/>')
       + W("v9r", manatee(680, 240, 1.0, "", True) + txt(680, 420, "พะยูน · แมนนาที", 40)),
    10: txt(480, 190, "SIREN", 120, "#e0243a", "v10a") + txt(480, 350, "Sirenia", 120, INK, "v10b") + txt(480, 450, "พะยูน · แมนนาที", 36, "#555"),
    11: waves(400) + W("v11d", manatee(500, 330, 0.95, "", False)) + txt(480, 170, "36 ตัว", 130, "#e0243a", "v11n") + txt(480, 230, "สำรวจเบื้องต้น มี.ค. 2567", 32, "#555"),
}
VGS = "\n".join(f'<div id="vg{i}" class="vg"><svg viewBox="0 0 960 520" width="960" height="520">{VIG[i]}</svg></div>' for i in VIG)

# ---- หมุดบนแผนที่ ----
pin_html = ""
for pid, lon, lat, label, sc in PINS:
    wlab = len(label) * 24 + 40
    pin_html += (f'<g id="pin_{pid}" transform="translate({mx(lon)},{my(lat)})"><g class="pi" style="opacity:0">'
                 f'<circle class="pdot" r="16" fill="#9aa3ad" stroke="{INK}" stroke-width="5"/>'
                 f'<g class="pdug" opacity="0"><ellipse cx="0" cy="-8" rx="34" ry="17" fill="#9aa3ad" stroke="{INK}" stroke-width="4"/><path d="M30,-10 L52,-24 L52,4Z" fill="#9aa3ad" stroke="{INK}" stroke-width="4"/><circle cx="-18" cy="-12" r="3" fill="{INK}"/></g>'
                 f'<g class="plab" opacity="0"><rect x="{-wlab / 2}" y="{40 if pid == 'usa' else -100}" width="{wlab}" height="50" rx="25" fill="#fff" stroke="{INK}" stroke-width="5"/>'
                 f'<text y="{76 if pid == 'usa' else -64}" font-size="32" font-weight="800" fill="{INK}" text-anchor="middle" font-family="Kanit">{label}</text></g></g></g>')
route_html = "".join(
    f'<line id="rt_{a}{b}" x1="{mx([p for p in PINS if p[0] == a][0][1])}" y1="{my([p for p in PINS if p[0] == a][0][2])}" x2="{mx([p for p in PINS if p[0] == b][0][1])}" y2="{my([p for p in PINS if p[0] == b][0][2])}" stroke="#ffd23f" stroke-width="6" stroke-dasharray="14 10" vector-effect="non-scaling-stroke" opacity="0"/>'
    for a, b, _ in ROUTES)

tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))

DATA = dict(SC=SC, SCE=SCE, CAM=[cam_xy(i) for i in range(13)], PINS=[[p[0], p[4]] for p in PINS], ROUTES=ROUTES, CAPS=CAPS, SYNC=SYNC,
            PART=PART, POSE=POSE, TOTAL=TOTAL, PARTTXT=PARTTXT)

HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLD%%": WORLD, "%%WORLDLINE%%": WORLDLINE, "%%PINS%%": pin_html, "%%ROUTES%%": route_html, "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์ ·", TOTAL, "วินาที")
for i in range(13):
    print(i + 1, SC[i], "→", SCE[i])
