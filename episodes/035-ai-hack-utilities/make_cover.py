"""สร้าง cover/index.html ของตอน 035 (หน้าปก 9:16: แผนที่ ASCII สีอำพัน + ไทยระบายสีธง + MALWARE) แล้วถ่ายภาพด้วย
  npx hyperframes snapshot cover --at 0 --no-end -o snapcover
"""
import json
from pathlib import Path

H = Path(__file__).resolve().parent
ASCII = (H / "video" / "ascii_map.html").read_text(encoding="utf-8")
M = json.loads((H / "video" / "ascii_marks.json").read_text())
CW, CH, TOP = 11.25, 18, 520
mk = lambda k, dx=0, dy=0: (round(M[k][0] * CW + dx), round(TOP + M[k][1] * CH + dy))
th, fr, ir = mk("TH", -30, -80), mk("FR", -30, -70), mk("IR", -30, -70)

html = f'''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" />
<style>
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }}
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }}
@font-face {{ font-family: "VT323"; font-weight: 400; src: url("fonts/VT323-Regular.ttf") format("truetype"); }}
:root {{ --ink:#1e1e24; --yellow:#ffd23f; --red:#e0243a; }}
body {{ margin:0; width:1080px; height:1920px; overflow:hidden; font-family:"Kanit",sans-serif; }}
#root {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:#0c0600; }}
.abs {{ position:absolute; }}
#amap {{ left:0; top:{TOP}px; width:1080px; height:760px; font-family:"VT323",monospace; font-size:28px; line-height:18px; white-space:pre; color:#ffb000; text-shadow:0 0 8px rgba(255,176,0,.75); }}
.ar {{ height:18px; }} .ar i {{ font-style:normal; }}
.ar i.c {{ color:#ffd27a; }} .ar i.l {{ color:#b87400; }} .ar i.o {{ color:#6b4300; }}
.scan {{ inset:0; background:repeating-linear-gradient(0deg, rgba(0,0,0,.3) 0 3px, rgba(0,0,0,0) 3px 7px); }}
.vig {{ inset:0; box-shadow: inset 0 0 260px 80px rgba(0,0,0,.85); background: linear-gradient(180deg, rgba(12,6,0,.55) 0%, rgba(12,6,0,0) 35%, rgba(12,6,0,.7) 100%); }}
.mk {{ font-family:"VT323",monospace; font-size:44px; line-height:44px; padding:0 10px; border:3px solid #ffb000; color:#ffb000; background:rgba(40,20,0,.8); white-space:nowrap; text-shadow:0 0 10px #ffb000; }}
.mk.r {{ color:#ff3b2e; border-color:#ff3b2e; background:rgba(40,0,0,.8); text-shadow:0 0 10px #ff3b2e; }}
.fl {{ display:inline-block; width:56px; height:38px; border:3px solid #fff; margin-right:12px; vertical-align:-6px; box-sizing:border-box; }}
.fr {{ background:linear-gradient(90deg,#0055A4 33.3%,#fff 33.3% 66.6%,#EF4135 66.6%); }}
.ir {{ background:linear-gradient(180deg,#239F40 33.3%,#fff 33.3% 66.6%,#DA0000 66.6%); }}
.th {{ background:linear-gradient(180deg,#A51931 16.6%,#fff 16.6% 33.3%,#2D2A4A 33.3% 66.6%,#fff 66.6% 83.3%,#A51931 83.3%); }}
.pill {{ left:0; top:130px; width:1080px; display:flex; justify-content:center; }}
.pill div {{ background:var(--red); color:#fff; border:8px solid var(--ink); border-radius:999px; padding:6px 52px 12px; font-size:60px; font-weight:800; }}
.t {{ left:0; width:1080px; text-align:center; font-weight:800; line-height:1.02; -webkit-text-stroke:28px var(--ink); paint-order:stroke fill; }}
.t1 {{ top:290px; font-size:168px; color:var(--yellow); white-space:nowrap; }}
.t2 {{ top:560px; font-size:96px; color:#fff; white-space:nowrap; }}
#mal {{ left:0; top:1000px; width:1080px; text-align:center; font-family:"VT323",monospace; font-size:230px; line-height:230px; color:#ff3b2e; letter-spacing:6px; text-shadow:8px 0 #ffb000,-8px 0 #ff00aa,0 0 60px #ff3b2e; }}
.band {{ left:0; top:1490px; width:1080px; text-align:center; }}
.band div {{ display:inline-block; background:var(--yellow); border:8px solid var(--ink); border-radius:28px; padding:6px 56px 16px; font-size:92px; font-weight:800; color:var(--ink); box-shadow:0 12px 0 rgba(0,0,0,.35); transform:rotate(-2deg); }}
.brand {{ left:0; top:1790px; width:1080px; text-align:center; font-size:46px; font-weight:800; color:#fff; -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }}
</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="1">
  <div class="abs" id="amap">{ASCII}</div>
  <div class="abs scan"></div>
  <div class="abs vig"></div>
  <div class="abs mk" style="left:{fr[0]}px;top:{fr[1]}px"><span class="fl fr"></span>FR</div>
  <div class="abs mk" style="left:{ir[0]}px;top:{ir[1]}px"><span class="fl ir"></span>IR</div>
  <div class="abs mk r" style="left:{th[0]}px;top:{th[1]}px"><span class="fl th"></span>TH ▒▒ TARGET</div>
  <div class="abs pill"><div>แฮกสาธารณูปโภค · สมมติ</div></div>
  <div class="abs t t1">ไฟดับ น้ำหยุด?</div>
  <div class="abs t t2">ถ้า AI แฮกไทย</div>
  <div class="abs" id="mal">MALWARE</div>
  <div class="abs band"><div>เตรียมตัวทันไหม?</div></div>
  <div class="abs brand">เล่าไม่รู้บ้าง...รู้บ้าง</div>
</div>
<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = {{ duration: function () {{ return 1; }}, pause: function () {{}}, seek: function () {{}}, time: function () {{ return 0; }} }};</script>
</body></html>'''
(H / "cover" / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html", len(html))
