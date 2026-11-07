"""สร้าง video/index.html ของตอน 035 (AI แฮกสาธารณูปโภคไทย) จาก lines.py + video/timing_gm.json
  python build.py   (ตั้ง PYTHONIOENCODING=utf-8 ถ้าคอนโซลเป็น cp874)
ยืมฟังก์ชันวาด (W/txt/stick/bag/radio/...) จาก ../025-whatif-world-war/build.py แล้วเพิ่มฉากของตอนนี้
ซับผูกกับเสียงด้วยพลังงานเสียง ไทย + อังกฤษตัวเล็ก"""
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
W, txt, stick, cash, idcard, card = (ns[k] for k in ("W", "txt", "stick", "cash", "idcard", "card"))
INK = ns["INK"]


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

TAGS = ["ถ้า AI แฮก · <r>ไฟ+ประปา</r>ไทย", "ฝรั่งเศส · <r>ตู้เย็นร้านค้า</r>ถูกแฮก", "ฝรั่งเศส · <r>ตู้แช่เลือด</r>", "สงครามอิหร่าน · <r>60+ กลุ่ม</r>", "ไทย · <r>ยังไม่เคย</r>ล่มทั้งประเทศ",
        "สมมติ · <r>ชั่วโมงแรก</r>", "สมมติ · <r>วันที่ 2</r>", "สมมติ · <r>วันที่ 3</r>", "เตรียมวันนี้ · <r>น้ำ+เงินสด</r>", "เตรียมวันนี้ · <r>แบต+วิทยุ</r>", "บ้านคุณมีครบ<r>กี่ข้อ?</r>"]
assert len(TAGS) == N

mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
BKK = (100.5, 13.75)
FRANCE = (2.5, 47.0)
GULF = (54.0, 29.0)


def cam_xy(lon, lat, k, py=None):
    if py is None:
        return [round(540 - mx(lon) * k, 1), round(690 - (my(lat) - 900) * k, 1), k]
    return [round(540 - mx(lon) * k, 1), round(py + 340 - my(lat) * k, 1), k]


WIDE = cam_xy(76, 20, 1.45, 500)
CAM = [WIDE, cam_xy(*FRANCE, 3.4, 260), cam_xy(*FRANCE, 3.4, 260), cam_xy(*GULF, 3.2, 260), cam_xy(*BKK, 3.0, 260), cam_xy(*BKK, 3.0, 260), cam_xy(*BKK, 3.0, 260),
       cam_xy(*BKK, 3.0, 260), cam_xy(*BKK, 3.0, 260), cam_xy(*BKK, 3.0, 260), WIDE]
assert len(CAM) == N
DRIFT = CAM[9]
GREENLL = []
CITIES = []
OUTL = json.loads((V / "outlines.json").read_text(encoding="utf-8"))
def flagfill(idn, d, x0, x1, y0, y1, kind, stroke):
    h, w = y1 - y0, x1 - x0
    if kind == "th":
        u = h / 6
        rr = [(0, 1, "#A51931"), (1, 1, "#fff"), (2, 2, "#2D2A4A"), (4, 1, "#fff"), (5, 1, "#A51931")]
        body = "".join(f'<rect x="{x0}" y="{y0 + a * u:.1f}" width="{w}" height="{b * u + .5:.1f}" fill="{c}"/>' for a, b, c in rr)
    else:
        u = h / 3
        body = "".join(f'<rect x="{x0}" y="{y0 + a * u:.1f}" width="{w}" height="{u + .5:.1f}" fill="{c}"/>' for a, c in [(0, "#239F40"), (1, "#fff"), (2, "#DA0000")])
    return (f'<g id="{idn}" class="it"><clipPath id="cp{idn}"><path d="{d}"/></clipPath><g clip-path="url(#cp{idn})" opacity=".92">{body}</g>'
            f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="3" stroke-linejoin="round" vector-effect="non-scaling-stroke"/></g>')


OUTL = json.loads((V / "outlines.json").read_text(encoding="utf-8"))
dots_html = (
    flagfill("outTh", OUTL["Thailand"], 2760, 2870, 690, 850, "th", "#ffffff")
    + flagfill("outIran", OUTL["Iran"], 2230, 2445, 495, 655, "ir", "#ffffff")
    + f'<g id="fdot" class="it" transform="translate({mx(FRANCE[0])},{my(FRANCE[1])})"><rect x="-22" y="-15" width="15" height="30" fill="#0055A4"/><rect x="-7" y="-15" width="14" height="30" fill="#fff"/><rect x="7" y="-15" width="15" height="30" fill="#EF4135"/><rect x="-22" y="-15" width="44" height="30" fill="none" stroke="#fff" stroke-width="3"/></g>'
    + f'<g id="bdot" class="it" transform="translate({mx(BKK[0])},{my(BKK[1])})"><circle r="11" fill="#e0243a" stroke="#fff" stroke-width="3"/></g>'
)
gdots_html = ""
bx, by = mx(BKK[0]), my(BKK[1])
GRAT = "".join(f"M{mx(lo)},0V1800" for lo in range(-180, 181, 15)) + "".join(f"M0,{my(la)}H3600" for la in range(-90, 91, 15))
ARC = f"M{mx(BKK[0])},{my(BKK[1])} l1,1"

_stick = stick


def stick(x, y, s=1.0, col=INK, idn="", fill="#fff"):
    return _stick(x, y, s, "#fff", idn, "#0a1830") if col == INK else _stick(x, y, s, col, idn, fill)


def x_mark(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M-50,-50 L50,50 M50,-50 L-50,50" stroke="#e0243a" stroke-width="16" stroke-linecap="round"/></g>')


def tick_mark(x, y, r=40, idn=""):
    return W(idn, f'<circle cx="{x}" cy="{y}" r="{r}" fill="#1f9d55" stroke="{INK}" stroke-width="5"/><path d="M{x - r * .45},{y + 2} L{x - r * .1},{y + r * .38} L{x + r * .5},{y - r * .35}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')


def bill(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-90" y="-120" width="180" height="240" rx="10" fill="#fff" stroke="{INK}" stroke-width="7"/><path d="M-60,-80 H60 M-60,-50 H60 M-60,-20 H30 M-60,10 H60 M-60,40 H20" stroke="#9aa3b5" stroke-width="7" stroke-linecap="round"/><rect x="-60" y="68" width="120" height="34" rx="8" fill="#ffd23f" stroke="{INK}" stroke-width="5"/></g>')


def plant(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-110" y="-10" width="220" height="110" fill="#cfd5e1" stroke="{INK}" stroke-width="7"/><rect x="-80" y="-90" width="42" height="80" fill="#9aa3b5" stroke="{INK}" stroke-width="6"/><rect x="-10" y="-120" width="42" height="110" fill="#9aa3b5" stroke="{INK}" stroke-width="6"/><path d="M60,-10 C40,-60 80,-70 62,-120 C110,-80 100,-40 60,-10Z" fill="#ff8a1f" stroke="{INK}" stroke-width="6" stroke-linejoin="round"/><rect x="-30" y="40" width="60" height="60" fill="#6d93c9" stroke="{INK}" stroke-width="5"/></g>')


def bar(x, y, w, h, col, idn=""):
    return W(idn, f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{col}" stroke="{INK}" stroke-width="7"/>')


def coin(x, y, r=34, idn=""):
    return W(idn, f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffd23f" stroke="{INK}" stroke-width="6"/><text x="{x}" y="{y + r * .35}" font-size="{r * 1.1}" font-weight="800" fill="{INK}" text-anchor="middle" font-family="Kanit">฿</text>')


def plug(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-45" y="-50" width="90" height="80" rx="16" fill="#e8eef6" stroke="{INK}" stroke-width="7"/><rect x="-26" y="-85" width="14" height="40" fill="{INK}"/><rect x="12" y="-85" width="14" height="40" fill="{INK}"/><path d="M0,30 V90" stroke="{INK}" stroke-width="10" stroke-linecap="round"/></g>')


def ac(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-120" y="-45" width="240" height="90" rx="22" fill="#e8eef6" stroke="{INK}" stroke-width="7"/><path d="M-90,25 H90" stroke="#9aa3b5" stroke-width="8" stroke-linecap="round"/><path d="M-60,70 q20,30 0,55 M0,70 q20,30 0,55 M60,70 q20,30 0,55" fill="none" stroke="#8fd8ee" stroke-width="8" stroke-linecap="round"/></g>')


BG = ''


def drop_(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M0,-90 C60,-10 70,30 0,70 C-70,30 -60,-10 0,-90Z" fill="#6fc3ec" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/></g>')


def bolt_(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><path d="M20,-100 L-50,10 L-5,10 L-25,100 L55,-20 L8,-20Z" fill="#ffd23f" stroke="{INK}" stroke-width="7" stroke-linejoin="round"/></g>')


def snow(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-70" y="-100" width="140" height="200" rx="14" fill="#e8f6ff" stroke="{INK}" stroke-width="7"/><path d="M-70,-30 H70" stroke="{INK}" stroke-width="6"/><text x="0" y="55" font-size="60" font-weight="800" fill="{INK}" text-anchor="middle" font-family="Kanit">-30°</text></g>')


def bottle(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-26" y="-100" width="52" height="30" rx="8" fill="#fff" stroke="{INK}" stroke-width="6"/><rect x="-42" y="-72" width="84" height="150" rx="22" fill="#8fd8ee" stroke="{INK}" stroke-width="7"/></g>')


def pill(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s}) rotate(-30)"><rect x="-70" y="-30" width="140" height="60" rx="30" fill="#fff" stroke="{INK}" stroke-width="7"/><path d="M0,-30 V30" stroke="{INK}" stroke-width="6"/><rect x="0" y="-30" width="70" height="60" rx="30" fill="#e0243a" stroke="{INK}" stroke-width="7"/></g>')


def phone(x, y, s=1.0, idn="", dead=False):
    xm = '<path d="M-40,-60 L40,60 M40,-60 L-40,60" stroke="#e0243a" stroke-width="14" stroke-linecap="round"/>' if dead else ''
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-55" y="-100" width="110" height="200" rx="18" fill="#cfd5e1" stroke="{INK}" stroke-width="7"/><rect x="-42" y="-78" width="84" height="130" rx="6" fill="#0a1830"/>{xm}</g>')


def radio(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-90" y="-45" width="180" height="100" rx="16" fill="#ffd23f" stroke="{INK}" stroke-width="7"/><circle cx="-40" cy="5" r="28" fill="#fff" stroke="{INK}" stroke-width="6"/><path d="M20,-10 H70 M20,10 H70 M20,30 H70" stroke="{INK}" stroke-width="6" stroke-linecap="round"/><path d="M60,-45 L100,-100" stroke="{INK}" stroke-width="7" stroke-linecap="round"/></g>')


def battery(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-90" y="-45" width="170" height="90" rx="14" fill="#fff" stroke="{INK}" stroke-width="7"/><rect x="80" y="-18" width="18" height="36" rx="5" fill="{INK}"/><rect x="-78" y="-33" width="146" height="66" rx="8" fill="#1f9d55"/></g>')


def medbox(x, y, s=1.0, idn=""):
    return W(idn, f'<g transform="translate({x},{y}) scale({s})"><rect x="-70" y="-60" width="140" height="120" rx="14" fill="#fff" stroke="{INK}" stroke-width="7"/><path d="M-12,-35 H12 V-12 H35 V12 H12 V35 H-12 V12 H-35 V-12 H-12Z" fill="#e0243a"/></g>')



def flag(code, x, y, w=130, idn=""):
    h = round(w * 2 / 3)
    st = f'stroke="{INK}" stroke-width="5"'
    if code == "fr":
        b = f'<rect x="0" y="0" width="{w / 3}" height="{h}" fill="#0055A4"/><rect x="{w / 3}" y="0" width="{w / 3}" height="{h}" fill="#fff"/><rect x="{2 * w / 3}" y="0" width="{w / 3}" height="{h}" fill="#EF4135"/>'
    elif code == "ir":
        b = (f'<rect x="0" y="0" width="{w}" height="{h / 3}" fill="#239F40"/><rect x="0" y="{h / 3}" width="{w}" height="{h / 3}" fill="#fff"/><rect x="0" y="{2 * h / 3}" width="{w}" height="{h / 3}" fill="#DA0000"/>'
             f'<circle cx="{w / 2}" cy="{h / 2}" r="{h / 9}" fill="none" stroke="#DA0000" stroke-width="5"/>')
    elif code == "th":
        u = h / 6
        b = (f'<rect x="0" y="0" width="{w}" height="{u}" fill="#A51931"/><rect x="0" y="{u}" width="{w}" height="{u}" fill="#fff"/><rect x="0" y="{2 * u}" width="{w}" height="{2 * u}" fill="#2D2A4A"/>'
             f'<rect x="0" y="{4 * u}" width="{w}" height="{u}" fill="#fff"/><rect x="0" y="{5 * u}" width="{w}" height="{u}" fill="#A51931"/>')
    else:  # us
        sp = "".join(f'<rect x="0" y="{k * h / 7}" width="{w}" height="{h / 7}" fill="{"#B22234" if k % 2 == 0 else "#fff"}"/>' for k in range(7))
        b = sp + f'<rect x="0" y="0" width="{w * .45}" height="{h * 4 / 7}" fill="#3C3B6E"/>'
    return W(idn, f'<g transform="translate({x},{y})">{b}<rect x="0" y="0" width="{w}" height="{h}" fill="none" {st}/></g>')

VG = {
    1: (snow(200, 250, 1.1, "b2a") + txt(660, 190, "ตู้เย็นซูเปอร์มาร์เก็ต", 52, "#fff", "b2t") + txt(660, 270, "หลายร้อยร้าน", 64, "#ffd23f", "b2u") + txt(660, 360, "ถูกแฮก ต้องทิ้งอาหาร", 46, "#fff", "b2v"), False),
    2: (bottle(190, 270, 1.3, "c3a") + snow(380, 260, 0.9, "c3b") + txt(720, 190, "ตู้แช่เลือด", 64, "#ffd23f", "c3t") + txt(720, 280, "ถูกปรับอุณหภูมิ", 50, "#fff", "c3u") + txt(720, 370, "จับได้ทัน ไม่เสียหาย", 44, "#8fd8ee", "c3v"), False),
    3: (txt(300, 260, "60+", 170, "#ffd23f", "d4n") + txt(300, 360, "กลุ่มแฮกเกอร์", 46, "#fff", "d4t") + drop_(700, 240, 1.4, "d4d") + txt(700, 400, "ระบบประปา สหรัฐ", 44, "#8fd8ee", "d4u") + txt(480, 480, "มีคนเตือน: เอไอ ช่วยให้เร็วขึ้น", 36, "#fff", "d4v"), False),
    4: (txt(480, 230, "ยังไม่เคย", 130, "#ffd23f", "e5n") + txt(480, 330, "ระบบล่มทั้งประเทศ", 60, "#fff", "e5t") + txt(480, 410, "จากการโจมตีไซเบอร์", 44, "#8fd8ee", "e5u"), False),
    5: (bolt_(220, 240, 1.3, "f6a") + drop_(740, 250, 1.3, "f6b") + txt(480, 440, "สมมติ · ชั่วโมงแรก", 52, "#ffd23f", "f6t") + txt(480, 90, "ไฟดับเป็นหย่อม · ประปาหยุด", 44, "#fff", "f6u"), False),
    6: (phone(260, 250, 1.3, "g7a", True) + cash(700, 260, 1.4, "g7b") + txt(480, 90, "สมมติ · วันที่ 2", 52, "#ffd23f", "g7t") + txt(260, 440, "สัญญาณหาย", 40, "#fff", "g7c") + txt(700, 440, "เงินสดเท่านั้น", 40, "#fff", "g7d"), False),
    7: (bottle(180, 250, 1.3, "h8a") + pill(480, 250, 1.4, "h8b") + medbox(780, 250, 1.1, "h8c") + txt(480, 90, "สมมติ · วันที่ 3", 52, "#ffd23f", "h8t") + txt(480, 440, "น้ำ · ยา · อาหาร อาจขาด", 44, "#fff", "h8u"), False),
    8: (bottle(250, 250, 1.5, "i9a") + cash(650, 260, 1.5, "i9b") + txt(250, 440, "น้ำดื่มสำรอง", 44, "#fff", "i9c") + txt(650, 440, "เงินสดติดบ้าน", 44, "#fff", "i9d") + txt(480, 90, "เตรียมวันนี้ ข้อ 1-2", 50, "#ffd23f", "i9e"), False),
    9: (battery(250, 250, 1.4, "j10a") + radio(680, 250, 1.2, "j10b") + txt(250, 440, "พาวเวอร์แบงก์", 44, "#fff", "j10c") + txt(680, 440, "วิทยุถ่านไฟฉาย", 44, "#fff", "j10d") + txt(480, 90, "เตรียมวันนี้ ข้อ 3-4", 50, "#ffd23f", "j10e"), False),
}
assert sorted(VG) == list(range(1, N - 1))
VG[N - 1] = (stick(480, 310, 1.6, INK, "k11s") + W("k11q", f'<circle cx="480" cy="170" r="70" fill="#ffd23f" stroke="{INK}" stroke-width="7"/>' + txt(480, 205, "?", 100, "#111")) + txt(480, 508, "คอมเมนต์ไว้", 36, "#fff", "k11t"), False)
assert sorted(VG) == list(range(1, N))

_FL = {1: [("fr", 40, 0, 170)], 2: [("fr", 40, 0, 170)], 3: [("ir", 40, 10, 210), ("us", 710, 10, 210)], 4: [("th", 375, 0, 210)],
       5: [("th", 20, 20, 150)], 6: [("th", 20, 20, 150)], 7: [("th", 20, 20, 150)], 8: [("th", 20, 20, 150)], 9: [("th", 20, 20, 150)]}
for _i, _fs in _FL.items():
    VG[_i] = ("".join(flag(f[0], f[1], f[2], f[3] if len(f) > 3 else 130, f"fl{_i}{_k}") for _k, f in enumerate(_fs)) + VG[_i][0], VG[_i][1])

LOGS = {
    1: ["> incident: cooling-ctrl / retail FR", "> setpoint changed remotely", "> result: food discarded"],
    2: ["> incident: blood-storage freezers", "> setpoint raised from -30", "> alarm: tech on duty ... CAUGHT", "> blood lost: 0"],
    3: ["> actors: pro-IR groups ... 60+", "> target: water-plc / US", "> analysts: AI may speed attacks"],
    4: ["> TH nationwide cyber outage: NONE", "> status: no national-level failure"],
    5: ["> SIMULATION // hypothetical", "T+1h  grid ... partial outage", "T+1h  water pumps ... STOPPED"],
    6: ["T+2d  mobile signal ... LOST (some areas)", "T+2d  payments ... cash only"],
    7: ["T+3d  water/medicine/food ... RISK", "T+3d  hospitals ... backup generators"],
    8: ["> checklist [1] drinking water ... PREPARE", "> checklist [2] cash at home ... PREPARE"],
    9: ["> checklist [3] power bank ... PREPARE", "> checklist [4] battery radio ... PREPARE"],
    10: ["> checklist: ___/4 ?", "> reply: comments"],
}
LOGS_HTML = "\n".join(
    f'<div class="lw" id="lw{i}">' + "".join(f"<div>{l}</div>" for l in ls) + "</div>" for i, ls in LOGS.items()
)
CUSTOM = set()
ITEMS = {i: [x for x in re.findall(r'id="([A-Za-z0-9_]+)" class="it"', VG[i][0]) if x not in CUSTOM] for i in VG}
VGS = "\n".join(card(f"vg{i}", VG[i][0], VG[i][1]) for i in sorted(VG))
tags_html = "\n".join(f'<div id="t{i}" class="tag" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))
(V / "items.json").write_text(json.dumps({str(k): len(v) for k, v in ITEMS.items()}))

DATA = dict(LOGN={str(k): len(v) for k, v in LOGS.items()}, SC=SC, SCE=SCE, CAM=CAM, DRIFT=DRIFT, CAPS=CAPS, SYNC=SYNC, TOTAL=TOTAL, GDOTS=GREENLL, ITEMS=ITEMS, NR=0)
HTML = (HERE / "template.html").read_text(encoding="utf-8")
for k, v in {"%%TOTAL%%": f"{TOTAL}", "%%WORLDLINE%%": WORLDLINE, "%%DOTS%%": dots_html, "%%ARC%%": ARC, "%%GDOTS%%": gdots_html, "%%BKK%%": f"{bx},{by}", "%%VGS%%": VGS,
             "%%TAGS%%": tags_html, "%%LOGS%%": LOGS_HTML, "%%ASCII%%": (V / "ascii_map.html").read_text(encoding="utf-8"), "%%MARKS%%": (V / "ascii_marks.json").read_text(), "%%DATA%%": json.dumps(DATA, ensure_ascii=False)}.items():
    HTML = HTML.replace(k, v)
(V / "index.html").write_text(HTML, encoding="utf-8")
print("เขียน video/index.html", len(HTML), "ไบต์,", TOTAL, "วินาที")
for i in range(N):
    print(i + 1, SC[i], "->", SCE[i])
