"""สร้าง index.html จาก template.html + audio/durations.json

  python build.py
"""

import json
from pathlib import Path

SRC = Path(__file__).resolve().parent
HERE = SRC.parent
import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--speed", type=float, default=1.0, help="ตัวคูณความเร็วเสียง (ใช้กับ --gemini ต้องมี narration-fast.wav)")
ap.add_argument("--gemini", action="store_true", help="ใช้เวลาจาก gemini/timing.json -> gemini/index.html")
args = ap.parse_args()
if args.gemini:
    HERE = HERE / "gemini"
    tm = json.loads((HERE / "timing.json").read_text(encoding="utf-8"))
    k = args.speed
    durs = [{"start": round(sc["chunks"][0]["t"] / k, 3), "dur": round(sc["voice"] / k, 3), "text": sc["chunks"][0]["text"]} for sc in tm["scenes"]]
    AUDIO = "narration-fast.wav" if k != 1.0 else "narration.wav"
else:
    durs = json.loads((HERE / "audio" / "durations.json").read_text(encoding="utf-8"))
    AUDIO = "audio/narration.mp3"

# บรรทัดแรกของแต่ละฉาก (S1..S10) ตาม script.md
SCENE_FIRST_LINES = [1, 4, 6, 8, 11, 15, 17, 18, 22, 24]

lines = [{"start": d["start"], "text": d["text"]} for d in durs]
last = durs[-1]
total = round(last["start"] + last["dur"] + 1.5, 2)
scenes = [lines[n - 1]["start"] for n in SCENE_FIRST_LINES]

jt = round(lines[16]["start"] + (lines[17]["start"] - lines[16]["start"]) * 0.62, 2)  # กลางบรรทัด 17 (ผีอำ)
data = (
    f"var JT = {jt};\n"
    f"var TOTAL = {total};\n"
    f"var SCENES = {json.dumps(scenes)};\n"
    f"var LINES = {json.dumps(lines, ensure_ascii=False)};\n"
)
html = (SRC / "template.html").read_text(encoding="utf-8").replace("audio/narration.mp3", AUDIO)
html = html.replace("/*__DATA__*/", data).replace("__TOTAL__", str(total)).replace("__JT__", str(jt)).replace("__AUDIO__", str(round(last["start"] + last["dur"], 2)))
(HERE / "index.html").write_text(html, encoding="utf-8")
print(f"index.html: {total}s, {len(scenes)} ฉาก, {len(lines)} บรรทัด")
