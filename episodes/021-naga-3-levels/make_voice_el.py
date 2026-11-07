"""พากย์บทใน script.md ด้วย ElevenLabs ทีละบรรทัด (ทดสอบเทียบกับ Edge TTS)
ผลลัพธ์: video/audio_el/line-NN.mp3, video/audio_el/vo.wav, video/timing_el.json
คีย์อ่านจาก ../../.env.local ไม่พิมพ์ออกหน้าจอ
  python make_voice_el.py --voice-id jucSqawHKM1rUNf78oZQ [--only 1 2 3]
"""
import argparse, json, os, subprocess, sys
from pathlib import Path

sys.path.insert(0, "C:/el")
from elevenlabs import ElevenLabs, VoiceSettings  # noqa: E402

HERE = Path(__file__).resolve().parent
AUD = HERE / "video" / "audio_el"
GAP, LEAD, TAIL = 0.3, 0.25, 1.6


def load_env():
    for line in (HERE.parent.parent / ".env.local").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"'))


def lines():
    body = (HERE / "script.md").read_text(encoding="utf-8").split("## เสียงพากย์ทั้งเรื่อง", 1)[1].split("## ช่องโหว่", 1)[0]
    return [l[2:].strip() for l in body.splitlines() if l.startswith("> ")]


def dur(p):
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(p)], capture_output=True, text=True, check=True).stdout
    return float(json.loads(o)["format"]["duration"])


ap = argparse.ArgumentParser()
ap.add_argument("--voice-id", required=True)
ap.add_argument("--model", default="eleven_v4")
ap.add_argument("--only", type=int, nargs="*", help="ทำเฉพาะบรรทัดที่ระบุ (ไม่รวมเป็น vo.wav)")
ap.add_argument("--stability", type=float, default=0.4)
a = ap.parse_args()

load_env()
client = ElevenLabs(api_key=os.environ["ELEVENLABS_API_KEY"])
AUD.mkdir(parents=True, exist_ok=True)
ls = lines()
for i, text in enumerate(ls, 1):
    if a.only and i not in a.only:
        continue
    audio = client.text_to_speech.convert(
        voice_id=a.voice_id, text=text, model_id=a.model, language_code="th",
        voice_settings=VoiceSettings(stability=a.stability, similarity_boost=0.75),
        previous_text=ls[i - 2] if i > 1 else None, next_text=ls[i] if i < len(ls) else None,
    )
    with open(AUD / f"line-{i:02d}.mp3", "wb") as f:
        for c in audio:
            f.write(c)
    print("เขียน line", i, round(dur(AUD / f"line-{i:02d}.mp3"), 2), "s")
if a.only:
    sys.exit()

t, timing, cmd = LEAD, [], ["ffmpeg", "-y", "-v", "error"]
for i, text in enumerate(ls, 1):
    p = AUD / f"line-{i:02d}.mp3"
    d = dur(p)
    timing.append({"n": i, "text": text, "start": round(t, 3), "end": round(t + d, 3)})
    cmd += ["-i", str(p)]
    t += d + GAP
total = round(timing[-1]["end"] + TAIL, 2)
parts = [f"[{i}:a]aresample=48000,adelay={int(e['start']*1000)}|{int(e['start']*1000)}[a{i}]" for i, e in enumerate(timing)]
parts.append("".join(f"[a{i}]" for i in range(len(ls))) + f"amix=inputs={len(ls)}:normalize=0,apad=whole_dur={total}[o]")
cmd += ["-filter_complex", ";".join(parts), "-map", "[o]", "-ac", "1", str(AUD / "vo.wav")]
subprocess.run(cmd, check=True)
(HERE / "video" / "timing_el.json").write_text(json.dumps({"total": total, "lines": timing}, ensure_ascii=False, indent=1), encoding="utf-8")
for e in timing:
    print(f"{e['n']}: {e['start']:6.2f}-{e['end']:6.2f}")
print("total", total)
