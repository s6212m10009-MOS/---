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

TAGS = ["สองเกาหลี <r>ตึงเครียด</r>", "ขีปนาวุธ <r>4 พ.ย.</r>", "ถ้ารบจริง <r>คนไทยทำไง?</r>", "<r>1</r> ติดตามสถานทูต", "<r>2</r> เอกสาร + เงินสด + ประกัน", "ยังไม่มีสงคราม <r>อย่าตื่นตระหนก</r>"]

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
INK = "#1E1E24"
# id, lon, lat, ป้าย, ฉากที่เปิด
PINS = [("dmz", 127.0, 38.1, "DMZ ชายแดน", 0), ("seoul", 126.98, 37.57, "โซล", 2), ("bkk", 100.5, 13.75, "กรุงเทพ", 4)]
# กล้อง: lon, lat, k, y ของหมุดบนวิวพอร์ต
CAM = [(127.4, 38.0, 8.0, 800), (129.5, 39.5, 7.0, 800), (127.0, 37.57, 24.0, 800), (127.0, 37.57, 24.0, 800), (113.7, 25.7, 2.6, 800), (100.5, 13.75, 3.5, 800)]


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
    # 0: ทุ่นระเบิดที่ชายแดน
    0: W("v0t", txt(480, 80, "ทุ่นระเบิดที่ชายแดน", 56))
       + W("v0m", '<g transform="translate(200,290)"><path d="M-95,0 H95 M0,-95 V95 M-67,-67 L67,67 M-67,67 L67,-67" stroke="#fff" stroke-width="10" stroke-linecap="round"/><circle r="70" fill="#3b3b44" stroke="#fff" stroke-width="6"/><circle r="16" fill="#e0243a"/></g>')
       + W("v0w", '<path d="M760,190 L860,370 H660Z" fill="#ffd23f" stroke="#fff" stroke-width="8" stroke-linejoin="round"/>' + txt(760, 335, "!", 110, "#e0243a"))
       + W("v0n", txt(480, 450, "ทหารใต้เจ็บ 2 นาย", 58, "#ffd23f") + txt(480, 505, "โซลชี้ว่าฝั่งเหนือฝัง", 38, "#9fd8ff")),
    # 1: ยิงขีปนาวุธ
    1: W("v1t", txt(480, 80, "ยิงขีปนาวุธหลายลูก", 56))
       + W("v1r", '<g transform="translate(200,290) rotate(40)"><path d="M0,-100 Q34,-45 26,55 H-26 Q-34,-45 0,-100Z" fill="#e8e8ef" stroke="#fff" stroke-width="6"/><path d="M-26,30 L-58,76 L-26,60Z M26,30 L58,76 L26,60Z" fill="#e0243a" stroke="#fff" stroke-width="5" stroke-linejoin="round"/><path d="M-14,58 L0,125 L14,58Z" fill="#ff9a2e"/><circle cy="-30" r="12" fill="#2f9fe0" stroke="#fff" stroke-width="4"/></g>')
       + W("v1d", '<rect x="520" y="200" width="380" height="150" rx="26" fill="#1e1e24" stroke="#fff" stroke-width="8"/>' + txt(710, 305, "4 พ.ย.", 96, "#ffd23f"))
       + W("v1k", txt(480, 455, "คิม โยจอง: ไม่สนใจเจรจา", 48)),
    # 2: โซลห่างชายแดน
    2: W("v2n", txt(480, 135, "&lt;50 กม.", 150, "#ffd23f") + txt(480, 215, "โซล → ชายแดน", 50))
       + W("v2p", stick(330, 350, 0.9) + stick(480, 350, 0.9) + stick(630, 350, 0.9))
       + W("v2l", txt(480, 500, "คนไทยในเกาหลีใต้ ทำงาน+เที่ยว", 40, "#9fd8ff")),
    # 3: สถานทูต + แจ้งญาติ
    3: W("v3t", txt(480, 65, "ติดตามประกาศสถานทูตไทย", 50))
       + W("v3b", '<path d="M480,110 V190" stroke="#fff" stroke-width="6"/><rect x="480" y="106" width="70" height="14" fill="#e0243a"/><rect x="480" y="120" width="70" height="14" fill="#fff"/><rect x="480" y="134" width="70" height="14" fill="#1f4fa0"/>'
                  '<path d="M360,260 L480,185 L600,260Z" fill="#1f6fd0" stroke="#fff" stroke-width="6" stroke-linejoin="round"/><rect x="380" y="260" width="200" height="130" fill="#e8e8ef" stroke="#fff" stroke-width="6"/>'
                  '<rect x="400" y="285" width="26" height="80" fill="#8f98a8"/><rect x="448" y="285" width="26" height="80" fill="#8f98a8"/><rect x="496" y="285" width="26" height="80" fill="#8f98a8"/><rect x="544" y="285" width="26" height="80" fill="#8f98a8"/>')
       + W("v3r", '<path d="M770,235 Q705,245 705,320 L685,352 H855 L835,320 Q835,245 770,235Z" fill="#ffd23f" stroke="#fff" stroke-width="6" stroke-linejoin="round"/><circle cx="770" cy="372" r="16" fill="#ffd23f" stroke="#fff" stroke-width="5"/>')
       + W("v3a", txt(480, 460, "บอกญาติ: เราอยู่ตรงไหน", 52, "#ffd23f")),
    # 4: พาสปอร์ต + เงินสด + ประกัน
    4: W("v4t", txt(480, 70, "เที่ยวบินอาจถูกยกเลิก", 52, "#ffd23f"))
       + W("v4a", '<rect x="95" y="170" width="150" height="200" rx="14" fill="#1f4fa0" stroke="#fff" stroke-width="7"/><circle cx="170" cy="255" r="34" fill="none" stroke="#fff" stroke-width="6"/><path d="M136,255 H204 M170,221 V289" stroke="#fff" stroke-width="5"/>' + txt(170, 440, "พาสปอร์ต", 42))
       + W("v4b", '<rect x="380" y="205" width="200" height="120" rx="14" fill="#1f9d55" stroke="#fff" stroke-width="7"/><circle cx="480" cy="265" r="34" fill="#fff"/>' + txt(480, 282, "฿", 50, "#1f9d55") + txt(480, 440, "เงินสดสำรอง", 42))
       + W("v4c", '<path d="M790,170 l80,28 v70 q0,60 -80,90 q-80,-30 -80,-90 v-70Z" fill="#2f9fe0" stroke="#fff" stroke-width="7" stroke-linejoin="round"/><path d="M752,272 l28,28 l50,-56" fill="none" stroke="#fff" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>' + txt(790, 440, "ประกันเดินทาง", 42)),
}

# กราฟิกบนแผนที่ (พิกัดภูมิศาสตร์ 1° = 10 หน่วย)
import math
_L_MIS = 100
_L_DIST = round(math.hypot(mx(127.0)-mx(126.98), my(38.0)-my(37.57)), 1)
_sx, _sy, _bx, _by = mx(126.98), my(37.57), mx(100.5), my(13.75)
_LF = round(math.hypot(_bx-_sx, _by-_sy), 1)
_ang = math.degrees(math.atan2(_by - _sy, _bx - _sx))
GEO = (
    f'<path id="g_dmz" d="M{mx(126.6)},{my(37.75)} L{mx(127.0)},{my(38.0)} L{mx(127.7)},{my(38.3)} L{mx(128.37)},{my(38.62)}" fill="none" stroke="#ff2b2b" stroke-width="7" stroke-dasharray="16 10" stroke-linecap="round" vector-effect="non-scaling-stroke" opacity="0"/>'
    f'<circle id="g_pulse" cx="{mx(127.0)}" cy="{my(38.1)}" r="1" fill="none" stroke="#ff2b2b" stroke-width="6" vector-effect="non-scaling-stroke" opacity="0"/>'
    f'<path id="g_mis" d="M{mx(125.7)},{my(39.0)} Q{mx(129.3)},{my(43.5)} {mx(133.0)},{my(40.5)}" fill="none" stroke="#ffd23f" stroke-width="1.3" stroke-linecap="round" stroke-dasharray="{_L_MIS} {_L_MIS*1.3}" stroke-dashoffset="{_L_MIS*1.15}"/>'
    f'<circle id="g_sp1" cx="{mx(133.0)}" cy="{my(40.5)}" r="1" fill="none" stroke="#fff" stroke-width="8" vector-effect="non-scaling-stroke" opacity="0"/>'
    f'<circle id="g_sp2" cx="{mx(133.0)}" cy="{my(40.5)}" r="1" fill="none" stroke="#9fd8ff" stroke-width="6" vector-effect="non-scaling-stroke" opacity="0"/>'
    f'<path id="g_dist" d="M{mx(126.98)},{my(37.57)} L{mx(127.0)},{my(38.0)}" fill="none" stroke="#ffd23f" stroke-width="0.35" stroke-linecap="round" stroke-dasharray="{_L_DIST} {_L_DIST*1.3}" stroke-dashoffset="{_L_DIST*1.15}"/>'
    f'<path id="g_fly" d="M{_sx},{_sy} L{_bx},{_by}" fill="none" stroke="#fff" stroke-width="2.3" stroke-linecap="round" stroke-dasharray="{_LF} {_LF*1.3}" stroke-dashoffset="{_LF*1.15}"/>'
    f'<g id="g_plane" opacity="0"><g transform="rotate({_ang:.1f})"><path d="M24,0 L-16,-14 L-8,0 L-16,14Z" fill="#fff" stroke="#1e1e24" stroke-width="3" stroke-linejoin="round"/></g></g>'
)
PLANE0 = [_sx, _sy]
PLANE1 = [_bx, _by]

VGS = "\n".join(f'<div id="vg{i}" class="vg"><svg viewBox="0 0 960 520" width="960" height="520">{VIG[i]}</svg></div>' for i in VIG)

pin_html = ""
for pid, lon, lat, label, sc in PINS:
    wlab = len(label) * 24 + 40
    pin_html += (f'<g id="pin_{pid}" transform="translate({mx(lon)},{my(lat)})"><g class="pi" style="opacity:0">'
                 f'<circle class="pdot" r="16" fill="#e0243a" stroke="#fff" stroke-width="5"/>'
                 f'<g class="plab" opacity="0"><rect x="{-wlab/2}" y="-100" width="{wlab}" height="50" rx="25" fill="#fff" stroke="{INK}" stroke-width="5"/>'
                 f'<text y="-64" font-size="30" font-weight="800" fill="{INK}" text-anchor="middle" font-family="Kanit">{label}</text></g></g></g>')

tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))
HOOK0 = [round(540 - mx(127) * 1.1, 1), -30, 1.1]
DATA = dict(HOOK0=HOOK0, SC=SC, SCE=SCE, CAM=[cam_xy(i) for i in range(N)], PINS=[[p[0], p[4]] for p in PINS], CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, PLANE0=PLANE0, PLANE1=PLANE1)

HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%PINS%%": pin_html, "%%GEO%%": GEO, "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์ ·", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "→", SCE[i])
