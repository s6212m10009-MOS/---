"""ตัดเสียงชุดใหญ่เป็นรายบรรทัดด้วยช่วงเงียบที่ใกล้จุดสัดส่วนตัวอักษร (whisper ภาษาไทยแบ่งไม่เจอ) -> audio_gm/NN.wav"""
import wave, numpy as np
from pathlib import Path
from lines import TTS
A = Path(__file__).resolve().parent / "video" / "audio_gm"
for bi, idx in enumerate([range(0, 5), range(5, 10)]):
    idx = list(idx)
    w = wave.open(str(A / f"batch{bi}.wav")); sr = w.getframerate(); raw = w.readframes(w.getnframes()); par = w.getparams(); w.close()
    x = np.frombuffer(raw, dtype="<i2"); a = np.abs(x.astype(float)) / 32768
    win = int(sr * .05); e = np.convolve(a, np.ones(win) / win, "same"); sil = e < e.max() * .03
    runs, s = [], None
    for i, v in enumerate(sil):
        if v and s is None: s = i
        if (not v) and s is not None:
            if (i - s) / sr > .25: runs.append((s / sr, i / sr))
            s = None
    L = [len(TTS[i].replace(" ", "")) for i in idx]; T = len(x) / sr
    cuts, acc = [0.0], 0
    for k in range(len(idx) - 1):
        acc += L[k]; exp = T * acc / sum(L)
        best = min(runs, key=lambda r: abs((r[0] + r[1]) / 2 - exp) - 1.5 * (r[1] - r[0]))
        cuts.append((best[0] + best[1]) / 2)
    cuts.append(T)
    print(bi, [round(c, 2) for c in cuts])
    for j, i in enumerate(idx):
        seg = x[int(cuts[j] * sr):int(cuts[j + 1] * sr)]
        with wave.open(str(A / f"{i:02}.wav"), "wb") as o:
            o.setparams(par); o.writeframes(seg.tobytes())
