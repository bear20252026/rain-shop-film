# Ink-wash painting toolkit: rice paper, washes with bleeding edges, pressure brush strokes, color tints.
# Everything works on float32 "density" layers (0 = no ink, 1 = full ink) that are composited onto paper at the end.
import numpy as np, cv2, math

INK = np.array([0.13, 0.12, 0.14], np.float32)       # warm black (BGR)
PAPER = np.array([0.80, 0.885, 0.925], np.float32)   # rice-paper cream (BGR)

_cache = {}
def vnoise(h, w, scale, seed=0, octaves=3):
    """smooth value noise in 0..1"""
    key = (h, w, scale, seed, octaves)
    if key in _cache: return _cache[key]
    r = np.random.default_rng(abs(int(seed))); out = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        s = max(1, scale / (2 ** o))
        g = r.random((int(math.ceil(h / s)) + 2, int(math.ceil(w / s)) + 2)).astype(np.float32)
        up = cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC)
        out += up[:h, :w] * amp; tot += amp; amp *= 0.5
    out /= tot; out = (out - out.min()) / (out.max() - out.min() + 1e-6)
    if len(_cache) > 60 or sum(a.nbytes for a in _cache.values()) > 300e6: _cache.clear()   # keep memory bounded (several workers run at once)
    _cache[key] = out
    return out

def smooth(x, a, b):
    t = np.clip((x - a) / (b - a + 1e-6), 0, 1); return t * t * (3 - 2 * t)

def paper(h, w, seed=1):
    base = np.broadcast_to(PAPER, (h, w, 3)).copy()
    big = vnoise(h, w, 300, seed, 3); fine = vnoise(h, w, 3, seed + 1, 2)
    r = np.random.default_rng(abs(int(seed)))
    fib = np.zeros((h, w), np.float32)
    for _ in range(int(h * w / 2500)):
        x, y = r.random() * w, r.random() * h; a = r.random() * math.pi; L = 6 + r.random() * 30
        cv2.line(fib, (int(x), int(y)), (int(x + L * math.cos(a)), int(y + L * math.sin(a))), float(0.5 + r.random() * 0.5), 1, cv2.LINE_AA)
    fib = cv2.GaussianBlur(fib, (0, 0), 0.7)
    shade = 1 - 0.05 * (big - 0.5) - 0.035 * (fine - 0.5) + 0.03 * fib
    return np.clip(base * shade[..., None], 0, 1)

def over(D, w):
    """layer translucent ink: D = 1-(1-D)(1-w)"""
    np.multiply(1 - D, 1 - w, out=D); np.subtract(1, D, out=D); return D

def wash(mask, density=0.5, bleed=3.0, rough=0.35, edge=0.35, gran=0.35, var=0.3, seed=0, scale=1.0, full=None):
    """turn a hard 0..1 mask into an ink wash with soft ragged edges, darker pooled rims and granulation.
    full=(H, W, y0, x0): mask is a crop of a bigger layer; noise is taken from that layer's field"""
    h, w = mask.shape
    if full is None: N = lambda sc, sd, o: vnoise(h, w, sc, sd, o)
    else:
        FH, FW, fy, fx = full; N = lambda sc, sd, o: vnoise(FH, FW, sc, sd, o)[fy:fy + h, fx:fx + w]
    m = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), max(0.5, bleed * scale))
    nz = N(10 * scale, seed + 7, 3)
    m = smooth(m + (nz - 0.5) * rough, 0.42, 0.58)
    rim = np.clip(m - cv2.GaussianBlur(m, (0, 0), 5 * scale), 0, 1) * 2.2
    g = N(2.5 * scale, seed + 3, 2); v = N(120 * scale, seed + 11, 3)
    d = m * density * (1 + gran * (g - 0.5)) * (1 + var * (v - 0.5)) + rim * edge * density
    return np.clip(d, 0, 1)

def stroke_mask(shape, pts, widths, dry=0.0, seed=0, taper=True):
    """pressure brush: pts list of (x,y); widths list (same length) or scalar. Returns density mask 0..1"""
    h, w = shape; m = np.zeros((h, w), np.float32)
    pts = np.asarray(pts, np.float32)
    if np.isscalar(widths): widths = np.full(len(pts), widths, np.float32)
    widths = np.asarray(widths, np.float32)
    if len(widths) != len(pts): widths = np.interp(np.linspace(0, 1, len(pts)), np.linspace(0, 1, len(widths)), widths).astype(np.float32)
    # resample densely
    seg = np.sqrt(((pts[1:] - pts[:-1]) ** 2).sum(1)); L = seg.sum()
    if L < 1: return m
    n = max(2, int(L / 0.8)); cum = np.concatenate([[0], np.cumsum(seg)]); s = np.linspace(0, L, n)
    xs = np.interp(s, cum, pts[:, 0]); ys = np.interp(s, cum, pts[:, 1]); ws = np.interp(s, cum, widths)
    if taper:
        u = s / L; ws = ws * np.minimum(1, np.minimum(u / 0.08, (1 - u) / 0.15) * 0.8 + 0.2)
    for x, y, r in zip(xs, ys, ws):
        cv2.circle(m, (int(x * 4), int(y * 4)), max(1, int(r * 4 / 2)), 1.0, -1, cv2.LINE_AA, 2)
    if dry > 0:
        r = np.random.default_rng(abs(int(seed)))
        # streaks along the stroke: perpendicular offsets that skip ink
        streak = np.ones((h, w), np.float32)
        for k in range(int(3 + dry * 6)):
            off = (r.random() - 0.5) * 0.9; start = r.random() * 0.5 + 0.3 * dry; end = min(1, start + 0.2 + r.random() * 0.6)
            i0, i1 = int(start * n), int(end * n)
            for i in range(i0, i1, 2):
                dx, dy = (ys[min(i + 1, n - 1)] - ys[max(i - 1, 0)]), -(xs[min(i + 1, n - 1)] - xs[max(i - 1, 0)])
                nn = math.hypot(dx, dy) + 1e-6
                cx, cy = xs[i] + dx / nn * off * ws[i], ys[i] + dy / nn * off * ws[i]
                cv2.circle(streak, (int(cx * 4), int(cy * 4)), max(1, int(ws[i] * 0.05 * 4)), 0.0, -1, cv2.LINE_AA, 2)
        m *= cv2.GaussianBlur(streak, (0, 0), 0.6)
    return m

def stroke(D, pts, widths, density=0.9, dry=0.2, seed=0, bleed=0.8, taper=True):
    # work only inside the stroke's bounding box (big speed-up on wide canvases)
    p = np.asarray(pts, np.float32).reshape(-1, 2)
    wmax = float(np.max(widths)) if not np.isscalar(widths) else float(widths)
    pad = int(wmax + bleed * 4 + 6)
    x0 = max(0, int(p[:, 0].min()) - pad); y0 = max(0, int(p[:, 1].min()) - pad)
    x1 = min(D.shape[1], int(p[:, 0].max()) + pad + 1); y1 = min(D.shape[0], int(p[:, 1].max()) + pad + 1)
    if x1 <= x0 or y1 <= y0: return D
    sub = D[y0:y1, x0:x1]
    m = stroke_mask(sub.shape, p - [x0, y0], widths, dry, seed, taper)
    m = cv2.GaussianBlur(m, (0, 0), bleed)
    g = vnoise(sub.shape[0], sub.shape[1], 2.0, seed + 5, 1)
    over(sub, np.clip(m * density * (0.85 + 0.3 * g), 0, 1)); return D

def poly_mask(shape, polys):
    m = np.zeros(shape, np.uint8)
    for p in polys: cv2.fillPoly(m, [np.round(np.asarray(p) * 8).astype(np.int32)], 255, cv2.LINE_AA, 3)
    return m.astype(np.float32) / 255

def ellipse_mask(shape, c, ax, ang=0):
    m = np.zeros(shape, np.uint8)
    cv2.ellipse(m, (int(c[0] * 8), int(c[1] * 8)), (int(ax[0] * 8), int(ax[1] * 8)), ang, 0, 360, 255, -1, cv2.LINE_AA, 3)
    return m.astype(np.float32) / 255

def composite(paper_img, D, tint=None):
    """D: ink density. tint: list of (alpha HxW, color BGR) multiplied in like watercolor"""
    out = paper_img.copy()
    if tint:
        for a, col in tint:
            out *= 1 - a[..., None] * (1 - np.asarray(col, np.float32))
    out = out * (1 - D[..., None]) + INK * D[..., None]
    return out

def bezier(p0, p1, p2, p3=None, n=24):
    t = np.linspace(0, 1, n)[:, None]; p0, p1, p2 = map(np.asarray, (p0, p1, p2))
    if p3 is None: return ((1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2)
    p3 = np.asarray(p3); return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)
