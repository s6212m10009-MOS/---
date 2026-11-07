"""ดึงภาพดาวเทียม (Esri World Imagery) มาต่อเป็นแผนที่ 3 ระดับซูม + เส้นพรมแดน (Natural Earth)

พิกัดทั้งหมดใน map/geo.json เป็น "world px" = พิกเซล Web Mercator ที่ซูม 11
ลบด้วยมุมซ้ายบนของชั้น thai (ORIGIN) เพื่อให้ตัวเลขไม่ใหญ่เกินไป

  python -I tools/build_map.py
"""

import io
import json
import math
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "map"
CACHE = OUT / "tiles"
TILE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
BORDERS = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson"
REF_Z = 11

# ชื่อชั้น: (ซูม, ลองจิจูดซ้าย, ละติจูดบน, ลองจิจูดขวา, ละติจูดล่าง)
# ลองจิจูดใช้ระบบ 0–360 (ตะวันตกของเส้นแบ่งวัน +360) ให้มหาสมุทรแปซิฟิกต่อเนื่องกัน
LAYERS = {
    "thai": (8, 96.0, 20.5, 107.0, 9.5),
    "central": (11, 100.2, 14.6, 100.85, 13.6),
    "ayut": (15, 100.535, 14.375, 100.60, 14.340),
    "thon": (17, 100.4830, 13.7480, 100.4960, 13.7380),
}
COUNTRIES = ["Thailand", "Cambodia"]


def px(lon, lat, z):
    n = 256 * 2 ** z
    x = (lon + 180) / 360 * n
    s = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n
    return x, y


def fetch(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return dest.read_bytes()
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "lao-mai-ru-map/1.0"})
            data = urllib.request.urlopen(req, timeout=30).read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            return data
        except Exception as e:  # ลองใหม่สั้น ๆ
            if attempt == 3:
                raise
            time.sleep(1 + attempt)


def build_layer(name, z, lon0, lat0, lon1, lat1):
    x0, y0 = px(lon0, lat0, z)
    x1, y1 = px(lon1, lat1, z)
    tx0, ty0, tx1, ty1 = int(x0 // 256), int(y0 // 256), int(x1 // 256), int(y1 // 256)
    jobs = [(tx, ty) for ty in range(ty0, ty1 + 1) for tx in range(tx0, tx1 + 1)]
    print(f"{name}: z{z} {len(jobs)} tiles", flush=True)

    def get(job):
        tx, ty = job
        wx = tx % (2 ** z)  # ข้ามเส้นแบ่งวัน
        return job, fetch(TILE.format(z=z, x=wx, y=ty), CACHE / f"{z}_{wx}_{ty}.jpg")

    canvas = Image.new("RGB", ((tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256))
    with ThreadPoolExecutor(8) as pool:
        for (tx, ty), data in pool.map(get, jobs):
            canvas.paste(Image.open(io.BytesIO(data)).convert("RGB"), ((tx - tx0) * 256, (ty - ty0) * 256))
    # เกรดสีให้มืดและอิ่มแบบคลิปต้นแบบ
    canvas = ImageEnhance.Color(canvas).enhance(1.15)
    canvas = ImageEnhance.Contrast(canvas).enhance(1.12)
    canvas = ImageEnhance.Brightness(canvas).enhance(0.78)
    canvas.save(OUT / f"{name}.jpg", quality=88, optimize=True)
    gray = ImageEnhance.Brightness(canvas.convert("L").convert("RGB")).enhance(0.9)
    gray.save(OUT / f"{name}-gray.jpg", quality=85, optimize=True)
    k = 2 ** (REF_Z - z)
    return {"x": tx0 * 256 * k, "y": ty0 * 256 * k, "w": canvas.width, "h": canvas.height, "k": k}


def main():
    OUT.mkdir(exist_ok=True)
    layers = {name: build_layer(name, *spec) for name, spec in LAYERS.items()}
    ox, oy = layers["thai"]["x"], layers["thai"]["y"]
    for L in layers.values():
        L["x"] -= ox
        L["y"] -= oy

    raw = fetch(BORDERS, OUT / "ne_50m_admin_0_countries.geojson")
    gj = json.loads(raw)
    borders = {}
    for f in gj["features"]:
        name = f["properties"]["NAME"]
        if name not in COUNTRIES:
            continue
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        rings = []
        for poly in polys:
            ring = poly[0]
            if len(ring) < 8:
                continue
            pts = []
            for lon, lat in ring:
                x, y = px(lon, lat, REF_Z)
                pts.append([round(x - ox, 1), round(y - oy, 1)])
            rings.append(pts)
        borders[name] = rings
        print(name, len(rings), "rings", sum(len(r) for r in rings), "pts")

    geo = {"refZoom": REF_Z, "origin": [ox, oy], "layers": layers, "borders": borders}
    (OUT / "geo.json").write_text(json.dumps(geo, separators=(",", ":")), encoding="utf-8")
    print("ok", {k: (v["w"], v["h"]) for k, v in layers.items()})


if __name__ == "__main__":
    sys.exit(main())
