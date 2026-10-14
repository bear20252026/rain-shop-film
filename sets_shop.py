# Inside the Rain Shop: open front on the rainy canal, tall shelves of weather jars, the counter,
# the altar (red jar drawn live), the rules board, the supper table and the stairs.
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from ink import *
from town import wobble, VERMILION, CELADON, CJK
from engine import OW, OH, JAR_COLS, GLOW, WARM, BRUSH
from sets import Painted, warp, cached, flatten

class Cv:
    def __init__(self, w, h=OH):
        self.D = np.zeros((h, w), np.float32); self.tints = []; self.shape = (h, w)
    def clear(self, poly, soft=1.0):
        m = cv2.GaussianBlur(poly_mask(self.shape, [poly]), (0, 0), soft)
        self.D *= 1 - m
        self.tints = [(a * (1 - m), c) for a, c in self.tints]
    def wash(self, poly, d, col=None, ca=0.6, **kw):
        m = poly_mask(self.shape, [poly]); over(self.D, wash(m, d, **kw))
        if col is not None: self.tints.append((m * ca, col))
        return m
    def st(self, pts, w, d=0.9, dry=0.3, seed=0, taper=True):
        stroke(self.D, pts, w, d, dry, seed, taper=taper)
    def text(self, x, y, s, size, d=0.9, anchor='mm', vertical=False, seed=3):
        img = Image.new('L', (self.shape[1], self.shape[0]), 0); dr = ImageDraw.Draw(img); f = ImageFont.truetype(BRUSH, size)
        if vertical:
            for i, ch in enumerate(s): dr.text((x, y + i * size * 1.08), ch, font=f, fill=255, anchor='mm')
        else: dr.text((x, y), s, font=f, fill=255, anchor=anchor)
        t = np.asarray(img, np.float32) / 255
        t = cv2.GaussianBlur(t, (0, 0), 0.7)
        t = smooth(t + (vnoise(self.shape[0], self.shape[1], 3, seed, 2) - 0.5) * 0.4, 0.3, 0.6)
        over(self.D, t * d)

def rect(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

def jar_poly(x, by, jw, jh, kind=0):
    if kind == 1:   # tall bottle
        half = [(x + jw * (0.35 + 0.65 * math.sin(a) ** 2), by - jh * (1 - math.cos(a)) / 2) for a in np.linspace(0, math.pi, 16)]
    elif kind == 2:  # gourd
        half = [(x + jw * (0.45 + 0.55 * abs(math.sin(a * 2)) * (1 if a < math.pi / 2 else 0.7)), by - jh * a / math.pi) for a in np.linspace(0, math.pi, 18)]
    else:
        half = [(x + jw * (0.55 + 0.45 * math.sin(a)), by - jh * (1 - math.cos(a)) / 2) for a in np.linspace(0, math.pi, 16)]
    body = [(x - (bx - x), byy) for bx, byy in half[::-1]] + half
    return body + [(x + jw * 0.35, by - jh - 6), (x - jw * 0.35, by - jh - 6)]

SHOP_W = 3000
FLOOR = 640          # where the back wall meets the floor
FEET = 740           # where people stand (front of the room)
SHELF_X = (520, 1720)
SHELF_Y = [205, 335, 465, 595]
ALTAR = (1975, 520)          # red jar sits here (drawn live)
GIGGLE_JAR = (1180, 465)     # the small 笑风 jar (drawn live)
COUNTER = (820, 1420, 575)   # x0, x1, top
NAMED = {'虎丘雷': (700, 205), '初霜': (1010, 335), '秋雾': (1450, 335), '梅雨': (1600, 465), '六月雪': (880, 595)}

def build_shop():
    C = Cv(SHOP_W); r = np.random.default_rng(7)
    P = paper(OH, SHOP_W, 41)
    # floor: grey stone tiles, slightly receding
    fl = C.wash(rect(0, FLOOR, SHOP_W, OH), 0.10, bleed=3, seed=1, var=0.8, gran=0.8)
    for k, y in enumerate([FLOOR + 22, FLOOR + 52, FLOOR + 92, FLOOR + 145]):
        C.st(wobble([(0, y), (SHOP_W, y)], 1.5, k), 1.4, 0.32, 0.6, 20 + k, taper=False)
    for x in range(-600, SHOP_W + 600, 150):
        C.st([(x, FLOOR), (x + (x - SHOP_W / 2) * 0.35, OH)], 1.2, 0.25, 0.6, int(x) + 999, taper=False)
    C.st(wobble([(0, FLOOR), (SHOP_W, FLOOR)], 1, 3), 4.0, 0.85, 0.3, 30, taper=False)
    # ceiling beam and rafters
    C.wash(rect(0, 0, SHOP_W, 46), 0.75, bleed=1.5, seed=2, gran=0.6, var=0.5)
    for x in range(30, SHOP_W, 120):
        C.st([(x, 46), (x + 4, 70)], 7, 0.75, 0.3, x)
    C.st(wobble([(0, 48), (SHOP_W, 48)], 1, 5), 5, 0.9, 0.3, 31, taper=False)
    # ---- open shop front (left): the canal in the rain beyond, pale and far
    C.wash(rect(40, 70, 470, FLOOR), 0.035, (0.95, 0.90, 0.85), 0.5, bleed=4, seed=5)
    for i, (x0, x1, ey) in enumerate([(30, 200, 300), (180, 360, 280), (330, 480, 310)]):
        C.wash([(x0 - 14, ey), (x1 + 14, ey), (x1 + 6, ey - 26), (x0 - 6, ey - 26)], 0.22, bleed=2, seed=40 + i)
        C.st(wobble([(x0 - 16, ey - 26), (x1 + 16, ey - 26)], 1, i), 3, 0.35, 0.3, 50 + i)
        C.wash(rect(x0 + 30, ey + 40, x0 + 50, ey + 64), 0.18, bleed=1, seed=60 + i)
    C.st(wobble([(40, 500), (470, 500)], 1, 9), 2.4, 0.3, 0.4, 70, taper=False)        # far quay
    for y in range(510, 630, 16): C.st([(60 + (y * 7) % 90, y), (200 + (y * 13) % 200, y)], 1.0, 0.15, 0.4, y, taper=False)
    # door posts, lintel, a half-folded lattice shutter
    for x in (40, 470):
        C.st(wobble([(x, 50), (x, FLOOR + 6)], 1.2, x), 22, 0.88, 0.35, 80 + x, taper=False)
    C.st(wobble([(30, 72), (480, 72)], 1, 11), 14, 0.9, 0.3, 90, taper=False)
    for k in range(3):
        x0 = 380 + k * 24
        C.wash(rect(x0, 90, x0 + 22, FLOOR - 10), 0.30, bleed=1, seed=100 + k)
        for y in range(110, FLOOR - 20, 26): C.st([(x0 + 2, y), (x0 + 20, y)], 1.2, 0.6, 0, y + k, taper=False)
        C.st([(x0, 90), (x0, FLOOR - 10)], 1.6, 0.8, 0, 110 + k, taper=False)
    # ---- the back wall between posts: white plaster, faint damp marks
    for x in (500, 1760, 2440):
        C.st(wobble([(x, 46), (x, FLOOR + 4)], 1.2, x), 20, 0.88, 0.35, 120 + x, taper=False)
    C.wash(rect(470, 600, SHOP_W, FLOOR), 0.04, bleed=10, seed=9, rough=0.6, var=1.0)
    # ---- shelves full of jars
    sx0, sx1 = SHELF_X
    C.wash(rect(sx0, 90, sx1, FLOOR), 0.56, bleed=2, seed=11, var=0.4, gran=0.25)     # dark cabinet back
    jars = []; labels = []
    for row, sy in enumerate(SHELF_Y):
        C.st(wobble([(sx0 - 6, sy), (sx1 + 6, sy)], 1, row), 7, 0.95, 0.2, 130 + row, taper=False)
        x = sx0 + 30 + r.random() * 10
        while x < sx1 - 40:
            kind = int(r.integers(0, 3)); jw = 14 + r.random() * 12; jh = 40 + r.random() * 46 if kind != 1 else 70 + r.random() * 30
            skip = (abs(x - GIGGLE_JAR[0]) < 40 and sy == GIGGLE_JAR[1])
            if not skip and sy - jh - 10 > (SHELF_Y[row - 1] if row else 90) + 6:
                jars.append((x, sy, jw, jh, kind))
            x += jw * 2 + 16 + r.random() * 18
    jm = np.zeros(C.shape, np.float32)
    for (x, sy, jw, jh, kind) in jars:
        jm = np.maximum(jm, poly_mask(C.shape, [jar_poly(x, sy - 3, jw, jh, kind)]))
    C.D *= 1 - cv2.GaussianBlur(jm, (0, 0), 0.8) * 0.92
    edge = np.clip(jm - cv2.erode(jm, np.ones((3, 3), np.uint8)), 0, 1)
    over(C.D, cv2.GaussianBlur(edge, (0, 0), 0.8) * 0.7)
    C.tints.append((wash(jm, 0.6, bleed=0.8, seed=12, edge=0.15, rough=0.1, var=0.5), CELADON))
    # paper labels on some jars
    for i, (x, sy, jw, jh, kind) in enumerate(jars):
        if i % 2 == 0:
            ly = sy - jh * 0.45
            lm = poly_mask(C.shape, [rect(x - 7, ly - 10, x + 7, ly + 10)])
            C.D *= 1 - lm * 0.9; C.tints = [(a * (1 - lm * 0.9), c) for a, c in C.tints]
            C.tints.append((lm * 0.35, (0.60, 0.75, 0.85)))
            for k in range(3): C.st([(x - 1 + (k - 1) * 4, ly - 6), (x - 1 + (k - 1) * 4, ly + 6)], 1.0, 0.6, 0.5, i * 7 + k, taper=False)
    for k in range(5):   # cabinet stiles
        x = sx0 + (sx1 - sx0) * k / 4
        C.st(wobble([(x, 86), (x, FLOOR)], 1, k), 6, 0.95, 0.3, 140 + k, taper=False)
    C.st(wobble([(sx0 - 10, 88), (sx1 + 10, 88)], 1, 2), 9, 0.95, 0.3, 146, taper=False)
    # ---- altar: narrow table, hanging scroll with 雨, candle sticks
    ax, ay = ALTAR
    C.wash(rect(ax - 120, ay, ax + 120, ay + 14), 0.85, bleed=1, seed=150)
    for x in (ax - 105, ax + 105): C.st([(x, ay + 12), (x + (4 if x > ax else -4), FLOOR + 30)], 8, 0.9, 0.3, 151 + x, taper=False)
    C.st([(ax - 135, ay - 2), (ax - 120, ay + 4)], 4, 0.9, 0, 153); C.st([(ax + 135, ay - 2), (ax + 120, ay + 4)], 4, 0.9, 0, 154)
    C.wash(rect(ax - 70, 110, ax + 70, 400), 0.04, (0.75, 0.86, 0.90), 0.5, bleed=1, seed=155)
    C.st([(ax - 80, 110), (ax + 80, 110)], 6, 0.9, 0.2, 156, taper=False); C.st([(ax - 78, 400), (ax + 78, 400)], 7, 0.9, 0.2, 157, taper=False)
    C.st([(ax, 70), (ax - 40, 110)], 1.2, 0.6, 0, 158, taper=False); C.st([(ax, 70), (ax + 40, 110)], 1.2, 0.6, 0, 159, taper=False)
    C.text(ax, 250, '雨', 150, 0.92, seed=160)
    for dx in (-80, 80):
        C.wash(rect(ax + dx - 5, ay - 46, ax + dx + 5, ay), 0.08, VERMILION, 0.8, bleed=0.6, seed=161 + dx)
        C.st([(ax + dx - 12, ay - 1), (ax + dx + 12, ay - 1)], 4, 0.9, 0, 163 + dx, taper=False)
    C.wash([(ax - 22, ay), (ax + 22, ay), (ax + 16, ay - 18), (ax - 16, ay - 18)], 0.2, bleed=1, seed=165)  # incense pot
    # ---- rules board (wood, black brush rules, right to left columns)
    bx0, bx1, by0, by1 = 2170, 2410, 180, 470
    C.wash(rect(bx0, by0, bx1, by1), 0.10, (0.55, 0.70, 0.82), 0.6, bleed=1, seed=170, gran=0.8)
    C.st(wobble([(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1), (bx0, by0)], 1, 3), 4, 0.9, 0.3, 171, taper=False)
    C.st([(bx0 + 40, by0), ((bx0 + bx1) / 2, 120), (bx1 - 40, by0)], 1.4, 0.7, 0, 172, taper=False)
    for i, s in enumerate(['一不准碰罐子', '二不准碰罐子', '三红的那个永远不准']):
        C.text(bx1 - 40 - i * 75, by0 + 30, s, 27, 0.92, vertical=True, seed=180 + i)
    # ---- supper table and stools, the stairs up
    tx0, tx1, ty = 2520, 2800, 610
    C.wash(rect(tx0, ty, tx1, ty + 16), 0.7, (0.45, 0.55, 0.70), 0.5, bleed=1, seed=190)
    for x in (tx0 + 14, tx1 - 14): C.st([(x, ty + 14), (x, FEET - 20)], 9, 0.9, 0.3, 191 + x, taper=False)
    for sx in (tx0 - 40, tx1 + 40):
        C.wash(rect(sx - 34, 660, sx + 34, 672), 0.6, bleed=1, seed=193 + sx)
        for x in (sx - 26, sx + 26): C.st([(x, 670), (x, FEET - 6)], 6, 0.85, 0.3, 194 + x, taper=False)
    # stairs: a diagonal stringer and treads rising to the right, the upper floor opening
    C.wash([(2860, FLOOR), (3000, FLOOR), (3000, 80), (2990, 80)], 0.10, bleed=3, seed=200)
    for k in range(12):
        y = FLOOR - 10 - k * 48; x = 2860 + k * 12
        C.st([(x, y), (x + 140, y)], 6, 0.85, 0.3, 201 + k, taper=False)
    C.st(wobble([(2850, FLOOR + 4), (3000, 50)], 2, 4), 10, 0.9, 0.35, 220, taper=False)
    img = flatten(C, P)
    jarr = np.array([(x, sy, jw, jh) for (x, sy, jw, jh, k) in jars], np.float32)
    # the counter, as a foreground piece (people behind it are hidden from the waist down)
    F = Cv(SHOP_W); cx0, cx1, ct = COUNTER
    m = F.wash(rect(cx0, ct, cx1, FEET - 10), 0.45, (0.45, 0.55, 0.72), 0.55, bleed=1, seed=230, gran=0.8, var=0.6)
    F.st(wobble([(cx0 - 14, ct), (cx1 + 14, ct)], 1, 1), 12, 0.95, 0.3, 231, taper=False)
    for x in (cx0, cx1): F.st([(x, ct), (x, FEET - 10)], 5, 0.9, 0.3, 232 + x, taper=False)
    for k in range(1, 4): F.st([(cx0 + (cx1 - cx0) * k / 4, ct + 18), (cx0 + (cx1 - cx0) * k / 4, FEET - 18)], 1.6, 0.5, 0.5, 240 + k, taper=False)
    # an abacus and a brush pot on the counter
    for k in range(9): F.st([(cx0 + 60 + k * 9, ct - 26), (cx0 + 60 + k * 9, ct - 2)], 1.2, 0.8, 0, 250 + k, taper=False)
    F.st(wobble([(cx0 + 52, ct - 28), (cx0 + 140, ct - 28), (cx0 + 140, ct - 2), (cx0 + 52, ct - 2), (cx0 + 52, ct - 28)], 0.5, 2), 3, 0.9, 0, 260, taper=False)
    for k in range(9):
        for j in range(3): over(F.D, ellipse_mask(F.shape, (cx0 + 60 + k * 9, ct - 22 + j * 8 + (k % 2) * 2), (3.5, 2.5)) * 0.85)
    F.wash(rect(cx1 - 110, ct - 40, cx1 - 80, ct), 0.3, bleed=1, seed=270)
    for k in range(3): F.st([(cx1 - 100 + k * 6, ct - 40), (cx1 - 104 + k * 9, ct - 80)], 1.6, 0.85, 0, 271 + k)
    fa = np.clip(poly_mask(F.shape, [[(cx0 - 16, ct - 8), (cx1 + 16, ct - 8), (cx1 + 4, FEET), (cx0 - 4, FEET)]]) + (F.D > 0.05), 0, 1)
    fa = cv2.GaussianBlur(fa.astype(np.float32), (0, 0), 0.8)
    Fp = paper(OH, SHOP_W, 43); frgb = flatten(F, Fp)
    return dict(img=img.astype(np.float16), jars=jarr, fg=frgb.astype(np.float16), fga=fa.astype(np.float16))

class ShopSet(Painted):
    def __init__(self): super().__init__('shop_in', build_shop, SHOP_W)
    @property
    def d(self):
        if self._d is None:
            self._d = cached(self.name, self.build)
            for k in ('img', 'fg', 'fga'): self._d[k] = self._d[k].astype(np.float32)
        return self._d
    def fg(self, t, left, top, z, args):
        if args.get('no_counter'): return None
        cx0, cx1, ct = COUNTER
        if (left + OW / z) < cx0 - 30 or left > cx1 + 30: return None
        return warp(self.d['fg'], left, top, z), warp(self.d['fga'], left, top, z)

SHOP = ShopSet()

def shop_live(ctx, glow=1.0, red=True, night=0.0, giggle=True, empty=0.0, candles=False, rain_door=1.0):
    """jar glows on the shelves (fewer as 'empty' rises), the red jar on the altar, the giggling-breeze jar, rain beyond the door"""
    t = ctx.Tabs; J = SHOP.d['jars']
    for j, (jx, jy, jw, jh) in enumerate(J):
        if empty > 0 and ((j * 37) % 100) / 100 < empty: continue
        ctx.add_glow(jx, jy - jh * 0.45, jw * 0.55, (0.20 + 0.08 * math.sin(t * 1.3 + j)) * glow * (1 + night), JAR_COLS[j % len(JAR_COLS)])
    if red: red_jar(ctx, *ALTAR)
    if giggle: ctx.jar(GIGGLE_JAR[0], GIGGLE_JAR[1] - 2, 0.75, seed=77)
    if candles:
        for dx in ((-80, 80) if candles is True else candles):
            fl = 0.85 + 0.15 * math.sin(t * 13 + dx) * math.sin(t * 7.3)
            ctx.add_glow(ALTAR[0] + dx, ALTAR[1] - 54, 5, 0.9 * fl, WARM)
    if rain_door > 0:     # rain seen through the open front
        sx0, sy0 = ctx.T(40, 70); sx1, sy1 = ctx.T(470, FLOOR)
        if sx1 > 0 and sx0 < OW:
            L = ctx.layer(max(0, sx0), max(0, sy0), min(OW, sx1), min(OH, sy1))
            h, w = L.D.shape; rr = np.random.default_rng(3)
            for k in range(int(140 * rain_door * (w * h) / (430 * 570 * ctx.z * ctx.z) + 10)):
                x = (rr.random() * w - t * 40) % w; y = (rr.random() * h + t * 900 * ctx.z) % (h + 40) - 20; l = (10 + rr.random() * 16) * ctx.z
                cv2.line(L.D, (int(x * 4), int(y * 4)), (int((x - l * 0.2) * 4), int((y - l) * 4)), 0.25 * rain_door, 1, cv2.LINE_AA, 2)

def red_jar(ctx, x, by, s=1.0, crack=0.0, glow=0.0, seed=99):
    """the red-sealed jar: grey glaze, vermilion paper seal tied with string, a faint blue heart"""
    sx, sy = ctx.T(x, by); se = s * ctx.z
    L = ctx.layer(sx - 60 * se, sy - 120 * se, sx + 60 * se, sy + 10 * se)
    jw, jh = 34 * se, 78 * se
    half = [(sx + jw * (0.5 + 0.5 * math.sin(a)), sy - jh * (1 - math.cos(a)) / 2) for a in np.linspace(0, math.pi, 20)]
    body = [(sx - (px - sx), py) for px, py in half[::-1]] + half + [(sx + jw * 0.4, sy - jh - 8 * se), (sx - jw * 0.4, sy - jh - 8 * se)]
    m = poly_mask(L.D.shape, [L.P(body)]); L.knock(m)
    over(L.D, wash(m, 0.16, bleed=0.6, seed=seed, edge=0.8, scale=max(0.6, se)))
    L.tints.append((m * 0.45, (0.62, 0.66, 0.66)))
    from chars import line
    line(L, half[::-1] + [(sx, sy)], 2.0, se, 0.9, 0.25, seed + 1, taper=False)
    line(L, [(sx - (px - sx), py) for px, py in half], 2.0, se, 0.9, 0.25, seed + 2, taper=False)
    # the seal: a vermilion paper cap with string
    cap = [(sx - jw * 0.48, sy - jh - 2 * se), (sx + jw * 0.48, sy - jh - 2 * se), (sx + jw * 0.62, sy - jh + 18 * se), (sx - jw * 0.62, sy - jh + 18 * se)]
    cm = poly_mask(L.D.shape, [L.P(cap)]); L.knock(cm)
    L.tints.append((cm * 0.92, VERMILION)); over(L.D, wash(cm, 0.08, bleed=0.5, seed=seed + 3, scale=max(0.6, se)))
    line(L, [(sx - jw * 0.6, sy - jh + 14 * se), (sx + jw * 0.6, sy - jh + 14 * se)], 1.6, se, 0.9, 0, seed + 4, taper=False)
    line(L, [(sx + jw * 0.55, sy - jh + 14 * se), (sx + jw * 0.75, sy - jh + 30 * se)], 1.2, se, 0.8, 0, seed + 5)
    if crack > 0:
        pts = [(sx - jw * 0.2, sy - jh * 0.95), (sx - jw * 0.05, sy - jh * 0.75), (sx - jw * 0.3, sy - jh * 0.55), (sx - jw * 0.1, sy - jh * 0.35), (sx - jw * 0.25, sy - jh * 0.12)]
        n = max(2, int(len(pts) * min(1, crack)) + 1)
        line(L, pts[:n], 1.6, se, 0.95, 0, seed + 6, taper=False)
    pulse = glow
    if pulse > 0:
        ctx.add_glow(sx, sy - jh * 0.45, jw * 0.6, pulse, np.array([1.0, 0.75, 0.45], np.float32), world=False)
    return (sx, sy - jh - 8 * se)
