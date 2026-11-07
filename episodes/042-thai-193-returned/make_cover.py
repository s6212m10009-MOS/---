"""สร้าง cover/index.html ตอน 042 (ปก 9:16 สไตล์เตือนภัย) แล้วถ่ายภาพ:
  python make_cover.py && cd cover && npx hyperframes snapshot --at 0 -o ../snapcover"""
import shutil
from pathlib import Path

H = Path(__file__).resolve().parent
C = H / "cover"
(C / "fonts").mkdir(parents=True, exist_ok=True); (C / "assets").mkdir(exist_ok=True)
for f in (H / "video" / "fonts").glob("*"):
    shutil.copy(f, C / "fonts" / f.name)
shutil.copy(H / "video" / "assets" / "watermark.png", C / "assets" / "watermark.png")
shutil.copy(H / "video" / "hyperframes.json", C / "hyperframes.json")

html = '''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" />
<style>
@font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }
@font-face { font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }
:root { --ink:#1e1e24; --yellow:#ffd23f; --red:#e0243a; --green:#31d07a; }
body { margin:0; width:1080px; height:1920px; overflow:hidden; font-family:"Kanit",sans-serif; }
#root { position:relative; width:1080px; height:1920px; overflow:hidden; background:#1a0206; }
.abs { position:absolute; }
#siren { left:-540px; top:0; width:2160px; height:1920px; background: conic-gradient(from 20deg at 50% 42%, rgba(255,30,50,.95), rgba(255,30,50,0) 16%, rgba(255,30,50,0) 50%, rgba(255,30,50,.95) 50.1%, rgba(255,30,50,0) 66%, rgba(255,30,50,0) 100%); }
.vig { inset:0; background: radial-gradient(ellipse at 50% 42%, rgba(0,0,0,0) 30%, rgba(10,0,4,.85) 100%); }
.hz { left:-100px; width:1280px; height:120px; background: repeating-linear-gradient(-45deg, #ffd23f 0 60px, #1e1e24 60px 120px); }
.pill { left:0; top:170px; width:1080px; display:flex; justify-content:center; }
.pill div { background:var(--yellow); color:var(--ink); border:8px solid var(--ink); border-radius:999px; padding:6px 52px 12px; font-size:58px; font-weight:800; }
.t { left:0; width:1080px; text-align:center; font-weight:800; line-height:1.02; -webkit-text-stroke:28px var(--ink); paint-order:stroke fill; white-space:nowrap; }
.t1 { top:1000px; font-size:200px; color:var(--yellow); }
.t2 { top:1230px; font-size:170px; color:#fff; }
#stamp { left:90px; top:1480px; width:900px; text-align:center; transform:rotate(-8deg); font-size:190px; font-weight:800; color:var(--green); -webkit-text-stroke:22px var(--ink); paint-order:stroke fill; }
.sub { left:0; top:1730px; width:1080px; text-align:center; font-size:52px; font-weight:800; color:#fff; -webkit-text-stroke:12px var(--ink); paint-order:stroke fill; }
.brand { left:0; top:1810px; width:1080px; text-align:center; font-size:44px; font-weight:800; color:var(--yellow); -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }
#wm { left:36px; top:150px; width:130px; height:130px; filter:drop-shadow(0 4px 10px rgba(0,0,0,.6)); }
</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="1">
  <div class="abs" id="siren"></div>
  <div class="abs vig"></div>
  <svg class="abs" style="left:240px;top:330px;filter:drop-shadow(0 0 30px rgba(224,36,58,.9))" width="600" height="600" viewBox="0 0 500 500"><circle cx="250" cy="250" r="225" fill="rgba(224,36,58,.2)" stroke="#e0243a" stroke-width="46"/><path d="M92,92 L408,408" stroke="#e0243a" stroke-width="46" stroke-linecap="round"/><text x="250" y="320" font-size="210" font-weight="800" text-anchor="middle" fill="#fff" stroke="#1e1e24" stroke-width="16" paint-order="stroke" font-family="Kanit" opacity=".95">193</text></svg>
  <div class="abs hz" style="top:0"></div><div class="abs hz" style="bottom:0"></div>
  <img class="abs" id="wm" src="assets/watermark.png" />
  <div class="abs pill"><div>ข่าวด่วน · เช็กแล้ว</div></div>
  <div class="abs t t1">แบน</div>
  <div class="abs t t2">กัมพูชา?</div>
  <div class="abs" id="stamp">ไม่จริง!</div>
  <div class="abs sub">แต่ 193 คนไทยถูกส่งกลับ จริง</div>
  <div class="abs brand">เล่าไม่รู้บ้าง...รู้บ้าง</div>
</div>
<script>window.__timelines = window.__timelines || {}; window.__timelines["main"] = { duration: function () { return 1; }, pause: function () {}, seek: function () {}, time: function () { return 0; } };</script>
</body></html>'''
(C / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html", len(html))
