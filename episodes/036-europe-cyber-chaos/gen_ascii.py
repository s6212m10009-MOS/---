"""สร้างแผนที่โลกแบบตัวอักษร (ASCII/CRT สีอำพัน) จาก video/world-line.txt -> video/ascii_map.html + video/ascii_marks.json
ตัวเลข 0/1 = แผ่นดิน, # = ชายฝั่ง   python gen_ascii.py"""
import json, re
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np

HERE = Path(__file__).resolve().parent
V = HERE / "video"
COLS, ROWS = 96, 41
LON0, LON1, LAT0, LAT1 = -12, 150, -40, 72
X0, X1, Y0, Y1 = (LON0 + 180) * 10, (LON1 + 180) * 10, (90 - LAT1) * 10, (90 - LAT0) * 10
SS = 6  # supersample
W, H = COLS * SS, ROWS * SS
sx, sy = W / (X1 - X0), H / (Y1 - Y0)

path = (V / "world-line.txt").read_text()
fill = Image.new("L", (W, H), 0)
edge = Image.new("L", (W, H), 0)
df, de = ImageDraw.Draw(fill), ImageDraw.Draw(edge)
for sub in re.split(r"(?=M)", path):
    pts = [(float(a), float(b)) for a, b in re.findall(r"(-?\d+\.?\d*)[ ,](-?\d+\.?\d*)", sub)]
    pts = [((x - X0) * sx, (y - Y0) * sy) for x, y in pts]
    if len(pts) < 3:
        continue
    if max(abs(p[0] - q[0]) for p, q in zip(pts, pts[1:])) > W * 0.5:
        continue  # เส้นข้ามขอบแผนที่
    df.polygon(pts, fill=255)
    de.line(pts, fill=255, width=2)
fa, ea = np.asarray(fill, dtype=float) / 255, np.asarray(edge, dtype=float) / 255
fa = fa.reshape(ROWS, SS, COLS, SS).mean(axis=(1, 3))
ea = ea.reshape(ROWS, SS, COLS, SS).mean(axis=(1, 3))
rng = np.random.default_rng(5)
rows = []
for r in range(ROWS):
    out, cur, buf = [], None, ""
    for c in range(COLS):
        if ea[r, c] > 0.18:
            ch, cl = "#", "c"
        elif fa[r, c] > 0.4:
            ch, cl = ("0" if rng.random() < .5 else "1"), "l"
        else:
            ch, cl = (".", "o") if rng.random() < 0.03 else (" ", "o")
        if cl != cur:
            if buf:
                out.append(f'<i class="{cur}">{buf}</i>')
            cur, buf = cl, ""
        buf += ch
    out.append(f'<i class="{cur}">{buf}</i>')
    rows.append("".join(out))
html = "\n".join(f'<div class="ar">{r}</div>' for r in rows)
(V / "ascii_map.html").write_text(html, encoding="utf-8")


def cell(lon, lat):
    return [round(((lon + 180) * 10 - X0) / (X1 - X0) * COLS, 1), round(((90 - lat) * 10 - Y0) / (Y1 - Y0) * ROWS, 1)]


marks = {"FR": cell(2.5, 47.0), "IR": cell(54.0, 32.0), "TH": cell(100.5, 13.75)}
(V / "ascii_marks.json").write_text(json.dumps(marks), encoding="utf-8")
print("ascii map", COLS, "x", ROWS, marks)
