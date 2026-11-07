"""ประกอบโปรเจกต์ HyperFrames ของแต่ละขนาดจาก src/ + shared/ + story.json + <variant>/timing.json

  python tools/build.py 916
  python tools/build.py 169
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LAYOUTS = {
    "916": {
        "W": 1080, "H": 1920,
        "compass": {"x": 540, "y": 330, "s": 0.8}, "chip": {"x": 540, "y": 470, "size": 30},
        "stage": {"x": 540, "base": 1100}, "board": {"w": 860, "h": 290, "head": 112, "sub": 44},
        "icon": {"size": 240, "gap": 26},
        "light": {"x": 540, "y": 820, "big": 820, "mid": 600, "small": 430, "drift": 30},
        "cap": {"left": 70, "top": 1180, "width": 940, "size": 52},
        "masc": {"left": 60, "top": 1440, "h": 360}, "mark": {"left": 56, "top": 150, "size": 84},
        "count": {"left": 60, "top": 250, "size": 44},
        "key": {"x": 540, "y": 820}, "logo": {"top": 990, "size": 62}, "credit": {"top": 1760},
        "threads": {"x": [190, 540, 890], "y": 640, "icon": 180, "w": 330, "h": 92, "font": 28,
                    "knot": {"x": 540, "y": 1040, "w": 660, "h": 110}},
    },
    "169": {
        "W": 1920, "H": 1080,
        "compass": {"x": 1600, "y": 290, "s": 0.85}, "chip": {"x": 1600, "y": 470, "size": 28},
        "stage": {"x": 720, "base": 720}, "board": {"w": 880, "h": 270, "head": 106, "sub": 42},
        "icon": {"size": 220, "gap": 22},
        "light": {"x": 720, "y": 450, "big": 900, "mid": 660, "small": 470, "drift": 40},
        "cap": {"left": 300, "top": 790, "width": 1320, "size": 48},
        "masc": {"left": 40, "top": 700, "h": 350}, "mark": {"left": 40, "top": 32, "size": 72},
        "count": {"left": 130, "top": 44, "size": 40},
        "key": {"x": 960, "y": 400}, "logo": {"top": 560, "size": 60}, "credit": {"top": 1020},
        "threads": {"x": [380, 720, 1060], "y": 250, "icon": 160, "w": 310, "h": 84, "font": 28,
                    "knot": {"x": 720, "y": 620, "w": 640, "h": 104}},
    },
}


def layout_css(L):
    c, m, mk = L["compass"], L["masc"], L["mark"]
    mw = m["h"] * 405 / 600
    lamp_x, lamp_y = m["left"] + 330 / 405 * mw - 100, m["top"] + 355 / 600 * m["h"] - 100
    return f"""
#compass{{left:{c['x'] - 200}px;top:{c['y'] - 200}px;transform:scale({c['s']})}}
#chips{{position:absolute;left:0;top:0}}
.chip{{left:{L['chip']['x']}px;top:{L['chip']['y']}px;font-size:{L['chip']['size']}px}}
.cap{{left:{L['cap']['left']}px;top:{L['cap']['top']}px;width:{L['cap']['width']}px;font-size:{L['cap']['size']}px}}
#count{{position:absolute;left:{L['count']['left']}px;top:{L['count']['top']}px}}
.cnt{{font-size:{L['count']['size']}px}}
#masc{{left:{m['left']}px;top:{m['top']}px;width:{mw:.0f}px;height:{m['h']}px}}
#lamp{{left:{lamp_x:.0f}px;top:{lamp_y:.0f}px}}
#mark{{left:{mk['left']}px;top:{mk['top']}px;width:{mk['size']}px;height:{mk['size']}px}}
#logo{{top:{L['logo']['top']}px;font-size:{L['logo']['size']}px}}
#credit{{top:{L['credit']['top']}px}}
"""


def main():
    variant = sys.argv[1]
    L = LAYOUTS[variant]
    out = ROOT / variant
    out.mkdir(exist_ok=True)
    for p in (ROOT / "shared").iterdir():
        dst = out / p.name
        if p.is_dir():
            shutil.copytree(p, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(p, dst)
    shutil.copy2(ROOT / "src" / "engine.js", out / "engine.js")

    story = json.loads((ROOT / "story.json").read_text(encoding="utf-8"))
    timing = json.loads((out / "timing.json").read_text(encoding="utf-8"))
    comp = f"h48-{variant}"
    data = {"compId": comp, "layout": L, "story": story, "timing": timing}
    (out / "data.js").write_text("window.DATA = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")

    kx, ky = L["key"]["x"], L["key"]["y"]
    html = (ROOT / "src" / "index.html").read_text(encoding="utf-8")
    for k, v in {
        "__LAYOUT_CSS__": layout_css(L), "__W__": L["W"], "__H__": L["H"], "__DUR__": timing["total"], "__COMP__": comp,
        "__LX__": L["light"]["x"], "__LY__": L["light"]["y"], "__KX__": kx, "__KYC__": ky - 40,
        "__KPATH__": f"M{kx - 22} {ky - 12} L{kx - 42} {ky + 96} H{kx + 42} L{kx + 22} {ky - 12}Z",
    }.items():
        html = html.replace(k, str(v))
    (out / "index.html").write_text(html, encoding="utf-8")
    (out / "hyperframes.json").write_text('{"version":1,"authoringSkill":"hyperframes"}', encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({"id": comp, "name": comp, "createdAt": "2026-11-01T10:00:00.000Z"}),
                                   encoding="utf-8")
    print("built", out)


if __name__ == "__main__":
    main()
