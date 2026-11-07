"""สร้าง cover/index.html ตอน 044 (ปก 9:16 แผนที่ยุโรป-แอตแลนติก + หมุด 4 ชาติ) แล้วถ่ายภาพ:
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

W, LON0 = 70, -2
K = 360 / W * 1080 / 8192
bx = (LON0 + 180) / 360 * 8192 * K - 540
by = 0
def xy(lon, lat):
    return (lon + 180) / 360 * 8192 * K - bx, (90 - lat) / 180 * 4096 * K - by
PINS = [("ไอซ์แลนด์", -19, 65), ("นอร์เวย์", 8.5, 61), ("ฟินแลนด์", 25, 64), ("สวิตเซอร์แลนด์", 8.2, 46.8)]
pins = ""
for n, lo, la in PINS:
    x, y = xy(lo, la)
    pins += (f'<svg class="abs" style="left:{x-42:.0f}px;top:{y-125:.0f}px;filter:drop-shadow(0 5px 8px rgba(0,0,0,.7))" width="84" height="130" viewBox="0 0 168 260"><path d="M84,250 C20,160 10,120 10,84 a74,74 0 1 1 148,0 C158,120 148,160 84,250Z" fill="#e0243a" stroke="#fff" stroke-width="10"/><circle cx="84" cy="84" r="30" fill="#fff"/></svg>'
             f'<div class="abs lab" style="left:{x-200:.0f}px;top:{y+6:.0f}px;width:400px">{n}</div>')
html = '''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" />
<style>
@font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }
@font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }
:root { --ink:#1e1e24; --yellow:#ffd23f; --red:#e0243a; }
body { margin:0; width:1080px; height:1920px; overflow:hidden; font-family:"Kanit",sans-serif; }
#root { position:relative; width:1080px; height:1920px; overflow:hidden; background:#050c1c; }
.abs { position:absolute; }
#map { left:0; top:0; width:1080px; height:1920px; background:url(assets/earth.jpg) no-repeat; background-size:%SIZEW%px %SIZEH%px; background-position:-%BX%px 0; }
.vig { inset:0; background: linear-gradient(180deg, rgba(5,12,30,0) 0%, rgba(5,12,30,0) 35%, rgba(5,12,30,.9) 62%, rgba(5,12,30,.95) 100%); }
.pill { left:0; top:110px; width:1080px; display:flex; justify-content:center; }
.pill div { background:var(--yellow); color:var(--ink); border:8px solid var(--ink); border-radius:999px; padding:6px 52px 12px; font-size:62px; font-weight:800; }
.lab { text-align:center; font-size:40px; font-weight:800; color:#fff; -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }
.t { left:0; width:1080px; text-align:center; font-weight:800; line-height:1.02; -webkit-text-stroke:28px var(--ink); paint-order:stroke fill; white-space:nowrap; }
.t1 { top:1000px; font-size:168px; color:var(--yellow); }
.t2 { top:1230px; font-size:168px; color:#fff; }
.sub { left:0; top:1600px; width:1080px; text-align:center; font-size:60px; font-weight:800; color:#fff; -webkit-text-stroke:12px var(--ink); paint-order:stroke fill; }
.brand { left:0; top:1790px; width:1080px; text-align:center; font-size:44px; font-weight:800; color:var(--yellow); -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }
</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="1">
  <div class="abs" id="map"></div>
  <div class="abs vig"></div>
  %PINS%
  <div class="abs pill"><div>AI ชี้ 5 ชาติ · ไทยไม่อยู่ในลิสต์</div></div>
  <div class="abs t t1">มหันตภัยโลก</div>
  <div class="abs t t2">หนีไปไหน?</div>
  <div class="abs sub">5 ประเทศที่รอดได้มากที่สุด</div>
  <div class="abs brand">เล่าไม่รู้บ้าง...รู้บ้าง</div>
</div>
<script>window.__timelines = window.__timelines || {}; window.__timelines["main"] = { duration: function () { return 1; }, pause: function () {}, seek: function () {}, time: function () { return 0; } };</script>
</body></html>'''
html = (html.replace("%SIZEW%", f"{8192 * K:.0f}").replace("%SIZEH%", f"{4096 * K:.0f}")
        .replace("%BX%", f"{bx:.0f}").replace("%PINS%", pins))
(C / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html", len(html))
