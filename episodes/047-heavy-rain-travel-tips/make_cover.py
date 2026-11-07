"""สร้าง cover/index.html ตอน 047 (ปก 9:16 แผนที่ดาวเทียมมืด + ฝน สไตล์ 028) แล้วถ่ายภาพ:
  python make_cover.py && cd cover && npx hyperframes snapshot --at 0 -o ../snapcover"""
import shutil
import numpy as np
from pathlib import Path
from PIL import Image, ImageEnhance

H = Path(__file__).resolve().parent
C = H / "cover"
(C / "fonts").mkdir(parents=True, exist_ok=True); (C / "assets").mkdir(exist_ok=True)
for f in (H / "video" / "fonts").glob("*"):
    shutil.copy(f, C / "fonts" / f.name)
shutil.copy(H / "video" / "hyperframes.json", C / "hyperframes.json")

# ตัดภาพดาวเทียมรอบไทย (lon 94-110, lat -2..26) ให้เป็น 9:16
PPD, LON0, LAT1 = 22.8, -5.0, 75.0
im = Image.open(H / "video" / "assets" / "sat.jpg")
box = (int((94 - LON0) * PPD), int((LAT1 - 26) * PPD), int((110 - LON0) * PPD), int((LAT1 + 2) * PPD))
bg = im.crop(box).resize((1080, 1920), Image.LANCZOS)
bg = ImageEnhance.Brightness(bg).enhance(0.8)
bg.save(C / "assets" / "bg.jpg", quality=88)

rng = np.random.default_rng(9)
rain = "".join(f'<path d="M{int(rng.integers(-40,1100))},{int(rng.integers(-60,1900))} l-{int(l)//3},{int(l)}" stroke="#bfe6ff" stroke-width="{3+i%3}" stroke-linecap="round" opacity="{.35+(i%4)*.12:.2f}"/>'
               for i, l in enumerate(rng.integers(50, 120, 90)))

html = f'''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" />
<style>
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }}
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }}
:root {{ --ink:#050D1F; --gold:#FFD23F; --red:#e0243a; --blue:#4cc3ff; }}
body {{ margin:0; width:1080px; height:1920px; overflow:hidden; font-family:"Kanit",sans-serif; }}
#root {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:#050c1c url(assets/bg.jpg) center/cover; }}
.abs {{ position:absolute; }}
.shade {{ inset:0; background: radial-gradient(circle at 50% 45%, rgba(5,12,28,.25), rgba(5,12,28,.8) 80%); box-shadow: inset 0 0 220px 60px rgba(5,15,35,.6); }}
.brand {{ left:60px; top:96px; font-size:40px; font-weight:800; color:var(--gold); -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }}
.pill {{ left:0; top:230px; width:1080px; display:flex; justify-content:center; }}
.pill div {{ background:var(--blue); color:var(--ink); border:8px solid var(--ink); border-radius:999px; padding:6px 52px 12px; font-size:60px; font-weight:800; }}
.t {{ left:0; width:1080px; text-align:center; font-weight:800; line-height:1.02; -webkit-text-stroke:26px var(--ink); paint-order:stroke fill; white-space:nowrap; }}
.t1 {{ top:440px; font-size:200px; color:var(--gold); }}
.t2 {{ top:700px; font-size:190px; color:#fff; }}
.t3 {{ top:1010px; font-size:150px; color:#fff; }}
.t4 {{ top:1210px; font-size:170px; color:var(--red); -webkit-text-stroke-color:#fff; }}
.sub {{ left:0; top:1500px; width:1080px; text-align:center; font-size:76px; font-weight:800; color:var(--blue); -webkit-text-stroke:14px var(--ink); paint-order:stroke fill; }}
</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="1">
  <div class="abs shade"></div>
  <svg class="abs" style="left:0;top:0" width="1080" height="1920" viewBox="0 0 1080 1920">{rain}</svg>
  <div class="abs brand">เล่าไม่รู้บ้าง...รู้บ้าง</div>
  <div class="abs pill"><div>เดินทางหน้าฝน</div></div>
  <div class="abs t t1">ฝนตกหนัก</div>
  <div class="abs t t2">ทั้งคืน</div>
  <div class="abs t t3">พรุ่งนี้เช้า</div>
  <div class="abs t t4">ไปไหนยังไง?</div>
  <div class="abs sub">เช็กก่อนออกจากบ้าน</div>
</div>
<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = {{ duration: function () {{ return 1; }}, pause: function () {{}}, seek: function () {{}}, time: function () {{ return 0; }} }};</script>
</body></html>'''
(C / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html", len(html))
