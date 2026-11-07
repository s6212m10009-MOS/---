import json, sys, urllib.request, numpy as np, rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
from PIL import Image
LON, LAT, H = 141.0328, 37.4211, 0.27   # ~±30 km
API="https://planetarycomputer.microsoft.com/api/stac/v1"
def post(url, body):
    r=urllib.request.Request(url,json.dumps(body).encode(),{"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(r,timeout=60))
def get(url): return json.load(urllib.request.urlopen(url,timeout=60))
def search(dt, plats=None, lt=15):
    b={"collections":["landsat-c2-l2"],"bbox":[LON-.02,LAT-.02,LON+.02,LAT+.02],"datetime":dt,"limit":200,
       "query":{"eo:cloud_cover":{"lt":lt}}}
    fs=post(API+"/search",b)["features"]
    if plats: fs=[f for f in fs if f["properties"]["platform"] in plats]
    return sorted(fs,key=lambda f:f["properties"]["eo:cloud_cover"])
def crop(item, out):
    tok=get("https://planetarycomputer.microsoft.com/api/sas/v1/token/landsat-c2-l2")["token"]
    p=item["properties"]; l8 = p["platform"] in ("landsat-8","landsat-9")
    bands=["red","green","blue"]; arr=[]
    for b in bands:
        with rasterio.open(item["assets"][b]["href"]+"?"+tok) as ds:
            bb=transform_bounds("EPSG:4326",ds.crs,LON-H*1.25,LAT-H,LON+H*1.25,LAT+H)
            w=from_bounds(*bb,transform=ds.transform)
            arr.append(ds.read(1,window=w).astype("float32"))
    n=min(a.shape[0] for a in arr); m=min(a.shape[1] for a in arr)
    arr=np.stack([a[:n,:m] for a in arr],-1)
    valid=arr>0
    refl=arr*0.0000275-0.2          # L2 scale factors
    refl=np.clip(refl,0,1)
    hi=0.32; img=np.clip(refl/hi,0,1)**(1/1.6)
    img[~valid]=0
    Image.fromarray((img*255).astype("uint8")).save(out)
    print(out,arr.shape,"zero-frac %.3f"%(1-valid.mean()))
if __name__=="__main__":
    if sys.argv[1]=="search":
        for f in search(sys.argv[2],{"landsat-8","landsat-9"})[:8]:
            p=f["properties"]; print(f["id"],p["datetime"][:10],p["platform"],p["eo:cloud_cover"])
    else:
        for iid,col in [a.split(":") for a in sys.argv[2:]]:
            it=get(f"{API}/collections/landsat-c2-l2/items/{iid}"); crop(it,f"imagery/{col}.png")
