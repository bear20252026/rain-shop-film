# Painted sets. Each has render(t, left, top, z, args) -> OHxOWx3 float image of the world seen through the camera.
import os, math, numpy as np, cv2
from ink import *
from town import *
from engine import CACHE, OW, OH, kf, JAR_COLS, GLOW, WARM
from chars import ease, lerp

def flatten(C, P):
    img = P.copy()
    for a, c in C.tints: img *= 1 - a[..., None] * (1 - np.asarray(c, np.float32))
    return img * (1 - C.D[..., None]) + INK * C.D[..., None]

def warp(img, left, top, z, x0=0, y0=0):
    """sample a world image (whose top-left is at world x0,y0) through the camera"""
    M = np.float32([[z, 0, -(left - x0) * z], [0, z, -(top - y0) * z]])
    return cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LINEAR if z <= 1.05 else cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def cached(name, build):
    f = os.path.join(CACHE, name + '.npz')
    if os.path.exists(f):
        z = np.load(f, allow_pickle=True); return {k: z[k] for k in z.files}
    d = build(); np.savez(f, **d); return d

class Painted:
    """a static painting (built once, cached) seen through the camera"""
    def __init__(self, name, build, w, h=OH):
        self.name, self.build, self.w, self.h = name, build, w, h; self._d = None
    @property
    def d(self):
        if self._d is None:
            self._d = cached(self.name, self.build)
            self._d['img'] = self._d['img'].astype(np.float32)
        return self._d
    def render(self, t, left, top, z, args):
        return warp(self.d['img'], left, top, z)

# ======================================================== THE TOWN (canal front)
WIN_LIT = [(105, 446, 26, 30), (1106, 416, 30, 34), (1224, 416, 30, 34), (1420, 438, 40, 30), (1632, 300, 92, 52), (1788, 300, 92, 52),
           (1979, 404, 28, 32), (2111, 404, 28, 32), (2330, 440, 40, 30), (2537, 418, 26, 30)]

def _mud(w, seed=5):
    """dry canal bed: cracked grey-brown mud, a few dead lotus stalks"""
    h = H - WATER_Y + 4
    P = paper(h, w, seed)
    D = np.zeros((h, w), np.float32)
    yy = np.arange(h, dtype=np.float32)[:, None]
    over(D, wash(np.ones((h, w), np.float32), 0.20, bleed=2, seed=seed, rough=0.3, var=0.9, gran=0.9) * (0.55 + 0.45 * (1 - yy / h)))
    r = np.random.default_rng(seed)
    # crack network: jittered polylines between random seeds (perspective-squashed)
    pts = np.column_stack([r.random(900) * w, r.random(900) ** 0.8 * h])
    for p in pts:
        a = r.random() * math.pi; L = 20 + r.random() * 40
        q = [p]
        for k in range(3):
            a += (r.random() - 0.5) * 1.2
            q.append(q[-1] + np.array([math.cos(a) * L / 3, math.sin(a) * L / 3 * (0.35 + 0.65 * q[-1][1] / h)]))
        stroke(D, q, 1.0 + 1.2 * p[1] / h, 0.45, 0.5, int(r.integers(1e6)))
    for k in range(40):     # dead lotus: bent stalks with a drooping dry leaf
        x = r.random() * w; y = 30 + r.random() * (h - 40)
        tx = x + (r.random() - 0.5) * 30; ty = y - 40 - r.random() * 50
        stroke(D, [(x, y), ((x + tx) / 2 + 6, (y + ty) / 2), (tx, ty)], np.array([2.2, 1.6, 1.0]), 0.7, 0.4, k + 900)
        stroke(D, [(tx, ty), (tx + 14, ty + 6), (tx + 22, ty + 20)], np.array([5, 4, 1.5]), 0.55, 0.6, k + 950)
    tint = [(np.full((h, w), 0.5, np.float32), (0.62, 0.72, 0.80))]
    img = P.copy()
    for a, c in tint: img *= 1 - a[..., None] * (1 - np.asarray(c, np.float32))
    return img * (1 - D[..., None]) + INK * D[..., None]

def _water_things():
    Cb = Canvas(WW); boat(Cb, 1150, 1.0, 121)
    Cp = Canvas(WW); stroke(Cp.D, wobble([(2090, WATER_Y + 40), (2092, WATER_Y - 62)], 1.5, 3), np.array([13, 11.0]), 0.9, 0.5, 131, taper=False)
    # the dry boat: same boat, tilted, sitting on the mud
    Cd = Canvas(WW); boat(Cd, 1150, 1.0, 121)
    M = cv2.getRotationMatrix2D((1150, WATER_Y + 52), -7, 1.0); M[1, 2] += 70
    Dd = cv2.warpAffine(Cd.D, M, (WW, H))
    return dict(Db=Cb.D, Dp=Cp.D, Dd=Dd)

def _color_map(S):
    """watercolor tints for the town once color returns"""
    mul = np.ones((H, WW, 3), np.float32)
    yy, xx = np.mgrid[0:H, 0:WW].astype(np.float32)
    def tint(a, c): mul[:] *= 1 - a[..., None] * (1 - np.asarray(c, np.float32))
    sky = np.clip(1 - yy / 420, 0, 1) * (1 - S['O']); tint(sky * 0.30, (0.96, 0.86, 0.72))          # pale blue sky
    Dh = np.zeros((H, WW), np.float32); Dh[:, :2300] = S['Dh']
    tint(np.clip(Dh * 3.5, 0, 1) * (1 - S['O']) * 0.75, (0.70, 0.86, 0.62))                          # green-blue hills
    roofs = np.clip(S['Dm'] * 1.2, 0, 1) * (yy < 520); tint(roofs * 0.35, (0.80, 0.70, 0.62))       # blue-grey tiles
    wat = (yy > WATER_Y).astype(np.float32); tint(wat * 0.55, (0.95, 0.80, 0.55))                    # blue canal
    return mul

class TownSet:
    def __init__(self):
        self._S = None
    @property
    def S(self):
        if self._S is None:
            z = np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static01.npz'), allow_pickle=True)
            S = {k: z[k] for k in z.files}
            S.update(cached('town_water', _water_things))
            S['mud'] = cached('town_mud', lambda: dict(img=_mud(WW).astype(np.float16)))['img'].astype(np.float32)
            S['cmul'] = cached('town_color', lambda: dict(img=_color_map(S).astype(np.float16)))['img'].astype(np.float32)
            S['MIST'] = vnoise(H, WW + 800, 160, 77, 3)
            S['STREAK'] = cv2.resize(vnoise(H - WATER_Y, (WW + 1200) // 10, 3, 91, 2), (WW + 1200, H - WATER_Y))
            r = np.random.default_rng(5); st = []
            for (tx, ty) in S['tips']:
                for k in range(9):
                    u = k / 9; ax = 960 + (tx - 960) * (0.35 + 0.65 * u) + r.normal(0, 6); ay = 330 + (ty - 330) * (0.35 + 0.65 * u) + r.normal(0, 8)
                    st.append((ax, ay, 110 + r.random() * 180, r.random() * 6.28, 0.6 + r.random() * 0.6))
            S['strands'] = st
            self._S = S
        return self._S
    def render(self, t, left, top, z, args):
        S = self.S
        water = args.get('water', 1.0); mist = args.get('mist', 1.0); col = args.get('color', 0.0); sun = args.get('sun', 0.0)
        x0 = int(math.floor(left)) - 2; y0 = max(0, int(math.floor(top)))
        cw = int(OW / z) + 6
        x0 = max(0, min(WW - cw, x0)); sl = slice(x0, x0 + cw)
        hx = int(x0 * 0.4) + 60
        Dh = S['Dh'][:, hx:hx + cw]
        if Dh.shape[1] < cw: Dh = np.pad(Dh, ((0, 0), (0, cw - Dh.shape[1])), mode='edge')
        D = Dh * (1 - S['O'][:, sl]); over(D, S['Dm'][:, sl])
        if mist > 0:
            mo = x0 + int(t * 14); m = S['MIST'][:, mo:mo + cw]
            yy = np.arange(H, dtype=np.float32)[:, None]
            band = np.exp(-((yy - 360) / 90) ** 2) * 0.55 + np.exp(-((yy - 560) / 40) ** 2) * 0.25
            D *= 1 - band * smooth(m, 0.35, 0.75) * mist
        img = S['P'][:, sl] * S['mul'][:, sl]
        if sun > 0:     # a flat vermilion sun of the drought, low in the sky, behind everything
            yy, xx = np.mgrid[0:H, 0:cw].astype(np.float32)
            sm = smooth(-np.sqrt((xx - (cw * 0.72)) ** 2 + (yy - 170) ** 2) + 70, -2, 2) * (1 - S['O'][:, sl]) * (D < 0.3)
            img *= 1 - (sm * 0.75 * sun)[..., None] * (1 - np.array([0.30, 0.42, 0.86], np.float32))
        img = img * (1 - D[..., None]) + INK * D[..., None]
        n = H - WATER_Y
        wy = WATER_Y + int((1 - water) * (n - 6))         # water surface (sinks as the canal dries)
        if water < 1:
            img[WATER_Y:] = S['mud'][:n, sl]
        if water > 0:
            m = H - wy
            ys = np.arange(m, dtype=np.float32)[:, None]; xs = np.arange(cw, dtype=np.float32)[None, :]
            depth = ys / m
            dx = np.sin(ys * 0.35 + t * 2.4 + xs * 0.004) * (1.5 + 7 * depth) + np.sin(ys * 0.11 - t * 1.3) * 3 * depth
            sy = (wy - 1 - ys - np.sin(xs * 0.02 + ys * 0.2 + t * 1.7) * 1.5 * depth).astype(np.float32)
            refl = cv2.remap(img, (xs + dx).astype(np.float32), np.broadcast_to(sy, (m, cw)).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            so = x0 + int(t * 25); st = S['STREAK'][:m, so:so + cw]
            alpha = (0.62 * (1 - depth) ** 1.4 + 0.06) * (0.55 + 0.45 * smooth(st, 0.25, 0.75))
            wpaper = S['P'][wy:, sl]
            wimg = wpaper * (1 - alpha[..., None]) + (refl * 0.92 + wpaper * 0.08) * alpha[..., None]
            if water < 1:   # wet edge line on the mud
                wimg[:3] *= 0.8
            img[wy:] = wimg
        # boat (rides the water level, or lies tilted on the mud) and the post
        if water > 0.15:
            off = wy - WATER_Y
            Db = np.roll(S['Db'][:, sl], off, axis=0) if off else S['Db'][:, sl]
        else:
            Db = S['Dd'][:, sl]
        Dw = Db.copy(); over(Dw, S['Dp'][:, sl])
        img = img * S['wmul'][:, sl]
        img = img * (1 - Dw[..., None]) + INK * Dw[..., None]
        if col > 0:
            img *= 1 - col * (1 - S['cmul'][:, sl])
        crop = img[y0:y0 + int(math.ceil(OH / z)) + 2, :]
        return warp(crop, left, top, z, x0, y0)

TOWN = TownSet()

def town_live(ctx, rain_amt=1.0, drips_on=True, strands_on=True, ripples_on=True, jars_glow=True, water=1.0, color=0.0, night=0.0, cormorant=True, look=0.0):
    """the town's moving bits: willow strands, eave drips, rain rings, glowing jars, Old Ink on his post"""
    S = TOWN.S; t = ctx.Tabs
    if strands_on:
        strands(ctx, S['strands'])
        if color > 0: ctx.L.tints.append((np.clip(ctx.L.D * 2.0, 0, 1) * color * 0.8, (0.40, 0.85, 0.55)))
    if drips_on and rain_amt > 0.2:
        drips(ctx, [1060, 1100, 1180, 1260, 1330, 1390, 1470, 1520, 1600, 1700, 1800, 1930, 2010, 2120, 2250, 2330, 2400, 2520, 2600], 400, WATER_Y - 20)
    if ripples_on and rain_amt > 0.2 and water > 0.3:
        ripples(ctx, WATER_Y + int((1 - water) * 190), H, int(40 * rain_amt))
    if jars_glow:
        for j, (jx, jy, jw, jh) in enumerate(S['jars']):
            ctx.add_glow(jx, jy - jh * 0.45, jw * 0.45, (0.16 + 0.07 * math.sin(t * 1.3 + j)) * (1 + night * 1.5) * jars_glow, JAR_COLS[j % len(JAR_COLS)])
    if night > 0:
        for (wx, wy, ww, wh) in WIN_LIT:
            ctx.add_glow(wx, wy, min(ww, wh) * 0.35, 0.35 * night, WARM)
    if cormorant: ctx.cormorant(2092, WATER_Y - 62, 1.0, look)
    if rain_amt > 0: rain(ctx, rain_amt)

def strands(ctx, anchors):
    from engine import strands as _s
    _s(ctx, anchors)

from engine import rain, drips, ripples
