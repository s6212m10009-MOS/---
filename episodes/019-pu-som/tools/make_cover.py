"""สร้างปก 9:16 และ 16:9 -> cover/*.html แล้วถ่ายเป็น png/jpg ด้วย Chrome headless"""
import subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

DEFS = """<defs>
<radialGradient id="goldGlow"><stop offset="0" stop-color="#FFE08A" stop-opacity=".95"/><stop offset=".5" stop-color="#E8A83A" stop-opacity=".4"/><stop offset="1" stop-color="#E8A83A" stop-opacity="0"/></radialGradient>
<radialGradient id="spiritGlow"><stop offset="0" stop-color="#9FE6F2" stop-opacity=".6"/><stop offset="1" stop-color="#9FE6F2" stop-opacity="0"/></radialGradient>
<linearGradient id="robe" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F3F7FA"/><stop offset=".7" stop-color="#C9DCE6" stop-opacity=".85"/><stop offset="1" stop-color="#9FE6F2" stop-opacity="0"/></linearGradient>
<g id="gBody"><path d="M-64 0 Q-76 -120 -42 -192 L42 -192 Q76 -120 64 0 Q42 -16 22 0 Q0 -18 -22 0 Q-42 -16 -64 0Z" fill="url(#robe)"/>
<path d="M-42 -186 Q-92 -140 -86 -70 Q-70 -92 -50 -100Z M42 -186 Q92 -140 86 -70 Q70 -92 50 -100Z" fill="#E4EEF4" opacity=".9"/></g>
<g id="gHead"><circle cx="0" cy="-218" r="38" fill="#E9EEF2"/>
<path d="M-38 -228 Q-52 -274 -12 -266 Q0 -282 14 -266 Q52 -274 38 -228 Q22 -252 0 -246 Q-22 -252 -38 -228Z" fill="#fff"/>
<path d="M-22 -196 Q0 -138 22 -196 Q0 -180 -22 -196Z" fill="#fff"/>
<ellipse cx="-14" cy="-220" rx="7" ry="9" fill="#0A0806"/><ellipse cx="14" cy="-220" rx="7" ry="9" fill="#0A0806"/>
<circle cx="-14" cy="-221" r="3" fill="#9FE6F2"/><circle cx="14" cy="-221" r="3" fill="#9FE6F2"/>
<path d="M-8 -203 Q0 -198 8 -203" stroke="#0A0806" stroke-width="3" fill="none" stroke-linecap="round"/></g>
<g id="jar"><ellipse cx="0" cy="-50" rx="130" ry="100" fill="url(#goldGlow)"/>
<path d="M-34 -118 Q-34 -134 -22 -134 H22 Q34 -134 34 -118 L40 -100 Q96 -72 84 -28 Q74 0 0 0 Q-74 0 -84 -28 Q-96 -72 -40 -100Z" fill="#8b5a2b" stroke="#2a170a" stroke-width="5"/>
<path d="M-60 -70 Q0 -52 60 -70" stroke="#D9A53A" stroke-width="7" fill="none"/>
<circle cx="-22" cy="-142" r="13" fill="#FFD45A"/><circle cx="8" cy="-148" r="15" fill="#F0B456"/><circle cx="34" cy="-140" r="12" fill="#FFD45A"/></g>
</defs>"""

FONTS = """@font-face{font-family:Chonburi;src:url('../fonts/Chonburi-Regular.ttf')}
@font-face{font-family:Anuphan;src:url('../fonts/Anuphan.ttf');font-weight:100 900}
*{box-sizing:border-box}
.gold{background:linear-gradient(180deg,#FFF6C0 0%,#FFD45A 35%,#E0A93A 70%,#8A5A12 100%);-webkit-background-clip:text;background-clip:text;color:transparent;font-family:Chonburi,serif;white-space:nowrap}"""

V = """<!doctype html><html lang="th"><head><meta charset="utf-8"><title>ปู่โสมเฝ้าทรัพย์ · ปก 9:16</title><style>
%FONTS%
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:#0A0806}
#t{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Anuphan,sans-serif;background:radial-gradient(ellipse 900px 1100px at 50% 55%,#1d1a2c 0%,#0A0806 72%)}
svg{position:absolute;left:0;top:0;width:1080px;height:1920px}
#fade{position:absolute;inset:0;background:linear-gradient(180deg,#0A0806 0%,rgba(10,8,6,.85) 20%,rgba(10,8,6,0) 38%,rgba(10,8,6,0) 72%,rgba(10,8,6,.85) 92%,#0A0806 100%)}
#brand{position:absolute;left:0;top:110px;width:1080px;display:flex;justify-content:center;align-items:center;gap:16px;font-size:40px;font-weight:600;color:#D9A53A;text-shadow:0 2px 6px #000}
#brand img{width:72px;height:72px}
#title{position:absolute;left:0;top:210px;width:1080px;text-align:center}
.pill{display:inline-block;font-size:52px;font-weight:700;color:#fff;background:#C8342A;border-radius:14px;padding:6px 30px;box-shadow:0 0 40px rgba(200,52,42,.5)}
.l1{font-size:210px;line-height:1.2;margin-top:6px;filter:drop-shadow(0 8px 0 #0A0806) drop-shadow(0 0 40px rgba(255,190,60,.6))}
.l2{font-family:Chonburi,serif;font-size:84px;line-height:1.3;color:#FFF6E0;white-space:nowrap;filter:drop-shadow(0 6px 0 #0A0806) drop-shadow(0 0 22px rgba(10,8,6,.95))}
.l2 b{color:#9FE6F2;font-weight:400}
#chip{position:absolute;left:0;top:1650px;width:1080px;text-align:center}
#chip span{display:inline-block;font-size:50px;font-weight:700;color:#0A0806;background:#FFD45A;border-radius:999px;padding:10px 44px;box-shadow:0 0 40px rgba(255,212,90,.4)}
#chip2{position:absolute;left:0;top:1760px;width:1080px;text-align:center;font-size:40px;font-weight:700;color:#F2E6C9;text-shadow:0 2px 8px #000}
#masc{position:absolute;right:30px;top:1170px;width:230px;filter:drop-shadow(0 10px 20px rgba(0,0,0,.8))}
#note{position:absolute;left:0;bottom:36px;width:1080px;text-align:center;font-size:24px;color:rgba(242,230,201,.55)}
</style></head><body><div id="t">
<svg viewBox="0 0 1080 1920">%DEFS%
<ellipse cx="540" cy="1150" rx="520" ry="560" fill="url(#spiritGlow)"/>
<g transform="translate(540,1400) scale(2.5)"><use href="#gBody"/><use href="#gHead"/></g>
<g transform="translate(540,1625) scale(1.3)"><use href="#jar"/></g></svg>
<div id="fade"></div>
<div id="brand"><img src="../assets/watermark.png" alt="">เล่าไม่รู้บ้าง...รู้บ้าง</div>
<div id="title"><div class="pill">ขุดแล้วเป็นบ้า · ร้านทองเจ๊ง?</div><div class="l1 gold">ปู่โสม</div><div class="l2"><b>ผีเฝ้าทรัพย์</b> มีจริงไหม?</div></div>
<div id="chip"><span>กรุวัดราชบูรณะ · พ.ศ. 2500</span></div>
<div id="chip2">ผีจริง หรือแค่เรื่องเล่า?</div>
<img id="masc" src="../assets/mascot.png" alt="">
<div id="note">ภาพจำลอง ไม่ใช่ภาพบุคคลหรือโบราณวัตถุจริง</div>
</div></body></html>"""

L = """<!doctype html><html lang="th"><head><meta charset="utf-8"><title>ปู่โสมเฝ้าทรัพย์ · ปก 16:9</title><style>
%FONTS%
html,body{margin:0;width:1280px;height:720px;overflow:hidden;background:#0A0806}
#t{position:relative;width:1280px;height:720px;overflow:hidden;font-family:Anuphan,sans-serif;background:radial-gradient(ellipse 900px 600px at 72% 50%,#1d1a2c 0%,#0A0806 75%)}
svg{position:absolute;left:0;top:0;width:1280px;height:720px}
#brand{position:absolute;left:60px;top:36px;display:flex;align-items:center;gap:12px;font-size:30px;font-weight:600;color:#D9A53A;text-shadow:0 2px 6px #000}
#brand img{width:56px;height:56px}
#title{position:absolute;left:60px;top:110px;width:700px}
.pill{display:inline-block;font-size:40px;font-weight:700;color:#fff;background:#C8342A;border-radius:12px;padding:4px 24px}
.l1{font-size:200px;line-height:1.15;filter:drop-shadow(0 7px 0 #0A0806) drop-shadow(0 0 36px rgba(255,190,60,.55))}
.l2{font-family:Chonburi,serif;font-size:64px;line-height:1.3;color:#FFF6E0;white-space:nowrap;filter:drop-shadow(0 5px 0 #0A0806)}
.l2 b{color:#9FE6F2;font-weight:400}
#chip{position:absolute;left:60px;bottom:44px}
#chip span{display:inline-block;font-size:36px;font-weight:700;color:#0A0806;background:#FFD45A;border-radius:999px;padding:6px 32px}
#masc{position:absolute;right:30px;bottom:10px;width:170px;filter:drop-shadow(0 10px 20px rgba(0,0,0,.8))}
#note{position:absolute;right:20px;top:14px;font-size:18px;color:rgba(242,230,201,.55)}
</style></head><body><div id="t">
<svg viewBox="0 0 1280 720">%DEFS%
<ellipse cx="930" cy="330" rx="330" ry="360" fill="url(#spiritGlow)"/>
<g transform="translate(930,620) scale(1.95)"><use href="#gBody"/><use href="#gHead"/></g>
<g transform="translate(800,700) scale(.9)"><use href="#jar"/></g></svg>
<div id="brand"><img src="../assets/watermark.png" alt="">เล่าไม่รู้บ้าง...รู้บ้าง</div>
<div id="title"><div class="pill">ขุดแล้วเป็นบ้า · ร้านทองเจ๊ง?</div><div class="l1 gold">ปู่โสม</div><div class="l2"><b>ผีเฝ้าทรัพย์</b> มีจริงไหม?</div></div>
<div id="chip"><span>กรุวัดราชบูรณะ · พ.ศ. 2500</span></div>
<img id="masc" src="../assets/mascot.png" alt="">
<div id="note">ภาพจำลอง ไม่ใช่ภาพบุคคลหรือโบราณวัตถุจริง</div>
</div></body></html>"""

for name, html, size in [("916", V, (1080, 1920)), ("169", L, (1280, 720))]:
    html = html.replace("%FONTS%", FONTS).replace("%DEFS%", DEFS)
    h = ROOT / "cover" / f"cover-{name}.html"
    h.write_text(html, encoding="utf-8")
    png = ROOT / "cover" / f"pu-som-cover-{name}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    "--force-device-scale-factor=1", f"--window-size={size[0]},{size[1]}", "--virtual-time-budget=8000",
                    f"--screenshot={png}", h.as_uri()], check=True, capture_output=True)
    Image.open(png).convert("RGB").save(png.with_suffix(".jpg"), quality=92)
    print(name, Image.open(png).size)
