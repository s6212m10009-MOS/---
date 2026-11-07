"""สร้าง video/index.html ของตอน 041 (เกาหลีใต้/กัมพูชา) จาก script.md + video/timing_gm.json
ฮุกแรง: ขาววาบ ไซเรนแดง ป้ายห้ามตบจอ ตราประทับ "ไม่จริง!" แล้วตัดเข้าแผนที่ + โมชั่นเตือนภัย
  python build.py
"""
import json, re, subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
V = HERE / "video"
geo = json.loads((V / "assets" / "geo.json").read_text(encoding="utf-8"))

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


timing = json.loads((V / "timing_gm.json").read_text(encoding="utf-8"))
TOTAL, LINES = timing["total"], timing["lines"]
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

NEW = [0.0] + [round(LINES[i]["start"] - 0.2, 2) for i in range(1, 7)] + [TOTAL]
OLD = [0, 5, 15, 25, 33, 41, 50, 56]

THAI_C = (8000, 9000)
EAST = (8700, 9300)
KEYS = [(0.0, *THAI_C, -3.8), (5.0, *EAST, -3.5), (15, *EAST, -3.2), (25, *EAST, -3.0), (41, *EAST, -3.0), (56, *THAI_C, -3.8)]


def remap(t):
    for i in range(7):
        if t <= OLD[i + 1] or i == 6:
            return round(NEW[i] + (t - OLD[i]) * (NEW[i + 1] - NEW[i]) / (OLD[i + 1] - OLD[i]), 3)


KEYS = [(remap(k[0]),) + tuple(k[1:]) for k in KEYS]
LAYERS = {k: {kk: v[kk] for kk in "xywhk"} for k, v in geo["layers"].items() if k in ("thai", "central")}
MAIN = "M" + " L".join(f"{x},{y}" for x, y in max(geo["borders"]["Thailand"], key=len)) + "Z"
BORDER = " ".join("M" + " L".join(f"{x},{y}" for x, y in ring) + "Z" for ring in geo["borders"]["Thailand"] if len(ring) > 50)

W = "#ffffff"
ST = f'fill="none" stroke="{W}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"'


def tri(x, y, s=1.0, idn=""):  # สามเหลี่ยมเตือนภัย
    return (f'<g id="{idn}" transform="translate({x},{y}) scale({s})"><path d="M0,-70 L68,50 H-68Z" fill="#ffd23f" stroke="#1e1e24" stroke-width="9" stroke-linejoin="round"/>'
            '<path d="M0,-30 V16" stroke="#1e1e24" stroke-width="13" stroke-linecap="round"/><circle cx="0" cy="34" r="8" fill="#1e1e24"/></g>')


def xmark(x, y, idn):
    return (f'<g id="{idn}" opacity="0"><circle cx="{x}" cy="{y}" r="52" fill="#e0243a" stroke="#1e1e24" stroke-width="6"/>'
            f'<path d="M{x-20},{y-20} L{x+20},{y+20} M{x+20},{y-20} L{x-20},{y+20}" stroke="#fff" stroke-width="12" stroke-linecap="round"/></g>')


def stick(x, y, s=1.0):
    return (f'<g transform="translate({x},{y}) scale({s})"><circle cx="0" cy="-60" r="26" fill="#fff" stroke="#1e1e24" stroke-width="6"/>'
            '<path d="M0,-34 V30 M0,-14 L-28,12 M0,-14 L28,12 M0,30 L-20,76 M0,30 L20,76" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/></g>')


def label(x, y, t, size=54, fill="#fff", anchor="middle", idn=""):
    return f'<text id="{idn}" x="{x}" y="{y}" font-size="{size}" font-weight="800" text-anchor="{anchor}" fill="{fill}" stroke="#1e1e24" stroke-width="11" paint-order="stroke">{t}</text>'


def cal(x, y, top, big):
    return (f'<g transform="translate({x},{y})"><rect x="-150" y="-130" width="300" height="260" rx="22" fill="#fff" stroke="#1e1e24" stroke-width="7"/>'
            f'<rect x="-150" y="-130" width="300" height="78" rx="22" fill="#e0243a" stroke="#1e1e24" stroke-width="7"/>'
            f'<text x="0" y="-74" font-size="50" font-weight="800" text-anchor="middle" fill="#fff">{top}</text>'
            f'<text x="0" y="62" font-size="92" font-weight="800" text-anchor="middle" fill="#1e1e24">{big}</text></g>')


def card(n):
    if n == 2:
        body = (cal(250, 230, "ธ.ค.", "2023") + tri(660, 230, 1.5, "tri2")
                + label(660, 380, "รู้แล้ว แต่ไม่ขยับ", 50, "#ffd23f"))
    elif n == 3:
        body = ('<g transform="translate(250,230)"><rect x="-150" y="-100" width="300" height="200" rx="14" fill="#fff" stroke="#1e1e24" stroke-width="7"/>'
                '<path d="M-150,-100 L0,20 L150,-100" fill="none" stroke="#1e1e24" stroke-width="7"/></g>'
                + label(250, 390, "สถานทูตขอ 2 ครั้ง", 46) + label(250, 62, "เม.ย. · ก.ค. 2024", 46, "#ffd23f")
                + '<g id="den3" opacity="0"><rect x="520" y="180" width="360" height="110" rx="14" fill="none" stroke="#e0243a" stroke-width="12" transform="rotate(-8 700 235)"/>'
                + label(700, 255, "ปฏิเสธ", 78, "#e0243a", idn="").replace('stroke="#1e1e24" stroke-width="11"', 'stroke="#fff" stroke-width="8"') + '</g>')
    elif n == 4:
        body = (cal(250, 230, "ก.ย.", "2025") + tri(660, 230, 1.5, "tri4")
                + label(660, 380, "เพิ่งยกระดับคำเตือน", 48, "#ffd23f") + label(250, 410, "หลังนักศึกษาเสียชีวิต", 40))
    elif n == 5:
        body = (stick(200, 330, 1.2) + stick(480, 330, 1.2) + stick(760, 330, 1.2)
                + tri(200, 130, .8) + tri(480, 130, .8) + tri(760, 130, .8)
                + label(480, 470, "ลงโทษทางวินัย 3 คน", 52, "#ffd23f"))
    elif n == 6:
        body = (label(230, 260, "386", 150, "#e0243a") + label(230, 330, "ปี 2025", 44)
                + '<path d="M390,230 H530 M490,190 L535,230 L490,270" fill="none" stroke="#fff" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>'
                + label(720, 260, "19", 170, "#31d07a", idn="n19") + label(720, 330, "ปี 2026 (9 เดือนแรก)", 40))
    else:
        return ""
    return f'<div class="vg" id="vg{n}"><svg viewBox="0 0 960 520" width="960" height="520" xmlns="http://www.w3.org/2000/svg" font-family="Kanit">{body}</svg></div>'


VGS = "\n".join(card(n) for n in range(2, 7))
TAGS = ["ข่าวลือ vs ข่าวจริง", "<r>รู้</r> ตั้งแต่ปลายปี 2023", "สถานทูต <r>ขอ</r> · กระทรวง <r>ปฏิเสธ</r>", "<r>ช้า</r> จนมีคนเสียชีวิต", "ผลตรวจสอบ", "ตัวเลข <r>ลดลง</r>", "ระวัง <r>งานเงินดี</r>"]
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
      .lyr { position: absolute; transform-origin: 0 0; filter: saturate(1.1) brightness(.85); }
      #bsvg { position: absolute; left: 0; top: 0; overflow: visible; }
      #dark { position: absolute; inset: 0; background: #060a1c; opacity: .3; z-index: 3; }
      #redpulse { position: absolute; inset: 0; z-index: 4; opacity: 0; pointer-events: none; background: radial-gradient(ellipse at 50% 50%, rgba(224,36,58,0) 30%, rgba(224,36,58,.75) 100%); }
      #card { position: absolute; left: 60px; top: 390px; width: 960px; height: 520px; z-index: 10; }
      .vg { position: absolute; left: 0; top: 0; width: 960px; height: 520px; opacity: 0; filter: drop-shadow(0 0 10px rgba(0,0,0,.85)) drop-shadow(0 4px 0 rgba(0,0,0,.6)); }
      #tagwrap { position: absolute; left: 0; top: 215px; width: 1080px; height: 110px; display: grid; place-items: center; z-index: 30; }
      .tag { grid-area: 1 / 1; background: #fff; border: 5px solid var(--ink); border-radius: 22px; padding: 8px 32px 12px; font-size: 48px; font-weight: 800; color: var(--ink); max-width: 940px; text-align: center; }
      .tag r { color: var(--red); }
      .caps { position: absolute; left: 0; top: 1500px; width: 1080px; height: 300px; z-index: 50; }
      .cap { position: absolute; left: 50px; top: 0; width: 980px; text-align: center; font-size: 62px; font-weight: 800; line-height: 1.32; color: #fff; -webkit-text-stroke: 14px var(--ink); paint-order: stroke fill; opacity: 0; text-wrap: balance; }
      .cap y { color: var(--yellow); }
      /* ฮุก: จอเตือนภัย */
      #alert { position: absolute; inset: 0; z-index: 6; overflow: hidden; background: #1a0206; }
      #siren { position: absolute; left: -540px; top: 0; width: 2160px; height: 1920px; background: conic-gradient(from 0deg at 50% 50%, rgba(255,30,50,.9), rgba(255,30,50,0) 18%, rgba(255,30,50,0) 50%, rgba(255,30,50,.9) 50.1%, rgba(255,30,50,0) 68%, rgba(255,30,50,0) 100%); }
      .hz { position: absolute; left: -100px; width: 1280px; height: 120px; background: repeating-linear-gradient(-45deg, #ffd23f 0 60px, #1e1e24 60px 120px); z-index: 2; }
      #hzT { top: 0; } #hzB { bottom: 0; }
      #nosign { position: absolute; left: 290px; top: 330px; width: 500px; height: 500px; z-index: 3; opacity: 0; }
      #hook { position: absolute; left: 0; top: 880px; width: 1080px; text-align: center; z-index: 45; }
      #hook div { opacity: 0; font-weight: 800; line-height: 1.05; -webkit-text-stroke: 24px var(--ink); paint-order: stroke fill; }
      #hook .h1 { font-size: 190px; color: var(--yellow); } #hook .h2 { font-size: 160px; color: #fff; }
      #stamp { position: absolute; left: 90px; top: 1230px; width: 900px; z-index: 48; text-align: center; opacity: 0; transform: rotate(-9deg); font-size: 190px; font-weight: 800; color: #31d07a; -webkit-text-stroke: 22px var(--ink); paint-order: stroke fill; }
      #wm { position: absolute; left: 36px; top: 40px; width: 130px; height: 130px; z-index: 70; opacity: .92; pointer-events: none; filter: drop-shadow(0 4px 10px rgba(0,0,0,.6)); }
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
          <svg id="bsvg" width="1" height="1"><path d="%%BORDER%%" fill="none" stroke="#7fe3ff" stroke-width="2.5" stroke-opacity=".9" vector-effect="non-scaling-stroke" />
          <path id="thLine" d="%%MAIN%%" pathLength="1" fill="none" stroke="#ffe85a" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="1 1.2" stroke-dashoffset="1.1" /></svg>
        </div>
        <div id="dark"></div>
      </div>
      <div id="redpulse"></div>
      <div id="alert">
        <div id="siren"></div>
        <div class="hz" id="hzT"></div><div class="hz" id="hzB"></div>
        <svg id="nosign" viewBox="0 0 500 500"><circle cx="250" cy="250" r="225" fill="rgba(224,36,58,.15)" stroke="#e0243a" stroke-width="46"/><path d="M92,92 L408,408" stroke="#e0243a" stroke-width="46" stroke-linecap="round"/></svg>
      </div>
      <div id="card">
%%VGS%%
      </div>
      <div id="endcta"><div class="tag" style="position: static">ส่งต่อให้คนที่กำลังหางาน</div></div>
      <div id="hook"><div class="h1">ห้ามไป</div><div class="h2">กัมพูชา?</div></div>
      <div id="stamp">ไม่จริง!</div>
      <img id="wm" src="assets/watermark.png" />
      <div id="flash"></div>
      <div class="caps" id="caps"></div>
      <audio id="aVO" data-start="0" data-duration="%%TOTAL%%" data-track-index="2" src="audio_gm/vo.wav" data-volume="1"></audio>
      <audio id="aSFX" data-start="0" data-duration="%%TOTAL%%" data-track-index="3" src="audio_gm/sfx.wav" data-volume="0.7"></audio>
      <audio id="aMusic" data-start="0" data-duration="%%TOTAL%%" data-track-index="4" src="audio_gm/music.wav" data-volume="0.3"></audio>
    </div>
    <script>
      var D = %%DATA%%;
      var cam = { x: D.KEYS[0][1], y: D.KEYS[0][2], L: D.KEYS[0][3] };
      var world = document.getElementById("world");
      Object.keys(D.LAYERS).forEach(function (k) { var a = D.LAYERS[k], el = document.getElementById("L" + k);
        el.style.left = a.x + "px"; el.style.top = a.y + "px"; el.style.width = (a.w * a.k) + "px"; el.style.height = (a.h * a.k) + "px"; });
      function clamp01(v) { return Math.max(0, Math.min(1, v)); }
      function apply() {
        var s = Math.pow(2, cam.L);
        world.style.transform = "translate(" + (540 - cam.x * s) + "px," + (960 - cam.y * s) + "px) scale(" + s + ")";
        document.getElementById("thLine").style.strokeWidth = (7 / s) + "px";
        document.getElementById("Lcentral").style.opacity = clamp01((cam.L + 2.6) / 1.2);
      }
      apply();
      var capsEl = document.getElementById("caps");
      D.CAPS.forEach(function (c, i) {
        var el = document.createElement("div"); el.className = "cap"; el.id = "k" + i;
        el.innerHTML = c[0].replace(/\[([^\]]+)\]/g, "<y>$1</y>"); capsEl.appendChild(el);
      });
      window.__timelines = window.__timelines || {};
      var tl = gsap.timeline({ paused: true });
      for (var i = 1; i < D.KEYS.length; i++) {
        var a = D.KEYS[i - 1], b = D.KEYS[i], dur = b[0] - a[0];
        if (dur <= 0) continue;
        tl.to(cam, { x: b[1], y: b[2], L: b[3], duration: dur, ease: "power1.inOut", onUpdate: apply, immediateRender: false }, a[0]);
      }
      D.CAPS.forEach(function (c, i) {
        tl.fromTo("#k" + i, { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.18, immediateRender: false }, c[1]);
        tl.to("#k" + i, { opacity: 0, duration: 0.12 }, c[2] - 0.12);
      });
      var OLD = D.OLD, NEW = D.NEW;
      function M(t) { for (var i = 0; i < 7; i++) { if (t <= OLD[i + 1] || i === 6) return NEW[i] + (t - OLD[i]) * (NEW[i + 1] - NEW[i]) / (OLD[i + 1] - OLD[i]); } }
      ["to", "fromTo", "set"].forEach(function (m) { var o = tl[m]; tl[m] = function () { var a = Array.prototype.slice.call(arguments); a[a.length - 1] = M(a[a.length - 1]); return o.apply(tl, a); }; });
      function flash(t, p) { tl.fromTo("#flash", { opacity: 0 }, { opacity: p || 0.9, duration: 0.06, immediateRender: false }, t).to("#flash", { opacity: 0, duration: 0.5 }, t + 0.08); }
      function show(sel, t0, t1) { tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: false }, t0); tl.to(sel, { opacity: 0, duration: 0.25 }, t1 - 0.25); }
      function shake(t, amp) { for (var q = 0; q < 8; q++) tl.set("#vp,#alert,#card", { x: (q % 2 ? -1 : 1) * amp * (1 - q / 8), y: (q % 2 ? 1 : -1) * amp * 0.6 * (1 - q / 8) }, t + q * 0.035); tl.set("#vp,#alert,#card", { x: 0, y: 0 }, t + 0.3); }
      function pulse(t0, t1, n) { for (var q = 0; q < n; q++) { var t = t0 + (t1 - t0) * q / n; tl.fromTo("#redpulse", { opacity: 0 }, { opacity: 1, duration: .15, immediateRender: false }, t).to("#redpulse", { opacity: 0, duration: .35 }, t + .15); } }

      // ===== ฮุกแรง (0-5 วิ) =====
      tl.fromTo("#flash", { opacity: 1 }, { opacity: 0, duration: 0.5, ease: "power2.out", immediateRender: false }, 0.02);
      tl.fromTo("#siren", { rotation: 0, transformOrigin: "50% 50%" }, { rotation: 720, duration: 4.7, ease: "none", immediateRender: false }, 0);
      tl.fromTo("#hzT", { x: 0 }, { x: -170, duration: 4.7, ease: "none", immediateRender: false }, 0);
      tl.fromTo("#hzB", { x: -170 }, { x: 0, duration: 4.7, ease: "none", immediateRender: false }, 0);
      tl.fromTo("#nosign", { opacity: 0, scale: 3.2 }, { opacity: 1, scale: 1, duration: 0.28, ease: "power4.out", immediateRender: false }, 0.1);
      tl.fromTo("#hook .h1", { opacity: 0, scale: 2.8 }, { opacity: 1, scale: 1, duration: 0.28, ease: "power4.out", immediateRender: false }, 0.3);
      tl.fromTo("#hook .h2", { opacity: 0, scale: 2.5 }, { opacity: 1, scale: 1, duration: 0.28, ease: "power4.out", immediateRender: false }, 0.75);
      tl.fromTo("#stamp", { opacity: 0, scale: 3.4 }, { opacity: 1, scale: 1, duration: 0.2, ease: "power4.in", immediateRender: false }, 2.2);
      tl.to("#stamp", { opacity: 0, y: -40, duration: 0.3 }, 4.5);
      tl.to("#hook", { opacity: 0, y: -60, duration: 0.3, ease: "power2.in" }, 4.55);
      tl.to("#alert", { opacity: 0, duration: 0.2 }, 4.7);
      shake(0.02, 34); shake(0.3, 20); shake(0.75, 20); shake(2.2, 36);
      flash(0.3, .5); flash(0.75, .5); flash(2.2, .85); flash(4.7, .9);
      pulse(0.4, 2.2, 5);
      // ===== เนื้อเรื่อง: แท็ก + การ์ด + โมชั่นเตือนภัย =====
      for (var q = 0; q < 7; q++) show("#tag" + q, OLD[q] + 0.1, OLD[q + 1]);
      tl.fromTo("#thLine", { strokeDashoffset: 1.1, opacity: 1 }, { strokeDashoffset: 0, duration: 3.4, ease: "power1.inOut", immediateRender: false }, 5.2);
      tl.to("#thLine", { opacity: 0, duration: .5 }, 14.6);
      function warn(id, t) { tl.fromTo(id, { scale: 0, transformOrigin: "50% 50%" }, { scale: 1, duration: .35, ease: "back.out(2.5)", immediateRender: false }, t);
        for (var q = 0; q < 4; q++) tl.fromTo(id, { scale: 1 }, { scale: 1.18, duration: .15, yoyo: true, repeat: 1, ease: "power1.inOut", immediateRender: false }, t + .9 + q * .8); }
      show("#vg2", 5.2, 15); warn("#tri2", 6.2); pulse(6.2, 12, 3);
      show("#vg3", 15.2, 25); tl.fromTo("#den3", { opacity: 0, scale: 3, transformOrigin: "700px 235px" }, { opacity: 1, scale: 1, duration: .22, ease: "power4.in", immediateRender: false }, 20.5);
      flash(20.5, .6); shake(20.5, 26);
      show("#vg4", 25.2, 33); warn("#tri4", 26); pulse(26, 32, 6); shake(26, 18);
      show("#vg5", 33.2, 41); flash(35, .4);
      show("#vg6", 41.2, 50); tl.fromTo("#n19", { scale: 2.2, transformOrigin: "720px 200px" }, { scale: 1, duration: .4, ease: "power3.out", immediateRender: false }, 44);
      tl.fromTo("#endcta", { opacity: 0 }, { opacity: 1, duration: .5, immediateRender: false }, 52.5);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""

data = {"KEYS": KEYS, "LAYERS": LAYERS, "CAPS": CAPS, "OLD": OLD, "NEW": NEW}
html = (template.replace("%%TOTAL%%", str(TOTAL)).replace("%%TAGS%%", TAGHTML).replace("%%VGS%%", VGS)
        .replace("%%BORDER%%", BORDER).replace("%%MAIN%%", MAIN).replace("%%DATA%%", json.dumps(data, ensure_ascii=False)))
(V / "index.html").write_text(html, encoding="utf-8")
print("ok", len(html), "bytes; captions", len(CAPS))
