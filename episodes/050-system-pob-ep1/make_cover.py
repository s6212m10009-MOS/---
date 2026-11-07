"""ปก 9:16 ตอน 050: ใช้ฉากย่าปากแดงจากวิดีโอจริง (เวลา 14.2 วิ) ซ่อนซับ/HUD แล้ววางหัวข้อทับ
  python make_cover.py && cd cover && npx hyperframes snapshot --no-end --at 14.2 -o ../snapcover"""
import re, shutil
from pathlib import Path

H = Path(__file__).resolve().parent
V, C = H / "video", H / "cover"
C.mkdir(exist_ok=True)
for d in ("fonts", "three", "assets"):
    shutil.copytree(V / d, C / d, dirs_exist_ok=True)
for f in ("hyperframes.json", "gsap.min.js", "scene.js"):
    shutil.copy(V / f, C / f)

html = (V / "index.html").read_text(encoding="utf-8")
html = re.sub(r'<audio[^>]*></audio>', "", html)
css = """
      .caps, #flash, #clock, .wrap, #follow { display: none !important; }
      .cv { position: absolute; left: 0; width: 1080px; text-align: center; font-weight: 800; line-height: 1.02; white-space: nowrap; z-index: 70;
            -webkit-text-stroke: 26px #0b0407; paint-order: stroke fill; }
      .c0 { top: 110px; font-size: 62px; color: #06181a; -webkit-text-stroke: 0; }
      .c0 span { display: inline-block; background: var(--sys); padding: 6px 42px 14px; border-radius: 16px; }
      .c1 { top: 1240px; font-size: 170px; color: #fff; }
      .c2 { top: 1415px; font-size: 226px; color: #ff4646; }
      .c3 { top: 1660px; font-size: 76px; color: var(--yellow); -webkit-text-stroke-width: 16px; }
      #coverbot { position: absolute; left: 0; top: 1060px; width: 1080px; height: 860px; z-index: 65; background: linear-gradient(180deg, rgba(10,3,6,0), rgba(10,3,6,.86) 34%, rgba(10,3,6,.96)); }
    </style>"""
html = html.replace("    </style>", css, 1)
html = html.replace('<div class="caps" id="caps"></div>',
                    '<div class="caps" id="caps"></div><div id="coverbot"></div>'
                    '<div class="cv c0"><span>ระบบล่าปอบ · EP.1</span></div>'
                    '<div class="cv c1">ย่าผม</div><div class="cv c2">เป็นปอบ?</div><div class="cv c3">เลิกกินหมากมา 10 ปีแล้ว</div>')
(C / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html", len(html))
