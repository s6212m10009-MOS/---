"""สร้างหน้าปก 9:16 ของตอน 025 -> cover/index.html (แล้วถ่ายภาพด้วย hyperframes snapshot) ยืมฟังก์ชันวาดกระเป๋าจาก build.py"""
from pathlib import Path
HERE = Path(__file__).resolve().parent
src = (HERE / "build.py").read_text(encoding="utf-8")
ns = {"INK": "#1E1E24"}
exec(src[src.index("def W("):src.index("def txt(")], ns)
exec(src[src.index("def bag("):src.index("def bottle(")], ns)
bag = ns["bag"](220, 250, 1.65)
html = f'''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" />
<style>
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-thai-800-normal.woff2") format("woff2"); unicode-range: U+0E01-0E5B, U+200C-200D, U+25CC; }}
@font-face {{ font-family: "Kanit"; font-weight: 800; src: url("fonts/kanit-latin-800-normal.woff2") format("woff2"); unicode-range: U+0000-00FF, U+2000-206F, U+20AC, U+2190-2199, U+2212, U+0E3F; }}
:root {{ --ink:#1e1e24; --yellow:#ffd23f; --red:#e0243a; }}
body {{ margin:0; width:1080px; height:1920px; overflow:hidden; font-family:"Kanit",sans-serif; }}
#root {{ position:relative; width:1080px; height:1920px; overflow:hidden; background:#050c1c url("assets/earth.jpg") -1400px -700px / 6000px 3000px no-repeat; }}
.shade {{ position:absolute; inset:0; background: radial-gradient(circle, rgba(224,36,58,0) 35%, rgba(224,36,58,.55) 100%), linear-gradient(180deg, rgba(2,6,15,.75) 0%, rgba(2,6,15,.35) 40%, rgba(2,6,15,.55) 100%); box-shadow: inset 0 0 260px 80px rgba(5,15,35,.75); }}
.abs {{ position:absolute; }}
.pill {{ left:0; top:130px; width:1080px; display:flex; justify-content:center; }}
.pill div {{ background:var(--ink); color:#fff; border-radius:999px; padding:8px 48px 12px; font-size:52px; font-weight:800; }}
.t {{ left:0; width:1080px; text-align:center; font-weight:800; line-height:1.02; -webkit-text-stroke:28px var(--ink); paint-order:stroke fill; text-shadow:0 14px 0 rgba(0,0,0,.35); }}
.t1 {{ top:260px; font-size:260px; color:var(--yellow); }}
.t2 {{ top:560px; font-size:124px; color:#fff; white-space:nowrap; }}
.card {{ position:absolute; top:880px; width:440px; height:540px; background:#fff; border:8px solid var(--ink); border-radius:38px; box-shadow:0 14px 0 rgba(0,0,0,.35); overflow:hidden; }}
.card svg {{ position:absolute; left:0; top:0; }}
.card .lab {{ position:absolute; left:0; bottom:18px; width:100%; text-align:center; font-size:56px; font-weight:800; }}
.big {{ left:0; width:100%; text-align:center; top:70px; font-size:170px; font-weight:800; color:var(--red); line-height:1; }}
.sub {{ left:0; width:100%; text-align:center; top:260px; font-size:64px; font-weight:800; color:var(--ink); }}
.vs {{ left:0; top:1060px; width:1080px; text-align:center; font-size:110px; font-weight:800; color:var(--yellow); -webkit-text-stroke:18px var(--ink); paint-order:stroke fill; z-index:5; }}
.band {{ left:0; top:1500px; width:1080px; text-align:center; }}
.band div {{ display:inline-block; background:var(--yellow); border:8px solid var(--ink); border-radius:28px; padding:6px 56px 16px; font-size:92px; font-weight:800; color:var(--ink); box-shadow:0 12px 0 rgba(0,0,0,.35); transform:rotate(-2deg); }}
.brand {{ left:0; top:1760px; width:1080px; text-align:center; font-size:46px; font-weight:800; color:#fff; -webkit-text-stroke:10px var(--ink); paint-order:stroke fill; }}
</style></head><body>
<div id="root" data-composition-id="main" data-width="1080" data-height="1920" data-start="0" data-duration="1">
  <div class="shade"></div>
  <div class="abs pill"><div>เตรียมรับมือ · ไฟดับ 7 วัน</div></div>
  <div class="abs t t1">WHAT IF</div>
  <div class="abs t t2">ถ้าเกิดสงครามโลก</div>
  <div class="card" style="left:50px"><svg width="440" height="540" viewBox="0 0 440 540">{bag}</svg><div class="lab" style="color:#e0243a">กระเป๋าฉุกเฉิน</div></div>
  <div class="card" style="left:590px"><div class="abs big">72</div><div class="abs sub">ชั่วโมง</div><div class="abs sub" style="top:340px;color:#555;font-size:52px">อย่างน้อย<br>ตามคำแนะนำ ปภ.</div></div>
  <div class="abs vs">+</div>
  <div class="abs band"><div>คุณมีของพอไหม?</div></div>
  <div class="abs brand">เล่าไม่รู้บ้าง...รู้บ้าง</div>
</div>
<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = {{ duration: function () {{ return 1; }}, pause: function () {{}}, seek: function () {{}}, time: function () {{ return 0; }} }};</script>
</body></html>'''
(HERE / "cover" / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html")
