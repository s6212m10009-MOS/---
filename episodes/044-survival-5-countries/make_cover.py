"""ปกตอน 044 (9:16): แผนที่โลกเต็มจอ + ไฟระเบิด + ถ้าโลกเกิด มหันตภัย WHAT IF?
  python make_cover.py && cd cover && npx hyperframes snapshot --at 0 -o ../snapcover"""
import shutil
from pathlib import Path
H = Path(__file__).resolve().parent
C = H / "cover"
(C / "fonts").mkdir(parents=True, exist_ok=True); (C / "assets").mkdir(exist_ok=True)
for f in (H / "video" / "fonts").glob("*"):
    shutil.copy(f, C / "fonts" / f.name)
shutil.copy(H / "video" / "assets" / "earth.jpg", C / "assets" / "earth.jpg")
shutil.copy(H / "video" / "assets" / "watermark.png", C / "assets" / "watermark.png")
shutil.copy(H / "video" / "hyperframes.json", C / "hyperframes.json")
K = 1.2 * 1080 / 3600 * 3.6  # earth.jpg ถูกใช้ที่ 8192px: ขยายให้สูงเกิน 1920
W = 8192 * 0.55; Hh = 4096 * 0.55   # ภาพ 4506x2253 (สูง > 1920)
bx = (25 + 180) / 360 * W - 540
by = 120
html = '''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" />
<style>
@font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }
@font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }
:root { --ink:#1e1e24; --yellow:#ffd23f; --red:#ff4b3a; }
body { margin:0; width:1080px; height:1920px; overflow:hidden; font-family:"Kanit",sans-serif; }
#root { position:relative; width:1080px; height:1920px; overflow:hidden; background:#050c1c; }
.abs { position:absolute; }
#map { left:0; top:0; width:1080px; height:1920px; background:url(assets/earth.jpg) no-repeat; background-size:%W%px %H%px; background-position:-%BX%px -%BY%px; }
.vig { inset:0; background: radial-gradient(ellipse at 50% 55%, rgba(0,0,0,0) 30%, rgba(5,12,30,.85) 100%); }
.fire { left:90px; top:980px; width:900px; height:900px; border-radius:50%; background: radial-gradient(circle, #fff 0%, #ffd23f 22%, #ff4b1a 48%, rgba(255,75,26,0) 70%); opacity:.9; }
.red { inset:0; background: rgba(193,18,31,.22); }
.t { left:0; width:1080px; text-align:center; font-weight:800; line-height:1.02; -webkit-text-stroke:28px var(--ink); paint-order:stroke fill; white-space:nowrap; }
.t0 { top:260px; font-size:130px; color:#fff; }
.t1 { top:410px; font-size:230px; color:var(--yellow); }
.t2 { top:650px; font-size:200px; color:var(--red); }
.sub { left:0; top:1650px; width:1080px; text-align:center; font-size:62px; font-weight:800; color:#fff; -webkit-text-stroke:12px var(--ink); paint-order:stroke fill; }
.brand { left:0; top:1790px; width:1080px; text-align:center; font-size:46px; font-weight:800; color:var(--yellow); -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }
#wm { left:36px; top:40px; width:130px; height:130px; filter:drop-shadow(0 4px 10px rgba(0,0,0,.6)); }
</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="1">
  <div class="abs" id="map"></div>
  <div class="abs red"></div>
  <div class="abs fire"></div>
  <div class="abs vig"></div>
  <img class="abs" id="wm" src="assets/watermark.png" />
  <div class="abs t t0">ถ้าโลกเกิด</div>
  <div class="abs t t1">มหันตภัย</div>
  <div class="abs t t2">WHAT IF?</div>
  <div class="abs sub">AI ชี้ 5 ชาติที่รอดได้</div>
  <div class="abs brand">เล่าไม่รู้บ้าง...รู้บ้าง</div>
</div>
<script>window.__timelines = window.__timelines || {}; window.__timelines["main"] = { duration: function () { return 1; }, pause: function () {}, seek: function () {}, time: function () { return 0; } };</script>
</body></html>'''
html = html.replace("%W%", f"{W:.0f}").replace("%H%", f"{Hh:.0f}").replace("%BX%", f"{bx:.0f}").replace("%BY%", f"{by:.0f}")
(C / "index.html").write_text(html, encoding="utf-8")
print("cover ok")
