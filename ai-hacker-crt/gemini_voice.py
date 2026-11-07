"""Thai voice with Gemini TTS (replaces voice.py / Edge TTS): narrator lines in ONE request, fake boss in another, then cut per line with the
library-independent helpers of ../make_voice_gemini.py (whisper only finds the cut points). Needs GEMINI_API_KEY.
Output: voices_raw/<id>.wav (24 kHz mono, trimmed, tempo applied) + voices_raw/dur.json.   python gemini_voice.py [--tempo 1.2]"""
import argparse, json, os, subprocess, sys, io
from pathlib import Path
import numpy as np, wave
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import make_voice_gemini as G
sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser(); ap.add_argument('--tempo', type=float, default=1.3); ap.add_argument('--boss-tempo', type=float, default=1.1)
ap.add_argument('--voice', default='Sadaltager'); ap.add_argument('--boss-voice', default='Charon')
a = ap.parse_args()
STYLE_N = 'เล่าเรื่องแบบลึกลับ น้ำเสียงเรียบนิ่ง ตึงเครียดเล็กน้อย จังหวะกระชับ ชัดถ้อยชัดคำ'
STYLE_B = 'เสียงผู้ชายวัยกลางคน รีบร้อน ใช้อำนาจ พูดเร็วเหมือนกำลังติดประชุม'
lines = json.load(open(HERE / 'lines.json', encoding='utf-8'))
say = {L['id']: L.get('say', L['text']) for L in lines}
nar = [L['id'] for L in lines if L['id'] != 'b1']
GM = HERE / 'voices_gm'; OUT = HERE / 'voices_raw'
if not os.environ.get('GEMINI_API_KEY'): sys.exit('GEMINI_API_KEY is not set')
from google import genai
from faster_whisper import WhisperModel
client = genai.Client()
batch = GM / 'narr.wav'
if not batch.exists(): G.synth(client, '\n'.join(say[i] for i in nar), batch, a.voice, STYLE_N)
boss = GM / 'b1.wav'
if not boss.exists(): G.synth(client, say['b1'], boss, a.boss_voice, STYLE_B)
wm = WhisperModel(G.WHISPER, device='cpu', compute_type='int8')
texts = [say[i] for i in nar]
words = G.transcribe(wm, batch, ' '.join(texts))
G.split_batch(batch, list(range(len(nar))), texts, words, GM)       # -> voices_gm/NN.wav
def finish(src, dst, tempo):
    raw = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(src), '-af', f'atempo={tempo}', '-ar', '24000', '-ac', '1', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    y = np.frombuffer(raw, dtype='<f4'); sr = 24000
    env = np.convolve(np.abs(y), np.ones(int(sr * .02)) / int(sr * .02), 'same'); idx = np.where(env > env.max() * .04)[0]
    y = y[max(0, idx[0] - int(.03 * sr)):min(len(y), idx[-1] + int(.06 * sr))]
    with wave.open(str(dst), 'wb') as w:
        w.setparams((1, 2, sr, 0, 'NONE', 'not compressed')); w.writeframes((np.clip(y, -1, 1) * 32767).astype('<i2').tobytes())
    return round(len(y) / sr, 3)
dur = {}
for k, i in enumerate(nar): dur[i] = finish(GM / f'{k:02}.wav', OUT / f'{i}.wav', {'n1': 1.4, 'n2': 1.35}.get(i, a.tempo))
dur['b1'] = finish(boss, OUT / 'b1.wav', a.boss_tempo)
json.dump(dur, open(OUT / 'dur.json', 'w')); print(dur)
