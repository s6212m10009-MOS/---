"""พากย์ตอน 034 ด้วย Edge TTS (th-TH-PremwadeeNeural) ทีละบรรทัด -> video/audio_gm/NN_t.wav, vo.wav, video/timing_gm.json
(รูปแบบเดียวกับ make_voice.py ฉบับ Gemini เพื่อให้ build.py / make_sfx.py ใช้ต่อได้)
  python make_voice_edge.py [--voice th-TH-PremwadeeNeural] [--rate +0%]"""
import argparse, asyncio, json, subprocess, wave
from pathlib import Path
import numpy as np
import edge_tts
from lines import TTS

HERE = Path(__file__).resolve().parent
AUD = HERE / "video" / "audio_gm"
SR, GAP, LEAD, TAIL = 48000, 0.3, 0.25, 2.2


def decode(p):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, dtype="<f4").astype(float)


async def main(voice, rate):
    AUD.mkdir(parents=True, exist_ok=True)
    t, timing, clips = LEAD, [], []
    for i, text in enumerate(TTS):
        mp3 = AUD / f"{i:02}.mp3"
        for att in range(8):
            try:
                await edge_tts.Communicate(text, voice, rate=rate).save(str(mp3))
                break
            except Exception as e:
                print("retry", i, att, type(e).__name__, flush=True)
                await asyncio.sleep(2 + att * 2)
        else:
            raise SystemExit("TTS failed at line %d" % i)
        x = decode(mp3)
        wav = AUD / f"{i:02}_t.wav"
        with wave.open(str(wav), "wb") as w:
            w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
            w.writeframes((np.clip(x, -.98, .98) * 32767).astype("<i2").tobytes())
        d = len(x) / SR
        timing.append({"n": i + 1, "text": text, "start": round(t, 3), "end": round(t + d, 3)})
        clips.append((t, x))
        t += d + GAP
    total = round(timing[-1]["end"] + TAIL, 2)
    n = int(SR * total) + 1
    sp = np.zeros(n)
    for at, x in clips:
        k = int(at * SR)
        sp[k:k + len(x)] += x[: n - k]
    sp = sp / max(float(np.abs(sp).max()), 1e-9) * 0.9
    with wave.open(str(AUD / "vo.wav"), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((np.clip(sp, -.98, .98) * 32767).astype("<i2").tobytes())
    (HERE / "video" / "timing_gm.json").write_text(json.dumps({"total": total, "lines": timing}, ensure_ascii=False, indent=1), encoding="utf-8")
    for e in timing:
        print(f"{e['n']}: {e['start']:6.2f}-{e['end']:6.2f}")
    print("total", total)


ap = argparse.ArgumentParser()
ap.add_argument("--voice", default="th-TH-PremwadeeNeural")
ap.add_argument("--rate", default="+0%")
a = ap.parse_args()
asyncio.run(main(a.voice, a.rate))
