"""สร้างฉากหลังภาพปกจากคอมโพสิชันจริง: cover/bg-fuse.png (ชนวนลุกสู่บัลลังก์) และ cover/bg-break.png (บัลลังก์แตก)

คัดลอก index.html เป็น cover/_bg.html แล้วแทรกสคริปต์ seek + ซ่อนซับ/แบรนด์ จากนั้นถ่ายด้วย Chrome headless
  python tools/make_cover_bg.py
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
SHOTS = {
    # ชื่อไฟล์: (เวลา, CSS ที่ซ่อน)
    "bg-fuse": (3.95, "#caps,#brand,#credit,#stage,#capshade,.card,.illus,#vignette{display:none!important}"),
    "bg-break": (4.75, "#caps,#brand,#credit,#stage,#capshade,.card,.illus,#vignette,#flash{display:none!important}"),
}

html = (ROOT / "index.html").read_text(encoding="utf-8")
(ROOT / "cover").mkdir(exist_ok=True)
for name, (t, hide) in SHOTS.items():
    inject = f"""<style>{hide}</style>
<script>
const __t = {t};
tl.seek(__t); render(__t); ready.then(() => {{ tl.seek(__t); render(__t); }});
</script>
</body>"""
    page = html.replace("</body>", inject, 1)
    tmp = ROOT / f"_{name}.html"
    tmp.write_text(page, encoding="utf-8")
    out = ROOT / "cover" / f"{name}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    "--force-device-scale-factor=1", "--window-size=1080,1920", "--virtual-time-budget=15000",
                    f"--screenshot={out}", tmp.as_uri()], check=True, capture_output=True)
    tmp.unlink()
    print(name, out.stat().st_size)
