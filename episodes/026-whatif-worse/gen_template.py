"""สร้าง template.html ของ 026 จากส่วนหัวของ 025 (CSS/โครง/ซับ) + template_tail.js (ไทม์ไลน์ของตอนนี้)"""
from pathlib import Path
HERE = Path(__file__).resolve().parent
src = (HERE.parent / "025-whatif-world-war" / "template.html").read_text(encoding="utf-8")
head = src[:src.index("      // ---------- timeline ----------")]
head = head.replace("#hook .h2 { font-size: 112px; color: #fff; }", "#hook .h2 { font-size: 92px; color: #fff; white-space: nowrap; }")
head = head.replace("%%DOTS%%\n", "%%DOTS%%\n%%GDOTS%%\n")
head = head.replace("ลองนับดูว่าคุณมีกี่อย่าง", "นับดูว่าคุณเตรียมไว้กี่วัน")
head = head.replace('      <div id="big72">72<small> ชม.</small></div>\n', "")
head = head.replace("background: #02060f; opacity: 0.25;", "background: #02060f; opacity: 0.5;")
# ฮุกใหม่ของ 026: ปฏิทินนับวัน (ไม่ใช้ WHAT IF + จุดแดงแบบ 025)
head = head.replace('<div class="h1">WHAT IF</div>', '<div class="h1">วันที่ 4</div>').replace("ถ้าเกิดสงครามโลก</div></div>", "ไฟยังไม่กลับมา</div></div>")
CAL_HTML = '      <div id="cal"><div class="cd" id="cd1">1</div><div class="cd" id="cd2">2</div><div class="cd" id="cd3">3</div><div class="cd now" id="cd4">4</div></div>\n      <div id="hook">'
head = head.replace('      <div id="hook">', CAL_HTML)
CAL_CSS = (
    "      #cal { position: absolute; left: 0; top: 960px; width: 1080px; display: flex; justify-content: center; gap: 28px; z-index: 44; }\n"
    "      .cd { opacity: 0; width: 150px; height: 150px; border-radius: 30px; background: #fff; border: 8px solid var(--ink); font-size: 100px; font-weight: 800; line-height: 140px; text-align: center; color: var(--ink); position: relative; box-shadow: 0 10px 0 rgba(0,0,0,.35); }\n"
    "      .cd.done::after { content: '\\2715'; position: absolute; inset: 0; color: var(--red); font-size: 150px; line-height: 140px; }\n"
    "      .cd.now { background: var(--yellow); color: var(--red); }\n"
    "      #flash {"
)
head = head.replace("      #flash {", CAL_CSS, 1)
(HERE / "template.html").write_text(head + (HERE / "template_tail.js").read_text(encoding="utf-8"), encoding="utf-8")
print("ok", "id=\"cal\"" in head)
