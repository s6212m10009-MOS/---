"""สร้าง cover/index.html ตอน 043 (ปก 9:16 แผนที่ไซนาย + น้ำท่วม, ไม่มีลายน้ำ) แล้วถ่ายภาพ:
  python make_cover.py && cd cover && npx hyperframes snapshot --at 0 -o ../snapcover"""
import shutil
from pathlib import Path

H = Path(__file__).resolve().parent
C = H / "cover"
(C / "fonts").mkdir(parents=True, exist_ok=True); (C / "assets").mkdir(exist_ok=True)
for f in (H / "video" / "fonts").glob("*"):
    shutil.copy(f, C / "fonts" / f.name)
shutil.copy(H / "video" / "assets" / "earth.jpg", C / "assets" / "earth.jpg")
shutil.copy(H / "video" / "hyperframes.json", C / "hyperframes.json")

# ศูนย์กลางภาพ = นูเวบา (34.66E, 29.03N) ที่ ~25 องศากว้าง
K = 360 / 25 * 1080 / 8192            # ขยายภาพ 8192px
bx = 4885 * K - 540
by = (90 - 29.03) / 180 * 4096 * K - 1000
html = '''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" />
<style>
@font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }
@font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }
:root { --ink:#1e1e24; --yellow:#ffd23f; --red:#e0243a; }
body { margin:0; width:1080px; height:1920px; overflow:hidden; font-family:"Kanit",sans-serif; }
#root { position:relative; width:1080px; height:1920px; overflow:hidden; background:#050c1c; }
.abs { position:absolute; }
#map { left:0; top:0; width:1080px; height:1920px; background:url(assets/earth.jpg) no-repeat; background-size:%SIZEW%px %SIZEH%px; background-position:-%BX%px -%BY%px; }
.vig { inset:0; background: radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 35%, rgba(5,12,30,.85) 100%); }
.pill { left:0; top:170px; width:1080px; display:flex; justify-content:center; }
.pill div { background:var(--yellow); color:var(--ink); border:8px solid var(--ink); border-radius:999px; padding:6px 52px 12px; font-size:58px; font-weight:800; }
.t { left:0; width:1080px; text-align:center; font-weight:800; line-height:1.02; -webkit-text-stroke:28px var(--ink); paint-order:stroke fill; white-space:nowrap; }
.t1 { top:330px; font-size:210px; color:var(--yellow); }
.t2 { top:560px; font-size:210px; color:#fff; }
.sub { left:0; top:1700px; width:1080px; text-align:center; font-size:56px; font-weight:800; color:#fff; -webkit-text-stroke:12px var(--ink); paint-order:stroke fill; }
.brand { left:0; top:1805px; width:1080px; text-align:center; font-size:44px; font-weight:800; color:var(--yellow); -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }
#pin { left:456px; top:750px; }
</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="1">
  <div class="abs" id="map"></div>
  <div class="abs vig"></div>
  <svg class="abs" style="left:0;top:1180px;filter:drop-shadow(0 8px 12px rgba(0,0,0,.6))" width="1080" height="740" viewBox="0 0 1080 740"><path d="M0,120 q45,-60 90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 V740 H0Z" fill="#2f9fe0" stroke="#fff" stroke-width="10"/><path d="M0,230 q45,-50 90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 t90,0 V740 H0Z" fill="#1e78c2" stroke="#fff" stroke-width="8" opacity=".95"/></svg>
  <svg class="abs" id="pin" style="filter:drop-shadow(0 6px 10px rgba(0,0,0,.7))" width="168" height="260" viewBox="0 0 168 260"><path d="M84,250 C20,160 10,120 10,84 a74,74 0 1 1 148,0 C158,120 148,160 84,250Z" fill="#e0243a" stroke="#fff" stroke-width="10"/><circle cx="84" cy="84" r="30" fill="#fff"/></svg>
  <div class="abs pill"><div>ข่าวจากไซนายใต้ · อียิปต์</div></div>
  <div class="abs t t1">ทะเลทราย</div>
  <div class="abs t t2">น้ำท่วม!</div>
  <div class="abs sub">ที่แห้งที่สุด ทำไมถึงท่วมได้?</div>
  <div class="abs brand">เล่าไม่รู้บ้าง...รู้บ้าง</div>
</div>
<script>window.__timelines = window.__timelines || {}; window.__timelines["main"] = { duration: function () { return 1; }, pause: function () {}, seek: function () {}, time: function () { return 0; } };</script>
</body></html>'''
html = (html.replace("%SIZEW%", f"{8192 * K:.0f}").replace("%SIZEH%", f"{4096 * K:.0f}")
        .replace("%BX%", f"{bx:.0f}").replace("%BY%", f"{by:.0f}"))
(C / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html", len(html))
