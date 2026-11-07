"""สร้าง cover/index.html ของตอน 033 (หน้าปก 9:16) แล้วถ่ายภาพด้วย npx hyperframes snapshot"""
import json
from pathlib import Path

H = Path(__file__).resolve().parent
WL = (H / "video" / "world-line.txt").read_text()
OUT = json.loads((H / "video" / "outlines.json").read_text(encoding="utf-8"))
mx = lambda lon: round((lon + 180) * 10, 1)
my = lambda lat: round((90 - lat) * 10, 1)
K = 1.0
TX = 540 - mx(76) * K
TY = 1050 - my(20) * K
dc = (mx(54.0), my(24.0))
ir = (mx(100.5), my(13.75))
GRAT = "".join(f"M{mx(lo)},0V1800" for lo in range(-180, 181, 15)) + "".join(f"M0,{my(la)}H3600" for la in range(-90, 91, 15))
ARC = f"M{dc[0]},{dc[1]} Q{(dc[0] + ir[0]) / 2},{my(-2)} {ir[0]},{ir[1]}"

html = f'''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" />
<style>
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }}
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }}
:root {{ --ink:#1e1e24; --yellow:#ffd23f; --red:#e0243a; }}
body {{ margin:0; width:1080px; height:1920px; overflow:hidden; font-family:"Kanit",sans-serif; }}
#root {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:#06101f; }}
svg {{ position:absolute; left:0; top:0; }}
.shade {{ position:absolute; inset:0; background: linear-gradient(180deg, rgba(5,12,28,.7) 0%, rgba(5,12,28,0) 40%, rgba(5,12,28,.6) 100%); box-shadow: inset 0 0 240px 70px rgba(5,12,28,.7); }}
.abs {{ position:absolute; }}
.pill {{ left:0; top:130px; width:1080px; display:flex; justify-content:center; }}
.pill div {{ background:var(--red); color:#fff; border:8px solid var(--ink); border-radius:999px; padding:6px 52px 12px; font-size:60px; font-weight:800; }}
.t {{ left:0; width:1080px; text-align:center; font-weight:800; line-height:1.02; -webkit-text-stroke:28px var(--ink); paint-order:stroke fill; }}
.t1 {{ top:330px; font-size:170px; color:var(--yellow); }}
.t2 {{ top:600px; font-size:84px; color:#fff; white-space:nowrap; }}
.band {{ left:0; top:1560px; width:1080px; text-align:center; }}
.band div {{ display:inline-block; background:var(--yellow); border:8px solid var(--ink); border-radius:28px; padding:6px 56px 16px; font-size:92px; font-weight:800; color:var(--ink); box-shadow:0 12px 0 rgba(0,0,0,.35); transform:rotate(-2deg); }}
.brand {{ left:0; top:1790px; width:1080px; text-align:center; font-size:46px; font-weight:800; color:#fff; -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }}
</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="1">
  <svg width="1080" height="1920" viewBox="0 0 1080 1920"><g transform="translate({TX:.1f},{TY:.1f}) scale({K})">
    <image href="assets/sat.jpg" x="1750" y="150" width="1550" height="1200" preserveAspectRatio="none"/>
    <path d="{ARC}" fill="none" stroke="#ffd23f" stroke-width="6" stroke-dasharray="16 12" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
    <path d="{WL}" fill="none" stroke="#ffffff" stroke-opacity="0.35" stroke-width="1.2" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>
    <path d="{OUT["Iran"]}" fill="#ffd23f" fill-opacity=".18" stroke="#ffd23f" stroke-width="4" stroke-linejoin="round" vector-effect="non-scaling-stroke"/>
    <circle cx="{dc[0]}" cy="{dc[1]}" r="26" fill="none" stroke="#4a8cff" stroke-width="5" vector-effect="non-scaling-stroke"/>
    <circle cx="{dc[0]}" cy="{dc[1]}" r="13" fill="#4a8cff" stroke="#fff" stroke-width="3" vector-effect="non-scaling-stroke"/>
  </g></svg>
  <div class="shade"></div>
  <div class="abs pill"><div>ค่าไฟ · สงครามอิหร่าน</div></div>
  <div class="abs t t1">ค่าไฟแพง?</div>
  <div class="abs t t2">ใบเสร็จยังไม่ขึ้น แต่มีคนอุ้ม</div>
  <div class="abs band"><div>เช็กก่อนบิลขึ้น!</div></div>
  <div class="abs brand">เล่าไม่รู้บ้าง...รู้บ้าง</div>
</div>
<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = {{ duration: function () {{ return 1; }}, pause: function () {{}}, seek: function () {{}}, time: function () {{ return 0; }} }};</script>
</body></html>'''
(H / "cover" / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html", len(html))
