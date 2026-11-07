"""สร้าง cover/index.html ตอน 040 (หน้าปก 9:16 ฟ้าฝ่า) แล้วถ่ายภาพ:
  python make_cover.py && cd cover && npx hyperframes snapshot --at 0 -o ../snapcover"""
from pathlib import Path

H = Path(__file__).resolve().parent
INK = "#1e1e24"
figure = (f'<g transform="translate(330,1325) scale(1.9)"><circle cx="0" cy="-60" r="26" fill="#fff" stroke="#fff" stroke-width="6"/>'
          f'<path d="M0,-34 V30 M0,-14 L-28,-34 M0,-14 L28,-34 M0,30 L-20,76 M0,30 L20,76" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/></g>')
html = f'''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" />
<style>
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }}
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }}
:root {{ --ink:{INK}; --yellow:#ffd23f; --red:#e0243a; }}
body {{ margin:0; width:1080px; height:1920px; overflow:hidden; font-family:"Kanit",sans-serif; }}
#root {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:#02040c; }}
.abs {{ position:absolute; }}
#bg {{ left:0; top:0; width:1080px; height:1920px; object-fit:cover; object-position:31% 50%; transform:scale(1.12); transform-origin:34% 45%; }}
.vig {{ inset:0; background: linear-gradient(180deg, rgba(2,4,12,.85) 0%, rgba(2,4,12,.1) 34%, rgba(2,4,12,.05) 58%, rgba(2,4,12,.92) 100%); box-shadow: inset 0 0 220px 60px rgba(2,4,12,.6); }}
.pill {{ left:0; top:130px; width:1080px; display:flex; justify-content:center; }}
.pill div {{ background:var(--red); color:#fff; border:8px solid var(--ink); border-radius:999px; padding:6px 52px 12px; font-size:58px; font-weight:800; }}
.t {{ left:0; width:1080px; text-align:center; font-weight:800; line-height:1.02; -webkit-text-stroke:28px var(--ink); paint-order:stroke fill; }}
.t1 {{ top:300px; font-size:138px; color:var(--yellow); white-space:nowrap; }}
.t2 {{ top:560px; font-size:118px; color:#fff; white-space:nowrap; }}
.band {{ left:0; top:1500px; width:1080px; text-align:center; }}
.band div {{ display:inline-block; background:var(--yellow); border:8px solid var(--ink); border-radius:28px; padding:6px 56px 16px; font-size:80px; font-weight:800; color:var(--ink); box-shadow:0 12px 0 rgba(0,0,0,.35); transform:rotate(-2deg); }}
.sub {{ left:0; top:1700px; width:1080px; text-align:center; font-size:56px; font-weight:800; color:#fff; -webkit-text-stroke:12px var(--ink); paint-order:stroke fill; }}
.brand {{ left:0; top:1810px; width:1080px; text-align:center; font-size:44px; font-weight:800; color:var(--yellow); -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }}
#wm {{ left:36px; top:40px; width:130px; height:130px; filter:drop-shadow(0 4px 10px rgba(0,0,0,.6)); }}
</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="1">
  <img class="abs" id="bg" src="assets/lightning.jpg" />
  <div class="abs vig"></div>
  <svg class="abs" style="left:0;top:0;filter:drop-shadow(0 0 10px rgba(0,0,0,.9))" width="1080" height="1920" viewBox="0 0 1080 1920">{figure}</svg>
  <img class="abs" id="wm" src="assets/watermark.png" />
  <div class="abs pill"><div>What if</div></div>
  <div class="abs t t1">ถ้าฟ้าฝ่าใกล้คุณ</div>
  <div class="abs t t2">เอาตัวรอดยังไง?</div>
  <div class="abs band"><div>ห้ามใต้ต้นไม้ · ห้ามนอนราบ</div></div>
  <div class="abs sub">ฟ้าผ่าห่างแค่ 10 เมตร</div>
  <div class="abs brand">เล่าไม่รู้บ้าง...รู้บ้าง</div>
</div>
<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = {{ duration: function () {{ return 1; }}, pause: function () {{}}, seek: function () {{}}, time: function () {{ return 0; }} }};</script>
</body></html>'''
(H / "cover" / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html", len(html))
