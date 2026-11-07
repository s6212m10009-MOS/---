import json, asyncio, edge_tts, subprocess, random
from pathlib import Path
H = Path(__file__).parent
S = json.loads((H/"script.json").read_text(encoding="utf-8"))
async def one(t, p):
    for a in range(25):
        try:
            await edge_tts.Communicate(t, "th-TH-PremwadeeNeural", rate="+8%").save(str(p))
            if p.stat().st_size > 0: return
        except Exception:
            await asyncio.sleep(1+random.random()*2)
    raise SystemExit("fail: "+t)
def trim(src, dst):
    subprocess.run(["ffmpeg","-v","error","-y","-i",str(src),"-af","silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=1:stop_threshold=-45dB:stop_duration=0.15,apad=pad_dur=0.12","-ar","24000","-ac","1",str(dst)],check=True)
async def main():
    for i, t in enumerate(S):
        files = []
        for k, c in enumerate(t.split(" ")):
            p = H/"audio"/f"{i}_{k}.mp3"; w = H/"audio"/f"{i}_{k}.wav"
            await one(c, p); trim(p, w); files.append(w)
        lst = H/"audio"/f"{i}.txt"
        lst.write_text("".join(f"file '{f.name}'\n" for f in files))
        subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(H/"audio"/f"{i}.wav")],check=True)
        print("ok", i, flush=True)
asyncio.run(main())
