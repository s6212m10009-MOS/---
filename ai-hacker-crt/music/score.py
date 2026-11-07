"""Original analog-synth score, rendered with numpy only (no samples). 96 BPM (beat .625 s, bar 2.5 s), D minor.
 0.2-5.0 sub drone | 5.0-10.0 square 16th sequencer enters | 10-15 filter opens | 15-20 single saw arpeggio grows with the face
 20-28.75 drone only (the call, the silence) | 28.75-30.0 digital zero | 30.0 gated-reverb hit | 32.5-40 one major chord (D) | 40-44.5 drone fades to nothing.
Writes music/score.wav (stereo, 48 kHz)."""
import os, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; D = os.path.dirname(os.path.abspath(__file__)); DUR = 44.5; N = int(DUR * SR)
rng = np.random.default_rng(11); BEAT = 60 / 96
t_all = np.arange(N) / SR
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def saw(f, n, detune=0.0):
    ph = np.cumsum(np.full(n, f * (1 + detune) / SR)); return 2 * (ph % 1) - 1
def sq(f, n): return np.sign(np.sin(2 * np.pi * np.cumsum(np.full(n, f / SR))))
def lp(x, f, o=4): return sosfilt(butter(o, min(f, SR * .45), 'low', fs=SR, output='sos'), x)
def adsr(n, a, d, s, r):
    e = np.ones(n); na, nd, nr = int(a * SR), int(d * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, max(na, 1)); e[na:na + nd] = np.linspace(1, s, max(nd, 1))[:max(0, n - na)] if nd else s
    e[na + nd:] = s
    if nr and nr < n: e[-nr:] *= np.linspace(1, 0, nr)
    return e
L = np.zeros(N); R = np.zeros(N)
def put(x, at, g=1.0, pan=0.0):
    i = int(at * SR)
    if i >= N: return
    x = x[:N - i] * g; l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(x)] += x * l * 1.414; R[i:i + len(x)] += x * r * 1.414
def reverb(x, rt=1.6, wet=.5):
    n = int(rt * SR); ir = rng.standard_normal(n) * np.exp(-np.arange(n) / (rt * SR / 4)); ir = lp(ir, 3500, 2); ir /= np.abs(ir).sum() / 8
    return x * (1 - wet) + fftconvolve(x, ir)[:len(x)] * wet

# --- drone: D1 + D2 saws, slow filter breathing, tape wow, a fifth appears in the middle ---
def drone(t0, t1, g, cut):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR
    wow = 1 + .0017 * np.sin(2 * np.pi * .35 * tt)
    x = saw(36.71 * wow.mean(), n) * .7 + saw(73.42, n, .003) * .35 + sq(36.71, n) * .25
    x = lp(x, cut, 4); e = np.minimum(1, tt / 1.5) * np.minimum(1, (t1 - t0 - tt) / 1.5)
    put(x * e, t0, g)
drone(.2, 5.0, .30, 220); drone(5.0, 22.4, .30, 320); drone(22.4, 28.75, .28, 200)
drone(30.0, 41.5, .26, 380)
# --- sequencer (square 16ths), enters at 5.0, filter opens 10-15, off at 20 ---
def seq(t0, t1):
    pat = [38, 38, 50, 38, 45, 38, 50, 38, 41, 38, 50, 38, 45, 38, 53, 38]        # D2 / A2 / F2 around D1-D2
    k = 0; t = t0
    while t < t1 - .01:
        m = pat[k % 16]; f = hz(m); d = BEAT / 4
        cut = 350 + 2600 * ((t - 5.0) / 10.0) ** 1.3                              # the filter opens
        n = int(d * SR * 1.1); tt = np.arange(n) / SR
        x = lp(sq(f, n) * .6 + saw(f, n, .004) * .4, cut, 2) * np.exp(-tt / (d * .8))
        vel = .55 + .45 * ((k % 4) == 0)
        put(x, t, .18 * vel * (.4 + .6 * min(1, (t - t0) / 2.5)), -.2 + .4 * ((k // 2) % 2))
        k += 1; t += d
seq(5.0, 20.0)
# --- arpeggio that grows as the face forms: notes are added bar by bar ---
def arp(t0, t1):
    notes = [62, 65, 69, 72, 74, 77, 81]                                            # D4 F4 A4 C5 D5 F5 A5 (Dm9-ish)
    k = 0; t = t0
    while t < t1:
        nn = 2 + int((t - t0) / (t1 - t0) * (len(notes) - 2)); m = notes[k % nn]
        n = int(BEAT * SR * .9); tt = np.arange(n) / SR
        x = lp(saw(hz(m), n) + saw(hz(m), n, .005), 2400 + 2000 * (t - t0) / (t1 - t0), 2) * np.exp(-tt / .22)
        put(x, t, .12 * (.5 + .5 * (t - t0) / (t1 - t0)), (-1) ** k * .35)
        k += 1; t += BEAT / 2
arp(15.0, 20.0)
# --- the hit at 30.0: gated reverb noise + low thump ---
n = int(1.2 * SR); tt = np.arange(n) / SR
hit = lp(rng.standard_normal(n), 3000, 2) * np.exp(-tt / .12) * .8 + np.sin(2 * np.pi * (60 - 25 * np.minimum(1, tt / .2)) * tt) * np.exp(-tt / .25) * 1.4
hit = reverb(hit, 1.2, .5) * (tt < .32) * np.minimum(1, (.32 - tt) / .02) + hit * (tt >= .32) * 0
put(hit, 30.0, .9)
# --- the chord at 32.5: D major, the only major chord; long reverb; held to ~40 ---
def pad(f, t0, t1, g):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR
    x = lp(saw(f, n, .003) + saw(f, n, -.004) + saw(f * 2, n) * .3, 2600, 2)
    e = np.minimum(1, tt / .06) * np.minimum(1, (t1 - t0 - tt) / 2.5)
    put(x * e, t0, g, rng.uniform(-.4, .4))
for m, g in [(50, .22), (57, .18), (62, .17), (66, .16), (69, .14), (74, .1)]: pad(hz(m), 32.5, 40.5, g)
# --- master: reverb on the pad region, silence windows ---
for ch in (L, R):
    ch[int(32.0 * SR):int(43 * SR)] = reverb(ch[int(32.0 * SR):int(43 * SR)], 2.0, .35)
    ch[int(28.75 * SR):int(30.0 * SR)] = 0                                           # digital zero: reverb tails included
    ch[int(41.5 * SR):] *= np.clip(1 - (t_all[int(41.5 * SR):] - 41.5) / 1.2, 0, 1)    # everything gone before the last held cursor
m = np.stack([L, R], 1); m = np.tanh(m * 1.1) * .9
sf.write(os.path.join(D, 'score.wav'), m.astype(np.float32), SR)
print('score', DUR, 's, peak', np.abs(m).max())
