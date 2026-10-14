# Code-made sound for the film: guzheng, dizi, erhu, bells, gong, woodblock; rain, wind, thunder, crowd, steps, splashes.
import numpy as np, wave
from scipy.signal import fftconvolve, butter, sosfilt
SR = 48000

def note(m): return 440.0 * 2 ** ((m - 69) / 12)
def tt(d): return np.arange(int(d * SR)) / SR
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, min(hi, SR / 2 - 100)], btype='band', fs=SR, output='sos'), x).astype(np.float32)
def lp(x, hi, order=2): return sosfilt(butter(order, hi, fs=SR, output='sos'), x).astype(np.float32)
def hp(x, lo, order=2): return sosfilt(butter(order, lo, btype='high', fs=SR, output='sos'), x).astype(np.float32)

PENT = [50, 52, 54, 57, 59, 62, 64, 66, 69, 71, 74, 76, 78, 81, 83, 86, 88, 90, 93]    # D major pentatonic
MINP = [50, 53, 55, 57, 60, 62, 65, 67, 69, 72, 74, 77, 79, 81, 84, 86]                 # D minor pentatonic (sad / night)

class Mix:
    def __init__(self, dur, seed=1):
        self.dur = dur; self.N = int(dur * SR) + SR; self.buf = np.zeros((self.N, 2), np.float32); self.dry = np.zeros((self.N, 2), np.float32)
        self.r = np.random.default_rng(seed)
    def add(self, sig, at, g=1.0, pan=0.5, wet=True):
        if sig.ndim == 1: sig = np.stack([sig * np.cos(pan * np.pi / 2), sig * np.sin(pan * np.pi / 2)], 1) * 1.41
        i = int(at * SR)
        if i < 0: sig = sig[-i:]; i = 0
        j = min(self.N, i + len(sig))
        if j > i: (self.buf if wet else self.dry)[i:j] += sig[:j - i] * g

    # ---------------------------------------------------------------- instruments
    def guzheng(self, f, d=3.0, amp=0.3, bend=0.0, bend_at=0.15):
        t = tt(d); vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.25) / 0.4, 0, 1)
        fb = f * (1 + bend * np.clip((t - bend_at) / 0.25, 0, 1)) * vib
        ph = 2 * np.pi * np.cumsum(fb) / SR
        s = sum((0.75 ** (k - 1)) / k ** 0.6 * np.sin(k * ph) * np.exp(-t * (1.4 + 0.9 * k)) for k in range(1, 10))
        pick = bp(self.r.normal(0, 1, len(t)), 2000, 7000) * np.exp(-t * 90) * 0.4
        return ((s + pick) * amp * np.minimum(1, t * 600)).astype(np.float32)
    def dizi(self, f, d, amp=0.12, slide=0.0):
        t = tt(d); vib = 1 + 0.006 * np.sin(2 * np.pi * 5.0 * t) * np.clip((t - 0.2) / 0.3, 0, 1)
        vib *= 1 + slide * (1 - np.clip(t / 0.12, 0, 1))
        ph = 2 * np.pi * f * np.cumsum(vib) / SR
        e = np.minimum(1, t / 0.07) * np.minimum(1, np.maximum(0, d - t) / 0.2)
        tone = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph) + 0.05 * np.sin(4 * ph)
        breath = bp(self.r.normal(0, 1, len(t)), f * 1.5, min(15000, f * 6)) * 0.25
        buzz = np.sin(ph) * bp(self.r.normal(0, 1, len(t)), 3000, 8000) * 0.08
        return ((tone + breath + buzz) * e * amp).astype(np.float32)
    def erhu(self, f, d, amp=0.10, slide=0.0):
        """bowed two-string fiddle: sawtooth-ish with a nasal formant, slow vibrato, a slide into the note"""
        t = tt(d); vib = 1 + 0.008 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - 0.3) / 0.5, 0, 1)
        vib *= 1 - slide * np.exp(-t * 10)
        ph = 2 * np.pi * f * np.cumsum(vib) / SR
        s = sum(np.sin(k * ph) / k * (1.0 if k < 6 else 0.6) for k in range(1, 14))
        s = bp(s.astype(np.float32), 300, 4000) + 0.3 * bp(s.astype(np.float32), 900, 1400)
        bow = bp(self.r.normal(0, 1, len(t)), 1500, 6000) * 0.04
        e = np.minimum(1, t / 0.15) * np.minimum(1, np.maximum(0, d - t) / 0.3)
        return ((s + bow) * e * amp).astype(np.float32)
    def bell(self, f, d=4, amp=0.2):
        t = tt(d); s = sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * dk) for k, a, dk in [(1, 1, 0.9), (2.0, 0.5, 1.4), (2.76, 0.4, 2.2), (5.4, 0.2, 3.5)])
        return (s * amp * np.minimum(1, t * 300)).astype(np.float32)
    def chime(self, f, amp=0.08):
        t = tt(1.5); return (sum(a * np.sin(2 * np.pi * f * k * t) * np.exp(-t * dk) for k, a, dk in [(1, 1, 3), (2.4, 0.4, 5), (4.1, 0.2, 8)]) * amp).astype(np.float32)
    def gong(self, d=6, amp=0.35, f0=90):
        t = tt(d)
        s = sum(a * np.sin(2 * np.pi * f0 * k * t * (1 - 0.01 * np.exp(-t * 2))) * np.exp(-t * dk) for k, a, dk in [(1, 1, 0.5), (1.52, 0.6, 0.7), (2.31, 0.45, 0.9), (3.1, 0.3, 1.3), (4.2, 0.2, 1.8)])
        swell = bp(self.r.normal(0, 1, len(t)), 200, 1500) * np.exp(-t * 0.8) * np.minimum(1, t * 3) * 0.15
        return ((s + swell) * amp * np.minimum(1, t * 200)).astype(np.float32)
    def woodblock(self, f=900, amp=0.15):
        t = tt(0.15); return (np.sin(2 * np.pi * f * t) * np.exp(-t * 60) * amp + bp(self.r.normal(0, 1, len(t)), 1500, 5000) * np.exp(-t * 200) * amp * 0.3).astype(np.float32)
    def drum(self, f=70, amp=0.3, d=0.8):
        t = tt(d); return (np.sin(2 * np.pi * f * t * (1 + 0.5 * np.exp(-t * 30))) * np.exp(-t * 6) * amp + lp(self.r.normal(0, 1, len(t)), 500) * np.exp(-t * 40) * amp * 0.3).astype(np.float32)

    # ---------------------------------------------------------------- phrases
    def zheng_phrase(self, at, notes, step=0.5, amp=0.25, pan=0.4, d=3.0):
        """notes: list of midi (or None for rest); evenly spaced"""
        for i, m in enumerate(notes):
            if m is None: continue
            b = 0.0
            if isinstance(m, tuple): m, b = m
            self.add(self.guzheng(note(m), d, amp, b), at + i * step, 1, pan)
    def gliss(self, at, lo=62, hi=93, dt=0.06, amp=0.15, down=False, scale=PENT):
        ns = [m for m in scale if lo <= m <= hi]
        if down: ns = ns[::-1]
        for i, m in enumerate(ns): self.add(self.guzheng(note(m), 2.5, amp), at + i * dt, 1, 0.3 + 0.4 * i / max(1, len(ns)))
    def tremolo(self, at, m, d, amp=0.06, pan=0.55):
        n = int(d / 0.07)
        for k in range(n): self.add(self.guzheng(note(m), 0.5, amp * (0.6 + 0.4 * np.sin(np.pi * k / max(1, n)))), at + k * 0.07, 1, pan)
    def melody(self, at, seq, inst='dizi', amp=0.10, pan=0.6):
        """seq: list of (midi or None, beats); beat = 0.5 s unless (midi, dur_sec) given via 'secs' style"""
        t = at
        for m, d in seq:
            if m is not None:
                if inst == 'dizi': self.add(self.dizi(note(m), d + 0.08, amp), t, 1, pan)
                elif inst == 'erhu': self.add(self.erhu(note(m), d + 0.1, amp), t, 1, pan)
                else: self.add(self.guzheng(note(m), max(1.5, d * 2), amp * 2.2), t, 1, pan)
            t += d
        return t
    def pad(self, at, d, notes, amp=0.03):
        """soft held chord (bowed, very quiet)"""
        for m in notes: self.add(self.erhu(note(m), d, amp), at, 1, 0.5)

    # ---------------------------------------------------------------- ambiences (with level envelopes)
    def env(self, keys, n):
        tk = np.array([k[0] for k in keys]) * SR; vk = np.array([k[1] for k in keys])
        return np.interp(np.arange(n), tk, vk).astype(np.float32)
    def rain(self, keys, heavy=1.0, t0=0.0, t1=None):
        t1 = t1 or self.dur; n = int((t1 - t0) * SR); r = self.r
        e = self.env([(k[0] - t0, k[1]) for k in keys], n)
        hiss = bp(r.normal(0, 1, n), 2500, 9000) * 0.05 + bp(r.normal(0, 1, n), 300, 1500) * 0.035 * heavy
        mod = 1 + 0.15 * np.sin(2 * np.pi * 0.11 * np.arange(n) / SR)
        self.add(np.stack([hiss * mod * e, np.roll(hiss, 4000) * mod * e], 1), t0, 1, wet=False)
        dur = t1 - t0
        for k in range(int(70 * dur)):
            at = r.random() * dur; lv = e[min(n - 1, int(at * SR))]
            if lv < 0.02: continue
            f = 1500 + r.random() * 4000; t = tt(0.02)
            self.add((np.sin(2 * np.pi * f * t * (1 - 3 * t)) * np.exp(-t * 300) * 0.03 * lv).astype(np.float32), t0 + at, 0.5 + r.random(), r.random())
    def drips(self, t0, t1, rate=2.0, amp=0.06):
        r = self.r
        for k in range(int((t1 - t0) * rate)):
            at = t0 + r.random() * (t1 - t0); f = 700 + r.random() * 700; t = tt(0.12)
            self.add((np.sin(2 * np.pi * f * (1 + 2.5 * t) * t) * np.exp(-t * 45) * amp).astype(np.float32), at, 1, 0.2 + 0.6 * r.random())
    def drip(self, at, amp=0.12, f=900):
        t = tt(0.2); self.add((np.sin(2 * np.pi * f * (1 + 2.5 * t) * t) * np.exp(-t * 35) * amp).astype(np.float32), at, 1, 0.5)
    def wind(self, t0, t1, amp=0.05, lo=200, hi=1200):
        n = int((t1 - t0) * SR); r = self.r
        x = bp(r.normal(0, 1, n), lo, hi) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * np.arange(n) / SR + r.random() * 6))
        e = np.minimum(1, np.minimum(np.arange(n) / SR / 1.0, (n - np.arange(n)) / SR / 1.0))
        self.add(np.stack([x * e, np.roll(x, 3000) * e], 1) * amp, t0, 1, wet=False)
    def cicadas(self, t0, t1, amp=0.025):
        n = int((t1 - t0) * SR); t = np.arange(n) / SR; r = self.r
        x = np.sin(2 * np.pi * 4300 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 38 * t)) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * t))
        x += bp(r.normal(0, 1, n), 4000, 7000) * 0.5
        e = np.minimum(1, np.minimum(t / 2, (t[-1] - t) / 2))
        self.add(np.stack([x * e, np.roll(x, 900) * e], 1).astype(np.float32) * amp, t0, 1, wet=False)
    def crickets(self, t0, t1, amp=0.02):
        r = self.r
        for k in range(int((t1 - t0) * 3)):
            at = t0 + r.random() * (t1 - t0); t = tt(0.25); f = 4500 + r.random() * 600
            x = np.sin(2 * np.pi * f * t) * (np.sin(2 * np.pi * 30 * t) > 0) * np.exp(-t * 6)
            self.add(x.astype(np.float32) * amp, at, 1, r.random())
    def birds(self, t0, t1, amp=0.03):
        r = self.r
        for k in range(int((t1 - t0) * 0.6)):
            at = t0 + r.random() * (t1 - t0); f0 = 2500 + r.random() * 1800
            for j in range(2 + int(r.random() * 3)):
                t = tt(0.09); x = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.3 * np.sin(t * 40))) / SR) * np.sin(np.pi * t / 0.09)
                self.add(x.astype(np.float32) * amp, at + j * 0.13, 1, r.random())
    def thunder(self, at, amp=0.5, far=False):
        t = tt(4.0); r = self.r
        x = lp(r.normal(0, 1, len(t)), 180 if far else 400) * (np.exp(-t * 1.2) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t + r.random())))
        crack = 0 if far else hp(r.normal(0, 1, len(t)), 1500) * np.exp(-t * 18) * 0.5
        self.add((x + crack).astype(np.float32) * amp, at, 1, 0.5)
    def rumble(self, at, d=3.0, amp=0.3, f=40):
        t = tt(d); x = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.5 * t)) * np.sin(np.pi * t / d) + lp(self.r.normal(0, 1, len(t)), 120) * np.sin(np.pi * t / d) * 2
        self.add(x.astype(np.float32) * amp, at, 1, 0.5)
    def step(self, at, amp=0.06, soft=False):
        t = tt(0.08); x = bp(self.r.normal(0, 1, len(t)), 200, 1500 if soft else 3000) * np.exp(-t * 60)
        self.add(x.astype(np.float32) * amp, at, 1, 0.4 + 0.2 * self.r.random())
    def steps(self, t0, t1, rate=2.2, amp=0.05, soft=False):
        k = 0
        while t0 + k / rate < t1: self.step(t0 + k / rate, amp, soft); k += 1
    def knock(self, at, amp=0.15):
        t = tt(0.2); x = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 40) + bp(self.r.normal(0, 1, len(t)), 500, 3000) * np.exp(-t * 80) * 0.4
        self.add(x.astype(np.float32) * amp, at, 1, 0.5)
    def crack(self, at, amp=0.3):
        t = tt(0.4); x = hp(self.r.normal(0, 1, len(t)), 2000) * np.exp(-t * 25) + np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 30) * 0.3
        self.add(x.astype(np.float32) * amp, at, 1, 0.5)
    def shatter(self, at, amp=0.35):
        self.crack(at, amp)
        for k in range(14): self.add(self.chime(2000 + self.r.random() * 3000, 0.04), at + 0.05 + self.r.random() * 0.4, 1, self.r.random())
    def splash(self, at, amp=0.2):
        t = tt(0.8); x = bp(self.r.normal(0, 1, len(t)), 400, 5000) * np.exp(-t * 6) * np.minimum(1, t * 50)
        self.add(x.astype(np.float32) * amp, at, 1, 0.5)
    def whoosh(self, at, d=1.0, amp=0.15, up=True):
        t = tt(d); n = len(t); x = self.r.normal(0, 1, n)
        out = np.zeros(n, np.float32); seg = 2400
        for i in range(0, n, seg):
            u = i / n; fc = 300 + 3000 * (u if up else 1 - u)
            out[i:i + seg] = bp(x[i:i + seg], fc * 0.7, fc * 1.4)
        self.add(out * np.sin(np.pi * t / d).astype(np.float32) * amp, at, 1, 0.5)
    def giggle(self, at, d=2.0, amp=0.07):
        """the giggling breeze: a run of little wind-chime laughs"""
        k = 0; r = self.r
        while k * 0.09 < d:
            f = note(PENT[10 + int(r.random() * 8)]); self.add(self.chime(f, amp * (0.5 + 0.5 * r.random())), at + k * 0.09, 1, 0.3 + 0.4 * r.random()); k += 1
    def crowd(self, t0, t1, amp=0.03, cheer=False):
        n = int((t1 - t0) * SR); r = self.r; x = np.zeros(n, np.float32)
        for k in range(10):
            f = 120 + r.random() * 160; tt_ = np.arange(n) / SR
            v = np.sin(2 * np.pi * f * tt_ * (1 + 0.05 * np.sin(2 * np.pi * (0.5 + r.random()) * tt_))) * (np.sin(2 * np.pi * (2 + r.random() * 3) * tt_ + r.random() * 6) > 0.3)
            x += bp(v.astype(np.float32), 200, 2500) * 0.2
        if cheer: x += bp(r.normal(0, 1, n), 800, 4000) * 0.5
        e = np.minimum(1, np.minimum(np.arange(n) / SR / 0.6, (n - np.arange(n)) / SR / 0.6))
        self.add(np.stack([x * e, np.roll(x, 2000) * e], 1) * amp, t0, 1, wet=False)
    def roar(self, at, d=2.5, amp=0.3):
        t = tt(d); f = 70 * (1 + 0.3 * np.sin(np.pi * t / d))
        x = sum(np.sin(2 * np.pi * np.cumsum(f * k) / SR) / k for k in range(1, 8)) * np.sin(np.pi * t / d)
        x = x + bp(self.r.normal(0, 1, len(t)), 200, 1200) * np.sin(np.pi * t / d) * 0.5
        self.add(x.astype(np.float32) * amp, at, 1, 0.5)
    def breath(self, at, d=2.0, amp=0.08):
        t = tt(d); x = bp(self.r.normal(0, 1, len(t)), 150, 700) * np.sin(np.pi * t / d) ** 2
        self.add(x.astype(np.float32) * amp, at, 1, 0.5)
    def creak(self, at, amp=0.08):
        t = tt(0.5); f = 300 + 80 * np.sin(2 * np.pi * 3 * t)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (np.sin(2 * np.pi * 25 * t) > 0) * np.sin(np.pi * t / 0.5)
        self.add(bp(x.astype(np.float32), 400, 2500) * amp, at, 1, 0.5)
    def squawk(self, at, amp=0.12):
        t = tt(0.35); f = 900 * (1 - 0.4 * t / 0.35)
        x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.sin(np.pi * t / 0.35)
        self.add(bp(x.astype(np.float32), 600, 3500) * amp, at, 1, 0.6)
    def snort(self, at, amp=0.08):
        t = tt(0.25); x = bp(self.r.normal(0, 1, len(t)), 300, 1200) * np.exp(-t * 14)
        self.add(x.astype(np.float32) * amp, at, 1, 0.6)
    def sweep(self, at, amp=0.06):
        t = tt(0.5); x = bp(self.r.normal(0, 1, len(t)), 1500, 6000) * np.sin(np.pi * t / 0.5)
        self.add(x.astype(np.float32) * amp, at, 1, 0.5)
    def pour(self, at, d=1.5, amp=0.08):
        t = tt(d); x = bp(self.r.normal(0, 1, len(t)), 600, 3000) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * t / d)
        self.add(x.astype(np.float32) * amp, at, 1, 0.5)
    def chopsticks(self, t0, t1, amp=0.05):
        r = self.r
        for k in range(int((t1 - t0) * 1.5)):
            at = t0 + r.random() * (t1 - t0); t = tt(0.05)
            self.add((np.sin(2 * np.pi * (2500 + r.random() * 800) * t) * np.exp(-t * 120) * amp).astype(np.float32), at, 1, 0.4 + 0.2 * r.random())
    def pencil(self, t0, t1, amp=0.025):
        n = int((t1 - t0) * SR); x = bp(self.r.normal(0, 1, n), 2000, 8000) * (np.sin(2 * np.pi * 3 * np.arange(n) / SR) > -0.2)
        self.add(x.astype(np.float32) * amp, t0, 1, 0.5)
    def oar(self, at, amp=0.1):
        t = tt(1.2); x = bp(self.r.normal(0, 1, len(t)), 200, 1500) * np.sin(np.pi * t / 1.2) ** 2
        self.add(x.astype(np.float32) * amp, at, 1, 0.4)

    # ---------------------------------------------------------------- output
    def reverb(self, x, secs=2.2, mix=0.25):
        m = int(secs * SR); t = np.arange(m) / SR; out = np.zeros_like(x)
        for c in range(2):
            ir = np.random.default_rng(c + 9).normal(0, 1, m) * np.exp(-t * 6.9 / secs)
            ir = sosfilt(butter(2, 5000, fs=SR, output='sos'), ir); ir /= np.sqrt((ir ** 2).sum())
            out[:, c] = fftconvolve(x[:, c], ir)[:len(x)]
        return x * (1 - mix) + out * mix * 1.5
    def write(self, fn, fade_in=0.5, fade_out=1.0, gain=2.2):
        y = self.reverb(self.buf) + self.dry
        n = int(self.dur * SR); y = y[:n]
        t = np.arange(n) / SR; y *= np.minimum(1, np.minimum(t / max(0.01, fade_in), (self.dur - t) / max(0.01, fade_out)))[:, None]
        y = np.tanh(y * gain) * 0.9
        with wave.open(fn, 'wb') as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
