"""ดึงภาพดาวเทียม Esri World Imagery (ซูม 5) แล้วแปลงเป็นพิกัด lon/lat แบบเท่ากันสำหรับแผนที่ของตอน 028
เก็บ tiles ไว้ใน sat_tiles/ (ใช้ซ้ำได้) -> video/assets/sat.jpg + sat.json (ขอบเขต)
ปรับโทนให้มืด/เขียวน้ำเงินแบบตอนยามาชิตะ และสร้างเส้นขอบประเทศเน้น (อิหร่าน/ไทย) -> video/outlines.json
  python -I build_sat.py"""
import io, json, math, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from PIL import Image, ImageEnhance

HERE = Path(__file__).resolve().parent
CACHE = HERE / "sat_tiles"
TILE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
Z = 5
LON0, LON1, LAT0, LAT1 = -5.0, 150.0, -45.0, 75.0   # ซ้าย ขวา ล่าง บน
PPD = 22.8                                         # พิกเซลต่อองศาของภาพผลลัพธ์


def merc(lon, lat, z):
    n = 256 * 2 ** z
    s = math.sin(math.radians(lat))
    return (lon + 180) / 360 * n, (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n


def fetch(x, y):
    dest = CACHE / f"{Z}_{x}_{y}.jpg"
    if dest.exists() and dest.stat().st_size > 0:
        return dest.read_bytes()
    for a in range(4):
        try:
            req = urllib.request.Request(TILE.format(z=Z, x=x, y=y), headers={"User-Agent": "lao-mai-ru-map/1.0"})
            d = urllib.request.urlopen(req, timeout=30).read()
            CACHE.mkdir(exist_ok=True)
            dest.write_bytes(d)
            return d
        except Exception:
            if a == 3:
                raise
            time.sleep(1 + a)


x0, y0 = merc(LON0, LAT1, Z)
x1, y1 = merc(LON1, LAT0, Z)
tx0, tx1, ty0, ty1 = int(x0 // 256), int(x1 // 256), int(y0 // 256), int(y1 // 256)
jobs = [(x, y) for y in range(ty0, ty1 + 1) for x in range(tx0, tx1 + 1)]
print("tiles", len(jobs), flush=True)
with ThreadPoolExecutor(8) as ex:
    data = dict(zip(jobs, ex.map(lambda j: fetch(*j), jobs)))
W, H = (tx1 - tx0 + 1) * 256, (ty1 - ty0 + 1) * 256
mos = Image.new("RGB", (W, H))
for (x, y), d in data.items():
    mos.paste(Image.open(io.BytesIO(d)).convert("RGB"), ((x - tx0) * 256, (y - ty0) * 256))
M = np.asarray(mos)

ow, oh = int((LON1 - LON0) * PPD), int((LAT1 - LAT0) * PPD)
lon = LON0 + (np.arange(ow) + .5) / ow * (LON1 - LON0)
lat = LAT1 - (np.arange(oh) + .5) / oh * (LAT1 - LAT0)
n = 256 * 2 ** Z
px = (lon + 180) / 360 * n - tx0 * 256
s = np.sin(np.radians(lat))
py = (0.5 - np.log((1 + s) / (1 - s)) / (4 * np.pi)) * n - ty0 * 256
xi = np.clip(px.astype(int), 0, W - 1)
yi = np.clip(py.astype(int), 0, H - 1)
out = Image.fromarray(M[yi[:, None], xi[None, :]])
out = ImageEnhance.Color(out).enhance(0.9)
out = ImageEnhance.Brightness(out).enhance(0.78)
out = ImageEnhance.Contrast(out).enhance(1.12)
tint = Image.new("RGB", out.size, (5, 13, 31))
out = Image.blend(out, tint, 0.28)
(HERE / "video" / "assets").mkdir(parents=True, exist_ok=True)
out.save(HERE / "video" / "assets" / "sat.jpg", quality=82)
(HERE / "video" / "sat.json").write_text(json.dumps(dict(lon0=LON0, lon1=LON1, lat0=LAT0, lat1=LAT1, w=ow, h=oh)))
print("sat.jpg", ow, oh)

geo = json.loads((HERE.parent / "007-yamashita-gold" / "map" / "ne_50m_admin_0_countries.geojson").read_text(encoding="utf-8"))
mx = lambda lo: round((lo + 180) * 10, 1)
my = lambda la: round((90 - la) * 10, 1)
res = {}
for f in geo["features"]:
    nm = f["properties"].get("ADMIN") or f["properties"].get("NAME")
    if nm not in ("Iran", "Thailand"):
        continue
    g = f["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    d = ""
    for poly in polys:
        for ring in poly:
            d += "M" + "L".join(f"{mx(a)} {my(b)}" for a, b, *_ in ring[::2]) + "Z"
    res[nm] = d
(HERE / "video" / "outlines.json").write_text(json.dumps(res))
print("outlines", list(res))
