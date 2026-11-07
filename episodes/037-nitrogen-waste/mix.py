import json, numpy as np, soundfile as sf, subprocess
from pathlib import Path
H = Path(__file__).parent; SR = 48000
TM = json.loads((H/"timing.json").read_text(encoding="utf-8")); total = TM["total"]; N = int(total*SR)+SR
rng = np.random.default_rng(5)
mus = np.zeros(N); sfx = np.zeros(N)
def put(buf, t, x, g=1.0):
    a = int(t*SR); 
    if a < 0 or a >= N: return
    x = x[:N-a]; buf[a:a+len(x)] += x*g
def tone(f, d, dec=6, harm=(1,.35,.15)):
    t = np.arange(int(d*SR))/SR; y = sum(h*np.sin(2*np.pi*f*(k+1)*t) for k,h in enumerate(harm)); return y*np.exp(-dec*t)*np.minimum(1, t*200)
# music: pentatonic marimba arpeggio + soft pad, 96 bpm
pent = [261.63, 293.66, 329.63, 392.0, 440.0, 523.25, 587.33, 659.25]
beat = 60/96; pat = [0,2,4,2, 1,3,5,3, 2,4,6,4, 1,3,4,2]
t = 0.0; k = 0
while t < total:
    n = pat[k%len(pat)]; put(mus, t, tone(pent[n], .6, 5), .5)
    if k%4 == 0: put(mus, t, tone(pent[n]/2, 1.6, 2.2, (1,.2)), .4)
    t += beat/2; k += 1
for ph, f in enumerate([130.81, 164.81, 196.0]):
    tt = np.arange(N)/SR; mus += .05*np.sin(2*np.pi*f*tt)*(0.6+0.4*np.sin(2*np.pi*tt/8+ph))
fade = np.minimum(1, np.minimum(np.arange(N)/(SR*1.0), np.maximum(0,(total*SR-np.arange(N)))/(SR*2.0))); mus *= fade*0.35
def noise_lp(d, fc):
    x = rng.standard_normal(int(d*SR)); a = np.exp(-2*np.pi*fc/SR); y = np.zeros_like(x); s = 0
    for i in range(len(x)): s = a*s+(1-a)*x[i]; y[i] = s
    return y*(1/ max(1e-6, np.abs(y).max()))
def whoosh(t0):
    d = .7; x = rng.standard_normal(int(d*SR)); tt = np.linspace(0,1,len(x)); env = np.sin(np.pi*tt)**2
    y = np.convolve(x, np.ones(24)/24, 'same')*env; put(sfx, t0-.35, y, .25)
def blip(t0, f0=500, up=900, d=.12, g=.25):
    tt = np.arange(int(d*SR))/SR; f = f0+(up-f0)*tt/d; y = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*22); put(sfx, t0, y, g)
def chirp(t0, g=.18):
    for j in range(rng.integers(2,5)):
        d=.09; tt=np.arange(int(d*SR))/SR; f=3200+rng.integers(0,900)+900*np.sin(2*np.pi*22*tt); y=np.sin(2*np.pi*np.cumsum(f)/SR)*np.sin(np.pi*tt/d); put(sfx, t0+j*.13, y, g)
def step(t0, g=.15):
    tt=np.arange(int(.08*SR))/SR; put(sfx, t0, np.sin(2*np.pi*90*tt)*np.exp(-tt*50)+.3*rng.standard_normal(len(tt))*np.exp(-tt*60), g)
S = TM["scenes"]
for i, s in enumerate(S):
    if i > 0: whoosh(s["t0"])
    for c in s["cues"][1:]: blip(s["t0"]+c-.03, 700+60*i, 1200+80*i, g=.10)
    a, b = s["t0"], s["t1"]
    if i in (0, 3, 4):
        for tt in np.arange(a+1.2, b-1, 2.7+.3*i): chirp(tt+rng.random())
    if i in (0, 3):
        for tt in np.arange(a+2, b-1, .55): step(tt, .05)
    if i == 1:
        for tt in np.arange(a+.3, b-.3, .35): blip(tt+rng.random()*.2, 300+rng.integers(0,300), 800+rng.integers(0,500), .1, .1)
        amb = noise_lp(b-a, 500); put(sfx, a, amb, .10)
    if i == 2:
        for tt in (a+2.5, a+5.5, a+8): put(sfx, tt, tone(190,.25,12,(1,.5)), .0)
sfx *= 1.0
nar, sr = sf.read(str(H/"narration.wav")); nar = np.interp(np.arange(N)/SR, np.arange(len(nar))/sr, nar) if sr != SR else nar
out = np.zeros(N); out[:len(nar)] = nar[:N]
mix = out*1.0 + mus + sfx*1.0
mix = np.tanh(mix*1.1); mix = mix/np.abs(mix).max()*.92
sf.write(str(H/"mix.wav"), mix[:int(total*SR)], SR); print("ok", total)
