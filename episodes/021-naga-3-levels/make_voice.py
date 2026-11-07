"""พากย์บทใน script.md (ส่วนเสียงพากย์ทั้งเรื่อง) ด้วย Edge TTS ทีละบรรทัด
ผลลัพธ์: video/audio/line-NN.mp3, video/audio/vo.wav, video/timing.json (เวลาเริ่ม/จบของแต่ละบรรทัด)
  python make_voice.py [--voice th-TH-PremwadeeNeural] [--rate +0%]
"""
import argparse, asyncio, json, subprocess
from pathlib import Path
import edge_tts

HERE = Path(__file__).resolve().parent
AUD = HERE / "video" / "audio"
GAP = 0.3     # เว้นระหว่างบรรทัด
LEAD = 0.25   # เงียบก่อนบรรทัดแรก
TAIL = 1.6    # ค้างท้ายคลิป


def lines():
    body = (HERE / "script.md").read_text(encoding="utf-8").split("## เสียงพากย์ทั้งเรื่อง", 1)[1].split("## ช่องโหว่", 1)[0]
    return [l[2:].strip() for l in body.splitlines() if l.startswith("> ")]


def dur(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(p)], capture_output=True, text=True, check=True).stdout
    return float(json.loads(o)["format"]["duration"])


async def main(voice, rate):
    AUD.mkdir(parents=True, exist_ok=True)
    ls = lines()
    t, timing = LEAD, []
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for i, text in enumerate(ls, 1):
        p = AUD / f"line-{i:02d}.mp3"
        await edge_tts.Communicate(text, voice, rate=rate).save(str(p))
        d = dur(p)
        timing.append({"n": i, "text": text, "start": round(t, 3), "end": round(t + d, 3)})
        cmd += ["-i", str(p)]
        t += d + GAP
    total = round(timing[-1]["end"] + TAIL, 2)
    parts = []
    for i, e in enumerate(timing):
        ms = int(e["start"] * 1000)
        parts.append(f"[{i}:a]aresample=48000,adelay={ms}|{ms}[a{i}]")
    mix = "".join(f"[a{i}]" for i in range(len(ls)))
    parts.append(f"{mix}amix=inputs={len(ls)}:normalize=0,apad=whole_dur={total}[o]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[o]", "-ac", "1", str(AUD / "vo.wav")]
    subprocess.run(cmd, check=True)
    (HERE / "video" / "timing.json").write_text(json.dumps({"total": total, "lines": timing}, ensure_ascii=False, indent=1), encoding="utf-8")
    for e in timing:
        print(f"{e['n']}: {e['start']:6.2f}-{e['end']:6.2f}  {e['text'][:40]}")
    print("total", total)


ap = argparse.ArgumentParser()
ap.add_argument("--voice", default="th-TH-PremwadeeNeural")
ap.add_argument("--rate", default="+0%")
a = ap.parse_args()
asyncio.run(main(a.voice, a.rate))
