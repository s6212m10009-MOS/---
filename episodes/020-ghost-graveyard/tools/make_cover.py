"""สร้างปก 9:16 และ 16:9 -> cover/*.html แล้วถ่ายเป็น png/jpg ด้วย Chrome headless"""
import subprocess
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
(ROOT / "cover").mkdir(exist_ok=True)

DEFS = """<defs>
<radialGradient id="moonGlow"><stop offset="0" stop-color="#dfe9ff" stop-opacity=".9"/><stop offset=".4" stop-color="#9db4d8" stop-opacity=".3"/><stop offset="1" stop-color="#9db4d8" stop-opacity="0"/></radialGradient>
<radialGradient id="redGlow"><stop offset="0" stop-color="#ff6a50" stop-opacity=".75"/><stop offset="1" stop-color="#e03a2e" stop-opacity="0"/></radialGradient>
<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#141824"/><stop offset="1" stop-color="#05060b"/></linearGradient>
<g id="manUp"><circle cx="0" cy="-282" r="26"/><path d="M-26 -250 Q-34 -150 -24 -118 H24 Q34 -150 26 -250Z"/><path d="M-24 -122 L-30 0 H-6 L0 -96 L6 0 H30 L24 -122Z"/><path d="M-26 -246 L-52 -150 L-38 -144 L-20 -210Z"/><path d="M26 -246 L64 -340 L78 -332 L36 -206Z"/></g>
<g id="stone"><path d="M-46 0 V-96 Q-46 -150 0 -150 Q46 -150 46 -96 V0Z"/><path d="M-20 -110 H20 M0 -128 V-84" stroke="#0a0c14" stroke-width="5" fill="none"/></g>
<g id="flagobj"><rect x="-7" y="-380" width="14" height="380" fill="#4a3320" stroke="#1b120a" stroke-width="3"/><path d="M7 -374 Q80 -394 150 -366 Q210 -344 270 -372 L270 -250 Q210 -224 150 -246 Q80 -274 7 -254Z" fill="#d8332a" stroke="#6b0f0a" stroke-width="3"/></g>
<g id="oldface"><path d="M-70 -80 Q-110 60 -90 220 Q-60 150 -50 40Z M70 -80 Q110 60 90 220 Q60 150 50 40Z M-50 -130 Q0 -170 50 -130 Q90 -60 70 40 Q60 -150 0 -150 Q-60 -150 -70 40 Q-90 -60 -50 -130Z" fill="#05060a"/>
<ellipse cx="0" cy="-30" rx="58" ry="84" fill="#d6dedd"/><ellipse cx="-24" cy="-44" rx="14" ry="22" fill="#05060a"/><ellipse cx="24" cy="-44" rx="14" ry="22" fill="#05060a"/><circle cx="-24" cy="-48" r="4" fill="#cfe6e8"/><circle cx="24" cy="-48" r="4" fill="#cfe6e8"/>
<path d="M-34 -16 Q-30 -4 -24 -10 M34 -16 Q30 -4 24 -10 M-14 -76 Q0 -86 14 -76 M-16 20 Q0 28 16 20" stroke="#7a8688" stroke-width="3" fill="none"/><ellipse cx="0" cy="34" rx="12" ry="5" fill="#05060a"/></g>
</defs>"""

FONTS = """@font-face{font-family:Chonburi;src:url('../fonts/Chonburi-Regular.ttf')}
@font-face{font-family:Anuphan;src:url('../fonts/Anuphan.ttf');font-weight:100 900}
*{box-sizing:border-box}
.red{background:linear-gradient(180deg,#ffb0a0 0%,#ff5a45 40%,#c02418 80%,#6b0f0a 100%);-webkit-background-clip:text;background-clip:text;color:transparent;font-family:Chonburi,serif;white-space:nowrap}"""

V = """<!doctype html><html lang="th"><head><meta charset="utf-8"><title>ป่าช้า · ปก 9:16</title><style>
%FONTS%
html,body{margin:0;width:1080px;height:1920px;overflow:hidden;background:#04050a}
#t{position:relative;width:1080px;height:1920px;overflow:hidden;font-family:Anuphan,sans-serif;background:radial-gradient(ellipse 1000px 1300px at 50% 40%,#1b2238 0%,#0a0d18 55%,#04050a 100%)}
svg{position:absolute;left:0;top:0;width:1080px;height:1920px}
#fade{position:absolute;inset:0;background:linear-gradient(180deg,#04050a 0%,rgba(4,5,10,.8) 16%,rgba(4,5,10,0) 34%,rgba(4,5,10,0) 74%,rgba(4,5,10,.9) 92%,#04050a 100%)}
#brand{position:absolute;left:0;top:100px;width:1080px;display:flex;justify-content:center;align-items:center;gap:16px;font-size:40px;font-weight:600;color:#9db4d8;text-shadow:0 2px 6px #000}
#brand img{width:72px;height:72px;border-radius:50%}
#title{position:absolute;left:0;top:200px;width:1080px;text-align:center}
.pill{display:inline-block;font-size:50px;font-weight:700;color:#fff;background:#c02418;border-radius:14px;padding:6px 30px;box-shadow:0 0 40px rgba(224,58,46,.55)}
.l1{font-size:260px;line-height:1.15;margin-top:8px;filter:drop-shadow(0 8px 0 #04050a) drop-shadow(0 0 44px rgba(224,58,46,.6))}
.l2{font-family:Chonburi,serif;font-size:80px;line-height:1.3;color:#e8e6dc;white-space:nowrap;filter:drop-shadow(0 6px 0 #04050a) drop-shadow(0 0 22px rgba(4,5,10,.95))}
#chip{position:absolute;left:0;top:1660px;width:1080px;text-align:center}
#chip span{display:inline-block;font-size:50px;font-weight:700;color:#04050a;background:#e8e6dc;border-radius:999px;padding:10px 44px;box-shadow:0 0 40px rgba(232,230,220,.3)}
#chip2{position:absolute;left:0;top:1768px;width:1080px;text-align:center;font-size:38px;font-weight:700;color:#98a2b8;text-shadow:0 2px 8px #000}
#note{position:absolute;left:0;bottom:30px;width:1080px;text-align:center;font-size:24px;color:rgba(232,230,220,.5)}
</style></head><body><div id="t">
<svg viewBox="0 0 1080 1920">%DEFS%
<circle cx="800" cy="760" r="460" fill="url(#moonGlow)"/><circle cx="800" cy="760" r="150" fill="#e8efff"/>
<g opacity=".22" transform="translate(300 1000) scale(2.6)"><use href="#oldface"/></g>
<circle cx="540" cy="1250" r="300" fill="url(#redGlow)"/>
<path d="M0 1450 Q540 1380 1080 1450 V1920 H0Z" fill="url(#ground)"/>
<g fill="#0d1020" stroke="#2a3250" stroke-width="3"><use href="#stone" transform="translate(110 1480) scale(1.1) rotate(-6)"/><use href="#stone" transform="translate(960 1470) scale(1.2) rotate(5)"/><use href="#stone" transform="translate(250 1420) scale(.7)"/><use href="#stone" transform="translate(850 1410) scale(.7)"/></g>
<g transform="translate(560 1560)"><use href="#flagobj" transform="scale(1.6)"/></g>
<use href="#manUp" transform="translate(380 1640) scale(1.8)" fill="#0a0c14" stroke="#6f8fc0" stroke-width="4"/></svg>
<div id="fade"></div>
<div id="brand"><img src="../assets/logo-name.jpg" alt="">เล่าไม่รู้บ้าง...รู้บ้าง</div>
<div id="title"><div class="pill">ห้ามเข้าหลัง 6 โมงเย็น</div><div class="l1 red">ป่าช้า</div><div class="l2">เขาปักธงบน<span style="color:#ff6a50">หัวผี</span></div></div>
<div id="chip"><span>เรื่องเล่าผีไทย · 3 นาที</span></div>
<div id="chip2">ดูจบแล้ว…อย่าเข้าไปคนเดียว</div>
<div id="note">เรื่องเล่าแต่งขึ้น · ภาพจำลองประกอบเรื่อง</div>
</div></body></html>"""

L = """<!doctype html><html lang="th"><head><meta charset="utf-8"><title>ป่าช้า · ปก 16:9</title><style>
%FONTS%
html,body{margin:0;width:1280px;height:720px;overflow:hidden;background:#04050a}
#t{position:relative;width:1280px;height:720px;overflow:hidden;font-family:Anuphan,sans-serif;background:radial-gradient(ellipse 900px 600px at 70% 45%,#1b2238 0%,#04050a 75%)}
svg{position:absolute;left:0;top:0;width:1280px;height:720px}
#brand{position:absolute;left:60px;top:34px;display:flex;align-items:center;gap:12px;font-size:30px;font-weight:600;color:#9db4d8;text-shadow:0 2px 6px #000}
#brand img{width:56px;height:56px;border-radius:50%}
#title{position:absolute;left:60px;top:110px;width:700px}
.pill{display:inline-block;font-size:38px;font-weight:700;color:#fff;background:#c02418;border-radius:12px;padding:4px 24px}
.l1{font-size:210px;line-height:1.15;filter:drop-shadow(0 7px 0 #04050a) drop-shadow(0 0 36px rgba(224,58,46,.55))}
.l2{font-family:Chonburi,serif;font-size:60px;line-height:1.3;color:#e8e6dc;white-space:nowrap;filter:drop-shadow(0 5px 0 #04050a)}
#chip{position:absolute;left:60px;bottom:44px}
#chip span{display:inline-block;font-size:34px;font-weight:700;color:#04050a;background:#e8e6dc;border-radius:999px;padding:6px 32px}
#note{position:absolute;right:20px;top:14px;font-size:18px;color:rgba(232,230,220,.5)}
</style></head><body><div id="t">
<svg viewBox="0 0 1280 720">%DEFS%
<circle cx="1020" cy="200" r="260" fill="url(#moonGlow)"/><circle cx="1020" cy="200" r="80" fill="#e8efff"/>
<g opacity=".25" transform="translate(900 360) scale(1.7)"><use href="#oldface"/></g>
<circle cx="900" cy="520" r="230" fill="url(#redGlow)"/>
<path d="M600 640 Q940 600 1280 640 V720 H600Z" fill="url(#ground)"/>
<g fill="#0d1020" stroke="#2a3250" stroke-width="3"><use href="#stone" transform="translate(700 660) scale(.7)"/><use href="#stone" transform="translate(1230 655) scale(.8)"/></g>
<g transform="translate(980 690)"><use href="#flagobj" transform="scale(1.1)"/></g>
<use href="#manUp" transform="translate(820 700) scale(1.3)" fill="#0a0c14" stroke="#6f8fc0" stroke-width="3"/></svg>
<div id="brand"><img src="../assets/logo-name.jpg" alt="">เล่าไม่รู้บ้าง...รู้บ้าง</div>
<div id="title"><div class="pill">ห้ามเข้าหลัง 6 โมงเย็น</div><div class="l1 red">ป่าช้า</div><div class="l2">เขาปักธงบน<span style="color:#ff6a50">หัวผี</span></div></div>
<div id="chip"><span>เรื่องเล่าผีไทย · 3 นาที</span></div>
<div id="note">เรื่องเล่าแต่งขึ้น · ภาพจำลองประกอบเรื่อง</div>
</div></body></html>"""

for name, html, size in [("916", V, (1080, 1920)), ("169", L, (1280, 720))]:
    html = html.replace("%FONTS%", FONTS).replace("%DEFS%", DEFS)
    h = ROOT / "cover" / f"cover-{name}.html"
    h.write_text(html, encoding="utf-8")
    png = ROOT / "cover" / f"graveyard-cover-{name}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    "--force-device-scale-factor=1", f"--window-size={size[0]},{size[1]}", "--virtual-time-budget=8000",
                    f"--screenshot={png}", h.as_uri()], check=True, capture_output=True)
    Image.open(png).convert("RGB").save(png.with_suffix(".jpg"), quality=92)
    print(name, Image.open(png).size)
