"""ประกอบโปรเจกต์ HyperFrames 9:16 ของแต่ละตอนจาก src/ + shared/ + <ตอน>/story.json + <ตอน>/episode.json + <ตอน>/916/timing.json

  python tools/build.py ep1-discovery
"""

import json
import shutil
import sys
from pathlib import Path

SERIES = Path(__file__).resolve().parent.parent

L = {
    "W": 1080, "H": 1920,
    "compass": {"x": 540, "y": 330, "s": 0.8}, "chip": {"x": 540, "y": 470, "size": 30},
    "stage": {"x": 540, "base": 1100}, "board": {"w": 860, "h": 290, "head": 112, "sub": 44},
    "icon": {"size": 240, "gap": 26},
    "light": {"x": 540, "y": 820, "big": 820, "mid": 600, "small": 430, "drift": 30},
    "cap": {"left": 70, "top": 1180, "width": 940, "size": 52},
    "masc": {"left": 60, "top": 1440, "h": 360}, "mark": {"left": 56, "top": 150, "size": 84},
    "count": {"left": 60, "top": 250, "size": 34},
    "key": {"x": 540, "y": 820}, "logo": {"top": 990, "size": 62}, "credit": {"top": 1760},
    "threads": {"x": [190, 540, 890], "y": 640, "icon": 180, "w": 330, "h": 92, "font": 28,
                "knot": {"x": 540, "y": 1040, "w": 660, "h": 110}},
}


def layout_css():
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
    ep_dir = SERIES / sys.argv[1]
    ep = json.loads((ep_dir / "episode.json").read_text(encoding="utf-8"))
    out = ep_dir / "916"
    out.mkdir(exist_ok=True)
    for p in (SERIES / "shared").iterdir():
        dst = out / p.name
        if p.is_dir():
            shutil.copytree(p, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(p, dst)
    shutil.copy2(SERIES / "src" / "engine.js", out / "engine.js")

    story = json.loads((ep_dir / "story.json").read_text(encoding="utf-8"))
    timing = json.loads((out / "timing.json").read_text(encoding="utf-8"))
    comp = f"mee-jing-mai-{ep_dir.name}"
    data = {"compId": comp, "layout": L, "story": story, "timing": timing, "ep": ep}
    (out / "data.js").write_text("window.DATA = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")

    kx, ky = L["key"]["x"], L["key"]["y"]
    html = (SERIES / "src" / "index.html").read_text(encoding="utf-8")
    for k, v in {
        "__LAYOUT_CSS__": layout_css(), "__W__": L["W"], "__H__": L["H"], "__DUR__": timing["total"], "__COMP__": comp,
        "__TITLE__": ep["title"], "__CREDIT__": ep["credit"],
        "__LX__": L["light"]["x"], "__LY__": L["light"]["y"], "__KX__": kx, "__KYC__": ky - 40,
        "__KPATH__": f"M{kx - 22} {ky - 12} L{kx - 42} {ky + 96} H{kx + 42} L{kx + 22} {ky - 12}Z",
    }.items():
        html = html.replace(k, str(v))
    (out / "index.html").write_text(html, encoding="utf-8")
    (out / "hyperframes.json").write_text('{"version":1,"authoringSkill":"hyperframes"}', encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({"id": comp, "name": comp, "createdAt": "2026-11-02T10:00:00.000Z"}),
                                   encoding="utf-8")
    print("built", out)


if __name__ == "__main__":
    main()
