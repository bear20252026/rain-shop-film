# The water town in a bold, free ink style (white walls, black roof strokes, lots of white space).
# Painting order matters: every nearer shape first clears ("whites out") what is behind it, then paints itself.
import numpy as np, cv2, math
from PIL import Image, ImageDraw, ImageFont
from ink import *

H = 804
WW = 2700
WATER_Y = 600
CJK = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
CELADON = (0.74, 0.80, 0.74)
VERMILION = (0.22, 0.30, 0.82)
SHOP_X0, SHOP_X1 = 1540, 1880

class Canvas:
    def __init__(self, w):
        self.D = np.zeros((H, w), np.float32); self.tints = []; self.shape = (H, w); self.O = np.zeros((H, w), np.float32)
    def clear(self, poly, soft=1.0):
        m = cv2.GaussianBlur(poly_mask(self.shape, [poly]), (0, 0), soft)
        self.D *= 1 - m; np.maximum(self.O, m, out=self.O)
        for i, (a, c) in enumerate(self.tints): self.tints[i] = (a * (1 - m), c)

def wobble(pts, amt, seed):
    r = np.random.default_rng(abs(int(seed))); pts = np.asarray(pts, np.float32)
    return pts + (r.random(pts.shape) - 0.5) * amt

def roof_band(C, x0, x1, eave_y, rh, tone, seed, curl=10, slope=0.0):
    """roof seen slightly from above: a dark sloped band with upturned ends, bold ridge stroke, thin eave line"""
    ov = 18 + rh * 0.3
    ridge_y = eave_y - rh
    ridge = bezier((x0 - ov * 0.4, ridge_y - curl * 0.6), ((x0 + x1) / 2, ridge_y + 3), (x1 + ov * 0.4, ridge_y - curl * 0.6), n=30)
    eave = bezier((x0 - ov, eave_y - curl), ((x0 + x1) / 2, eave_y + 2), (x1 + ov, eave_y - curl), n=30)
    poly = np.vstack([ridge, eave[::-1]])
    C.clear(poly, 1.2)
    m = poly_mask(C.shape, [poly])
    # gradient: darker near the ridge, lighter toward the eave (wet ink running down)
    yy = np.arange(H, dtype=np.float32)[:, None]
    grad = np.clip(1 - (yy - ridge_y) / (rh + 1) * 0.55, 0.35, 1)
    over(C.D, wash(m, 0.72 * tone, bleed=1.2, seed=seed, gran=0.6, var=0.5, edge=0.3) * grad)
    # tile rows: faint vertical strokes
    r = np.random.default_rng(abs(int(seed)))
    for x in np.arange(x0 - ov * 0.7, x1 + ov * 0.7, 9 + r.random() * 2):
        if r.random() < 0.6:
            stroke(C.D, [(x, ridge_y + 4), (x + (x - (x0 + x1) / 2) * 0.05, eave_y - 3)], 1.6, 0.30 * tone, 0.5, int(r.integers(1e6)), taper=False)
    stroke(C.D, wobble(ridge, 1.5, seed), np.linspace(9, 11, 30) * (0.6 + 0.4 * tone), 0.95 * tone, 0.35, seed + 1)
    stroke(C.D, wobble(eave, 1.0, seed + 1), np.full(30, 3.5), 0.9 * tone, 0.4, seed + 2)
    # upturned tips
    for sx, d in ((x0 - ov, -1), (x1 + ov, 1)):
        stroke(C.D, [(sx - d * 6, eave_y - curl + 2), (sx + d * 4, eave_y - curl - 8)], 3.5, 0.9 * tone, 0, seed + 3 + d, taper=True)
    return ridge_y

def wall(C, x0, x1, top, bot, tone, seed, lines=True):
    C.clear([(x0, top), (x1, top), (x1, bot), (x0, bot)], 0.8)
    if lines:
        r = np.random.default_rng(abs(int(seed)))
        # broken, light side lines: the white wall is mostly paper
        for x in (x0, x1):
            y = top
            while y < bot:
                L = 30 + r.random() * 80; e = min(bot, y + L)
                stroke(C.D, [(x + (r.random() - 0.5) * 2, y), (x + (r.random() - 0.5) * 2, e)], 1.6, 0.45 * tone, 0.3, int(r.integers(1e6)))
                y = e + 6 + r.random() * 30
        # damp stains near the water
        st = poly_mask(C.shape, [[(x0, bot - 70), (x1, bot - 50), (x1, bot), (x0, bot)]])
        over(C.D, wash(st, 0.05 * tone if tone > 0.9 else 0.0, bleed=12, seed=seed + 2, rough=0.6, var=1.0))

def window(C, cx, cy, w, h, tone, seed, kind='dark'):
    if kind == 'dark':
        m = poly_mask(C.shape, [[(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]])
        over(C.D, wash(m, 0.85 * tone, bleed=0.9, seed=seed, edge=0.2, gran=0.5))
    else:   # lattice
        m = poly_mask(C.shape, [[(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]])
        over(C.D, wash(m, 0.3 * tone, bleed=0.9, seed=seed))
        for k in range(1, 4): stroke(C.D, [(cx - w / 2 + w * k / 4, cy - h / 2), (cx - w / 2 + w * k / 4, cy + h / 2)], 1.4, 0.7 * tone, 0, seed + k, taper=False)
        stroke(C.D, [(cx - w / 2, cy), (cx + w / 2, cy)], 1.4, 0.7 * tone, 0, seed + 9, taper=False)
        stroke(C.D, [(cx - w / 2 - 3, cy - h / 2), (cx + w / 2 + 3, cy - h / 2), (cx + w / 2 + 3, cy + h / 2), (cx - w / 2 - 3, cy + h / 2), (cx - w / 2 - 3, cy - h / 2)], 2.2, 0.85 * tone, 0.2, seed + 10, taper=False)

def gable_wall(C, x0, x1, top, steps, tone, seed):
    """stepped horse-head wall end: white stepped silhouette with black caps"""
    w = x1 - x0; sw = w / (2 * steps + 2.5)
    poly = [(x0, top + steps * 40 + 40)]
    caps = []
    for i in range(steps + 1):
        y = top + (steps - i) * 34
        xa = x0 + i * sw; xb = x1 - i * sw
        caps.append((xa, xb, y))
    pts = []
    for (xa, xb, y) in caps: pts.append((xa, y + 34)); pts.append((xa, y))
    right = []
    for (xa, xb, y) in caps[::-1]: right.append((xb, y)); right.append((xb, y + 34))
    poly = [(x0, top + steps * 40 + 120)] + pts + right + [(x1, top + steps * 40 + 120)]
    C.clear(poly, 0.8)
    for i, (xa, xb, y) in enumerate(caps):
        stroke(C.D, wobble([(xa - 8, y - 1), (xb + 8, y - 1)], 1.2, seed + i), np.array([6, 9, 9, 6.0])[:2] if False else 8.5, 0.95 * tone, 0.35, seed + i, taper=False)
        stroke(C.D, [(xa - 10, y + 1), (xa - 4, y - 8)], 3, 0.9 * tone, 0, seed + 20 + i)
        stroke(C.D, [(xb + 10, y + 1), (xb + 4, y - 8)], 3, 0.9 * tone, 0, seed + 30 + i)
        stroke(C.D, [(xa, y + 5), (xa, y + 34)], 1.4, 0.4 * tone, 0.4, seed + 40 + i, taper=False)
        stroke(C.D, [(xb, y + 5), (xb, y + 34)], 1.4, 0.4 * tone, 0.4, seed + 50 + i, taper=False)

def house(C, x0, x1, eave_y, bot, tone, seed, rh=46, wins=(), door=None, gable=None):
    roof_band(C, x0, x1, eave_y, rh, tone, seed)
    wall(C, x0, x1, eave_y + 2, bot, tone, seed + 5)
    # the eave casts a soft grey shadow on the white wall
    sh = poly_mask(C.shape, [[(x0, eave_y + 2), (x1, eave_y + 2), (x1, eave_y + 16), (x0, eave_y + 22)]])
    over(C.D, wash(sh, (0.16 if tone > 0.9 else 0.0), bleed=5, seed=seed + 6, rough=0.3))
    for i, (u, v, w, h, k) in enumerate(wins):
        window(C, x0 + u * (x1 - x0), eave_y + v, w, h, tone, seed + 10 + i, k)
    if door:
        u, w, h = door; cx = x0 + u * (x1 - x0)
        m = poly_mask(C.shape, [[(cx - w / 2, bot - h), (cx + w / 2, bot - h), (cx + w / 2, bot), (cx - w / 2, bot)]])
        over(C.D, wash(m, 0.8 * tone, bleed=1, seed=seed + 30, edge=0.2))
        stroke(C.D, [(cx - w / 2 - 8, bot - h - 6), (cx + w / 2 + 8, bot - h - 6)], 4, 0.9 * tone, 0.3, seed + 31)
    if gable:
        side, steps = gable
        gx0 = x0 - 10 if side == 'l' else x1 - 86
        gable_wall(C, gx0, gx0 + 96, eave_y - rh - steps * 34 + 20, steps, tone, seed + 60)

def far_hills(w, seed=1):
    C = Canvas(w); xs = np.arange(w); yy = np.arange(H)[:, None]
    for k, (base, amp, den, sd) in enumerate([(260, 120, 0.10, 3), (330, 90, 0.16, 4)]):
        n = vnoise(1, w, 300 - 80 * k, sd, 4)[0]
        ridge = base - amp * n - 20 * np.sin(xs / (170 + 50 * k) + sd)
        m = (yy > ridge[None, :]).astype(np.float32)
        fade = np.clip(1 - (yy - ridge[None, :]) / (130 - 20 * k), 0, 1) ** 1.5
        over(C.D, wash(m, den, bleed=5, seed=sd, rough=0.25) * fade)
    return C

def bridge(C, x0, x1, tone, seed):
    cx = (x0 + x1) / 2; R = 140; top = 455
    deck = bezier((x0, WATER_Y - 14), (cx, top - 70), (x1, WATER_Y - 14), n=60)
    under = [(cx + R * math.cos(a), WATER_Y + 2 - R * math.sin(a)) for a in np.linspace(0, math.pi, 60)]
    body = np.vstack([deck - [0, 30], np.array(under)])
    C.clear(body, 1.0)
    m = poly_mask(C.shape, [np.vstack([deck, np.array(under)])])
    over(C.D, wash(m, 0.16 * tone, bleed=3, seed=seed, var=0.8, gran=0.8))
    stroke(C.D, wobble(deck, 1.5, seed), np.full(60, 6.5), 0.92 * tone, 0.35, seed + 1)
    stroke(C.D, wobble(under, 1.5, seed + 1), np.full(60, 5.0), 0.85 * tone, 0.35, seed + 3)
    outer = [(cx + (R + 24) * math.cos(a), WATER_Y + 2 - (R + 24) * math.sin(a)) for a in np.linspace(0.05, math.pi - 0.05, 40)]
    stroke(C.D, wobble(outer, 1.5, seed + 2), np.full(40, 2.0), 0.5 * tone, 0.5, seed + 40)
    r = np.random.default_rng(abs(int(seed)))
    for k in range(10):
        u = 0.12 + 0.76 * k / 9; i = int(u * 59); x, y = deck[i]
        stroke(C.D, [(x, y - 1), (x + 1, y - 24)], 3.0, 0.85 * tone, 0.2, seed + 60 + k, taper=False)
    stroke(C.D, wobble(deck[7:53] - [0, 24], 1.2, seed + 5), np.full(46, 2.4), 0.8 * tone, 0.4, seed + 80)

def boat(C, cx, tone, seed):
    y = WATER_Y + 52
    hull_top = bezier((cx - 160, y - 26), (cx, y - 6), (cx + 160, y - 30), n=40)
    hull_bot = bezier((cx + 160, y - 30), (cx + 20, y + 26), (cx - 160, y - 26), n=40)
    C.clear(np.vstack([hull_top, hull_bot]), 1)
    over(C.D, wash(poly_mask(C.shape, [np.vstack([hull_top, hull_bot])]), 0.55 * tone, bleed=1.5, seed=seed, gran=0.6))
    stroke(C.D, hull_bot, np.full(40, 4.5), 0.9 * tone, 0.4, seed + 1)
    # black arched awning
    aw = np.array([(cx - 40 + 62 * math.cos(a), y - 14 - 44 * math.sin(a)) for a in np.linspace(math.pi, 0, 30)])
    over(C.D, wash(poly_mask(C.shape, [aw]), 0.88 * tone, bleed=1.0, seed=seed + 2, gran=0.5))
    for k in range(4): stroke(C.D, [(cx - 92 + 34 * k, y - 16), (cx - 92 + 34 * k + 2, y - 48 + abs(1.5 - k) * 8)], 1.4, 0.3, 0, seed + 3 + k)
    stroke(C.D, [(cx - 120, y - 22), (cx - 250, y - 120)], np.array([4, 2.0]), 0.85 * tone, 0.4, seed + 9)

def willow(C, x, seed):
    """trunk and main branches only; the hanging strands are drawn per frame so they can sway"""
    stroke(C.D, wobble([(x, WATER_Y - 12), (x - 10, 470), (x + 8, 360), (x - 6, 250), (x + 6, 170)], 3, seed), np.array([22, 19, 15, 10, 5.0]), 0.85, 0.8, seed)
    for k, (dx, dy, w) in enumerate([(120, -70, 9), (-110, -50, 8), (80, -140, 6), (-70, -150, 6), (150, 10, 6)]):
        y0 = 330 - k * 30
        stroke(C.D, [(x, y0), (x + dx * 0.5, y0 + dy * 0.6), (x + dx, y0 + dy)], np.array([w, w * 0.6, 2.0]), 0.85, 0.6, seed + 1 + k)
    # the tips of branches (where strands hang from)
    return [(x + dx, 330 - k * 30 + dy) for k, (dx, dy, w) in enumerate([(120, -70, 9), (-110, -50, 8), (80, -140, 6), (-70, -150, 6), (150, 10, 6)])]

def banner(C, x, y0, seed):
    w, h = 50, 150
    stroke(C.D, [(x - w / 2 - 8, y0), (x + w / 2 + 8, y0)], 4, 0.9, 0.1, seed, taper=False)
    C.clear([(x - w / 2, y0 + 3), (x + w / 2, y0 + 3), (x + w / 2 + 2, y0 + h), (x - w / 2 + 2, y0 + h)], 0.6)
    over(C.D, wash(poly_mask(C.shape, [[(x - w / 2, y0 + 3), (x + w / 2, y0 + 3), (x + w / 2 + 2, y0 + h), (x - w / 2 + 2, y0 + h)]]), 0.05, bleed=1, seed=seed + 1))
    for dx in (-w / 2, w / 2): stroke(C.D, [(x + dx, y0 + 3), (x + dx + 2, y0 + h)], 1.4, 0.5, 0.3, seed + 2 + int(dx), taper=False)
    img = Image.new('L', (C.shape[1], C.shape[0]), 0); d = ImageDraw.Draw(img); f = ImageFont.truetype(CJK, 38)
    d.text((x + 1, y0 + 44), '雨', font=f, fill=255, anchor='mm'); d.text((x + 1, y0 + 100), '铺', font=f, fill=255, anchor='mm')
    t = np.asarray(img, np.float32) / 255
    t = cv2.dilate(t, np.ones((3, 3), np.uint8)); t = cv2.GaussianBlur(t, (0, 0), 1.0)
    t = smooth(t + (vnoise(C.shape[0], C.shape[1], 3, seed + 4, 2) - 0.5) * 0.45, 0.3, 0.6)
    over(C.D, t * 0.92)
    C.tints.append((poly_mask(C.shape, [[(x - w / 2 + 1, y0 + h - 16), (x + w / 2 + 1, y0 + h - 16), (x + w / 2 + 2, y0 + h), (x - w / 2 + 2, y0 + h)]]) * 0.75, VERMILION))

def shop(C, seed=900):
    x0, x1 = SHOP_X0, SHOP_X1; bot = WATER_Y - 18
    # upper storey with its own roof
    roof_band(C, x0 - 10, x1 + 10, 250, 54, 1.0, seed, curl=14)
    wall(C, x0, x1, 252, bot, 1.0, seed + 1)
    window(C, x0 + 92, 300, 92, 52, 1.0, seed + 2, 'lattice'); window(C, x1 - 92, 300, 92, 52, 1.0, seed + 3, 'lattice')
    # lower eave over the open shop front
    ey = 392
    roof_band(C, x0 + 6, x1 - 6, ey, 34, 1.0, seed + 10, curl=9)
    fx0, fx1, fy0 = x0 + 18, x1 - 18, ey + 14
    sh = poly_mask(C.shape, [[(fx0, fy0), (fx1, fy0), (fx1, bot), (fx0, bot)]])
    over(C.D, wash(sh, 0.78, bleed=2, seed=seed + 11, var=0.5, gran=0.6))
    # shelves and jars
    jars = []; r = np.random.default_rng(abs(int(seed)))
    for row, sy in enumerate([fy0 + 56, fy0 + 112, fy0 + 166]):
        stroke(C.D, wobble([(fx0 + 6, sy), (fx1 - 6, sy)], 1, row), 4.5, 0.95, 0.2, seed + 20 + row, taper=False)
        x = fx0 + 24 + r.random() * 8
        while x < fx1 - 26:
            jw = 9 + r.random() * 7; jh = 18 + r.random() * 16
            if not (row == 0 and abs(x - (fx0 + fx1) / 2) < 30): jars.append((x, sy, jw, jh))
            x += jw * 2 + 9 + r.random() * 12
    jm = np.zeros(C.shape, np.float32)
    for (x, sy, jw, jh) in jars:
        half = [(x + jw * (0.55 + 0.45 * math.sin(a)), sy - jh * (1 - math.cos(a)) / 2) for a in np.linspace(0, math.pi, 14)]
        body = [(x - (bx - x), by) for bx, by in half[::-1]] + half
        jm = np.maximum(jm, poly_mask(C.shape, [body + [(x + jw * 0.35, sy - jh - 5), (x - jw * 0.35, sy - jh - 5)]]))
    C.D *= 1 - cv2.GaussianBlur(jm, (0, 0), 0.8) * 0.9
    edge = np.clip(jm - cv2.erode(jm, np.ones((3, 3), np.uint8)), 0, 1)
    over(C.D, cv2.GaussianBlur(edge, (0, 0), 0.7) * 0.55)
    C.tints.append((wash(jm, 0.55, bleed=0.8, seed=seed + 30, edge=0.15, rough=0.1, var=0.4), CELADON))
    # the red-sealed jar, alone on the top shelf in the middle
    rx, ry = (fx0 + fx1) / 2, fy0 + 56
    rb = [(rx + 18 * (0.55 + 0.45 * math.sin(a)), ry - 36 * (1 - math.cos(a)) / 2) for a in np.linspace(0, math.pi, 14)]
    rb = [(rx - (bx - rx), by) for bx, by in rb[::-1]] + rb + [(rx + 7, ry - 41), (rx - 7, ry - 41)]
    rm = poly_mask(C.shape, [rb]); C.D *= 1 - rm * 0.9
    over(C.D, cv2.GaussianBlur(np.clip(rm - cv2.erode(rm, np.ones((3, 3), np.uint8)), 0, 1), (0, 0), 0.7) * 0.6)
    C.tints.append((rm * 0.55, (0.55, 0.62, 0.62)))
    seal = poly_mask(C.shape, [[(rx - 10, ry - 44), (rx + 10, ry - 44), (rx + 12, ry - 30), (rx - 12, ry - 30)]])
    C.tints.append((seal * 0.9, VERMILION))
    for x in [x0 + 12, (x0 + x1) / 2, x1 - 12]: stroke(C.D, wobble([(x, fy0 - 6), (x, bot)], 1.2, int(x)), 6, 0.92, 0.35, seed + int(x), taper=False)
    stroke(C.D, wobble([(x0 - 14, bot), (x1 + 14, bot)], 1, 5), 5, 0.9, 0.3, seed + 40, taper=False)
    return jars, (rx, ry), ey

def build_static():
    C = Canvas(WW)
    # back row: houses further away, lighter and higher
    for i, (x0, x1, ey, g) in enumerate([(60, 330, 330, None), (900, 1160, 300, ('l', 2)), (1240, 1520, 318, None), (1980, 2260, 296, ('r', 2)), (2330, 2640, 322, None)]):
        house(C, x0, x1, ey, 520, 0.42, 300 + i * 17, rh=36, wins=((0.3, 40, 20, 22, 'dark'), (0.7, 40, 20, 22, 'dark')), gable=g)
    willow_tips = willow(C, 960, 31)
    # front row
    house(C, 0, 210, 400, WATER_Y - 18, 1.0, 11, rh=40, wins=((0.5, 46, 26, 30, 'dark'),), door=(0.5, 46, 100))
    bridge(C, 210, 820, 1.0, 21)
    house(C, 1030, 1300, 368, WATER_Y - 18, 1.0, 41, rh=48, wins=((0.28, 48, 30, 34, 'dark'), (0.72, 48, 30, 34, 'lattice')), door=(0.5, 50, 112), gable=('l', 2))
    house(C, 1300, 1540, 392, WATER_Y - 18, 1.0, 51, rh=40, wins=((0.5, 46, 40, 30, 'lattice'),))
    jars, red_jar, ey = shop(C)
    banner(C, SHOP_X1 + 36, ey + 4, 61)
    house(C, 1880, 2210, 356, WATER_Y - 18, 1.0, 71, rh=50, wins=((0.3, 48, 28, 32, 'dark'), (0.7, 48, 28, 32, 'dark')), door=(0.5, 54, 110), gable=('r', 3))
    house(C, 2210, 2450, 396, WATER_Y - 18, 1.0, 81, rh=38, wins=((0.5, 44, 40, 30, 'lattice'),))
    house(C, 2450, 2700, 372, WATER_Y - 18, 1.0, 91, rh=46, wins=((0.35, 46, 26, 30, 'dark'),), door=(0.7, 46, 104), gable=('l', 2))
    # quay edge: one long confident line with a few stone joints
    stroke(C.D, wobble(np.array([(820, WATER_Y - 18), (WW, WATER_Y - 18)]), 0, 1), 4.5, 0.9, 0.4, 101, taper=False)
    stroke(C.D, wobble(np.array([(0, WATER_Y - 18), (210, WATER_Y - 18)]), 0, 1), 4.5, 0.9, 0.4, 102, taper=False)
    qm = poly_mask(C.shape, [[(820, WATER_Y - 16), (WW, WATER_Y - 16), (WW, WATER_Y + 2), (820, WATER_Y + 2)]])
    over(C.D, wash(qm, 0.22, bleed=1.5, seed=103, gran=0.8, var=0.7))
    r = np.random.default_rng(104)
    for x in np.cumsum(40 + r.random(60) * 40) + 820:
        if x < WW: stroke(C.D, [(x, WATER_Y - 15), (x + 1, WATER_Y + 1)], 1.3, 0.45, 0.3, int(x), taper=False)
    for k in range(3):
        sx = SHOP_X0 + 70
        stroke(C.D, [(sx - 60 + 10 * k, WATER_Y - 12 + 6 * k), (sx + 60 - 10 * k, WATER_Y - 12 + 6 * k)], 2.4, 0.6, 0.3, 110 + k, taper=False)
    return C, jars, red_jar, ey, willow_tips

def build_water_things():
    """things standing in the water, painted after the reflection"""
    C = Canvas(WW)
    boat(C, 1150, 1.0, 121)
    stroke(C.D, wobble([(2090, WATER_Y + 40), (2092, WATER_Y - 62)], 1.5, 3), np.array([13, 11.0]), 0.9, 0.5, 131, taper=False)
    return C
