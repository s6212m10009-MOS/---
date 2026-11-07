"""timing.json -> data.js ให้ index.html อ่านแบบ synchronous"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
timing = json.loads((ROOT / "timing.json").read_text(encoding="utf-8"))
(ROOT / "data.js").write_text("window.DATA=" + json.dumps({"timing": timing}, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
print("data.js written", timing["total"])
