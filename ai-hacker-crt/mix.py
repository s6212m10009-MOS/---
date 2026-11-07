"""ai-hacker-crt mix (foley adapted from the library demo): foley (all synthesised) + narration (ducking the score) + music/score.wav → mix.wav
Events come from events.json (node core/render/events.mjs exports window.EV). The foley follows the "materials": relays, plastic keycaps, the picture tube, the phone line."""
import json, os, sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, 'C:/Users/nimineemu/lemo-opuscar/core/audio')
from sfx import compress, limit
SR = 48000
rng = np.random.default_rng(7)
E = json.load(open(os.path.join(D, 'events.json')))
DUR = E['dur']; N = int(DUR * SR)
def T(d): return np.arange(int(round(d * SR))) / SR
def nz(d): return rng.standard_normal(int(round(d * SR)))
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f, o=2): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
bus = {k: np.zeros((N, 2)) for k in ['sfx', 'bed', 'vo', 'music']}
def add(name, x, at, g=1.0, pan=0.0):
    i = int(round(at * SR));
    if i >= N or len(x) == 0: return
    x = x[:N - i] * g
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[name][i:i + len(x), 0] += x * l * 1.414; bus[name][i:i + len(x), 1] += x * r * 1.414

# ---------- Foley ----------
def key(v=1.0, kind='key'):
    """Buckling-spring mechanical key: plastic clack + spring ping + low tap of the keycap bouncing back"""
    d = .09; t = T(d)
    p = rng.uniform(.93, 1.08)
    clickn = hp(nz(d), 2200) * np.exp(-t / .0028)
    ping = np.sin(2 * np.pi * 3400 * p * t) * np.exp(-t / .03) * .22 + np.sin(2 * np.pi * 5230 * p * t) * np.exp(-t / .015) * .1
    thock = bp(nz(d), 260 * p, 900 * p) * np.exp(-np.maximum(0, t - .012) / .012) * (t > .01) * 1.3
    if kind == 'space': thock *= 1.6; ping *= .4; thock = lp(thock, 500)
    if kind == 'enter': thock *= 2.0
    return (clickn * .8 + ping + thock) * v
def tick(v=1.0):           # characters arriving from the other end: a light teletype tick
    d = .03; t = T(d)
    return (bp(nz(d), 1200, 4200) * np.exp(-t / .004) + np.sin(2 * np.pi * 1850 * t) * np.exp(-t / .008) * .3) * v
def relay(v=1.0):
    d = .12; t = T(d)
    return (hp(nz(d), 1500) * np.exp(-t / .004) * .8 + bp(nz(d), 80, 400) * np.exp(-t / .03) * 1.4 +
            hp(nz(d), 1500) * np.exp(-np.maximum(0, t - .035) / .003) * (t > .035) * .4) * v
def degauss(v=1.0):
    """Degauss coil: a fast-decaying 60Hz-plus-harmonics "hummm" + one dull "thunk" """
    d = 1.3; t = T(d)
    wob = 1 + .04 * np.sin(2 * np.pi * 7 * t)
    hum = sum(np.sin(2 * np.pi * 60 * h * t * wob) / h for h in (1, 2, 3, 5)) * np.exp(-t / .35)
    th = lp(nz(d), 120) * np.exp(-t / .08) * 3
    return (np.tanh(hum * 1.5) * .6 + th) * v
def data_chirp(v=1.0):
    d = .05; t = T(d); f = rng.choice([1200, 1500, 1800, 2200])
    return np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t / .015) * .25 * v
def ratchet(v=1.0):
    d = .02; t = T(d)
    return hp(nz(d), 2500) * np.exp(-t / .002) * v
def err(f=466, d=.16, v=1.0):
    t = T(d); x = np.sign(np.sin(2 * np.pi * f * t)) * .5 + np.sin(2 * np.pi * f * 2 * t) * .15
    e = np.minimum(1, t / .004) * np.minimum(1, (d - t) / .01)
    return lp(np.tanh(x * 1.6), 3500) * e * v
def bel(v=1.0):
    d = .45; t = T(d)
    return (np.sin(2 * np.pi * 1000 * t) + .3 * np.sin(2 * np.pi * 2000 * t)) * np.exp(-t / .12) * np.minimum(1, t / .003) * v
def modem(d, up=False, v=1.0):
    """Original handshake: answer tone (two phase reversals) → dual tone → alternating 1200/2400 → scrambled data noise. The sending version is shorter and higher."""
    t = T(d); x = np.zeros_like(t)
    if not up:
        a = t < .42
        ph = np.pi * ((t > .14).astype(float) + (t > .28))
        x += np.sin(2 * np.pi * 2100 * t + ph) * a * .5
        b = (t >= .42) & (t < .72)
        x += (np.sin(2 * np.pi * 1200 * t) * .3 + np.sin(2 * np.pi * 2400 * t) * .25) * b * (1 + .5 * np.sign(np.sin(2 * np.pi * 9 * t)))
        c = t >= .72
        fsk = np.where(np.sin(2 * np.pi * 37 * t + 3 * np.sin(2 * np.pi * 5 * t)) > 0, 1200, 2400)
        x += np.sin(2 * np.pi * np.cumsum(fsk) / SR) * c * .25
        x += bp(nz(d), 600, 3200) * c * .5 * (.6 + .4 * np.sin(2 * np.pi * 11 * t))
    else:
        fsk = np.where(rng.random(len(t) // 240 + 1).repeat(240)[:len(t)] > .5, 1070, 1270)
        x += np.sin(2 * np.pi * np.cumsum(fsk) / SR) * .3
        x += bp(nz(d), 900, 3600) * .35 * (t > .25)
    e = np.minimum(1, t / .01) * np.minimum(1, (d - t) / .02)
    return lp(np.tanh(x * 1.3), 3800) * e * v      # phone-line bandwidth
def swell(d, v=1.0, down=False):
    t = T(d); e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    f = np.linspace(200, 1400, len(t)) if not down else np.linspace(1400, 200, len(t))
    x = lp(nz(d), 900) * e * .6 + np.sin(2 * np.pi * np.cumsum(f) / SR) * e * .05
    return x * v
def poweroff(v=1.0):
    d = 1.0; t = T(d)
    th = lp(nz(d), 150) * np.exp(-t / .06) * 2.5
    crack = hp(nz(d), 3000) * np.exp(-t / .05) * .5
    return (th + crack) * v
def landtick(n, v=1.0):
    d = .02; t = T(d); x = np.zeros_like(t)
    for _ in range(min(n, 5)):
        f = rng.uniform(2200, 6000); o = rng.uniform(0, .008)
        x += np.sin(2 * np.pi * f * t) * np.exp(-np.maximum(0, t - o) / .003) * (t >= o)
    return x * v * min(1.6, np.sqrt(n) / 3)


def linehiss(d, v=1.0):
    """The phone line under the fake call: band-limited noise with a faint 50 Hz-ish buzz and a few dropouts"""
    t = T(d); x = bp(nz(d), 300, 3400) * (.5 + .5 * np.sin(2 * np.pi * 3.1 * t) ** 2) * .35 + np.sin(2 * np.pi * 100 * t) * .02
    e = np.minimum(1, t / .15) * np.minimum(1, (d - t) / .4); return x * e * v
def shock(v=1.0):
    d = 1.4; t = T(d)
    hum = sum(np.sin(2 * np.pi * 60 * h * t) / h for h in (1, 2, 3, 5)) * np.exp(-t / .4)
    th = lp(nz(d), 140) * np.exp(-t / .1) * 3
    return (np.tanh(hum * 1.4) * .6 + th + hp(nz(d), 3000) * np.exp(-t / .03) * .6) * v

for e in E['ev']:
    t, ty = e['t'], e['type']
    pan = rng.uniform(-.25, .25)
    if ty in ('key', 'space', 'enter'): add('sfx', key(1.0, ty if ty != 'key' else 'key'), t, .5, pan)
    elif ty == 'mtype': add('sfx', key(1.0, 'space' if e.get('ch') == ' ' else 'key'), t, .22, pan)
    elif ty == 'tick': add('sfx', tick(), t, .3, .15)
    elif ty == 'relay': add('sfx', relay(), t, .8)
    elif ty == 'degauss': add('sfx', degauss(), t, .55)
    elif ty == 'ratchet': add('sfx', ratchet(), t, .22, .3)
    elif ty == 'err': add('sfx', err(466), t, .32)
    elif ty == 'err2': add('sfx', err(233, .38), t, .34)
    elif ty == 'bel': add('sfx', bel(), t, .3)
    elif ty == 'linehiss': add('sfx', linehiss(e['d']), t, .5)
    elif ty == 'shock': add('sfx', shock(), t, .8)
    elif ty == 'land': add('sfx', landtick(e['n']), t, .09, rng.uniform(-.5, .5))

# ---------- Machine noise floor (fan + 120 Hz + very faint flyback whine); it keeps going to the end: no power-off in this film ----------
t = np.arange(N) / SR
fan = lp(rng.standard_normal(N), 700) * .05 + lp(rng.standard_normal(N), 180) * .05 + np.sin(2 * np.pi * 120 * t) * .006
fan *= np.clip((t - .22) / 1.2, 0, 1) ** 1.5
whf = 15734 - 1800 * np.exp(-np.maximum(0, t - .35) / .25)
whine = np.sin(2 * np.pi * np.cumsum(whf) / SR) * .0022 * (t > .35) * (1 + .15 * np.sin(2 * np.pi * .3 * t))
bus['bed'][:, 0] += fan + whine; bus['bed'][:, 1] += fan * .97 + whine

# ---------- Voice ----------
vo_env = np.zeros(N)
for e in E['ev']:
    if e['type'] != 'vo': continue
    y, sr = sf.read(os.path.join(D, 'voices', e['id'] + '.wav'))
    if y.ndim > 1: y = y.mean(1)
    y = resample_poly(y, SR, sr)
    y = compress(y / np.abs(y).max() * .8, thr=.2, ratio=3); y = y / np.abs(y).max() * .75
    add('vo', y, e['t'], 1.0 if e['id'] != 'b1' else .9, 0 if e['id'] != 'b1' else .2)
    i = int(e['t'] * SR); vo_env[i:i + len(y)] = 1
k = int(.25 * SR); duck = 1 - .6 * np.clip(np.convolve(vo_env, np.ones(k) / k, 'same') * 1.5, 0, 1)   # about -8 dB

# ---------- Score ----------
m, sr = sf.read(os.path.join(D, 'music', 'score.wav'))
if sr != SR: m = resample_poly(m, SR, sr, axis=0)
m = m[:N]; bus['music'][:len(m)] += m * 1.25
bus['music'] *= duck[:, None]

mix = bus['music'] + bus['vo'] * 1.25 + bus['sfx'] * .9 + bus['bed']
# the digital-zero second: everything out (the final Enter key at 28.7 is already over)
z = (t >= 28.78) & (t < 30.0); mix[z] = 0
mix = np.stack([limit(mix[:, 0], .95), limit(mix[:, 1], .95)], 1)
sf.write(os.path.join(D, 'mix.wav'), mix.astype(np.float32), SR)
def rms(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
for a, b, lab in [(0, 5, 'hook'), (5, 10, 'scan'), (15, 20, 'face'), (22.5, 25, 'silence1'), (28.8, 30, 'zero'), (30, 32.5, 'shock'), (32.5, 38, 'rule'), (42.5, 44.5, 'end')]:
    s = slice(int(a * SR), int(b * SR))
    print(f"{lab:9s} music {rms(bus['music'][s]):6.1f}  vo {rms(bus['vo'][s]):6.1f}  sfx {rms(bus['sfx'][s]):6.1f}  bed {rms(bus['bed'][s]):6.1f}  mix {rms(mix[s]):6.1f}")
print('peak', np.abs(mix).max())
