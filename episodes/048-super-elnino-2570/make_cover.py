"""ปก 9:16 ตอน 048: ใช้ฉากแผนที่ 2.5D จากวิดีโอจริง (เวลา 9.5 วิ: ความร้อนแปซิฟิก + หมุดไทย) ซ่อนซับ/ฮุก แล้ววางหัวข้อทับ
  python make_cover.py && cd cover && npx hyperframes snapshot --at 9.5 -o ../snapcover"""
import re, shutil
from pathlib import Path

H = Path(__file__).resolve().parent
V, C = H / "video", H / "cover"
(C / "fonts").mkdir(parents=True, exist_ok=True)
for f in (V / "fonts").glob("*"):
    shutil.copy(f, C / "fonts" / f.name)
shutil.copy(V / "hyperframes.json", C / "hyperframes.json")

html = (V / "index.html").read_text(encoding="utf-8")
html = re.sub(r'<audio[^>]*></audio>', "", html)
css = """
      .caps, #card, #tagwrap, #big, #stamp, #black, #flash, #hook, #topic { display: none !important; }
      #brand { font-size: 40px; font-weight: 800; -webkit-text-stroke: 10px var(--ink); paint-order: stroke fill; text-shadow: none; }
      .cv { position: absolute; left: 0; width: 1080px; text-align: center; font-weight: 800; line-height: 1.02; white-space: nowrap; z-index: 70;
            -webkit-text-stroke: 26px #050D1F; paint-order: stroke fill; }
      .cvpill { position: absolute; left: 0; top: 980px; width: 1080px; display: flex; justify-content: center; z-index: 70; }
      .cvpill div { background: var(--red); color: #fff; border: 8px solid #fff; border-radius: 999px; padding: 4px 56px 14px; font-size: 92px; font-weight: 800; transform: rotate(-3deg); }
      .c1 { top: 1190px; font-size: 150px; color: #fff; }
      .c2 { top: 1345px; font-size: 210px; color: var(--yellow); }
      .c3 { top: 1560px; font-size: 104px; color: #fff; }
      .c4 { top: 1720px; font-size: 70px; color: #4cc3ff; -webkit-text-stroke-width: 14px; }
      .c0 { top: 190px; font-size: 230px; color: var(--yellow); }
      .c0s { top: 450px; font-size: 64px; color: #fff; -webkit-text-stroke-width: 14px; }
      #coverbot { position: absolute; left: 0; top: 960px; width: 1080px; height: 960px; z-index: 65; background: linear-gradient(180deg, rgba(4,9,21,0), rgba(4,9,21,.85) 35%, rgba(4,9,21,.95)); }
    </style>"""
html = html.replace("    </style>", css, 1)
html = html.replace('<div class="caps" id="caps"></div>',
                    '<div class="caps" id="caps"></div><div id="coverbot"></div><div class="cvpill"><div>WHAT IF?</div></div>'
                    '<div class="cv c0">+1.7°C</div><div class="cv c0s">อุณหภูมิโลกอาจพุ่งทำสถิติ</div><div class="cv c1">ปี 2570</div><div class="cv c2">ร้อนที่สุด</div><div class="cv c3">ในประวัติศาสตร์</div><div class="cv c4">ซูเปอร์เอลนีโญ · ไทยโดนอะไรบ้าง?</div>')
(C / "index.html").write_text(html, encoding="utf-8")
print("cover/index.html", len(html))
