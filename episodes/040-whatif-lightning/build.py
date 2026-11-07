"""สร้าง video/index.html ของตอน 040 (ฟ้าฝ่า) จาก script.md
พื้นหลัง: แผนที่ดาวเทียมไทย → ภาคกลาง → กรุงเทพ → ถนน (ชั้นจาก video/assets/geo.json)
  python build.py [--total 56]
ตอนนี้ซับใช้เวลาตามตารางใน script.md; เมื่อมีเสียงพากย์แล้วให้ใส่ video/timing_gm.json (เหมือน 022) แล้วรันใหม่
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = HERE / "video"
geo = json.loads((V / "assets" / "geo.json").read_text(encoding="utf-8"))

# ---- บทพูดต่อซีนจาก script.md ----
rows = []
for l in (HERE / "script.md").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\| (\d+) \| [\d–]+ \| (.*?) \| (.*?) \| .*\|$", l)
    if m:
        rows.append(m.group(3))
assert len(rows) == 7, len(rows)


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


# ---- ผูกซับ/ซีนกับเสียงพากย์จริง (วิธีเดียวกับ 022: พลังงานเสียง + สัดส่วนตัวอักษร + หาจุดเงียบ) ----
import subprocess
import numpy as np
timing = json.loads((V / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL = timing["total"]
LINES = timing["lines"]
SR = 16000


def envelope(wav):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    x = np.abs(np.frombuffer(raw, dtype="<f4"))
    win = int(SR * 0.03)
    return np.convolve(x, np.ones(win) / win, mode="same")


CAPS = []
for i, r in enumerate(rows):
    cs = chunk(r)
    env = envelope(V / "audio_gm" / f"{i:02}_t.wav")
    voiced = np.where(env > env.max() * 0.08)[0]
    t0, t1 = voiced[0] / SR, voiced[-1] / SR
    w = [len(re.sub(r"[\s\[\]]", "", c)) for c in cs]
    cuts, acc = [], 0
    for k in range(len(cs) - 1):
        acc += w[k]
        t = t0 + (t1 - t0) * acc / sum(w)
        lo, hi = max(int((t - .4) * SR), int(t0 * SR)), min(int((t + .4) * SR), int(t1 * SR))
        cuts.append((lo + int(np.argmin(env[lo:hi]))) / SR if hi > lo else t)
    starts = [t0] + cuts
    for k in range(1, len(starts)):
        starts[k] = max(starts[k], starts[k - 1] + .5)
    off = LINES[i]["start"]
    for k, c in enumerate(cs):
        CAPS.append([c, round(off + starts[k], 2), round(off + (starts[k + 1] if k + 1 < len(starts) else t1 + .3), 2)])

# หน้าต่างซีนใหม่ตามเสียง และฟังก์ชันแปลงเวลาเก่า→ใหม่ (เส้นตรงเป็นช่วง)
NEW = [0.0] + [round(LINES[i]["start"] - 0.2, 2) for i in range(1, 7)] + [TOTAL]
OLD = [0, 5, 15, 25, 33, 41, 50, 56]
SCN = [[NEW[i], NEW[i + 1]] for i in range(7)]


def remap(t):
    for i in range(7):
        if t <= OLD[i + 1] or i == 6:
            return round(NEW[i] + (t - OLD[i]) * (NEW[i + 1] - NEW[i]) / (OLD[i + 1] - OLD[i]), 3)


# ---- กล้อง: พิกัดอ้างอิง ref px (ซูม 11) กับระดับซูม L=log2(px หน้าจอ / ref px) ----
BKK = (7092.5, 10507.6)
BKK2 = (7084, 10510)    # กลางชั้น thon (ถนนกรุงเทพ) ใช้ตอนซูมลึก
FARM = (7000, 9650)
THAI_C = (8000, 9000)   # กลางประเทศ (ref px ซูม 11)
# (เวลา, จุด x, y, L)
KEYS = [
    (0.0, *THAI_C, -3.8), (1.6, *BKK, -3.6), (3.4, *BKK2, 2.8), (4.8, *BKK2, 4.4),       # ซีน 1 ซูมลงถนน
    (5.4, *THAI_C, -3.8), (14.8, *THAI_C, -3.8),                                       # ซีน 2 ทั้งประเทศ
    (15.4, *THAI_C, -3.8), (19.0, *BKK, -1.0), (24.8, *BKK, 2.0),                      # ซีน 3 ภาคกลาง→กรุงเทพ
    (25.4, *FARM, 0.2), (32.8, *FARM, 1.3),                                            # ซีน 4 ทุ่งนา
    (33.4, *FARM, 1.5), (40.8, *FARM, 1.8),                                            # ซีน 5
    (41.4, *THAI_C, -3.8), (44.6, *BKK, -1.2), (49.8, *BKK, 2.4),                      # ซีน 6 กลับสู่กรุงเทพ
    (50.4, *THAI_C, -3.8), (56.0, *THAI_C, -3.8),                                      # ซีน 7
]

KEYS = [(remap(k[0]),) + tuple(k[1:]) for k in KEYS]
LAYERS = {k: {kk: v[kk] for kk in "xywhk"} for k, v in geo["layers"].items() if k in ("thai", "central", "thon")}
BORDER = " ".join(
    "M" + " L".join(f"{x},{y}" for x, y in ring) + "Z"
    for ring in geo["borders"]["Thailand"] if len(ring) > 50
)

MAIN = "M" + " L".join(f"{x},{y}" for x, y in max(geo["borders"]["Thailand"], key=len)) + "Z"
INK = "#1E1E24"


def stick(x, y, s=1.0, pose="stand"):
    head = f'<circle cx="0" cy="-60" r="26" fill="#fff" stroke="{INK}" stroke-width="6"/>'
    st = f'fill="none" stroke="{INK}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"'
    if pose == "crouch":
        body = f'<path d="M0,-34 L10,0 M10,0 L-30,20 L-20,52 M10,0 L40,24 L22,56 M-6,-26 L-26,-50 M6,-26 L26,-50" {st}/>'
        head = f'<circle cx="-4" cy="-48" r="24" fill="#fff" stroke="{INK}" stroke-width="6"/>'
    elif pose == "lie":
        body = f'<path d="M-60,0 H50 M-30,0 L-44,-26 M10,0 L28,-24 M50,0 L82,12 M50,0 L78,-14" {st}/>'
        head = f'<circle cx="-90" cy="-4" r="24" fill="#fff" stroke="{INK}" stroke-width="6"/>'
    elif pose == "run":
        body = f'<path d="M0,-34 L8,24 M0,-14 L-30,-30 M0,-14 L26,6 M8,24 L-18,60 M8,24 L38,44" {st}/>'
    else:
        body = f'<path d="M0,-34 V30 M0,-14 L-28,12 M0,-14 L28,12 M0,30 L-20,76 M0,30 L20,76" {st}/>'
    return f'<g transform="translate({x},{y}) scale({s})">{head}{body}</g>'


def bolt(x0, y0, x1, y1, idn=""):
    dx = (x1 - x0) / 5
    pts = [(x0, y0)]
    for i in range(1, 5):
        pts.append((x0 + dx * i + (22 if i % 2 else -22), y0 + (y1 - y0) * i / 5))
    pts.append((x1, y1))
    d = "M" + " L".join(f"{a},{b}" for a, b in pts)
    return (f'<g id="{idn}" opacity="0"><path d="{d}" fill="none" stroke="#fff6a8" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" opacity=".55"/>'
            f'<path d="{d}" fill="none" stroke="#ffffff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/></g>')


def card(n):
    sky, ground = "#2b3a67", "#3b5d3a"
    bg = '<path d="M0,400 H960" stroke="#1e1e24" stroke-width="7" stroke-linecap="round"/>'
    if n == 2:  # ตัวเลข + กระแสวิ่งตามพื้น
        bg = '<path d="M0,380 H960" stroke="#1e1e24" stroke-width="7" stroke-linecap="round"/>'
        body = (bolt(240, 0, 240, 380, "b2")
                + '<g id="rings2"><ellipse cx="240" cy="388" rx="40" ry="10" fill="none" stroke="#ffe85a" stroke-width="6"/><ellipse cx="240" cy="388" rx="110" ry="24" fill="none" stroke="#ffe85a" stroke-width="5" opacity=".7"/><ellipse cx="240" cy="388" rx="190" ry="40" fill="none" stroke="#ffe85a" stroke-width="4" opacity=".45"/></g>'
                + stick(650, 380, 1.0, "stand")
                + '<text x="300" y="110" font-size="50" font-weight="800" fill="#ffd23f" stroke="#1e1e24" stroke-width="10" paint-order="stroke">5 เท่า ของผิวดวงอาทิตย์</text>'
                + '<text x="300" y="180" font-size="50" font-weight="800" fill="#fff" stroke="#1e1e24" stroke-width="10" paint-order="stroke">ร้อยล้านโวลต์</text>')
    elif n == 3:  # ตึก + รถ
        body = ('<rect x="120" y="150" width="220" height="250" fill="#8895a8" stroke="#1e1e24" stroke-width="6"/>'
                + ''.join(f'<rect x="{150 + c * 60}" y="{180 + r * 70}" width="34" height="42" fill="#ffe28a" stroke="#1e1e24" stroke-width="4"/>' for c in range(3) for r in range(3))
                + bolt(560, 0, 560, 290, "b3")
                + '<g id="car3"><rect x="470" y="300" width="230" height="64" rx="16" fill="#e0243a" stroke="#1e1e24" stroke-width="6"/><path d="M510,300 L540,252 H640 L670,300Z" fill="#bfe2f2" stroke="#1e1e24" stroke-width="6"/><circle cx="520" cy="372" r="24" fill="#222" stroke="#1e1e24" stroke-width="6"/><circle cx="652" cy="372" r="24" fill="#222" stroke="#1e1e24" stroke-width="6"/></g>'
                + '<path id="flow3" d="M560,60 L560,290 M470,300 V396 M700,300 V396" fill="none" stroke="#ffe85a" stroke-width="6" stroke-dasharray="14 12" opacity="0"/>'
                + stick(780, 400, 0.9, "run")
                + '<g id="pin3" opacity="0"><circle cx="230" cy="110" r="26" fill="#1f9d55" stroke="#1e1e24" stroke-width="6"/><path d="M216,110 L227,121 L246,98" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/></g>')
    elif n == 4:  # ต้นไม้โดดเดี่ยว
        body = ('<rect x="470" y="210" width="36" height="190" fill="#6b4a22" stroke="#1e1e24" stroke-width="6"/>'
                '<circle cx="488" cy="170" r="104" fill="#2e8b4a" stroke="#1e1e24" stroke-width="6"/>'
                + bolt(488, 0, 488, 80, "b4") + stick(580, 400, 1.0, "stand")
                + '<path id="arc4" d="M520,250 L548,300 L536,330 L568,372" fill="none" stroke="#fff6a8" stroke-width="9" stroke-linecap="round" opacity="0"/>'
                + '<g id="x4" opacity="0"><circle cx="800" cy="130" r="48" fill="#e0243a" stroke="#1e1e24" stroke-width="6"/><path d="M780,110 L820,150 M820,110 L780,150" stroke="#fff" stroke-width="11" stroke-linecap="round"/></g>')
    elif n == 5:  # ย่อ vs นอน
        body = (stick(250, 380, 1.1, "crouch")
                + '<g id="ok5" opacity="0"><circle cx="250" cy="120" r="48" fill="#1f9d55" stroke="#1e1e24" stroke-width="6"/><path d="M228,120 L244,138 L274,102" fill="none" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/></g>'
                + '<g id="lie5" opacity="0">' + stick(700, 395, 1.1, "lie")
                + '<path d="M560,402 H860" stroke="#ffe85a" stroke-width="7" stroke-dasharray="12 10"/></g>'
                + '<g id="x5" opacity="0"><circle cx="700" cy="140" r="48" fill="#e0243a" stroke="#1e1e24" stroke-width="6"/><path d="M680,120 L720,160 M720,120 L680,160" stroke="#fff" stroke-width="11" stroke-linecap="round"/></g>')
    elif n == 6:  # ช่วยคน + 1669
        body = (stick(300, 392, 1.0, "lie") + stick(520, 380, 1.0, "run")
                + '<g id="ph6" opacity="0"><rect x="680" y="110" width="150" height="260" rx="24" fill="#fff" stroke="#1e1e24" stroke-width="7"/><text x="755" y="260" font-size="58" font-weight="800" text-anchor="middle" fill="#e0243a">1669</text></g>'
                + '<path id="hb6" d="M80,150 H150 L170,100 L200,200 L225,150 H300" fill="none" stroke="#e0243a" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" opacity="0"/>')
    else:
        return ""
    svg = (bg + body).replace("#1e1e24", "#ffffff").replace("#1E1E24", "#ffffff")
    svg = re.sub(r'(<text[^>]*?)stroke="#ffffff"', lambda m: m.group(1) + 'stroke="#1e1e24"', svg)
    return f'<div class="vg" id="vg{n}"><svg viewBox="0 0 960 520" width="960" height="520" xmlns="http://www.w3.org/2000/svg" font-family="Kanit">{svg}</svg></div>'


VGS = "\n".join(card(n) for n in range(2, 7))
TAGS = ["ถ้าฟ้าฝ่าใกล้คุณ", "ฟ้าผ่าอันตรายยังไง", "ขั้น 1 · <r>เข้าที่กำบัง</r>", "ขั้น 2 · <r>ห้ามใต้ต้นไม้</r>", "ขั้น 2 · <r>ย่อ ห้ามนอน</r>", "ขั้น 3 · <r>ช่วยคน</r>", "<r>เกษตรกรไทย</r> เสี่ยงสุด"]
TAGHTML = "\n".join(f'        <div class="tag" id="tag{i}" style="opacity:0">{t}</div>' for i, t in enumerate(TAGS))

template = r"""<!doctype html>
<html lang="th">
  <head>
    <meta charset="UTF-8" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      @font-face { font-family: "Kanit"; font-weight: 600; src: url("fonts/kanit-thai-600-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }
      @font-face { font-family: "Kanit"; font-weight: 600; src: url("fonts/kanit-latin-600-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }
      @font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }
      @font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }
      :root { --ink: #1e1e24; --red: #e0243a; --yellow: #ffd23f; }
      body { margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #050c1c; font-family: "Kanit", sans-serif; }
      #root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #050c1c; }
      #vp { position: absolute; inset: 0; overflow: hidden; }
      #vp::after { content: ""; position: absolute; inset: 0; pointer-events: none; box-shadow: inset 0 0 220px 60px rgba(5, 15, 35, 0.65); z-index: 5; }
      #world { position: absolute; left: 0; top: 0; width: 0; height: 0; transform-origin: 0 0; }
      #Lthai { -webkit-mask-image: radial-gradient(ellipse 50% 50% at 50% 50%, #000 62%, transparent 100%); mask-image: radial-gradient(ellipse 50% 50% at 50% 50%, #000 62%, transparent 100%); }
      #Lthon { -webkit-mask-image: radial-gradient(ellipse 50% 50% at 50% 50%, #000 50%, transparent 100%); mask-image: radial-gradient(ellipse 50% 50% at 50% 50%, #000 50%, transparent 100%); }
      .lyr { position: absolute; image-rendering: auto; transform-origin: 0 0; filter: saturate(1.1) brightness(.85); }
      #bsvg { position: absolute; left: 0; top: 0; overflow: visible; }
      #dark { position: absolute; inset: 0; background: #060a1c; opacity: .3; z-index: 3; }
      #card { position: absolute; left: 60px; top: 390px; width: 960px; height: 520px; z-index: 10; }
      .vg { position: absolute; left: 0; top: 0; width: 960px; height: 520px; overflow: visible; box-sizing: border-box; opacity: 0; filter: drop-shadow(0 0 10px rgba(0,0,0,.85)) drop-shadow(0 4px 0 rgba(0,0,0,.6)); }
      .vg svg { position: absolute; left: -6px; top: -6px; }
      #tagwrap { position: absolute; left: 0; top: 215px; width: 1080px; height: 110px; display: grid; place-items: center; z-index: 30; }
      .tag { grid-area: 1 / 1; background: #fff; border: 5px solid var(--ink); border-radius: 22px; padding: 8px 32px 12px; font-size: 48px; font-weight: 800; color: var(--ink); max-width: 940px; text-align: center; box-shadow: 0 6px 0 rgba(30,30,36,.18); }
      .tag r { color: var(--red); }
      #hook { position: absolute; left: 0; top: 560px; width: 1080px; text-align: center; z-index: 45; }
      #hook div { opacity: 0; font-weight: 800; line-height: 1.05; -webkit-text-stroke: 24px var(--ink); paint-order: stroke fill; }
      #hook .h1 { font-size: 170px; color: var(--yellow); } #hook .h2 { font-size: 150px; color: #fff; }
      .caps { position: absolute; left: 0; top: 1500px; width: 1080px; height: 300px; z-index: 50; }
      .cap { position: absolute; left: 50px; top: 0; width: 980px; text-align: center; font-size: 62px; font-weight: 800; line-height: 1.32; color: #fff; -webkit-text-stroke: 14px var(--ink); paint-order: stroke fill; opacity: 0; text-wrap: balance; }
      .cap y { color: var(--yellow); }
      #hl { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 12; opacity: 0; pointer-events: none; background: radial-gradient(ellipse 520px 380px at 50% 50%, rgba(255,140,20,.55), rgba(255,140,20,0) 70%); mix-blend-mode: screen; }
      #ltwrap { position: absolute; inset: 0; z-index: 6; overflow: hidden; background: #02040c; }
      #lt { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; object-fit: cover; object-position: 31% 50%; transform-origin: 34% 50%; }
      #ltcr { position: absolute; left: 36px; bottom: 36px; font-size: 26px; font-weight: 600; color: rgba(255,255,255,.75); text-shadow: 0 2px 6px #000; }
      #wm { position: absolute; left: 36px; top: 40px; width: 130px; height: 130px; z-index: 70; opacity: .92; pointer-events: none; filter: drop-shadow(0 4px 10px rgba(0,0,0,.6)); }
      #bkk { position: absolute; left: 0; top: 0; width: 0; height: 0; z-index: 9; opacity: 0; pointer-events: none; }
      #bkk .ring { position: absolute; left: -60px; top: -60px; width: 120px; height: 120px; border: 7px solid #ffe85a; border-radius: 50%; box-sizing: border-box; }
      #bkk .dot { position: absolute; left: -15px; top: -15px; width: 30px; height: 30px; background: #e0243a; border: 5px solid #fff; border-radius: 50%; box-sizing: border-box; }
      #bkk .lbl { position: absolute; left: 36px; top: -66px; white-space: nowrap; font-size: 56px; font-weight: 800; color: #fff; -webkit-text-stroke: 12px var(--ink); paint-order: stroke fill; }
      #flash { position: absolute; inset: 0; background: #fff; opacity: 0; z-index: 60; pointer-events: none; }
      #endcta { position: absolute; left: 0; top: 1330px; width: 1080px; display: flex; justify-content: center; z-index: 20; opacity: 0; }
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="%%TOTAL%%">
      <div id="tagwrap">
%%TAGS%%
      </div>
      <div id="vp">
        <div id="world">
          <img class="lyr" id="Lthai" src="assets/thai.jpg" />
          <img class="lyr" id="Lcentral" src="assets/central.jpg" />
          <img class="lyr" id="Lthon" src="assets/thon.jpg" />
          <svg id="bsvg" width="1" height="1"><path d="%%BORDER%%" fill="none" stroke="#7fe3ff" stroke-width="2.5" stroke-opacity=".9" vector-effect="non-scaling-stroke" />
          <path id="thGlow" d="%%MAIN%%" pathLength="1" fill="none" stroke="#ffe85a" stroke-opacity=".35" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="1 1.2" stroke-dashoffset="1.1" />
          <path id="thLine" d="%%MAIN%%" pathLength="1" fill="none" stroke="#ffe85a" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="1 1.2" stroke-dashoffset="1.1" /></svg>
        </div>
        <div id="dark"></div>
      </div>
      <div id="bkk"><div class="ring" id="bkr1"></div><div class="ring" id="bkr2"></div><div class="dot"></div><div class="lbl">กรุงเทพฯ</div></div>
      <div id="hl"></div>
      <div id="ltwrap"><img id="lt" src="assets/lightning.jpg" /><div id="ltcr">ภาพ: C. Clark / NOAA NSSL (สาธารณสมบัติ)</div></div>
      <div id="card">
%%VGS%%
      </div>
      <div id="endcta"><div class="tag" style="position: static">ส่งต่อให้คนทำงานกลางแจ้ง</div></div>
      <div id="hook"><div class="h1">ฟ้าผ่า</div><div class="h2">ห่าง 10 เมตร</div></div>
      <img id="wm" src="assets/watermark.png" />
      <div id="flash"></div>
      <div class="caps" id="caps"></div>
      <audio id="aVO" data-start="0" data-duration="%%TOTAL%%" data-track-index="2" src="audio_gm/vo.wav" data-volume="1"></audio>
      <audio id="aSFX" data-start="0" data-duration="%%TOTAL%%" data-track-index="3" src="audio_gm/sfx.wav" data-volume="0.6"></audio>
      <audio id="aMusic" data-start="0" data-duration="%%TOTAL%%" data-track-index="4" src="audio_gm/music.wav" data-volume="0.3"></audio>
    </div>
    <script>
      var D = %%DATA%%;
      var cam = { x: D.KEYS[0][1], y: D.KEYS[0][2], L: D.KEYS[0][3] };
      var world = document.getElementById("world");
      function layerStyle(id, a) {
        var el = document.getElementById(id), s = Math.pow(2, cam.L);
        el.style.left = a.x + "px"; el.style.top = a.y + "px";
        el.style.width = (a.w * a.k) + "px"; el.style.height = (a.h * a.k) + "px";
      }
      Object.keys(D.LAYERS).forEach(function (k) { layerStyle("L" + k, D.LAYERS[k]); });
      function clamp01(v) { return Math.max(0, Math.min(1, v)); }
      function apply() {
        var s = Math.pow(2, cam.L);
        world.style.transform = "translate(" + (540 - cam.x * s) + "px," + (960 - cam.y * s) + "px) scale(" + s + ")";
        var bk = document.getElementById("bkk");
        bk.style.left = (540 + (D.BKK[0] - cam.x) * s) + "px"; bk.style.top = (960 + (D.BKK[1] - cam.y) * s) + "px";
        document.getElementById("thLine").style.strokeWidth = (7 / s) + "px"; document.getElementById("thGlow").style.strokeWidth = (22 / s) + "px";
        // เฟดชั้นแผนที่ตามระดับซูม: thai (ไกล) → central (กลาง) → thon (ใกล้)
        document.getElementById("Lthai").style.opacity = 1;
        document.getElementById("Lcentral").style.opacity = clamp01((cam.L + 2.6) / 1.2);
        document.getElementById("Lthon").style.opacity = clamp01((cam.L - 2.2) / 1.2);
      }
      apply();

      // ---------- captions ----------
      var capsEl = document.getElementById("caps");
      D.CAPS.forEach(function (c, i) {
        var el = document.createElement("div");
        el.className = "cap"; el.id = "k" + i;
        el.innerHTML = c[0].replace(/\[([^\]]+)\]/g, "<y>$1</y>");
        capsEl.appendChild(el);
      });

      window.__timelines = window.__timelines || {};
      var tl = gsap.timeline({ paused: true });
      // กล้องซูมต่อเนื่อง
      for (var i = 1; i < D.KEYS.length; i++) {
        var a = D.KEYS[i - 1], b = D.KEYS[i], dur = b[0] - a[0];
        if (dur <= 0) continue;
        tl.to(cam, { x: b[1], y: b[2], L: b[3], duration: dur, ease: "power1.inOut", onUpdate: apply, immediateRender: false }, a[0]);
      }
      D.CAPS.forEach(function (c, i) {
        tl.fromTo("#k" + i, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.18, immediateRender: false }, c[1]);
        tl.to("#k" + i, { opacity: 0, duration: 0.12 }, c[2] - 0.12);
      });
      // เหตุการณ์ด้านล่างเขียนด้วยเวลาตามตารางเดิม -> แปลงเป็นเวลาตามเสียงจริง
      var OLD = D.OLD, NEW = D.NEW;
      function M(t) { for (var i = 0; i < 7; i++) { if (t <= OLD[i + 1] || i === 6) return NEW[i] + (t - OLD[i]) * (NEW[i + 1] - NEW[i]) / (OLD[i + 1] - OLD[i]); } }
      ["to", "fromTo", "set"].forEach(function (m) { var o = tl[m]; tl[m] = function () { var a = Array.prototype.slice.call(arguments); a[a.length - 1] = M(a[a.length - 1]); return o.apply(tl, a); }; });
      function flash(t, p) { tl.fromTo("#flash", { opacity: 0 }, { opacity: p || 0.9, duration: 0.06, immediateRender: false }, t).to("#flash", { opacity: 0, duration: 0.5 }, t + 0.08); }
      function show(sel, t0, t1) { tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: false }, t0); tl.to(sel, { opacity: 0, duration: 0.25 }, t1 - 0.25); }
      function bolt(sel, t) { tl.set(sel, { opacity: 1 }, t).set(sel, { opacity: 0 }, t + 0.12).set(sel, { opacity: 1 }, t + 0.2).set(sel, { opacity: 0 }, t + 0.35); }

      // ซีน 1: ฮุกแบบ Ep39 -- ขาววาบตั้งแต่เฟรมแรก ตัวหนังสือตบจอ จอสั่น
      tl.fromTo("#flash", { opacity: 0.95 }, { opacity: 0, duration: 0.55, ease: "power2.out", immediateRender: false }, 0.02);
      tl.fromTo("#hook .h1", { opacity: 0, scale: 2.6 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power4.out", immediateRender: false }, 0.15);
      tl.fromTo("#hook .h2", { opacity: 0, scale: 2.3 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power4.out", immediateRender: false }, 0.65);
      tl.to("#hook", { opacity: 0, y: -60, duration: 0.35, ease: "power2.in" }, 4.55);
      tl.fromTo("#lt", { scale: 1.3 }, { scale: 1.0, duration: 2.4, ease: "power2.out", immediateRender: false }, 0);
      tl.to("#ltwrap", { opacity: 0, duration: 0.1 }, 1.3);
      function shake(t, amp) { for (var q = 0; q < 8; q++) tl.set("#vp,#ltwrap", { x: (q % 2 ? -1 : 1) * amp * (1 - q / 8), y: (q % 2 ? 1 : -1) * amp * 0.6 * (1 - q / 8) }, t + q * 0.035); tl.set("#vp,#ltwrap", { x: 0, y: 0 }, t + 0.3); }
      shake(0.02, 26); shake(1.3, 12); shake(3.3, 14); shake(4.7, 30);
      flash(1.3, .6); flash(3.3, .7); flash(4.7, 1);
      tl.to("#dark", { opacity: .15, duration: .1 }, 4.7).to("#dark", { opacity: .3, duration: 1 }, 4.85);
      // แท็กแต่ละซีน
      var SCN = D.SCN;
      for (var q = 0; q < 7; q++) show("#tag" + q, OLD[q] + 0.1, OLD[q + 1]);
      // เส้นแผนที่ประกอบเรื่อง: ขอบประเทศไทยวาดเป็นเส้น + วงกรุงเทพฯ
      function draw(t0, d, t1) { tl.fromTo("#thLine,#thGlow", { strokeDashoffset: 1.1, opacity: 1 }, { strokeDashoffset: 0, duration: d, ease: "power1.inOut", immediateRender: false }, t0); tl.to("#thLine,#thGlow", { opacity: 0, duration: .5 }, t1); }
      function mark(t0, t1) { tl.fromTo("#bkk", { opacity: 0 }, { opacity: 1, duration: .3, immediateRender: false }, t0); tl.to("#bkk", { opacity: 0, duration: .3 }, t1 - .3);
        for (var q = 0; q < 3; q++) { tl.fromTo("#bkr1", { scale: .3, opacity: 1 }, { scale: 1.8, opacity: 0, duration: .9, ease: "power2.out", immediateRender: false }, t0 + .2 + q * 1.0); } }
      draw(0.4, 3.2, 4.4); mark(1.0, 4.6);
      draw(5.4, 3.6, 14.6); mark(6.0, 14.8);
      mark(15.4, 24.6);
      draw(41.4, 3.0, 49.6); mark(42.0, 49.8);
      draw(50.4, 2.6, 55.8); mark(51.0, 55.9);
      // ซีน 2
      show("#vg2", 5.2, 15); bolt("#b2", 6.0); flash(6.0, .5);
      tl.fromTo("#rings2", { scale: .2, opacity: 0, transformOrigin: "240px 388px" }, { scale: 1, opacity: 1, duration: 2.4, ease: "power2.out", immediateRender: false }, 7.5);
      // ซีน 3
      show("#vg3", 15.2, 25); tl.fromTo("#pin3", { opacity: 0 }, { opacity: 1, duration: .3, immediateRender: false }, 18);
      bolt("#b3", 20); flash(20, .5); tl.fromTo("#flow3", { opacity: 0 }, { opacity: 1, duration: .2, immediateRender: false }, 20).to("#flow3", { opacity: 0, duration: .3 }, 21.6);
      // ซีน 4
      show("#vg4", 25.2, 33); bolt("#b4", 27); flash(27, .5);
      tl.fromTo("#arc4", { opacity: 0 }, { opacity: 1, duration: .1, immediateRender: false }, 27.3).to("#arc4", { opacity: 0, duration: .3 }, 28.2);
      tl.fromTo("#x4", { opacity: 0, scale: 0, transformOrigin: "800px 130px" }, { opacity: 1, scale: 1, duration: .3, ease: "back.out(2)", immediateRender: false }, 28.4);
      // ซีน 5
      show("#vg5", 33.2, 41);
      tl.fromTo("#ok5", { opacity: 0 }, { opacity: 1, duration: .2, immediateRender: false }, 35.2);
      tl.fromTo("#lie5", { opacity: 0 }, { opacity: 1, duration: .2, immediateRender: false }, 38);
      tl.fromTo("#x5", { opacity: 0, scale: 0, transformOrigin: "700px 140px" }, { opacity: 1, scale: 1, duration: .3, ease: "back.out(2)", immediateRender: false }, 38.6);
      // ซีน 6
      show("#vg6", 41.2, 50); tl.fromTo("#ph6", { opacity: 0 }, { opacity: 1, duration: .3, immediateRender: false }, 44);
      tl.fromTo("#hb6", { opacity: 0 }, { opacity: 1, duration: .3, immediateRender: false }, 46.5);
      // ซีน 7
      tl.fromTo("#hl", { opacity: 0 }, { opacity: 1, duration: 1.2, immediateRender: false }, 50.5);
      tl.fromTo("#endcta", { opacity: 0 }, { opacity: 1, duration: .5, immediateRender: false }, 52.5);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

data = {"KEYS": KEYS, "LAYERS": LAYERS, "CAPS": CAPS, "SCN": SCN, "BKK": BKK, "OLD": OLD, "NEW": NEW}
html = (template.replace("%%TOTAL%%", str(TOTAL)).replace("%%TAGS%%", TAGHTML).replace("%%VGS%%", VGS)
        .replace("%%BORDER%%", BORDER).replace("%%MAIN%%", MAIN).replace("%%DATA%%", json.dumps(data, ensure_ascii=False)))
(V / "index.html").write_text(html, encoding="utf-8")
print("ok", len(html), "bytes; captions", len(CAPS))
