"""Thai voice for the film: Edge TTS per line (retries: the service sometimes returns no audio) -> voices_raw/<id>.wav (24 kHz mono, silence trimmed) + dur.json
Also writes voices_raw/span.json: for every line, where the voiced part starts/ends inside the wav (used for typing the LOG strip in sync).
  python voice.py
"""
import asyncio, json, os, subprocess, io, hashlib
import numpy as np, soundfile as sf
import edge_tts
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'voices_raw'); os.makedirs(os.path.join(OUT, '.cache'), exist_ok=True)
SR = 24000
lines = json.load(open(os.path.join(HERE, 'lines.json'), encoding='utf-8'))

async def fetch(say, voice, rate, mp3):
    for attempt in range(8):
        try:
            await edge_tts.Communicate(say, voice, rate=rate).save(mp3 + '.part')
            if os.path.getsize(mp3 + '.part') > 0:
                os.replace(mp3 + '.part', mp3); return
        except Exception as e:
            await asyncio.sleep(1 + attempt)
    raise SystemExit(f'could not fetch: {say}')

def to_wav(mp3):
    r = subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', mp3, '-ar', str(SR), '-ac', '1', '-f', 'wav', '-'], capture_output=True, check=True)
    a, _ = sf.read(io.BytesIO(r.stdout), dtype='float32'); return a

dur, span = {}, {}
for L in lines:
    say = L.get('say', L['text']); voice = L['voice']; rate = L.get('rate', '+0%')
    key = hashlib.sha1(json.dumps([voice, rate, say], ensure_ascii=False).encode()).hexdigest()[:16]
    mp3 = os.path.join(OUT, '.cache', key + '.mp3')
    if not os.path.exists(mp3): asyncio.run(fetch(say, voice, rate, mp3))
    a = to_wav(mp3)
    env = np.convolve(np.abs(a), np.ones(int(SR * .02)) / int(SR * .02), 'same')
    idx = np.where(env > env.max() * .04)[0]
    i0, i1 = max(0, idx[0] - int(.03 * SR)), min(len(a), idx[-1] + int(.06 * SR))
    a = a[i0:i1]
    sf.write(os.path.join(OUT, L['id'] + '.wav'), a, SR)
    dur[L['id']] = round(len(a) / SR, 3)
    print(L['id'], dur[L['id']])
json.dump(dur, open(os.path.join(OUT, 'dur.json'), 'w'))
