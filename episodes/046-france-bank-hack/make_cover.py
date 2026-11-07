"""สร้าง cover/index.html ตอน 046 (ปก 9:16 สีกรมท่า-ทอง ชื่อช่อง) แล้วถ่ายภาพ:
  python make_cover.py && cd cover && npx hyperframes snapshot --at 0 -o ../snapcover"""
import shutil
from pathlib import Path

H = Path(__file__).resolve().parent
C = H / "cover"
(C / "fonts").mkdir(parents=True, exist_ok=True); (C / "assets").mkdir(exist_ok=True)
for f in (H / "video" / "fonts").glob("*"):
    shutil.copy(f, C / "fonts" / f.name)
for n in ("watermark.png", "plaque.png"):
    shutil.copy(H / "video" / "assets" / n, C / "assets" / n)
shutil.copy(H / "video" / "hyperframes.json", C / "hyperframes.json")

html = '''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" />
<style>
@font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }
@font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }
:root { --ink:#050D1F; --gold:#FFD45A; --red:#e0243a; }
body { margin:0; width:1080px; height:1920px; overflow:hidden; font-family:"Kanit",sans-serif; }
#root { position:relative; width:1080px; height:1920px; overflow:hidden; background: radial-gradient(circle at 50% 38%, #12295a, #050d1f 70%); }
.abs { position:absolute; }
.grid { inset:0; background-image: linear-gradient(rgba(255,212,90,.08) 2px, transparent 2px), linear-gradient(90deg, rgba(255,212,90,.08) 2px, transparent 2px); background-size: 90px 90px; }
.glow { left:90px; top:300px; width:900px; height:900px; border-radius:50%; background: radial-gradient(circle, rgba(224,36,58,.55), rgba(224,36,58,0) 65%); }
.hz { left:-100px; width:1280px; height:100px; background: repeating-linear-gradient(-45deg, #D9A53A 0 50px, #050D1F 50px 100px); }
.pill { left:0; top:200px; width:1080px; display:flex; justify-content:center; }
.pill div { background:var(--gold); color:var(--ink); border:8px solid var(--ink); border-radius:999px; padding:6px 52px 12px; font-size:58px; font-weight:800; }
.num { left:0; top:380px; width:1080px; text-align:center; font-size:330px; font-weight:800; color:var(--gold); -webkit-text-stroke:30px var(--ink); paint-order:stroke fill; line-height:1; }
.unit { left:0; top:690px; width:1080px; text-align:center; font-size:190px; font-weight:800; color:#fff; -webkit-text-stroke:26px var(--ink); paint-order:stroke fill; line-height:1; }
.t { left:0; width:1080px; text-align:center; font-weight:800; line-height:1.02; -webkit-text-stroke:26px var(--ink); paint-order:stroke fill; white-space:nowrap; }
.t1 { top:960px; font-size:200px; color:#fff; }
.t2 { top:1210px; font-size:152px; color:var(--red); -webkit-text-stroke-color:#fff; }
.sub { left:0; top:1415px; width:1080px; text-align:center; font-size:68px; font-weight:800; color:var(--gold); -webkit-text-stroke:14px var(--ink); paint-order:stroke fill; }
#plaque { left:400px; top:1520px; width:280px; height:280px; border-radius:30px; border:6px solid #D9A53A; box-shadow:0 0 50px rgba(255,212,90,.5); }
#wm { left:36px; top:130px; width:120px; height:120px; filter:drop-shadow(0 4px 10px rgba(0,0,0,.6)); }
.brand { left:170px; top:150px; font-size:44px; font-weight:800; color:var(--gold); -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }
</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="1">
  <div class="abs grid"></div>
  <div class="abs glow"></div>
  <div class="abs hz" style="top:0"></div><div class="abs hz" style="bottom:0"></div>
  <img class="abs" id="wm" src="assets/watermark.png" />
  <div class="abs brand" style="top:140px;left:170px;display:none">เล่าไม่รู้บ้าง...รู้บ้าง</div>
  <div class="abs pill"><div>ธนาคารฝรั่งเศส ถูกแฮก</div></div>
  <div class="abs num">3,750</div>
  <div class="abs unit">ล้านบาท</div>
  <div class="abs t t1">หายไป!</div>
  <div class="abs t t2">ไทยเสี่ยงไหม?</div>
  <div class="abs sub">เตรียมตัวก่อนแอปล่ม</div>
  <img class="abs" id="plaque" src="assets/plaque.png" />
</div>
<script>window.__timelines = window.__timelines || {}; window.__timelines["main"] = { duration: function () { return 1; }, pause: function () {}, seek: function () {}, time: function () { return 0; } };</script>
</body></html>'''
(C / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html", len(html))
