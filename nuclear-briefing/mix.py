"""Score, foley, beds and voice -> out/mix.wav (48 kHz stereo). Single source of times: events.json (from film.js EV)."""
import json, wave
from pathlib import Path
import numpy as np
from scipy import signal
HERE = Path(__file__).resolve().parent
SR = 48000; BAR = 240 / 84; BEAT = 60 / 84
ev = json.load(open(HERE / 'events.json'))
DUR = ev['dur']; E = ev['ev']
N = int(SR * (DUR + 1.0))
rng = np.random.default_rng(7)

def buf(): return np.zeros((2, N))
def tt(d): return np.arange(int(d * SR)) / SR
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return signal.sosfilt(signal.butter(o, [a, b], 'band', fs=SR, output='sos'), x)
def add(b, x, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i < 0: return
    x = np.asarray(x)[: max(0, N - i)]
    if len(x) == 0: return
    b[0, i:i + len(x)] += x * g * (1 - pan) * 0.7
    b[1, i:i + len(x)] += x * g * (1 + pan) * 0.7
def env_ad(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)
def noise(n): return rng.standard_normal(n)
def saw(f, d, det=(1.0,)):
    t = tt(d)
    return sum(signal.sawtooth(2 * np.pi * f * k * t + rng.random() * 6) for k in det) / len(det)
def fm_ping(f, d=1.2, idx=3.0):
    t = tt(d)
    return np.sin(2 * np.pi * f * t + idx * np.exp(-t * 7) * np.sin(2 * np.pi * f * 1.5 * t)) * np.exp(-t * 3.2)
def timpani(f=70, d=1.6):
    t = tt(d); fr = f * (1 + 0.9 * np.exp(-t * 28)); ph = 2 * np.pi * np.cumsum(fr) / SR
    return np.sin(ph) * np.exp(-t * 3.2) + 0.5 * np.sin(ph * 1.5) * np.exp(-t * 6) + 0.25 * lp(noise(len(t)), 600) * np.exp(-t * 30)
def thump(d=1.3, f=48):
    t = tt(d); ph = 2 * np.pi * np.cumsum(f * (1 + 2.2 * np.exp(-t * 18))) / SR
    return np.sin(ph) * np.exp(-t * 4.0)
def metal(f, d):      # bowed metal: inharmonic partials, slow attack (the one wet timbre)
    t = tt(d)
    x = sum(a * np.sin(2 * np.pi * f * r * t + rng.random() * 6) for r, a in [(1, 1), (2.76, .5), (5.4, .3), (8.93, .18)])
    return x * np.minimum(t / 1.1, 1) * np.exp(-np.maximum(t - 1.2, 0) / 1.0) * (1 + 0.1 * np.sin(2 * np.pi * 5 * t))
def brass(f, d):
    t = tt(d)
    x = lp(saw(f, d, (1, 1.004, .996)) + saw(f * 2, d, (1, 1.006)) * .4, 1400, 3)
    return x * np.minimum(t / 0.04, 1) * np.exp(-t / 0.9)

mus, fx, bed, vox = buf(), buf(), buf(), buf()
duck = np.ones(N)        # music/foley gain: the two silences and the suck-outs

def sil(a, b, fade=0.25):
    i0, i1, k = int(a * SR), int(b * SR), int(fade * SR)
    lo = max(0, i0 - k)
    duck[lo:i0] = np.minimum(duck[lo:i0], np.linspace(1, 0, i0 - lo))
    duck[i0:i1] = 0.0
    duck[i1:i1 + k] = np.minimum(duck[i1:i1 + k], np.linspace(0, 1, len(duck[i1:i1 + k])))

for e in E:
    if e['type'] == 'silence': sil(e['t'], e['until'])
    if e['type'] == 'suckout':
        i0 = int(e['t'] * SR); n = int(e['dur'] * SR)
        duck[i0:i0 + n] = np.minimum(duck[i0:i0 + n], 0.06)

# ---- beds (always on, thin; louder at orbit)
t = tt(DUR + 1); L = len(t)
hum = (np.sin(2 * np.pi * 55 * t) + .5 * np.sin(2 * np.pi * 110.4 * t) * (1 + .3 * np.sin(2 * np.pi * .13 * t))) * .5
hiss = bp(noise(L), 2500, 9000) * .05
orbit_gain = np.clip(1 - np.maximum(t - 10.0, 0) / 2.4, 0.12, 1) * (1 - np.clip((t - 40) / 3, 0, 1) * .5)
bs = (hum * .35 + hiss) * orbit_gain
bed[0, :L] += bs; bed[1, :L] += np.roll(bs, 37)
sea = lp(noise(L), 700) * (np.clip((t - 11.0) / 3, 0, 1) * np.clip((25 - t) / 4, 0, 1)) * .22   # L-cut: the sea is heard before the reading
bed[0, :L] += sea; bed[1, :L] += np.roll(sea, 211)
wind = lp(noise(L), 400) * .035 * (1 + .5 * np.sin(2 * np.pi * .08 * t))
bed[0, :L] += wind; bed[1, :L] += wind

# ---- music: pad + pulse bass + telemetry plucks
def pad(b, at, d, notes, g=.07):
    for f in notes:
        x = lp(saw(f, d, (1, 1.006, .994)), 900, 3); t_ = tt(d)
        x = x * np.minimum(t_ / 1.2, 1) * np.minimum((d - t_) / 1.2, 1)
        add(b, x, at, g)
pad(mus, 0.4, 10.6, [146.8, 174.6, 220.0], .05)
for k in range(24):                                     # FM telemetry plucks, 8ths -> 16ths into the dive
    at = 0.7 + k * (BEAT / 2 if k < 8 else BEAT / 4)
    if at < 11.0: add(mus, fm_ping([587, 698, 880, 698][k % 4], .5, 2.0), at, .05, (k % 3 - 1) * .5)
bass_roots = [73.4, 65.4, 58.3, 55.0]                   # D C Bb A
t0, t1 = 12.0, 36.5
for bar in range(4, 14):
    f = bass_roots[(bar - 4) % 4]
    for b in range(4):
        at = bar * BAR + b * BEAT
        if t0 <= at < t1:
            d = .5; tq = tt(d)
            x = lp(signal.square(2 * np.pi * f * tq, .35) + .6 * np.sin(2 * np.pi * f * 2 * tq) + .3 * np.sin(2 * np.pi * f * 3 * tq), 500, 2)
            add(mus, x * env_ad(len(x), .004, .22), at, .10 if b == 0 else .06)
    pad(mus, bar * BAR, BAR + .6, [f * 2, f * 3, f * 4], .028)
for k in range(int((t1 - t0) / (BEAT / 2))):             # dry ticks on the grid
    at = t0 + k * BEAT / 2; n = int(.03 * SR)
    add(fx, hp(noise(n), 5000) * env_ad(n, .001, .008), at, .06 if k % 2 == 0 else .03, ((k % 4) - 1.5) / 3)

# ---- foley from events
for e in E:
    a, ty = e['t'], e['type']
    if ty == 'tick':
        n = int(.03 * SR); add(fx, hp(noise(n), 4000) * env_ad(n, .001, .008), a, .08)
    elif ty == 'riser':
        d = e['dur']; q = tt(d)
        sw = bp(noise(len(q)), 400, 7000, 2) * (q / d) ** 2.2
        tone = np.sin(2 * np.pi * np.cumsum(180 * 2 ** (3 * q / d)) / SR) * (q / d) ** 2
        add(fx, (sw * .5 + tone * .12) * np.minimum((d - q) / .05, 1), a, .5)
    elif ty == 'servo':
        d = e['dur']; q = tt(d)
        add(fx, np.sin(2 * np.pi * np.cumsum(300 + 900 * q / d) / SR) * .02 * np.minimum(q / .5, 1), a, 1, .3)
    elif ty == 'ping':
        add(fx, fm_ping(e.get('f', 1568)), a, .16)
    elif ty == 'ratchet':
        n = int(.02 * SR); fr = 900 if e.get('accent') else 600
        x = hp(noise(n), 3000) * env_ad(n, .0005, .005) + np.sin(2 * np.pi * fr * tt(.02)) * env_ad(n, .0005, .006) * .5
        add(fx, x, a, .16 if e.get('accent') else .09)
    elif ty == 'scan':
        d = e['dur']; q = tt(d); x = noise(len(q)); y = np.zeros_like(x); ch = 2048
        for i in range(0, len(x), ch):
            fc = float(np.clip(6000 * (1 - q[min(i, len(q) - 1)] / d) + 400, 300, 8000))
            seg_ = x[i:i + ch]
            y[i:i + ch] = bp(seg_, fc * .7, min(fc * 1.3, 20000), 2)
        add(fx, y * np.minimum(q / .2, 1) * np.minimum((d - q) / .3, 1), a, .22)
    elif ty == 'impact':
        big = e.get('size') == 'xl'; f = e.get('f', 73.4 if big else 98)
        d1 = 2.4 if big else 1.4
        x = timpani(f, d1) + thump(d1, 48) * (1.0 if big else .6)
        add(fx, x, a, .55 if big else .32)
        if big:
            add(fx, brass(73.4, 2.8) * .8 + brass(110, 2.8) * .5, a, .22)
            n = int(2.0 * SR); add(fx, bp(noise(n), 600, 9000) * env_ad(n, .002, .5), a, .18)
    elif ty == 'blast':
        big = e.get('size') == 'xl'; d = 3.4 if big else 2.4; q = tt(d)
        n0 = int(.012 * SR); crack = hp(noise(n0), 1500) * env_ad(n0, .0003, .004)
        boom = np.sin(2 * np.pi * np.cumsum(28 + 62 * np.exp(-q * 3.2)) / SR) * np.exp(-q * (1.1 if big else 1.6))
        rum = lp(noise(len(q)), 160, 3) * np.exp(-q * 1.0) * 1.6
        add(fx, boom * 1.3 + rum * .8, a, .55 if big else .42)
        add(fx, crack * 2.0, a, .5 if big else .3)
        qw = tt(d - .3); wave_ = bp(noise(len(qw)), 250, 2600, 2) * np.minimum(qw / .25, 1) * np.exp(-qw * 1.7)
        add(fx, wave_, a + .3, .45 if big else .28)
        if e.get('ring'):
            qr = tt(3.0); add(fx, np.sin(2 * np.pi * 5200 * qr) * np.exp(-qr * 1.1) * .05 * np.minimum(qr / .4, 1), a + .1, 1)
    elif ty == 'wet':
        add(mus, metal(293.7, e['dur']) * .5 + metal(440, e['dur']) * .3, a, .10)
    elif ty == 'climb':
        d = e['dur']; pad(mus, a, d, [73.4, 110.0, 146.8, 185.0], .05)
        q = tt(d); add(fx, bp(noise(len(q)), 500, 8000) * (q / d) ** 3 * .25, a, 1)
    elif ty == 'frame':
        n = int(.9 * SR); add(fx, hp(noise(n), 3000) * np.hanning(n) * .2, a - .3, .4)
    elif ty == 'voice':
        with wave.open(str(HERE / 'voice' / 'raw' / f"{e['id']}.wav")) as w:
            y = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(float) / 32768
            sr_in = w.getframerate()
        y = signal.resample_poly(y, SR // sr_in, 1) if SR % sr_in == 0 else signal.resample(y, int(len(y) * SR / sr_in))
        y = hp(y, 80, 2); y = np.tanh(y * 1.8) / 1.8             # light compression (TTS has a high peak/RMS ratio)
        y *= 0.55 / max(1e-6, np.abs(y).max())
        add(vox, y, a, 1.0)

# ---- bus: duck music and foley under the voice, apply the silences, balance
def rms(x): return float(np.sqrt(np.mean(x ** 2) + 1e-12))
env = lp(np.abs(vox[0]), 8, 1)
vduck = 1 - 0.45 * np.clip(env / 0.08, 0, 1)
for b in (mus, fx):
    b *= duck * vduck
bed *= 0.45 * (0.55 + 0.45 * duck)
mus *= 1.3
mix = vox + mus + fx + bed
print('peak before', round(float(np.abs(mix).max()), 3))
mix = np.tanh(mix * 1.1) / 1.1
mix /= max(1.0, np.abs(mix).max() / 0.89)
(HERE / 'out').mkdir(exist_ok=True)
with wave.open(str(HERE / 'out' / 'mix.wav'), 'wb') as w:
    w.setparams((2, 2, SR, 0, 'NONE', 'not compressed'))
    w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('mix done; rms voice %.3f music %.3f fx %.3f bed %.3f' % (rms(vox), rms(mus), rms(fx), rms(bed)))
