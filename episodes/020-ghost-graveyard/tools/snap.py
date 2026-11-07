"""ถ่ายเฟรมตัวอย่างจาก index.html ที่เวลาที่กำหนด แล้วรวมเป็น review/contact.jpg (ตรวจงานก่อนเรนเดอร์)

  python tools/snap.py 0.5 3 7.2 ...
"""

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUT = ROOT / "review" / "snap"
OUT.mkdir(parents=True, exist_ok=True)
html = (ROOT / "index.html").read_text(encoding="utf-8")


def shot(t):
    inject = f"<script>tl.seek({t}); render({t}); ready.then(() => {{ tl.seek({t}); render({t}); }});</script>\n</body>"
    tmp = ROOT / f"_snap_{t}.html"
    tmp.write_text(html.replace("</body>", inject, 1), encoding="utf-8")
    png = OUT / f"{t:07.2f}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    "--force-device-scale-factor=1", "--window-size=1080,1920", "--virtual-time-budget=15000",
                    f"--screenshot={png}", tmp.as_uri()], check=True, capture_output=True)
    tmp.unlink()
    return t, png


times = [float(a) for a in sys.argv[1:]]
with ThreadPoolExecutor(6) as pool:
    shots = list(pool.map(shot, times))
cols, w, h = 6, 270, 480
rows = (len(shots) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * (h + 26)), "#111")
d = ImageDraw.Draw(sheet)
for i, (t, png) in enumerate(shots):
    x, y = (i % cols) * w, (i // cols) * (h + 26)
    sheet.paste(Image.open(png).convert("RGB").resize((w, h)), (x, y + 26))
    d.text((x + 6, y + 6), f"{t:.2f}s", fill="#FFD45A")
sheet.save(ROOT / "review" / "contact.jpg", quality=85)
print("ok", len(shots))
