"""voices_raw/*.wav -> voices/*.wav. The narrator stays natural (light compression happens in mix.py). The fake boss (b1) gets the "AI copy" treatment:
light ring modulation + 6 ms comb + telephone band-pass + saturation."""
import json, os, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
D = os.path.dirname(os.path.abspath(__file__))
lines = json.load(open(os.path.join(D, 'lines.json'), encoding='utf-8'))
os.makedirs(os.path.join(D, 'voices'), exist_ok=True)
dur = {}
for L in lines:
    y, sr = sf.read(os.path.join(D, 'voices_raw', L['id'] + '.wav'))
    if L['id'] == 'b1':
        t = np.arange(len(y)) / sr
        y = y * .8 + y * np.sin(2 * np.pi * 70 * t) * .2 * 1.6
        k = int(.006 * sr); z = y.copy()
        for _ in range(3): z[k:] = z[k:] + .3 * z[:-k] * .8
        y = y * .72 + z * .28
        y = sosfilt(butter(2, [300, 3400], 'bandpass', fs=sr, output='sos'), y)
        y = np.tanh(y / np.abs(y).max() * 1.6) * .8
    sf.write(os.path.join(D, 'voices', L['id'] + '.wav'), y.astype(np.float32), sr)
    dur[L['id']] = round(len(y) / sr, 3)
json.dump(dur, open(os.path.join(D, 'voices', 'dur.json'), 'w'), indent=1)
print(dur)
