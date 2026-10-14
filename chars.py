# Characters in a loose Feng Zikai-like ink style: rounded silhouettes, few confident lines, soft flat washes, tiny faces.
import numpy as np, cv2, math
from ink import *

INDIGO = (0.66, 0.52, 0.40)   # BGR soft indigo
SKIN = (0.72, 0.82, 0.95)

class Layer:
    """a local drawing box in world coords: density + tint alphas, composited later"""
    def __init__(self, x0, y0, w, h):
        self.x0, self.y0 = int(x0), int(y0); self.D = np.zeros((h, w), np.float32); self.tints = []; self.M = np.zeros((h, w), np.float32)
    def P(self, pts): return np.asarray(pts, np.float32) - [self.x0, self.y0]
    def knock(self, m, k=1.0, roi=None):
        if roi is not None:   # m covers only rows y0:y1, cols x0:x1
            y0, y1, x0, x1 = roi; f = 1 - m * k
            self.D[y0:y1, x0:x1] *= f; np.maximum(self.M[y0:y1, x0:x1], m * k, out=self.M[y0:y1, x0:x1])
            for a, c in self.tints: a[y0:y1, x0:x1] *= f
            return
        self.D *= 1 - m * k; np.maximum(self.M, m * k, out=self.M)
        self.tints = [(a * (1 - m * k), c) for a, c in self.tints]

def lerp(a, b, u): return a + (b - a) * u
def ease(u): u = min(1, max(0, u)); return u * u * (3 - 2 * u)

def path(start, *segs, n=18):
    """start point then segments of (c1, c2, end) cubic beziers; returns polyline"""
    pts = [np.asarray(start, np.float32)]; cur = start
    for c1, c2, e in segs:
        b = bezier(cur, c1, c2, e, n=n); pts.extend(b[1:]); cur = e
    return np.array(pts, np.float32)

def xf(pts, fx, fy, s, lean=0.0, br=0.0):
    """local (feet origin, y up negative) -> world, with a forward lean of the upper body and breathing"""
    p = np.asarray(pts, np.float32).copy()
    up = np.clip(-p[:, 1] / 150.0, 0, 1.3)
    p[:, 0] -= lean * up ** 1.5 * 10
    p[:, 1] += br * up
    return p * s + [fx, fy]

def fill(L, poly, density, tint=None, talpha=0.6, s=1.0, seed=0, gran=0.25, edge=0.35, knock=True):
    H, W = L.D.shape; lp = L.P(poly); sc = max(0.6, s)
    # work only in the shape's box (plus room for the blurs); noise is cut from the full-layer field so it does not shift
    pad = int(math.ceil(4 * max(0.9 * s, 5 * sc) + 6))
    x0, y0 = max(0, int(lp[:, 0].min()) - pad), max(0, int(lp[:, 1].min()) - pad)
    x1, y1 = min(W, int(math.ceil(lp[:, 0].max())) + pad), min(H, int(math.ceil(lp[:, 1].max())) + pad)
    if x1 <= x0 or y1 <= y0: return np.zeros((H, W), np.float32)
    m = poly_mask((y1 - y0, x1 - x0), [lp - [x0, y0]])
    if knock: L.knock(cv2.GaussianBlur(m, (0, 0), 0.6), roi=(y0, y1, x0, x1))
    over(L.D[y0:y1, x0:x1], wash(m, density, bleed=0.9 * s, rough=0.18, seed=seed, gran=gran, edge=edge, var=0.35, scale=sc, full=(H, W, y0, x0)))
    mf = np.zeros((H, W), np.float32); mf[y0:y1, x0:x1] = m
    if tint is not None: L.tints.append((mf * talpha, tint))
    return mf

def line(L, pts, w, s=1.0, density=0.9, dry=0.25, seed=0, taper=True):
    pts = np.asarray(pts, np.float32)
    ws = w if np.isscalar(w) else np.asarray(w, np.float32)
    stroke(L.D, L.P(pts), (ws * s) if np.isscalar(ws) else ws * s, density, dry, seed, bleed=0.6, taper=taper)

def granny(L, fx, fy, t, pose, s=1.0, seed=7):
    """Granny Yun, facing left. pose: hand (local), lean (0..1), look (head tilt up, deg)"""
    lean = pose.get('lean', 0.3); br = math.sin(t * 2.0) * 0.9
    X = lambda pts: xf(pts, fx, fy, s, lean, br)
    # shoes and trousers (short, wide, dark)
    for sx in (-12, 10):
        sh = path((sx - 13, -2), ((sx - 13, -10), (sx + 6, -11), (sx + 9, -6)), ((sx + 11, -2), (sx + 6, 1), (sx - 2, 1)), ((sx - 9, 1), (sx - 14, 1), (sx - 13, -2)))
        fill(L, X(sh), 0.92, s=s, seed=seed + sx)
    tr = path((-19, -52), ((-20, -36), (-22, -18), (-24, -8)), ((-14, -6), (-6, -6), (-2, -8)), ((-1, -24), (2, -30), (4, -30)), ((6, -24), (7, -14), (6, -8)), ((12, -6), (20, -6), (23, -8)), ((22, -20), (24, -38), (24, -54)))
    fill(L, X(tr), 0.58, s=s, seed=seed + 1, gran=0.15)
    line(L, X(path((4, -30), ((5, -22), (5, -14), (5, -9)))), 1.2, s, 0.5, 0, seed + 2)
    # jacket: long, rounded, hunched back
    jk = path((-12, -124), ((-22, -112), (-26, -90), (-27, -54)),
              ((-12, -48), (14, -48), (31, -54)),
              ((33, -78), (33, -104), (24, -122)),
              ((16, -132), (0, -134), (-12, -124)))
    fill(L, X(jk), 0.16, INDIGO, 0.75, s=s, seed=seed + 3, gran=0.2, edge=0.5)
    # back contour (bold) and front contour (lighter), hem
    line(L, X(path((-2, -133), ((12, -132), (28, -118), (32, -96)), ((34, -78), (32, -64), (31, -54)))), np.array([2.0] + [3.4] * 30 + [1.8]), s, 0.92, 0.35, seed + 4)
    line(L, X(path((-12, -124), ((-20, -112), (-25, -92), (-27, -55)))), 2.2, s, 0.85, 0.3, seed + 5)
    line(L, X(path((-27, -54), ((-12, -49), (14, -49), (31, -54)))), 1.8, s, 0.8, 0.4, seed + 6)
    # side-fastened front edge with knot buttons, a soft fold
    line(L, X(path((-8, -127), ((-4, -118), (4, -110), (2, -100)))), 1.4, s, 0.75, 0.2, seed + 7)
    for bx, by in ((-1, -116), (3, -104)):
        over(L.D, ellipse_mask(L.D.shape, L.P(X([(bx, by)]))[0], (1.6 * s, 1.6 * s)) * 0.9)
    line(L, X(path((16, -100), ((14, -86), (16, -72), (12, -60)))), 1.0, s, 0.35, 0.3, seed + 8)
    # head (big and round), hair pulled back into a bun
    look = pose.get('look', 0)
    hcx, hcy = -3, -146
    head = X([(hcx + 18 * math.cos(a), hcy + 19 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40)])
    hm = fill(L, head, 0.03, SKIN, 0.55, s=s, seed=seed + 9, edge=0.2)
    # hair: covers top and back of head
    hair = X(path((-19, -150), ((-18, -164), (-6, -170), (4, -168)), ((14, -166), (20, -156), (17, -142)), ((14, -136), (10, -134), (8, -136)), ((8, -146), (2, -154), (-6, -155)), ((-12, -156), (-16, -154), (-19, -150))))
    fill(L, hair, 0.30, s=s, seed=seed + 10, gran=0.4, edge=0.4)
    for k in range(5):
        a0 = -14 + k * 6
        line(L, X(path((a0, -160 + abs(k - 2)), ((a0 + 6, -166), (a0 + 12, -164), (a0 + 16, -158)))), 0.8, s, 0.45, 0.4, seed + 11 + k)
    bun = X([(18 + 8 * math.cos(a), -158 + 7.5 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 30)])
    fill(L, bun, 0.55, s=s, seed=seed + 20, gran=0.5)
    pin = X([(12, -164), (25, -153)])
    line(L, pin, 1.1, s, 0.55, 0, seed + 21, taper=False)
    L.tints.append((stroke_mask(L.D.shape, L.P(pin), 1.6 * s, taper=False) * 0.6, (0.60, 0.74, 0.55)))
    # head outline: confident single stroke, broken at the back where the hair is
    line(L, X([(hcx + 18 * math.cos(a), hcy + 19 * math.sin(a)) for a in np.linspace(math.pi * 0.42, math.pi * 1.35, 26)]), 1.7, s, 0.9, 0.2, seed + 22)
    # ear
    line(L, X(path((4, -149), ((8, -152), (9, -144), (5, -142)))), 1.2, s, 0.75, 0, seed + 23)
    # face: squinting curved eye (grumpy brow), little nose, downturned mouth, wrinkles
    blink = (t % 4.7) < 0.13
    if blink: line(L, X([(-14, -147), (-8, -147)]), 1.2, s, 0.9, 0, seed + 24, taper=False)
    else:
        line(L, X(path((-15, -148), ((-13, -150), (-10, -150), (-8, -148)))), 1.5, s, 0.95, 0, seed + 24)
        over(L.D, ellipse_mask(L.D.shape, L.P(X([(-11.5, -147.2)]))[0], (1.3 * s, 1.3 * s)) * 0.9)
    line(L, X([(-17, -154), (-12, -155.5), (-7, -154)]), 1.3, s, 0.85, 0.2, seed + 25)
    line(L, X(path((-20, -146), ((-23, -141), (-22, -139), (-18, -139)))), 1.1, s, 0.8, 0, seed + 26)
    line(L, X(path((-17, -133), ((-15, -134.5), (-12, -134.5), (-10, -133)))), 1.1, s, 0.8, 0, seed + 27)
    line(L, X([(-6, -146), (-4, -143)]), 0.8, s, 0.4, 0, seed + 28)
    line(L, X([(-8, -140), (-6, -136)]), 0.8, s, 0.35, 0, seed + 29)
    L.tints.append((ellipse_mask(L.D.shape, L.P(X([(-8, -139)]))[0], (4 * s, 2.5 * s)) * 0.25, (0.55, 0.62, 0.92)))   # rosy cheek
    # arm: wide sleeve from shoulder to wrist, small hand
    hx, hy = pose['hand']
    sx0, sy0 = 4, -120
    ex, ey = (sx0 + hx) / 2 + 4, (sy0 + hy) / 2 + 14
    nrm = lambda ax, ay: (ay / (math.hypot(ax, ay) + 1e-6), -ax / (math.hypot(ax, ay) + 1e-6))
    n1 = nrm(ex - sx0, ey - sy0); n2 = nrm(hx - ex, hy - ey)
    top = [(sx0 + n1[0] * 9, sy0 + n1[1] * 9), (ex + (n1[0] + n2[0]) * 4.5, ey + (n1[1] + n2[1]) * 4.5), (hx + 4 + n2[0] * 9, hy + n2[1] * 9)]
    bot = [(hx + 4 - n2[0] * 9, hy - n2[1] * 9), (ex - (n1[0] + n2[0]) * 4.5, ey - (n1[1] + n2[1]) * 4.5), (sx0 - n1[0] * 9, sy0 - n1[1] * 9)]
    sl = np.vstack([bezier(top[0], top[1], top[2], n=16), bezier(bot[0], bot[1], bot[2], n=16)])
    fill(L, X(sl), 0.18, INDIGO, 0.8, s=s, seed=seed + 30, gran=0.2, edge=0.5)
    line(L, X(bezier(top[0], top[1], top[2], n=16)), 1.8, s, 0.9, 0.3, seed + 31)
    line(L, X(bezier(bot[0], bot[1], bot[2], n=16)), 1.6, s, 0.85, 0.3, seed + 32)
    line(L, X([top[2], bot[0]]), 1.4, s, 0.85, 0, seed + 33, taper=False)
    hand = X([(hx - 3, hy)])[0]
    hm = X([(hx - 3 + 4.5 * math.cos(a), hy + 4 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 20)])
    fill(L, hm, 0.03, SKIN, 0.6, s=s, seed=seed + 34)
    line(L, hm[2:16], 1.0, s, 0.8, 0, seed + 35)
    return hand

def ladle(L, hand, ang_deg, tilt_deg, s=1.0, seed=31, length=100):
    a = math.radians(ang_deg)
    tip = (hand[0] - math.cos(a) * length * s, hand[1] - math.sin(a) * length * s)
    back = (hand[0] + math.cos(a) * 16 * s, hand[1] + math.sin(a) * 16 * s)
    line(L, [back, tip], 2.4, s, 0.85, 0.35, seed, taper=False)
    for k in (0.32, 0.66):
        p = (lerp(back[0], tip[0], k), lerp(back[1], tip[1], k)); nx, ny = -math.sin(a) * 2.4 * s, math.cos(a) * 2.4 * s
        line(L, [(p[0] - nx, p[1] - ny), (p[0] + nx, p[1] + ny)], 1.1, s, 0.8, 0, seed + int(k * 10), taper=False)
    tl = math.radians(tilt_deg); r = 11 * s
    cx, cy = tip[0] - 3 * s, tip[1] + 4 * s
    bowl = [(cx + r * math.cos(th + tl), cy + r * 0.8 * math.sin(th + tl)) for th in np.linspace(0, math.pi, 16)]
    m = poly_mask(L.D.shape, [L.P(bowl)]); L.knock(m)
    over(L.D, wash(m, 0.25, bleed=0.6, seed=seed + 3, scale=s))
    L.tints.append((m * 0.5, (0.55, 0.72, 0.80)))          # bamboo-wood color
    line(L, bowl, 1.7, s, 0.9, 0.2, seed + 4, taper=False)
    line(L, [bowl[0], bowl[-1]], 1.3, s, 0.85, 0, seed + 5, taper=False)
    return (cx, cy + 2 * s), (bowl[0], bowl[-1])

def jar(L, cx, by, s=1.0, seed=41):
    jw, jh = 21 * s, 42 * s
    half = [(cx + jw * (0.5 + 0.5 * math.sin(a)), by - jh * (1 - math.cos(a)) / 2) for a in np.linspace(0, math.pi, 18)]
    body = [(cx - (x - cx), y) for x, y in half[::-1]] + half + [(cx + jw * 0.42, by - jh - 6 * s), (cx - jw * 0.42, by - jh - 6 * s)]
    m = poly_mask(L.D.shape, [L.P(body)]); L.knock(m)
    over(L.D, wash(m, 0.08, bleed=0.6, seed=seed, edge=0.7, scale=s))
    L.tints.append((m * 0.7, (0.70, 0.80, 0.68)))
    line(L, half[::-1] + [(cx, by)], 1.6, s, 0.85, 0.25, seed + 1, taper=False)
    line(L, [(cx - (x - cx), y) for x, y in half], 1.6, s, 0.85, 0.25, seed + 2, taper=False)
    line(L, [(cx - jw * 0.45, by - jh - 6 * s), (cx + jw * 0.45, by - jh - 6 * s)], 2.0, s, 0.9, 0, seed + 3, taper=False)
    L.knock(stroke_mask(L.D.shape, L.P([(cx - jw * 0.55, by - jh * 0.72), (cx - jw * 0.64, by - jh * 0.35)]), 3 * s), 0.8)
    return (cx, by - jh - 6 * s)

def cormorant(L, x, y, t, s=1.0, seed=51, look=0.0):
    """Old Ink sitting on a post top at (x,y). look: 0 faces left, 1 faces right"""
    X = lambda pts: np.asarray(pts, np.float32) * s + [x, y]
    body = X(path((-8, -6), ((-16, -22), (-14, -46), (-6, -56)), ((2, -62), (12, -52), (14, -34)), ((16, -18), (14, -4), (8, 0)), ((2, 2), (-4, 0), (-8, -6))))
    fill(L, body, 0.85, s=s, seed=seed, gran=0.15, edge=0.25)
    line(L, X(path((0, -50), ((10, -40), (14, -22), (18, -2)))), np.array([2] + [3.2] * 30 + [1.5]), s, 0.95, 0.15, seed + 1)
    line(L, X([(10, 0), (20, 16)]), 3.5, s, 0.9, 0.5, seed + 2)
    line(L, X([(-2, 0), (-4, 6)]), 1.6, s, 0.8, 0, seed + 3); line(L, X([(4, 2), (4, 7)]), 1.6, s, 0.8, 0, seed + 4)
    bob = math.sin(t * 1.3) * 1.2
    d = -1 if look < 0.5 else 1
    hx, hy = -6 + 4 * d, -84 + bob
    neck = X(path((-4, -54), ((-10, -64), (-8 + 3 * d, -76), (hx, hy))))
    line(L, neck, np.linspace(9, 6, len(neck)), s, 0.95, 0.0, seed + 5, taper=False)
    head = X([(hx + 6.5 * math.cos(a), hy + 5.5 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 20)])
    fill(L, head, 0.95, s=s, seed=seed + 6)
    beak = X([(hx + d * 5, hy + 0.5), (hx + d * 19, hy + 1.5), (hx + d * 21, hy + 4.5)])
    line(L, beak, np.array([3.0, 1.8, 1.2]), s, 0.95, 0, seed + 7, taper=False)
    L.knock(ellipse_mask(L.D.shape, L.P(X([(hx + d * 2.2, hy - 1.2)]))[0], (1.3 * s, 1.3 * s)), 0.9)
    L.tints.append((ellipse_mask(L.D.shape, L.P(X([(hx + d * 3, hy + 4.5)]))[0], (5 * s, 2.6 * s)) * 0.6, (0.55, 0.78, 0.92)))
