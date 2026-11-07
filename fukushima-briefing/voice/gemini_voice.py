"""Thai narration for the Fukushima film: ONE Gemini TTS request, cut per line (whisper only finds cut points).
Output: voice/raw/<id>.wav (24 kHz mono, tempo applied) + voice/raw/dur.json.  python gemini_voice.py [--tempo 1.25]"""
import argparse, json, os, subprocess, sys, wave
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))          # Desktop root: make_voice_gemini.py
import make_voice_gemini as G
sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser(); ap.add_argument('--tempo', type=float, default=1.25); ap.add_argument('--voice', default='Sadaltager')
a = ap.parse_args()
STYLE = 'นักวิเคราะห์ภาพดาวเทียม น้ำเสียงนิ่ง เรียบ แห้ง จังหวะสั้นกระชับ ไม่เร้าอารมณ์ ชัดถ้อยชัดคำ'
lines = json.load(open(HERE / 'lines.json', encoding='utf-8'))
ids = [L['id'] for L in lines]; texts = [L.get('say', L['text']) for L in lines]
GM = HERE / 'gm'; OUT = HERE / 'raw'; GM.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
if not os.environ.get('GEMINI_API_KEY'): sys.exit('GEMINI_API_KEY is not set')
from google import genai
from faster_whisper import WhisperModel
client = genai.Client()
batch = GM / 'narr.wav'
if not batch.exists(): G.synth(client, '\n'.join(texts), batch, a.voice, STYLE)
wm = WhisperModel(G.WHISPER, device='cpu', compute_type='int8')
words = G.transcribe(wm, batch, ' '.join(texts))
G.split_batch(batch, list(range(len(ids))), texts, words, GM)
def finish(src, dst, tempo):
    raw = subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(src),'-af',f'atempo={tempo}','-ar','24000','-ac','1','-f','f32le','-'],capture_output=True,check=True).stdout
    y = np.frombuffer(raw, dtype='<f4'); sr = 24000
    env = np.convolve(np.abs(y), np.ones(int(sr*.02))/int(sr*.02), 'same'); idx = np.where(env > env.max()*.04)[0]
    y = y[max(0, idx[0]-int(.03*sr)):min(len(y), idx[-1]+int(.06*sr))]
    with wave.open(str(dst), 'wb') as w:
        w.setparams((1,2,sr,0,'NONE','not compressed')); w.writeframes((np.clip(y,-1,1)*32767).astype('<i2').tobytes())
    return round(len(y)/sr, 3)
dur = {i: finish(GM/f'{k:02}.wav', OUT/f'{i}.wav', a.tempo) for k, i in enumerate(ids)}
json.dump(dur, open(OUT/'dur.json','w')); print(dur, 'sum', round(sum(dur.values()),1))
