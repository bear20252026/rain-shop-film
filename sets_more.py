# More painted sets: Xiaoman's room, the stone bridge, the laundry/market lane, the mudflat at the town's edge,
# the sky, the rooftops, the shadow-puppet screen, the city window, plain paper.
import math, numpy as np, cv2
from ink import *
from town import wobble, VERMILION, CELADON, roof_band, wall, window, house, far_hills, Canvas, gable_wall
from engine import OW, OH, JAR_COLS, GLOW, WARM, BRUSH
from sets import Painted, warp, cached, flatten
from sets_shop import Cv, rect, jar_poly
import town

def hills(C, w, base=(260, 330), dens=(0.10, 0.16), seed=1, h=OH):
    xs = np.arange(w); yy = np.arange(h)[:, None]
    for k, (b, den) in enumerate(zip(base, dens)):
        n = vnoise(1, w, 300 - 80 * k, seed + k, 4)[0]
        ridge = b - 110 * n - 20 * np.sin(xs / (170 + 50 * k) + seed)
        m = (yy > ridge[None, :]).astype(np.float32)
        fade = np.clip(1 - (yy - ridge[None, :]) / (130 - 20 * k), 0, 1) ** 1.5
        over(C.D, wash(m, den, bleed=5, seed=seed + k, rough=0.25) * fade)

class Big(Canvas):
    """town.Canvas with any height (town.py helpers use the module height H)"""
    def __init__(self, w, h=OH):
        self.D = np.zeros((h, w), np.float32); self.tints = []; self.shape = (h, w); self.O = np.zeros((h, w), np.float32)

def reflect(img, wy, t, x0, amp=1.0, alpha0=0.62):
    """rippling reflection of everything above water line wy into the rows below it (in place)"""
    H_, W_ = img.shape[:2]; n = H_ - wy
    if n <= 2: return img
    ys = np.arange(n, dtype=np.float32)[:, None]; xs = np.arange(W_, dtype=np.float32)[None, :]
    depth = ys / n
    dx = (np.sin(ys * 0.35 + t * 2.4 + (xs + x0) * 0.004) * (1.5 + 7 * depth) + np.sin(ys * 0.11 - t * 1.3) * 3 * depth) * amp
    sy = (wy - 1 - ys - np.sin((xs + x0) * 0.02 + ys * 0.2 + t * 1.7) * 1.5 * depth * amp).astype(np.float32)
    refl = cv2.remap(img, (xs + dx).astype(np.float32), np.broadcast_to(sy, (n, W_)).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    st = vnoise(n, 400, 3, 91, 2)
    st = cv2.resize(st, (W_ * 3, n))[:, int(t * 25 + x0) % W_: int(t * 25 + x0) % W_ + W_]
    alpha = (alpha0 * (1 - depth) ** 1.4 + 0.06) * (0.55 + 0.45 * smooth(st, 0.25, 0.75))
    base = img[wy:].copy()
    img[wy:] = base * (1 - alpha[..., None]) + (refl * 0.92 + base * 0.08) * alpha[..., None]
    return img

class WaterSet(Painted):
    """painting with a live rippling canal below wy (args: water=0 hides it)"""
    def __init__(self, name, build, w, wy, h=OH):
        super().__init__(name, build, w, h); self.wy = wy
    def render(self, t, left, top, z, args):
        d = self.d
        x0 = max(0, int(math.floor(left)) - 2); cw = min(self.w - x0, int(OW / z) + 6)
        y0 = max(0, int(math.floor(top))); ch = min(self.h - y0, int(OH / z) + 6)
        crop = d['img'][:, x0:x0 + cw].copy()
        if args.get('water', 1.0) > 0 and 'water' in d:
            crop[self.wy:] = d['water'][:, x0:x0 + cw]
            reflect(crop, self.wy, t, x0)
            if 'wfg' in d:      # things standing in the water, painted after the reflection
                a = d['wfga'][:, x0:x0 + cw, None]; crop = crop * (1 - a) + d['wfg'][:, x0:x0 + cw] * a
        return warp(crop[y0:y0 + ch], left, top, z, x0, y0)

def tofloat(d):
    for k in list(d.keys()):
        if d[k].dtype == np.float16: d[k] = d[k].astype(np.float32)
    return d

class P2(Painted):
    @property
    def d(self):
        if self._d is None: self._d = tofloat(cached(self.name, self.build))
        return self._d
class W2(WaterSet):
    @property
    def d(self):
        if self._d is None: self._d = tofloat(cached(self.name, self.build))
        return self._d

# =================================================================== XIAOMAN'S ROOM (upstairs)
ROOM_W = 2400; ROOM_FLOOR = 650; ROOM_FEET = 740
WINDOW = (880, 150, 1300, 470)
BED = (1560, 2300, 560)        # x0, x1, mattress top (lie Xiaoman at about y 555)
DESK = (360, 780, 560)

def build_room():
    C = Cv(ROOM_W); P = paper(OH, ROOM_W, 51)
    # sloping attic ceiling: rafters fanning, dark under the ridge
    C.wash([(0, 0), (ROOM_W, 0), (ROOM_W, 70), (0, 150)], 0.55, bleed=2, seed=1, var=0.6, gran=0.7)
    for k in range(0, ROOM_W + 200, 110):
        C.st([(k, 0), (k - 30, 150 - k * 80 / ROOM_W)], 6, 0.75, 0.4, k)
    C.st(wobble([(0, 150), (ROOM_W, 70)], 2, 1), 9, 0.9, 0.35, 2, taper=False)
    # floor boards
    C.wash(rect(0, ROOM_FLOOR, ROOM_W, OH), 0.12, (0.55, 0.68, 0.80), 0.35, bleed=3, seed=3, var=0.7)
    for k, y in enumerate([ROOM_FLOOR + 30, ROOM_FLOOR + 70, ROOM_FLOOR + 125]):
        C.st(wobble([(0, y), (ROOM_W, y)], 1.5, k), 1.4, 0.3, 0.6, 10 + k, taper=False)
    C.st(wobble([(0, ROOM_FLOOR), (ROOM_W, ROOM_FLOOR)], 1, 4), 4, 0.85, 0.3, 14, taper=False)
    for x in (120, 1440, 2330): C.st(wobble([(x, 120 - x * 0.03), (x, ROOM_FLOOR + 4)], 1, x), 16, 0.85, 0.35, 20 + x, taper=False)
    # the window: neighbours' roofs in the rain, a lattice frame
    x0, y0, x1, y1 = WINDOW
    C.wash(rect(x0, y0, x1, y1), 0.04, (0.95, 0.90, 0.85), 0.5, bleed=2, seed=30)
    for i, (a, b, ey) in enumerate([(x0 - 40, x0 + 220, 330), (x0 + 180, x1 + 40, 300), (x0 + 60, x0 + 300, 420)]):
        poly = [(a, ey), (b, ey), (b - 20, ey - 40), (a + 20, ey - 40)]
        C.wash(poly, 0.30 + 0.1 * i, bleed=2, seed=31 + i, gran=0.6)
        C.st(wobble([(a + 14, ey - 40), (b - 14, ey - 40)], 1, i), 4, 0.5, 0.3, 40 + i)
        C.wash(rect(a + 40, ey, b - 40, ey + 80), 0.04, bleed=2, seed=45 + i)
    m = np.ones(C.shape, np.float32); m[y0:y1, x0:x1] = 0      # keep the outside inside the frame
    C.D = np.where(m > 0, C.D, C.D)
    for k in range(1, 4):
        x = x0 + (x1 - x0) * k / 4; C.st([(x, y0), (x, y1)], 4, 0.9, 0.2, 50 + k, taper=False)
    for k in range(1, 3):
        y = y0 + (y1 - y0) * k / 3; C.st([(x0, y), (x1, y)], 4, 0.9, 0.2, 55 + k, taper=False)
    C.st(wobble([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], 1, 6), 12, 0.92, 0.3, 60, taper=False)
    C.wash(rect(x0 - 30, y1 + 6, x1 + 30, y1 + 22), 0.7, bleed=1, seed=61)
    # desk with an oil lamp, paper and a pencil pot; a stool
    dx0, dx1, dy = DESK
    C.wash(rect(dx0, dy, dx1, dy + 18), 0.75, (0.45, 0.55, 0.70), 0.5, bleed=1, seed=70)
    for x in (dx0 + 16, dx1 - 16): C.st([(x, dy + 16), (x, ROOM_FEET - 30)], 9, 0.9, 0.3, 71 + x, taper=False)
    C.wash([(dx0 + 230, dy), (dx0 + 330, dy), (dx0 + 320, dy - 6), (dx0 + 240, dy - 6)], 0.05, bleed=1, seed=73)
    C.wash([(dx0 + 60, dy), (dx0 + 90, dy), (dx0 + 86, dy - 40), (dx0 + 64, dy - 40)], 0.25, bleed=1, seed=74)   # lamp base
    C.st(wobble([(dx0 + 52, dy - 40), (dx0 + 98, dy - 40)], 0.5, 1), 3, 0.9, 0, 75, taper=False)
    C.wash([(dx0 + 58, dy - 42), (dx0 + 92, dy - 42), (dx0 + 86, dy - 92), (dx0 + 64, dy - 92)], 0.03, (0.80, 0.90, 0.95), 0.4, bleed=1, seed=76)
    C.st(wobble([(dx0 + 58, dy - 42), (dx0 + 64, dy - 92), (dx0 + 86, dy - 92), (dx0 + 92, dy - 42)], 0.5, 2), 1.6, 0.85, 0, 77, taper=False)
    C.wash(rect(dx1 - 70, dy - 34, dx1 - 44, dy), 0.3, bleed=1, seed=78)
    for k in range(3): C.st([(dx1 - 64 + k * 7, dy - 34), (dx1 - 70 + k * 11, dy - 64)], 1.6, 0.85, 0, 79 + k)
    # the bed: carved frame posts, a canopy beam, indigo quilt, white pillow
    bx0, bx1, by = BED
    for x in (bx0, bx1): C.st(wobble([(x, 200), (x, ROOM_FEET - 10)], 1, x), 12, 0.9, 0.35, 90 + x, taper=False)
    C.st(wobble([(bx0 - 20, 200), (bx1 + 20, 200)], 1, 3), 14, 0.9, 0.3, 93, taper=False)
    C.st(wobble([(bx0, 230), ((bx0 + bx1) / 2, 250), (bx1, 230)], 2, 4), 3, 0.5, 0.4, 94)
    for k in range(6): C.st([(bx0 + 20 + k * 140, 216), (bx0 + 60 + k * 140, 300)], 2, 0.25, 0.5, 95 + k)   # gauze
    C.wash(rect(bx0, by + 20, bx1, ROOM_FEET - 30), 0.65, (0.45, 0.55, 0.70), 0.5, bleed=1, seed=100)
    C.wash([(bx0 + 8, by + 22), (bx1 - 8, by + 22), (bx1 - 4, by - 10), (bx0 + 200, by - 26), (bx0 + 8, by - 8)], 0.10, (0.70, 0.52, 0.40), 0.75, bleed=1.5, seed=101, gran=0.4)
    C.st(wobble([(bx0 + 8, by - 8), (bx0 + 200, by - 26), (bx1 - 4, by - 10)], 1, 5), 2.2, 0.85, 0.3, 102)
    r = np.random.default_rng(3)
    for k in range(26):    # little flower pattern on the quilt
        x = bx0 + 30 + r.random() * (bx1 - bx0 - 60); y = by - 6 + r.random() * 22
        for a in range(5): over(C.D, ellipse_mask(C.shape, (x + 4 * math.cos(a * 1.26), y + 4 * math.sin(a * 1.26)), (2.4, 2.4)) * 0.3)
    C.wash([(bx1 - 190, by - 4), (bx1 - 30, by - 4), (bx1 - 34, by - 40), (bx1 - 186, by - 40)], 0.03, bleed=1.5, seed=103)
    C.st(wobble([(bx1 - 190, by - 4), (bx1 - 186, by - 40), (bx1 - 34, by - 40), (bx1 - 30, by - 4)], 1, 6), 1.8, 0.8, 0.3, 104, taper=False)
    # backpack slumped on the floor
    bp_ = [(1210 + 45 * math.cos(q) * (1.1 if q > math.pi else 1), ROOM_FEET - 40 + 42 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 30)]
    C.wash(bp_, 0.18, (0.55, 0.62, 0.85), 0.7, bleed=1, seed=110)
    C.st(wobble(bp_, 1, 7), 2, 0.9, 0.3, 111)
    return dict(img=flatten(C, P).astype(np.float16))

ROOM = P2('room', build_room, ROOM_W)

def room_live(ctx, rain_amt=1.0, lamp=0.0):
    t = ctx.Tabs; x0, y0, x1, y1 = WINDOW
    if rain_amt > 0:
        sx0, sy0 = ctx.T(x0 + 6, y0 + 6); sx1, sy1 = ctx.T(x1 - 6, y1 - 6)
        if sx1 > 0 and sx0 < OW:
            L = ctx.layer(max(0, sx0), max(0, sy0), min(OW, sx1), min(OH, sy1))
            h, w = L.D.shape; rr = np.random.default_rng(4)
            for k in range(int(90 * rain_amt)):
                x = (rr.random() * w - t * 30) % w; y = (rr.random() * h + t * 800 * ctx.z) % (h + 40) - 20; l = (10 + rr.random() * 14) * ctx.z
                cv2.line(L.D, (int(x * 4), int(y * 4)), (int((x - l * 0.15) * 4), int((y - l) * 4)), 0.3 * rain_amt, 1, cv2.LINE_AA, 2)
    if lamp > 0:
        fl = 0.9 + 0.1 * math.sin(t * 11) * math.sin(t * 5.3)
        ctx.add_glow(DESK[0] + 75, DESK[2] - 66, 7, lamp * fl, WARM)
        ctx.add_glow(DESK[0] + 75, DESK[2] - 66, 60, 0.18 * lamp, WARM)

# =================================================================== THE STONE BRIDGE (close)
BR_W = 2800; BR_WY = 640; BR_CX = 1400
def deck_y(x):
    """top of the bridge deck at x (people stand here)"""
    u = (x - BR_CX) / 760.0
    return 600 - 300 * max(0, 1 - u * u) ** 0.9 if abs(u) < 1 else 600

def build_bridge():
    C = Big(BR_W); P = paper(OH, BR_W, 61)
    hills(C, BR_W, (240, 300), (0.09, 0.14), 5)
    # houses on the far bank, light
    for i, (a, b, ey) in enumerate([(0, 360, 360), (380, 700, 330), (2100, 2420, 340), (2440, 2800, 370)]):
        house(C, a, b, ey, BR_WY - 30, 0.55, 500 + i * 7, rh=44, wins=((0.3, 44, 30, 32, 'dark'), (0.7, 44, 30, 32, 'lattice')))
    stroke(C.D, wobble([(0, BR_WY - 30), (BR_W, BR_WY - 30)], 1, 1), 3.5, 0.6, 0.4, 7, taper=False)
    # the bridge: a big single arch, stone courses, steps, balustrade
    xs = np.linspace(BR_CX - 780, BR_CX + 780, 120)
    deck = np.array([(x, deck_y(x)) for x in xs])
    R = 330; archc = (BR_CX, BR_WY + 20)
    arch = np.array([(archc[0] + R * math.cos(a), archc[1] - R * math.sin(a) * 0.95) for a in np.linspace(0, math.pi, 90)])
    body = np.vstack([deck - [0, 60], deck[::-1] + [0, 0]])
    full = np.vstack([deck - [0, 58], [(BR_CX + 800, BR_WY + 10)], arch, [(BR_CX - 800, BR_WY + 10)]])
    C.clear(full, 1.0)
    m = poly_mask(C.shape, [np.vstack([deck, [(BR_CX + 800, BR_WY + 10)], arch, [(BR_CX - 800, BR_WY + 10)]])])
    over(C.D, wash(m, 0.16, bleed=3, seed=11, var=0.8, gran=0.9))
    stroke(C.D, wobble(deck, 1.5, 3), 7, 0.92, 0.35, 12)
    stroke(C.D, wobble(arch, 1.5, 4), 7, 0.9, 0.35, 13)
    arch2 = np.array([(archc[0] + (R + 40) * math.cos(a), archc[1] - (R + 40) * math.sin(a) * 0.95) for a in np.linspace(0.04, math.pi - 0.04, 80)])
    stroke(C.D, wobble(arch2, 1.5, 5), 2.5, 0.6, 0.5, 14)
    for a in np.linspace(0.12, math.pi - 0.12, 15):     # voussoir joints
        p0 = (archc[0] + R * math.cos(a), archc[1] - R * math.sin(a) * 0.95); p1 = (archc[0] + (R + 40) * math.cos(a), archc[1] - (R + 40) * math.sin(a) * 0.95)
        stroke(C.D, [p0, p1], 1.6, 0.6, 0.3, int(a * 100), taper=False)
    r = np.random.default_rng(9)
    for k in range(70):   # stone courses
        x = BR_CX - 760 + r.random() * 1520; y = deck_y(x) + 20 + r.random() * 240
        if y < BR_WY and math.hypot((x - archc[0]) / (R + 50), (y - archc[1]) / ((R + 50) * 0.95)) > 1:
            stroke(C.D, [(x, y), (x + 30 + r.random() * 40, y)], 1.3, 0.35, 0.5, 100 + k, taper=False)
    # balustrade: posts and rail following the deck (people stand in front of it)
    rail = deck - [0, 46]
    stroke(C.D, wobble(rail[6:-6], 1, 6), 4, 0.85, 0.35, 15)
    for i in range(6, len(xs) - 6, 9):
        x, y = deck[i]; stroke(C.D, [(x, y - 2), (x, y - 52)], 8, 0.85, 0.3, 200 + i, taper=False)
        over(C.D, ellipse_mask(C.shape, (x, y - 54), (6, 5)) * 0.8)
    # willow on the left bank (strands are live), stone steps down to the water on the right
    stroke(C.D, wobble([(330, BR_WY - 26), (318, 470), (342, 340), (322, 220), (338, 120)], 3, 7), np.array([30, 25, 19, 13, 6.0]), 0.85, 0.8, 16)
    for k, (dx, dy, w) in enumerate([(160, -90, 11), (-150, -60, 10), (110, -180, 8), (-90, -190, 7), (200, 20, 7)]):
        y0 = 300 - k * 34
        stroke(C.D, [(330, y0), (330 + dx * 0.5, y0 + dy * 0.6), (330 + dx, y0 + dy)], np.array([w, w * 0.6, 2.0]), 0.85, 0.6, 17 + k)
    img = flatten(C, P)
    wat = paper(OH - BR_WY, BR_W, 62)
    return dict(img=img.astype(np.float16), water=wat.astype(np.float16))

BRIDGE = W2('bridge', build_bridge, BR_W, BR_WY)
BRIDGE_TIPS = [(330 + dx, 300 - k * 34 + dy) for k, (dx, dy, w) in enumerate([(160, -90, 11), (-150, -60, 10), (110, -180, 8), (-90, -190, 7), (200, 20, 7)])]
def bridge_strands():
    r = np.random.default_rng(6); st = []
    for (tx, ty) in BRIDGE_TIPS:
        for k in range(10):
            u = k / 10; ax = 330 + (tx - 330) * (0.35 + 0.65 * u) + r.normal(0, 6); ay = 300 + (ty - 300) * (0.35 + 0.65 * u) + r.normal(0, 8)
            st.append((ax, ay, 140 + r.random() * 220, r.random() * 6.28, 0.6 + r.random() * 0.6))
    return st
BR_STRANDS = bridge_strands()

# =================================================================== THE LANE (laundry and market)
LANE_W = 4400; LANE_G = 700
def build_lane():
    C = Big(LANE_W); P = paper(OH, LANE_W, 71)
    r = np.random.default_rng(11)
    # far roofs over the wall tops
    for i in range(14):
        a = i * 330 - 60 + r.random() * 60; b = a + 260 + r.random() * 120; ey = 170 + r.random() * 40
        roof_band(C, a, b, ey, 30, 0.35, 700 + i)
    # the lane's back row: white walls, doors, windows, gables
    x = 0; i = 0
    while x < LANE_W:
        w = 380 + r.random() * 220; ey = 250 + r.random() * 50
        house(C, x, x + w, ey, LANE_G - 40, 1.0, 800 + i * 13, rh=44,
              wins=((0.25, 70, 34, 38, 'lattice' if i % 2 else 'dark'), (0.75, 70, 34, 38, 'dark')), door=(0.5, 60, 140) if i % 3 != 1 else None,
              gable=(('l', 2) if i % 4 == 0 else None))
        x += w; i += 1
    # paving
    stroke(C.D, wobble([(0, LANE_G - 40), (LANE_W, LANE_G - 40)], 1, 2), 4, 0.85, 0.35, 900, taper=False)
    gm = poly_mask(C.shape, [rect(0, LANE_G - 38, LANE_W, OH)])
    over(C.D, wash(gm, 0.10, bleed=2, seed=901, gran=0.9, var=0.7))
    for k, y in enumerate([LANE_G - 10, LANE_G + 30, LANE_G + 80]):
        stroke(C.D, wobble([(0, y), (LANE_W, y)], 1.5, k), 1.3, 0.3, 0.6, 910 + k, taper=False)
    for xx in range(0, LANE_W, 90):
        stroke(C.D, [(xx + r.random() * 30, LANE_G - 38), (xx + r.random() * 30 - 20, OH)], 1.2, 0.22, 0.6, 920 + xx, taper=False)
    # market stalls: awnings on poles, baskets of greens, crates
    stalls = [700, 1500, 2600, 3500]
    for k, sx in enumerate(stalls):
        aw = [(sx - 150, 420), (sx + 150, 420), (sx + 180, 470), (sx - 180, 470)]
        C.clear(aw, 1); over(C.D, wash(poly_mask(C.shape, [aw]), 0.12, bleed=1.5, seed=930 + k, gran=0.6))
        C.tints.append((poly_mask(C.shape, [aw]) * 0.45, [(0.60, 0.72, 0.85), (0.70, 0.75, 0.62), (0.55, 0.62, 0.80), (0.75, 0.70, 0.60)][k]))
        for j in range(7): stroke(C.D, [(sx - 150 + j * 50, 420), (sx - 180 + j * 60, 470)], 1.2, 0.5, 0, 940 + k * 10 + j)
        for px in (sx - 165, sx + 165): stroke(C.D, [(px, 465), (px, LANE_G - 30)], 5, 0.9, 0.3, 960 + px, taper=False)
        tb = rect(sx - 140, 560, sx + 140, 578); C.clear(tb, 1); over(C.D, wash(poly_mask(C.shape, [tb]), 0.7, bleed=1, seed=970 + k))
        for px in (sx - 125, sx + 125): stroke(C.D, [(px, 576), (px, LANE_G - 34)], 5, 0.85, 0.3, 975 + px, taper=False)
        for j in range(3):   # baskets with produce
            bx = sx - 90 + j * 90
            bk = [(bx - 36, 560), (bx + 36, 560), (bx + 28, 528), (bx - 28, 528)]
            C.clear(bk, 0.6); over(C.D, wash(poly_mask(C.shape, [bk]), 0.25, bleed=1, seed=980 + k * 3 + j, gran=0.9))
            for q in range(5):
                cx = bx - 22 + q * 11; cy = 522 - (q % 2) * 6
                mm = ellipse_mask(C.shape, (cx, cy), (8, 7)); C.D *= 1 - mm
                over(C.D, wash(mm, 0.08, bleed=0.6, seed=990 + q))
                C.tints.append((mm * 0.6, [(0.45, 0.75, 0.55), (0.35, 0.50, 0.85), (0.45, 0.80, 0.90)][(k + j) % 3]))
                stroke(C.D, [(cx + 8 * math.cos(a), cy + 7 * math.sin(a)) for a in np.linspace(0, 6.3, 14)], 1.2, 0.7, 0, 995 + q, taper=False)
    # bamboo laundry poles across the lane (cloth is live)
    poles = []
    for k, px in enumerate([300, 1100, 1900, 2250, 3000, 3900]):
        y = 300 + (k % 3) * 22
        stroke(C.D, wobble([(px - 260, y + 8), (px + 260, y - 8)], 1, k), 5, 0.85, 0.35, 1000 + k)
        poles.append((px - 240, y + 7, px + 240, y - 7))
    return dict(img=flatten(C, P).astype(np.float16), poles=np.array(poles, np.float32))

LANE = P2('lane', build_lane, LANE_W)

LAUNDRY_COLS = [(0.80, 0.82, 0.85), (0.70, 0.55, 0.45), (0.55, 0.65, 0.90), (0.85, 0.85, 0.80), (0.65, 0.75, 0.62)]
def laundry(ctx, wind=0.3, gust=0.0):
    """cloth hanging from the poles, swaying; gust (0..1) lifts it sideways"""
    t = ctx.Tabs
    for k, (x0, y0, x1, y1) in enumerate(LANE.d['poles']):
        n = 4
        for j in range(n):
            u0 = 0.08 + j * 0.23; u1 = u0 + 0.16
            ax, ay = x0 + (x1 - x0) * u0, y0 + (y1 - y0) * u0; bx, by = x0 + (x1 - x0) * u1, y0 + (y1 - y0) * u1
            sa, _ = ctx.T(ax, ay)
            if sa < -300 or sa > OW + 300: continue
            hgt = 70 + ((k * 7 + j * 3) % 5) * 14
            sw = math.sin(t * 2.2 + k + j * 1.7) * 8 * wind + gust * 60 * (0.8 + 0.4 * math.sin(t * 9 + j))
            lift = gust * 0.5
            poly = [(ax, ay), (bx, by), (bx + sw * 1.1, by + hgt * (1 - lift) + math.sin(t * 3 + j) * 4 * wind), ((ax + bx) / 2 + sw, (ay + by) / 2 + hgt * (1.05 - lift)), (ax + sw * 0.9, ay + hgt * (1 - lift))]
            pts = ctx.Tp(poly)
            xs, ys = pts[:, 0], pts[:, 1]
            L = ctx.layer(xs.min() - 10, ys.min() - 10, xs.max() + 10, ys.max() + 10)
            from chars import fill, line
            fill(L, pts, 0.04, LAUNDRY_COLS[(k + j) % 5], 0.7, s=ctx.z, seed=k * 10 + j, edge=0.6)
            line(L, np.vstack([pts, pts[:1]]), 1.4, ctx.z, 0.8, 0.3, k * 10 + j + 5, taper=False)

# =================================================================== THE MUDFLAT (town's edge, dry riverbed)
MUD_W = 3600; MUD_HZ = 400
QIAN_BOAT = (2650, 640)
def build_mudflat():
    C = Big(MUD_W); P = paper(OH, MUD_W, 81)
    hills(C, MUD_W, (250, 320), (0.08, 0.12), 9)
    # the town, far on the left: small roofs and walls
    for i in range(10):
        a = 60 + i * 120 + (i % 3) * 14; b = a + 100 + (i % 2) * 40; ey = MUD_HZ - 34 - (i % 3) * 12
        roof_band(C, a, b, ey, 14, 0.7, 1100 + i, curl=4)
        wall(C, a + 4, b - 4, ey + 1, MUD_HZ, 0.6, 1120 + i, lines=False)
    stroke(C.D, wobble([(0, MUD_HZ), (MUD_W, MUD_HZ)], 2, 3), 2.2, 0.55, 0.4, 1150, taper=False)
    # dry riverbed in perspective: banks converging, cracked mud plates
    yy = np.arange(OH, dtype=np.float32)[:, None]
    mm = (yy > MUD_HZ).astype(np.float32) * np.ones((1, MUD_W), np.float32)
    over(C.D, wash(mm, 0.15, bleed=2, seed=1160, var=1.0, gran=1.0) * np.clip((yy - MUD_HZ) / 300, 0.3, 1))
    C.tints.append((mm * 0.55, (0.60, 0.70, 0.80)))
    r = np.random.default_rng(13)
    for k in range(2600):
        x = r.random() * MUD_W; y = MUD_HZ + 6 + (r.random() ** 1.6) * (OH - MUD_HZ)
        d = (y - MUD_HZ) / (OH - MUD_HZ); L = 10 + d * 70
        a = r.random() * math.pi; q = [(x, y)]
        for j in range(3):
            a += (r.random() - 0.5) * 1.3
            q.append((q[-1][0] + math.cos(a) * L / 3, q[-1][1] + math.sin(a) * L / 3 * (0.25 + 0.5 * d)))
        stroke(C.D, q, 0.6 + 1.8 * d, 0.5, 0.5, 1200 + k)
    for k in range(30):    # stranded stones and dead reeds
        x = r.random() * MUD_W; y = MUD_HZ + 30 + r.random() * 360; d = (y - MUD_HZ) / 400
        e = ellipse_mask(C.shape, (x, y), (6 + 18 * d, 3 + 8 * d)); C.D *= 1 - e
        over(C.D, wash(e, 0.5, bleed=1, seed=1300 + k))
        for j in range(3): stroke(C.D, [(x + j * 6 * d, y), (x + j * 9 * d + 10, y - 40 * d - 10)], 1 + d, 0.6, 0.4, 1310 + k * 3 + j)
    # Qian's painted boat, stuck: lacquer red hull, gold trim, a little cabin, tilted
    bx, by = QIAN_BOAT
    B = Big(MUD_W)
    top = bezier((bx - 330, by - 70), (bx, by - 30), (bx + 330, by - 90), n=40)
    bot = bezier((bx + 330, by - 90), (bx + 40, by + 70), (bx - 330, by - 70), n=40)
    hull = np.vstack([top, bot])
    B.clear(hull, 1); hm = poly_mask(B.shape, [hull])
    over(B.D, wash(hm, 0.22, bleed=1.5, seed=1400, gran=0.6)); B.tints.append((hm * 0.85, (0.22, 0.28, 0.72)))
    stroke(B.D, wobble(top, 1, 1), 7, 0.92, 0.3, 1401); stroke(B.D, wobble(bot, 1, 2), 5, 0.9, 0.35, 1402)
    trim = top + [0, 16]; tm = stroke_mask(B.shape, trim, 6)
    B.tints.append((tm * 0.9, (0.25, 0.72, 0.92)))
    cab = [(bx - 150, by - 50), (bx + 110, by - 56), (bx + 104, by - 150), (bx - 144, by - 144)]
    B.clear(cab, 1); cm = poly_mask(B.shape, [cab]); over(B.D, wash(cm, 0.08, bleed=1, seed=1403)); B.tints.append((cm * 0.5, (0.45, 0.70, 0.85)))
    for k in range(5): stroke(B.D, [(bx - 130 + k * 58, by - 56), (bx - 128 + k * 58, by - 146)], 2, 0.8, 0, 1404 + k, taper=False)
    roof = list(bezier((bx - 200, by - 132), (bx - 20, by - 160), (bx + 170, by - 146), n=20)) + list(bezier((bx + 120, by - 186), (bx - 20, by - 196), (bx - 160, by - 178), n=20))
    B.clear(roof, 1); rm = poly_mask(B.shape, [roof]); over(B.D, wash(rm, 0.75, bleed=1, seed=1410, gran=0.6))
    stroke(B.D, wobble(list(bezier((bx - 214, by - 120), (bx - 20, by - 162), (bx + 186, by - 134), n=20)), 1, 3), 5, 0.95, 0.3, 1411)
    for k in range(2):
        lx = bx - 190 + k * 360; lm = ellipse_mask(B.shape, (lx, by - 100), (14, 18)); B.clear(np.array([(lx - 14, by - 118), (lx + 14, by - 118), (lx + 14, by - 82), (lx - 14, by - 82)]), 1)
        B.tints.append((lm * 0.9, VERMILION)); stroke(B.D, [(lx, by - 132), (lx, by - 118)], 1.2, 0.8, 0, 1420 + k)
    M = cv2.getRotationMatrix2D((bx, by), 6, 1.0)
    rot = lambda a: cv2.warpAffine(a, M, (MUD_W, OH))
    Bm = rot(np.clip(poly_mask(B.shape, [hull]) + poly_mask(B.shape, [cab]) + poly_mask(B.shape, [roof]), 0, 1))
    C.D *= 1 - Bm; C.tints = [(a * (1 - Bm), c) for a, c in C.tints]
    over(C.D, rot(B.D)); C.tints += [(rot(a), c) for a, c in B.tints]
    # planks laid across the mud toward the boat
    for k in range(5):
        x = bx - 480 + k * 70; y = by + 30 + (k % 2) * 6
        stroke(C.D, [(x, y), (x + 80, y - 4)], 9, 0.6, 0.5, 1430 + k, taper=False)
    return dict(img=flatten(C, P).astype(np.float16))

MUDFLAT = P2('mudflat', build_mudflat, MUD_W)

def mud_y(y): return y      # people stand anywhere on the flat; scale them by depth
def depth_s(y, s0=1.6):
    return s0 * (0.35 + 0.65 * (y - MUD_HZ) / (OH - MUD_HZ))

# =================================================================== SKY (tall: mudflat at the bottom, clouds above)
SKY_W, SKY_H = 2600, 2400
def build_sky():
    town.H = SKY_H
    try: return _build_sky()
    finally: town.H = OH
def _build_sky():
    C = Big(SKY_W, SKY_H); P = paper(SKY_H, SKY_W, 91)
    r = np.random.default_rng(21)
    yy = np.arange(SKY_H, dtype=np.float32)[:, None]
    # a soft wet sky wash, darker high up
    over(C.D, wash(np.ones((SKY_H, SKY_W), np.float32), 0.10, bleed=10, seed=2, var=1.2, gran=0.5) * np.clip(1 - yy / SKY_H, 0.15, 1))
    # clouds: soft wet ink, built from stretched noise; darker, heavier bands higher up
    for k, (sc, thr, d) in enumerate([(380, 0.55, 0.16), (220, 0.60, 0.20), (120, 0.66, 0.16)]):
        n = vnoise(SKY_H // 3, SKY_W // 1, sc, 30 + k, 4)
        n = cv2.resize(n, (SKY_W, SKY_H))
        dens = np.clip(1.15 - yy / SKY_H, 0.2, 1.0)
        m = smooth(n, thr, thr + 0.12)
        bottoms = np.clip(m - np.roll(m, -18, axis=0), 0, 1)     # wet pooled undersides
        over(C.D, cv2.GaussianBlur(m, (0, 0), 3) * d * dens + bottoms * 0.10 * dens)
    # far ground at the bottom: the town and hills
    base = SKY_H - 300
    xs = np.arange(SKY_W); n = vnoise(1, SKY_W, 220, 5, 4)[0]
    ridge = base - 80 * n
    m = (yy > ridge[None, :]).astype(np.float32)
    over(C.D, wash(m, 0.14, bleed=4, seed=7) * np.clip(1 - (yy - ridge[None, :]) / 140, 0, 1))
    for i in range(16):
        a = 200 + i * 80; b = a + 60; ey = base + 30 - (i % 3) * 8
        roof_band(C, a, b, ey, 10, 0.6, 1500 + i, curl=3)
        wall(C, a + 3, b - 3, ey, base + 60, 0.5, 1520 + i, lines=False)
    gm = (yy > base + 60).astype(np.float32) * np.ones((1, SKY_W), np.float32)
    over(C.D, wash(gm, 0.12, bleed=2, seed=8, var=0.9, gran=0.9))
    return dict(img=flatten(C, P).astype(np.float16))

SKY = P2('sky', build_sky, SKY_W, SKY_H)

# =================================================================== ROOFTOPS (night chase)
ROOF_W = 4200
SKYLIGHT = (1500, 690)
def build_roofs():
    C = Big(ROOF_W); P = paper(OH, ROOF_W, 101)
    hills(C, ROOF_W, (300, 360), (0.08, 0.12), 13)
    r = np.random.default_rng(31)
    # layers of roofs, far (light, small) to near (dark, big)
    for layer, (n, y0, rh, tone) in enumerate([(18, 360, 30, 0.35), (12, 440, 60, 0.6), (8, 560, 110, 0.95)]):
        x = -100
        while x < ROOF_W:
            w = 240 + r.random() * 200 + layer * 100; ey = y0 + r.random() * 30 + layer * 30
            sd = 1600 + layer * 100 + int(x) % 97
            nw = int(w // (150 + 40 * layer))
            wins = tuple(((k + 0.7) / (nw + 0.4), 30 + 10 * layer + r.random() * 8, 14 + 8 * layer, 16 + 10 * layer, int(r.random() * 3)) for k in range(nw) if r.random() < 0.7)
            gable = (('l' if r.random() < 0.5 else 'r'), 1 + layer // 2) if r.random() < 0.45 else None
            house(C, x, x + w, ey + rh, OH, tone, sd, rh=rh, wins=wins, gable=gable)
            x += w + 30 + r.random() * 50
    # the skylight over the shop (a dark square hole in the tiles)
    sx, sy = SKYLIGHT
    m = poly_mask(C.shape, [[(sx - 50, sy - 20), (sx + 50, sy - 22), (sx + 54, sy + 22), (sx - 54, sy + 22)]])
    over(C.D, wash(m, 0.9, bleed=1, seed=1700))
    # the moon, a pale disc behind a cloud band
    mm = ellipse_mask(C.shape, (3300, 140), (70, 70)); C.D *= 1 - mm
    stroke(C.D, [(3300 + 70 * math.cos(a), 140 + 70 * math.sin(a)) for a in np.linspace(0, 6.3, 50)], 1.5, 0.4, 0.3, 1701, taper=False)
    cb = poly_mask(C.shape, [[(3100, 150), (3500, 140), (3520, 175), (3080, 180)]])
    over(C.D, wash(cb, 0.12, bleed=8, seed=1702, rough=0.5))
    return dict(img=flatten(C, P).astype(np.float16))

ROOFS = P2('roofs', build_roofs, ROOF_W)
def roof_y(x):
    """walkable ridge line for the chase on the near roofs (approx.)"""
    return 634 + 6 * math.sin(x / 300.0)

# =================================================================== SHADOW SCREEN (the flashback)
def build_screen():
    C = Big(OW); P = paper(OH, OW, 111)
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    lit = np.exp(-(((xx - OW / 2) / 900) ** 2 + ((yy - OH / 2) / 600) ** 2))
    C.tints.append(((1 - lit) * 0.45, (0.55, 0.62, 0.80)))
    C.tints.append((lit * 0.25, (0.60, 0.80, 1.0)))
    for k, (a, b) in enumerate([((0, 0), (OW, 0)), ((0, OH - 1), (OW, OH - 1))]):
        stroke(C.D, [a, b], 34, 0.95, 0.3, 1800 + k, taper=False)
    for x in (0, OW - 1): stroke(C.D, [(x, 0), (x, OH)], 30, 0.95, 0.3, 1810 + x, taper=False)
    return dict(img=flatten(C, P).astype(np.float16))
SCREEN = P2('screen', build_screen, OW)

# =================================================================== CITY WINDOW
def build_city():
    C = Big(OW); P = paper(OH, OW, 121)
    r = np.random.default_rng(41)
    over(C.D, np.full((OH, OW), 0.10, np.float32))
    for k in range(26):    # grey towers, flat, many windows
        x = r.random() * OW; w = 80 + r.random() * 160; top = 60 + r.random() * 300; d = 0.15 + r.random() * 0.25
        m = poly_mask(C.shape, [rect(x, top, x + w, OH)]); over(C.D, wash(m, d, bleed=1.5, seed=1900 + k, var=0.4))
        for yy in range(int(top) + 20, OH, 34):
            for xx in range(int(x) + 12, int(x + w) - 12, 26):
                if r.random() < 0.7: over(C.D, poly_mask(C.shape, [rect(xx, yy, xx + 12, yy + 16)]) * 0.12)
    # the window frame (aluminium grey) and the sill inside
    for x in (300, 1620): stroke(C.D, [(x, 0), (x, OH)], 26, 0.7, 0.1, 1950 + x, taper=False)
    stroke(C.D, [(300, 60), (1620, 60)], 22, 0.7, 0.1, 1960, taper=False)
    stroke(C.D, [(960, 60), (960, 600)], 14, 0.6, 0.1, 1961, taper=False)
    sill = poly_mask(C.shape, [rect(0, 600, OW, OH)]); C.D *= 1 - sill * 0.9
    over(C.D, wash(sill, 0.18, bleed=1, seed=1962)); stroke(C.D, [(0, 600), (OW, 600)], 6, 0.85, 0.1, 1963, taper=False)
    m = np.zeros((OH, OW), np.float32); m[:, :300] = 1; m[:, 1620:] = 1; m[:60] = 1
    C.D[m > 0] = np.maximum(C.D[m > 0] * 0.3, 0.55)
    return dict(img=flatten(C, P).astype(np.float16))
CITY = P2('city', build_city, OW)

def city_live(ctx, amount=1.0):
    """rain running down the glass: beads and trails"""
    t = ctx.Tabs; L = ctx.layer(300, 60, 1620, 600, front=True); r = np.random.default_rng(8)
    for k in range(int(70 * amount)):
        x = r.random() * 1320; sp = 20 + r.random() * 60; y = (r.random() * 600 + t * sp) % 560
        cv2.line(L.D, (int(x * 4), int(max(0, y - 40 - sp) * 4)), (int(x * 4), int(y * 4)), 0.10, 2, cv2.LINE_AA, 2)
        cv2.circle(L.D, (int(x * 4), int(y * 4)), 10, 0.45, -1, cv2.LINE_AA, 2)
        cv2.circle(L.M, (int((x - 1) * 4), int((y - 1) * 4)), 4, 0.8, -1, cv2.LINE_AA, 2)

# =================================================================== PAPER (cards)
PAPER_SET = P2('paper', lambda: dict(img=paper(OH, OW, 131).astype(np.float16)), OW)
