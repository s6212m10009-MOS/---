import sys, numpy as np, wave
sys.path.insert(0, sys.argv[1] + "/core/audio")
from sfx import SR, t_, env_exp, bp, lp, hp, noise, click
DUR = 21.5; N = int(DUR * SR); out = np.zeros((N, 2), np.float32)
def add(x, at, g=1.0, pan=0.0):
    i = int(at * SR); n = min(len(x), N - i)
    if n <= 0: return
    out[i:i+n, 0] += x[:n] * g * (1 - max(0, pan)); out[i:i+n, 1] += x[:n] * g * (1 + min(0, pan))
def tone(f, d, tau, harm=((1, 1), (4, .25), (10, .08))):
    tt = t_(d); return sum(a * np.sin(2*np.pi*f*h*tt) for h, a in harm) * env_exp(d, tau) * np.minimum(1, tt / .003)
def kick(): tt = t_(.3); return np.sin(2*np.pi*(50 + 90*np.exp(-tt/.03))*tt) * np.exp(-tt/.12)
def hat(): return hp(noise(.06), 7000) * env_exp(.06, .012) * .5
def whoosh(d=.5, up=True):
    x = noise(d); tt = t_(d); e = np.sin(np.pi * np.minimum(1, tt / d)) ** 2
    return bp(x, 400, 3500) * e * .6
def ping(f=1760): return tone(f, .6, .15, ((1, 1), (2.76, .3)))
def thump(): tt = t_(.25); return np.sin(2*np.pi*70*tt) * np.exp(-tt/.07)
BPM = 110; B = 60 / BPM
penta = [261.6, 293.7, 329.6, 392.0, 440.0, 523.3, 587.3, 659.3]
bass = [130.8, 98.0, 110.0, 87.3]  # C G A F per bar
bars = int(DUR / (B * 4)) + 1
rng = np.random.default_rng(3)
music = np.zeros((N, 2), np.float32)
saved, out = out, music
for bar in range(bars):
    t0 = bar * 4 * B
    if t0 >= DUR: break
    add(tone(bass[bar % 4], B * 1.8, .5, ((1, 1), (2, .3))), t0, .30)
    add(tone(bass[bar % 4], B * 1.8, .5, ((1, 1), (2, .3))), t0 + 2 * B, .26)
    for k in range(4): add(kick(), t0 + k * B, .35 if k % 2 == 0 else .0)
    for k in range(8): add(hat(), t0 + k * B / 2 + B / 4 * 0 + B / 2 * (k % 2 == 1) * 0, .10 if k % 2 else .06)
    for k in range(8):
        f = penta[(bar * 3 + k * 2 + (k % 3)) % len(penta)] * (2 if k % 4 == 3 else 1)
        add(tone(f, .5, .13), t0 + k * B / 2, .15, pan=(-.4 if k % 2 else .4))
    pad = [261.6, 329.6, 392.0] if bar % 2 == 0 else [220.0, 261.6, 329.6]
    for f in pad: add(lp(tone(f, 4 * B, 3.0, ((1, 1), (2, .4), (3, .2))), 2200), t0, .05)
# music envelope: fade in, silence 17.0-17.8, fade out
tt = np.arange(N) / SR
env = np.minimum(1, tt / .8) * np.where((tt > 16.9) & (tt < 17.9), 0, 1) * np.minimum(1, (DUR - tt) / 1.5)
env = np.convolve(env, np.ones(2400) / 2400, 'same')
music *= env[:, None].astype(np.float32)
out = saved; out += music
CAPS = [.3, 4.7, 9.3, 13.8, 18.0]
for c in CAPS:
    add(click(1.0, .9), c + .0, .35); add(click(.8, .9), c + .14, .4); add(thump(), c + .14, .25); add(whoosh(.35), c - .05 if c > 1 else 0, .0)
add(thump(), .4, .4); add(ping(1320), .45, .3)               # pin pop (B1)
add(whoosh(.5), .8, .35)                                     # card
for i in range(14): add(click(1.6, .5), .8 + i * .036, .12)  # counter ticks
add(whoosh(.6), 4.5, .4); add(whoosh(.5), 9.4, .4); add(whoosh(.6), 14.0, .4)
for i, t in enumerate([5.6, 6.8, 8.0, 8.6]): add(ping(1320 + i * 220), t, .22)  # route cities
add(thump(), 9.9, .4); add(ping(1320), 9.95, .3); add(whoosh(.5), 10.4, .35)
for i in range(5): add(ping(880 + i * 150), 14.2 + .35 * i + .3, .22)  # region fills
add(whoosh(.5), 15.4, .35)
add(thump(), 18.0, .3)
pk = np.abs(out).max(); out *= .9 / pk
w = wave.open(sys.argv[2], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out * 32767).astype('<i2').tobytes()); w.close(); print('ok', DUR)
