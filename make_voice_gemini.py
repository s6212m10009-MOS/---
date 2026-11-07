"""เสียงพากย์ Gemini TTS แทน Edge TTS -> audio/NN.wav, audio/NN.json, timing.json, narration.wav, narration-th.txt

ใช้ story.json แบบเดียวกับ tools/make_voice.py ของแต่ละตอน และเขียนไฟล์ผลลัพธ์ชื่อเดิม
- ส่งหลายซีนในคำขอเดียว (แผนฟรีเรียกได้แค่วันละ 10 ครั้ง นาทีละ 3 ครั้ง) แล้วตัดแบ่งเป็นซีนเอง
- Gemini ไม่ส่งเวลาของคำกลับมา จึงถอดเสียงด้วย faster-whisper แล้วเทียบตัวอักษรกับบท
  เพื่อหาจุดตัดซีนและเวลาขึ้นซับแต่ละท่อน

ต้องตั้ง GEMINI_API_KEY ก่อน (ใช้ set_gemini_key.ps1)
  python make_voice_gemini.py episodes/011-xxx                    # สร้างเฉพาะซีนที่ยังไม่มีเสียง
  python make_voice_gemini.py episodes/011-xxx --fresh            # สร้างเสียงใหม่ทั้งหมด
  python make_voice_gemini.py episodes/011-xxx --redo 3 7         # สร้างใหม่เฉพาะซีน 3 และ 7
  python make_voice_gemini.py episodes/010-uk-nuclear-subs --out gemini-test   # เขียนลงโฟลเดอร์อื่น ไม่ทับของเดิม
"""

import argparse
import difflib
import json
import os
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np

MODEL = "gemini-3.8-flash-tts"
VOICE = "Sadaltager"
STYLE = "เล่าเรื่องสารคดีน่าติดตาม น้ำเสียงลึกลับนิดๆ จังหวะกระชับ ชัดถ้อยชัดคำ"
WHISPER = "small"     # ใช้แค่หาเวลา ไม่ต้องถอดถูกทุกคำ
MAX_CHARS = 2500      # ตัวอักษรต่อคำขอ (~1 นาทีเสียง) ยาวกว่านี้โทนเสียงมักเพี้ยน
SR = 48000
LEAD = 0.15      # เงียบก่อนเริ่มพูดในแต่ละซีน
TAIL = 0.3       # เผื่อหลังพูดจบ
END_HOLD = 3.2   # ซีนปิดค้างไว้นานขึ้น


def scene_text(s):
    return " ".join(v for _, v in s["parts"])


def synth(client, text, path, voice, style):
    part = {"text": text}
    if style:
        part["speech_metadata"] = {"style": style}
    for attempt in range(5):
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=[{"role": "user", "parts": [part]}],
                config={"response_modalities": ["AUDIO"],
                        "speech_config": {"voice_config": {"voice": voice}}},
            )
            path.write_bytes(resp.candidates[0].content.parts[0].inline_data.data)
            return
        except Exception as e:
            msg = str(e)
            if "PerDay" in msg or "per day" in msg:
                sys.exit("โควตาฟรีของวันนี้หมดแล้ว (วันละ 10 ครั้ง) — รอรีเซ็ตตอน 14:00 หรือเปิด billing ใน AI Studio\n"
                         "รันคำสั่งเดิมอีกครั้งได้เลย ซีนที่ทำเสร็จแล้วจะไม่ถูกสร้างซ้ำ")
            wait = 25 * (attempt + 1)  # นาทีละ 3 ครั้ง -> รอแล้วลองใหม่
            print(f"  ผิดพลาด: {msg[:90]} — รอ {wait} วินาที", flush=True)
            time.sleep(wait)
    sys.exit(f"สร้างเสียงไม่สำเร็จ: {path.name}")


def transcribe(model, path, text):
    # ถอดไฟล์เองด้วย ffmpeg (av ที่ติดตั้งอยู่ไม่เข้ากับ faster-whisper)
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", "16000", "-"])
    segs, _ = model.transcribe(np.frombuffer(raw, dtype="<f4"), language="th", word_timestamps=True,
                               initial_prompt=text[:800], vad_filter=False)
    return [{"t": round(w.start, 3), "d": round(w.end - w.start, 3), "w": w.word.strip()}
            for s in segs for w in s.words if w.word.strip()]


def char_times(text, words):
    """ตำแหน่งตัวอักษรในบท -> (เวลาเริ่ม, เวลาจบ) โดยเทียบกับคำที่ whisper ถอดได้ (ไม่นับช่องว่าง)"""
    ref_idx = [i for i, c in enumerate(text) if not c.isspace()]
    ref = "".join(text[i] for i in ref_idx)
    hyp, hyp_t = "", []
    for w in words:
        chars = "".join(c for c in w["w"] if not c.isspace())
        step = w["d"] / max(len(chars), 1)
        for j, c in enumerate(chars):
            hyp += c
            hyp_t.append((w["t"] + step * j, w["t"] + step * (j + 1)))
    out = {}
    for a, b, n in difflib.SequenceMatcher(None, ref, hyp, autojunk=False).get_matching_blocks():
        for k in range(n):
            out[ref_idx[a + k]] = hyp_t[b + k]
    return dict(sorted(out.items()))


def chunk_times(parts, words):
    """เวลาเริ่มของแต่ละท่อนซับ = เวลาของตัวอักษรแรกในท่อนที่จับคู่กับเสียงได้"""
    voice = " ".join(v for _, v in parts)
    starts, pos = [], 0
    for _, v in parts:
        starts.append(voice.index(v, pos))
        pos = starts[-1] + len(v)
    ct = char_times(voice, words)
    out = []
    for s in starts:
        t = next((t0 for i, (t0, _) in ct.items() if i >= s), out[-1] if out else 0.0)
        out.append(max(t, out[-1]) if out else t)
    return out


def split_batch(batch_wav, scenes, texts, words, audio_dir):
    """ตัดเสียงที่พากย์รวดเดียวหลายซีน ออกเป็น NN.wav + NN.json ตรงกลางช่วงเงียบระหว่างซีน"""
    joined, offs = "", []
    for t in texts:
        offs.append(len(joined))
        joined += t + "\n"
    ct = char_times(joined, words)
    with wave.open(str(batch_wav)) as w:
        params, frames = w.getparams(), w.readframes(w.getnframes())
    rate, width = params.framerate, params.sampwidth * params.nchannels
    total = len(frames) / width / rate
    pcm = np.abs(np.frombuffer(frames, dtype="<i2").reshape(-1, params.nchannels).mean(axis=1))
    win = int(rate * 0.03)
    energy = np.convolve(pcm, np.ones(win) / win, mode="same")

    def quietest(t):  # จุดที่เงียบที่สุดใกล้ t (±0.4 วินาที) กันตัดโดนต้นหรือท้ายคำ
        a, b = max(int((t - 0.4) * rate), 0), min(int((t + 0.4) * rate), len(energy))
        return (a + int(np.argmin(energy[a:b]))) / rate if b > a else t

    spans = []
    for k, t in enumerate(texts):
        hit = [v for i, v in ct.items() if offs[k] <= i < offs[k] + len(t)]
        spans.append((hit[0][0], hit[-1][1]) if hit else None)
    cuts = [0.0]
    for k in range(1, len(texts)):
        prev = next((s for s in reversed(spans[:k]) if s), None)
        nxt = next((s for s in spans[k:] if s), None)
        cut = quietest((prev[1] + nxt[0]) / 2 if prev and nxt else total * k / len(texts))
        cuts.append(max(cut, cuts[-1]))
    cuts.append(total)
    for k, i in enumerate(scenes):
        a, b = cuts[k], cuts[k + 1]
        with wave.open(str(audio_dir / f"{i:02}.wav"), "wb") as w:
            w.setparams(params)
            w.writeframes(frames[int(a * rate) * width:int(b * rate) * width])
        part = [{**x, "t": round(x["t"] - a, 3)} for x in words if a <= x["t"] < b]
        (audio_dir / f"{i:02}.json").write_text(json.dumps(part, ensure_ascii=False), encoding="utf-8")
        print(f"  ซีน {i}: {a:6.2f}-{b:6.2f} วินาที" + ("" if spans[k] else "  (หาจุดตัดไม่เจอ แบ่งตามสัดส่วน)"), flush=True)


def decode(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-af",
                                   "loudnorm=I=-16:TP=-1.5:LRA=8", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, dtype="<f4").astype(np.float64)


def batches(todo, story):
    """จัดซีนที่ต้องสร้างเป็นชุด: ซีนติดกัน รวมไม่เกิน MAX_CHARS"""
    out = []
    for i in todo:
        n = len(scene_text(story[i]))
        if out and out[-1][-1] == i - 1 and sum(len(scene_text(story[j])) for j in out[-1]) + n <= MAX_CHARS:
            out[-1].append(i)
        else:
            out.append([i])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode", type=Path)
    ap.add_argument("--out", type=Path, help="โฟลเดอร์ผลลัพธ์ (ค่าเริ่มต้น = โฟลเดอร์ตอน)")
    ap.add_argument("--fresh", action="store_true")
    ap.add_argument("--redo", type=int, nargs="*", default=[])
    ap.add_argument("--voice", default=VOICE)
    ap.add_argument("--style", default=STYLE)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    ep = args.episode.resolve()
    out = (ep / args.out) if args.out and not args.out.is_absolute() else (args.out or ep)
    story = json.loads((ep / "story.json").read_text(encoding="utf-8"))
    audio = out / "audio"
    audio.mkdir(parents=True, exist_ok=True)

    todo = [i for i in range(len(story))
            if args.fresh or i in args.redo or not (audio / f"{i:02}.wav").exists()]
    wm = None

    def whisper():
        nonlocal wm
        if wm is None:
            from faster_whisper import WhisperModel
            print("โหลด whisper", WHISPER, "(ครั้งแรกจะดาวน์โหลดโมเดล)", flush=True)
            wm = WhisperModel(WHISPER, device="cpu", compute_type="int8")
        return wm

    if todo:
        if not os.environ.get("GEMINI_API_KEY"):
            sys.exit("ยังไม่ได้ตั้ง GEMINI_API_KEY — รัน set_gemini_key.ps1 ก่อน")
        from google import genai
        client = genai.Client()
        groups = batches(todo, story)
        print(f"ต้องสร้าง {len(todo)} ซีน ใช้ {len(groups)} คำขอ", flush=True)
        for g in groups:
            texts = [scene_text(story[i]) for i in g]
            print("TTS ซีน", g, flush=True)
            if len(g) == 1:
                synth(client, texts[0], audio / f"{g[0]:02}.wav", args.voice, args.style)
                (audio / f"{g[0]:02}.json").unlink(missing_ok=True)
                continue
            tmp = audio / f"batch-{g[0]:02}-{g[-1]:02}.wav"
            synth(client, "\n".join(texts), tmp, args.voice, args.style)
            words = transcribe(whisper(), tmp, " ".join(texts))
            split_batch(tmp, g, texts, words, audio)
            tmp.unlink()

    for i in range(len(story)):
        if not (audio / f"{i:02}.json").exists():
            words = transcribe(whisper(), audio / f"{i:02}.wav", scene_text(story[i]))
            (audio / f"{i:02}.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
            print("ถอดเสียง", i, len(words), "คำ", flush=True)

    timing, clips, start = [], [], 0.0
    for i, s in enumerate(story):
        a = decode(audio / f"{i:02}.wav")
        words = json.loads((audio / f"{i:02}.json").read_text(encoding="utf-8"))
        vdur = len(a) / SR
        dur = round(LEAD + vdur + (END_HOLD if s["id"] == "end" else TAIL), 2)
        cts = chunk_times(s["parts"], words)
        timing.append({
            "id": s["id"], "start": round(start, 3), "duration": dur, "voice": round(vdur, 3),
            "chunks": [{"text": c, "t": round(start + LEAD + t, 3)} for (c, _), t in zip(s["parts"], cts)],
        })
        clips.append((start + LEAD, a))
        print(f"{i:2} {s['id']:9} start {start:6.2f} dur {dur:5.2f} ซับ {[round(t, 2) for t in cts]}", flush=True)
        start += dur

    total = round(start, 2)
    n = int(SR * total) + 1
    speech = np.zeros(n)
    for at, a in clips:
        k = int(at * SR)
        speech[k:k + len(a)] += a[: n - k]
    with wave.open(str(out / "narration.wav"), "wb") as w:
        w.setparams((1, 2, SR, 0, "NONE", "not compressed"))
        w.writeframes((np.clip(speech, -.98, .98) * 32767).astype("<i2").tobytes())
    (out / "timing.json").write_text(json.dumps({"total": total, "scenes": timing}, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "narration-th.txt").write_text("\n".join(scene_text(s) for s in story), encoding="utf-8")
    print("total", total, "->", out)


if __name__ == "__main__":
    main()
