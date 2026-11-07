import json, subprocess, numpy as np, wave
from pathlib import Path
H = Path(__file__).parent; A = H/"audio"
S = json.loads((H/"script.json").read_text(encoding="utf-8"))
LEAD, TAIL, LASTTAIL = 0.6, 0.8, 2.6
def dur(p): return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(p)]))
scenes, caps, t0, segs = [], [], 0.0, []
for i, txt in enumerate(S):
    chunks = txt.split(" "); ds = [dur(A/f"{i}_{k}.wav") for k in range(len(chunks))]
    cue, acc = [], LEAD
    for d in ds: cue.append(acc); acc += d
    total = acc + (LASTTAIL if i == len(S)-1 else TAIL)
    scenes.append({"t0": round(t0,3), "t1": round(t0+total,3), "dur": round(total,3), "cues": [round(c,3) for c in cue], "ends": [round(c+d,3) for c,d in zip(cue,ds)], "chunks": chunks})
    # captions: group chunks to <=30 chars
    grp, cur = [], []
    for k, c in enumerate(chunks):
        if cur and sum(len(x) for _, x in cur) + len(c) > 30: grp.append(cur); cur = []
        cur.append((k, c))
    if cur: grp.append(cur)
    for g in grp:
        k0, k1 = g[0][0], g[-1][0]
        caps.append({"t0": round(t0+cue[k0]-.05,3), "t1": round(t0+cue[k1]+ds[k1]+.1,3), "text": " ".join(x for _, x in g)})
    segs.append((t0+LEAD, A/f"{i}.wav", total-LEAD)); t0 += total
total = t0
# fix caption overlaps
for a, b in zip(caps, caps[1:]): a["t1"] = min(a["t1"], b["t0"])
# mixed narration track + envelope
SR = 24000; buf = np.zeros(int(total*SR)+SR)
for st, p, _ in segs:
    raw = subprocess.check_output(["ffmpeg","-v","error","-i",str(p),"-f","f32le","-ac","1","-ar",str(SR),"-"]); x = np.frombuffer(raw, dtype="<f4")
    a = int(st*SR); buf[a:a+len(x)] += x
peak = np.abs(buf).max(); buf = buf/peak*0.9
import soundfile as sf
sf.write(str(H/"narration.wav"), buf, SR)
fps = 24; env = []
w = int(SR/fps)
for f in range(int(total*fps)+2):
    seg = np.abs(buf[f*w:(f+1)*w]); env.append(float(seg.mean()) if len(seg) else 0.0)
m = max(env); env = [round(min(1.0, e/(m*0.45)),3) for e in env]
(H/"timing.json").write_text(json.dumps({"total": round(total,3), "scenes": scenes, "caps": caps, "env": env}, ensure_ascii=False), encoding="utf-8")
print([ (s["t0"], s["dur"]) for s in scenes], total)
