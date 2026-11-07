"""สร้าง cover/index.html ตอน 039 (หน้าปก 9:16 ไต้หวัน) แล้วถ่ายภาพ:
  npx hyperframes snapshot cover --at 0 --no-end -o snapcover"""
import math, re
from pathlib import Path

H = Path(__file__).resolve().parent
WL = (H / "video" / "world-line.txt").read_text()
TW = ""
for sub in re.split(r"(?=M)", WL):
    pts = [(float(a), float(b)) for a, b in re.findall(r"(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)", sub)]
    if pts and all(3000 <= x <= 3030 and 645 <= y <= 690 for x, y in pts):
        TW = sub.strip()
S = 3534 / 1550 * 1.7            # px ต่อหน่วยแผนที่ (ซูม 1.7)
CXU, CYU = 3010, 665             # ศูนย์ไต้หวัน (หน่วยแผนที่)
SX, SY = 540, 1010               # ตำแหน่งบนจอ
bgx, bgy = SX - (CXU - 1750) * S, SY - (CYU - 150) * S
bgw, bgh = 3534 * 1.7, 2736 * 1.7


def icon(d, R, th, s, fill):
    x, y = SX + R * math.sin(math.radians(th)), SY - R * math.cos(math.radians(th))
    return f'<g transform="translate({x:.1f},{y:.1f}) rotate({th + 90}) scale({s})"><path d="{d}" fill="{fill}" stroke="#1E1E24" stroke-width="1.4" stroke-linejoin="round"/></g>'


PLANE = "M0,-9 L2,-3 L10,2 L10,4.5 L2,2.5 L2,6.5 L5,8.5 L5,10 L0,9 L-5,10 L-5,8.5 L-2,6.5 L-2,2.5 L-10,4.5 L-10,2 L-2,-3Z"
SHIP = "M-10,-3 H10 L7,4 H-7Z M-3,-3 V-8 H4 V-3"
ic = "".join(icon(PLANE, 330, k * 360 / 22, 2.6, "#ff4d4d") for k in range(22)) + "".join(icon(SHIP, 215, 10 + k * 360 / 12, 2.4, "#e8eef6") for k in range(12))
tw = f'<g transform="translate({SX - CXU * S:.1f},{SY - CYU * S:.1f}) scale({S:.4f})"><path d="{TW}" fill="#ff4d4d" fill-opacity=".7" stroke="#fff" stroke-width="1.2" stroke-linejoin="round"/></g>'

html = f'''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" />
<style>
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }}
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }}
:root {{ --ink:#1e1e24; --yellow:#ffd23f; --red:#e0243a; }}
body {{ margin:0; width:1080px; height:1920px; overflow:hidden; font-family:"Kanit",sans-serif; }}
#root {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:#050c1c; }}
.abs {{ position:absolute; }}
#bg {{ left:0; top:0; width:1080px; height:1920px; background:url("assets/sat.jpg") {bgx:.0f}px {bgy:.0f}px / {bgw:.0f}px {bgh:.0f}px no-repeat; }}
.vig {{ inset:0; background: linear-gradient(180deg, rgba(5,12,28,.82) 0%, rgba(5,12,28,.15) 32%, rgba(5,12,28,.1) 60%, rgba(5,12,28,.9) 100%); box-shadow: inset 0 0 240px 70px rgba(2,6,15,.7); }}
.pill {{ left:0; top:130px; width:1080px; display:flex; justify-content:center; }}
.pill div {{ background:var(--red); color:#fff; border:8px solid var(--ink); border-radius:999px; padding:6px 52px 12px; font-size:58px; font-weight:800; }}
.t {{ left:0; width:1080px; text-align:center; font-weight:800; line-height:1.02; -webkit-text-stroke:28px var(--ink); paint-order:stroke fill; }}
.t1 {{ top:290px; font-size:148px; color:var(--yellow); white-space:nowrap; }}
.t2 {{ top:560px; font-size:110px; color:#fff; white-space:nowrap; }}
.band {{ left:0; top:1500px; width:1080px; text-align:center; }}
.band div {{ display:inline-block; background:var(--yellow); border:8px solid var(--ink); border-radius:28px; padding:6px 56px 16px; font-size:84px; font-weight:800; color:var(--ink); box-shadow:0 12px 0 rgba(0,0,0,.35); transform:rotate(-2deg); }}
.sub {{ left:0; top:1700px; width:1080px; text-align:center; font-size:56px; font-weight:800; color:#fff; -webkit-text-stroke:12px var(--ink); paint-order:stroke fill; }}
.brand {{ left:0; top:1810px; width:1080px; text-align:center; font-size:44px; font-weight:800; color:var(--yellow); -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }}
</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="1">
  <div class="abs" id="bg"></div>
  <div class="abs vig"></div>
  <svg class="abs" style="left:0;top:0" width="1080" height="1920" viewBox="0 0 1080 1920">{tw}<circle cx="{SX}" cy="{SY}" r="105" fill="none" stroke="#ff4d4d" stroke-width="7" stroke-dasharray="16 12"/>{ic}</svg>
  <div class="abs pill"><div>ซ้อมรบกดดัน · สมมติ</div></div>
  <div class="abs t t1">ปิดล้อมไต้หวัน?</div>
  <div class="abs t t2">ของแพงไหม?</div>
  <div class="abs band"><div>ชิปหยุด มือถือ รถ แพงขึ้น?</div></div>
  <div class="abs sub">เครื่องบิน 49 ลำ ในวันเดียว</div>
  <div class="abs brand">เล่าไม่รู้บ้าง...รู้บ้าง</div>
</div>
<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = {{ duration: function () {{ return 1; }}, pause: function () {{}}, seek: function () {{}}, time: function () {{ return 0; }} }};</script>
</body></html>'''
(H / "cover" / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html", len(html))
