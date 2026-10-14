# Style-test sound: rain on tiles and canal, eave drips, guzheng, dizi flute, a glow chime, a guzheng glissando for the pour, gong on the title.
import sys, numpy as np, wave
from scipy.signal import fftconvolve, butter, sosfilt
SR = 48000; DUR = 20.0
N = int(DUR * SR); buf = np.zeros((N, 2), np.float32); r = np.random.default_rng(3)
def note(m): return 440.0 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR
def add(sig, at, g=1.0, pan=0.5):
    if sig.ndim == 1: sig = np.stack([sig * np.cos(pan * np.pi / 2), sig * np.sin(pan * np.pi / 2)], 1) * 1.41
    i = int(at * SR); j = min(N, i + len(sig))
    if j > i: buf[i:j] += sig[:j - i] * g
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x).astype(np.float32)

def guzheng(f, d=3.0, amp=0.3, bend=0.0):
    t = tt(d); vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.25) / 0.4, 0, 1)
    fb = f * (1 + bend * np.clip((t - 0.15) / 0.25, 0, 1)) * vib
    ph = 2 * np.pi * np.cumsum(fb) / SR
    s = sum((0.75 ** (k - 1)) / k ** 0.6 * np.sin(k * ph) * np.exp(-t * (1.4 + 0.9 * k)) for k in range(1, 10))
    pick = bp(r.normal(0, 1, len(t)), 2000, 7000) * np.exp(-t * 90) * 0.4
    return ((s + pick) * amp * np.minimum(1, t * 600)).astype(np.float32)

def dizi(f, d, amp=0.12):
    t = tt(d); vib = 1 + 0.006 * np.sin(2 * np.pi * 5.0 * t) * np.clip((t - 0.2) / 0.3, 0, 1)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    e = np.minimum(1, t / 0.07) * np.minimum(1, np.maximum(0, d - t) / 0.2)
    tone = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph) + 0.05 * np.sin(4 * ph)
    breath = bp(r.normal(0, 1, len(t)), f * 1.5, min(15000, f * 6)) * 0.25
    buzz = np.sin(ph) * bp(r.normal(0, 1, len(t)), 3000, 8000) * 0.08     # the membrane buzz
    return ((tone + breath + buzz) * e * amp).astype(np.float32)

def bell(f, d=4, amp=0.2):
    t = tt(d); s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * dk) for k, a, dk in [(1, 1, 0.9), (2.0, 0.5, 1.4), (2.76, 0.4, 2.2), (5.4, 0.2, 3.5)])
    return (s * amp * np.minimum(1, t * 300)).astype(np.float32)

def gong(d=6, amp=0.35):
    t = tt(d); f0 = 90
    s = sum(a * np.sin(2 * np.pi * f0 * k * t * (1 - 0.01 * np.exp(-t * 2))) * np.exp(-t * dk) for k, a, dk in [(1, 1, 0.5), (1.52, 0.6, 0.7), (2.31, 0.45, 0.9), (3.1, 0.3, 1.3), (4.2, 0.2, 1.8)])
    swell = bp(r.normal(0, 1, len(t)), 200, 1500) * np.exp(-t * 0.8) * np.minimum(1, t * 3) * 0.15
    return ((s + swell) * amp * np.minimum(1, t * 200)).astype(np.float32)

# ---- rain bed: hiss on tiles + softer canal wash + random droplets
n = N
hiss = bp(r.normal(0, 1, n), 2500, 9000) * 0.05 + bp(r.normal(0, 1, n), 300, 1500) * 0.035
mod = 1 + 0.15 * np.sin(2 * np.pi * 0.11 * np.arange(n) / SR)
add(np.stack([hiss * mod, np.roll(hiss, 4000) * mod], 1), 0)
for k in range(1400):
    at = r.random() * DUR; f = 1500 + r.random() * 4000; d = 0.02
    t = tt(d); add((np.sin(2 * np.pi * f * t * (1 - 3 * t)) * np.exp(-t * 300) * 0.03).astype(np.float32), at, 0.5 + r.random(), r.random())
# eave drips: round "plip" sounds
for k in range(40):
    at = 0.5 + r.random() * 19; f = 700 + r.random() * 700; t = tt(0.12)
    add((np.sin(2 * np.pi * f * (1 + 2.5 * t) * t) * np.exp(-t * 45) * 0.06).astype(np.float32), at, 1, 0.3 + 0.4 * r.random())

# ---- music: D major pentatonic (D E F# A B)
PENT = [62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86]
# guzheng opening: sparse low phrase
for at, m, b in [(1.0, 50, 0), (1.6, 57, 0), (2.4, 62, 0.06), (4.0, 54, 0), (4.6, 57, 0), (5.4, 59, -0.03), (7.0, 50, 0), (7.6, 57, 0), (8.4, 66, 0.05)]:
    add(guzheng(note(m), 3.5, 0.28, b), at, 1, 0.4)
# dizi melody over it
for at, m, d in [(5.6, 81, 1.0), (6.6, 78, 0.5), (7.1, 76, 0.5), (7.6, 74, 1.4), (9.2, 76, 0.5), (9.7, 78, 0.5), (10.2, 81, 0.6)]:
    add(dizi(note(m), d + 0.1, 0.10), at, 1, 0.6)
# the glowing drop: a bright bell + soft chord
add(bell(note(93), 4, 0.12), 10.5, 1, 0.45); add(bell(note(98), 3, 0.06), 10.55, 1, 0.6)
for m in (62, 66, 69): add(guzheng(note(m), 4, 0.12), 10.6, 1, 0.5)
# pour: guzheng glissando up the pentatonic scale
for i, m in enumerate(PENT + [88, 90, 93]):
    add(guzheng(note(m), 2.5, 0.16), 14.5 + i * 0.07, 1, 0.3 + 0.03 * i)
# jar glows: tremolo on a high A (guzheng 'yao zhi')
for k in range(int(1.6 / 0.07)):
    add(guzheng(note(81), 0.5, 0.05 + 0.03 * np.sin(np.pi * k / 23)), 15.6 + k * 0.07, 1, 0.55)
# dizi long tone into the title
add(dizi(note(74), 2.2, 0.09), 15.8, 1, 0.6)
# title: gong and a low open fifth
add(gong(5, 0.4), 17.3, 1, 0.5)
for m in (38, 45, 50, 57): add(guzheng(note(m), 4.5, 0.18), 17.35, 1, 0.45)
add(bell(note(86), 3, 0.06), 18.2, 1, 0.7)   # the red seal

# ---- reverb and master
def reverb(x, secs=2.2, mix=0.25):
    m = int(secs * SR); t = np.arange(m) / SR; out = np.zeros_like(x)
    for c in range(2):
        ir = np.random.default_rng(c + 9).normal(0, 1, m) * np.exp(-t * 6.9 / secs)
        ir = sosfilt(butter(2, 5000, fs=SR, output='sos'), ir); ir /= np.sqrt((ir ** 2).sum())
        out[:, c] = fftconvolve(x[:, c], ir)[:len(x)]
    return x * (1 - mix) + out * mix * 1.5
y = reverb(buf)
t = np.arange(N) / SR; y *= np.minimum(1, np.minimum(t / 1.0, (DUR - t) / 0.8))[:, None]
y = y / np.abs(y).max() * 1.3; y = np.tanh(y) / np.tanh(1.3) * 0.88
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
print('ok')
