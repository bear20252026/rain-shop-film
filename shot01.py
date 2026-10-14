# Style test: Plum-rain dawn. Pan along the canal town, find Granny catching rain; a drop glows; she pours it into a jar; title.
import sys, os, math, subprocess, numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ink import *
from town import *
from chars import *
from PIL import Image, ImageDraw, ImageFont

FPS = 24; OW, OH = 1920, 804; DUR = 20.0
HERE = os.path.dirname(os.path.abspath(__file__))
GLOW = np.array([0.98, 0.95, 0.70], np.float32)     # BGR: pale jade-cyan light
GOLD = np.array([0.55, 0.85, 1.0], np.float32)
JAR_COLS = [np.array(c, np.float32) for c in [(0.80, 0.70, 1.0), (0.45, 0.80, 1.0), (1.0, 0.80, 0.55), (0.95, 0.65, 0.85), (0.70, 1.0, 0.75)]]

def static():
    f = os.path.join(HERE, 'static01.npz')
    if os.path.exists(f):
        z = np.load(f, allow_pickle=True); return {k: z[k] for k in z.files}
    C, jars, red, ey, tips = build_static()
    Fh = far_hills(2300)
    Wt = build_water_things()
    P = paper(H, WW, 2)
    # mid tints flattened into one multiply image
    mul = np.ones((H, WW, 3), np.float32)
    for a, c in C.tints: mul *= 1 - a[..., None] * (1 - np.asarray(c, np.float32))
    wmul = np.ones((H, WW, 3), np.float32)
    for a, c in Wt.tints: wmul *= 1 - a[..., None] * (1 - np.asarray(c, np.float32))
    d = dict(Dm=C.D, O=C.O, mul=mul, Dh=Fh.D, Dw=Wt.D, wmul=wmul, P=P, tips=np.array(tips, np.float32), jars=np.array(jars, np.float32))
    np.savez(f, **d); return d

S = static()
MIST = vnoise(H, WW + 800, 160, 77, 3)
STREAK = cv2.resize(vnoise(H - WATER_Y, (WW + 1200) // 10, 3, 91, 2), (WW + 1200, H - WATER_Y))
R = np.random.default_rng(5)

# willow strands: anchored along the branches, hanging down
STRANDS = []
for (tx, ty) in S['tips']:
    for k in range(9):
        u = k / 9; ax = 960 + (tx - 960) * (0.35 + 0.65 * u) + R.normal(0, 6); ay = 330 + (ty - 330) * (0.35 + 0.65 * u) + R.normal(0, 8)
        STRANDS.append((ax, ay, 110 + R.random() * 180, R.random() * 6.28, 0.6 + R.random() * 0.6))

# rain streaks (world coords, wrap around)
NR = 520
RAIN = np.column_stack([R.random(NR) * 2200, R.random(NR) * H, 14 + R.random(NR) * 22, 0.25 + R.random(NR) * 0.45])
# drips from the eaves
DRIP_X = [1060, 1100, 1180, 1260, 1330, 1390, 1470, 1520, 1600, 1700, 1800, 1930, 2010, 2120, 2250, 2330, 2400, 2520, 2600]

GX, GY, GS = 1500, WATER_Y - 18, 1.12       # Granny's feet, scale
JAR_X = 1418
POST = (2092, WATER_Y - 62)

def cam(t):
    u = ease(min(1, t / 13.0))
    cx = 40 + (1040 - 40) * u           # left edge of view at zoom 1
    z = 1 + 1.1 * ease((t - 12.0) / 6.5)
    # zoom target: Granny and the jar
    fx, fy = 1462, 500
    left = cx; top = 0.0
    # interpolate the window so that at full zoom it is centred on the target
    w = OW / z; hgt = OH / z
    k = ease((t - 12.0) / 6.5)
    left = lerp(cx, fx - w / 2, k); top = lerp(0, fy - hgt / 2, k)
    return left, top, z

def pose(t):
    # 0-10.5 catching; 10.5 the glowing drop; 12-14 lower to the jar; 14.4-17 pour; 17.5+ straighten
    a = ease((t - 12.0) / 2.2); b = ease((t - 17.6) / 1.6)
    hand = (lerp(-34, -26, a), lerp(-120, -96, a))
    hand = (lerp(hand[0], -30, b), lerp(hand[1], -108, b))
    ang = lerp(26, -6, a); ang = lerp(ang, 30, b)
    tilt = -55 * ease((t - 14.2) / 0.8) * (1 - ease((t - 16.8) / 0.7))
    lean = 0.35 + 0.35 * a - 0.3 * b
    return dict(hand=hand, lean=lean), ang, tilt

def render(t):
    left, top, z = cam(t)
    x0 = int(math.floor(left)) - 2; y0 = int(math.floor(top))
    cw = int(OW / z) + 6; ch = min(H - y0, int(OH / z) + 6)
    x0 = max(0, min(WW - cw, x0))
    sl = slice(x0, x0 + cw)
    # ---- background: hills (parallax) behind the town
    hx = int(x0 * 0.4) + 60
    Dh = S['Dh'][:, hx:hx + cw]
    D = Dh * (1 - S['O'][:, sl]); over(D, S['Dm'][:, sl])
    # drifting mist band: lightens the far hills and the back row
    mo = x0 + int(t * 14); m = MIST[:, mo:mo + cw]
    yy = np.arange(H, dtype=np.float32)[:, None]
    band = np.exp(-((yy - 360) / 90) ** 2) * 0.55 + np.exp(-((yy - 560) / 40) ** 2) * 0.25
    D *= 1 - band * smooth(m, 0.35, 0.75)
    img = S['P'][:, sl] * S['mul'][:, sl]
    img = img * (1 - D[..., None]) + INK * D[..., None]
    # ---- water: rippled reflection of everything above the waterline
    n = H - WATER_Y
    ys = np.arange(n, dtype=np.float32)[:, None]; xs = np.arange(cw, dtype=np.float32)[None, :]
    depth = ys / n
    dx = np.sin(ys * 0.35 + t * 2.4 + xs * 0.004) * (1.5 + 7 * depth) + np.sin(ys * 0.11 - t * 1.3) * 3 * depth
    sy = (WATER_Y - 1 - ys - np.sin(xs * 0.02 + ys * 0.2 + t * 1.7) * 1.5 * depth).astype(np.float32)
    mapx = (xs + dx).astype(np.float32); mapy = np.broadcast_to(sy, (n, cw)).astype(np.float32)
    refl = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # broken horizontal streaks
    so = x0 + int(t * 25); st = STREAK[:n, so:so + cw]
    alpha = (0.62 * (1 - depth) ** 1.4 + 0.06) * (0.55 + 0.45 * smooth(st, 0.25, 0.75))
    wpaper = S['P'][WATER_Y:, sl]
    img[WATER_Y:] = wpaper * (1 - alpha[..., None]) + (refl * 0.92 + wpaper * 0.08) * alpha[..., None]
    # things in the water (boat, post)
    Dw = S['Dw'][:, sl]
    img = img * S['wmul'][:, sl]
    img = img * (1 - Dw[..., None]) + INK * Dw[..., None]
    # ---- warp the painted world to the screen
    crop = img[y0:y0 + int(math.ceil(OH / z)) + 2, :]
    M = np.float32([[z, 0, -(left - x0) * z], [0, z, -(top - y0) * z]])
    img = cv2.warpAffine(crop, M, (OW, OH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    T = lambda x, y: ((x - left) * z, (y - top) * z)
    # ---- live layer in screen space (stays crisp when the camera pushes in)
    L = Layer(0, 0, OW, OH)
    for (ax, ay, ln, ph, sp) in STRANDS:
        sx0, _ = T(ax, ay)
        if sx0 < -400 or sx0 > OW + 400: continue
        k = np.linspace(0, 1, 16)
        sway = (math.sin(t * sp * 1.4 + ph) * 10 + math.sin(t * 0.5 + ph) * 6) * k ** 1.6
        pts = np.array([T(x, y) for x, y in zip(ax + sway + k * 6, ay + k * ln)])
        cv2.polylines(L.D, [np.round(pts * 4).astype(np.int32)], False, 0.45, max(1, int(z * 0.9)), cv2.LINE_AA, 2)
        for i in range(3, 16, 2):
            px, py = pts[i]; cv2.line(L.D, (int(px * 4), int(py * 4)), (int((px + (4 + (i % 3)) * z) * 4), int((py + 7 * z) * 4)), 0.35, max(1, int(z * 1.4)), cv2.LINE_AA, 2)
    for i, dxp in enumerate(DRIP_X):
        per = 0.9 + (i * 0.37) % 0.8; ph = (t + i * 0.53) % per / per
        ey = 400 + (i % 3) * 8; yd = ey + ph ** 2 * (WATER_Y - 20 - ey)
        p0 = T(dxp, yd); p1 = T(dxp, yd + 6)
        if -10 < p0[0] < OW + 10:
            cv2.line(L.D, (int(p0[0] * 4), int(p0[1] * 4)), (int(p1[0] * 4), int(p1[1] * 4)), 0.5, max(1, int(1.6 * z)), cv2.LINE_AA, 2)
    rr = np.random.default_rng(int(t * 6))
    for k in range(40):
        rx = left + rr.random() * OW / z; ry = WATER_Y + 8 + rr.random() ** 1.5 * (H - WATER_Y - 10); age = (rr.random() + t * 1.7) % 1
        rad = (3 + age * 14 * (0.6 + (ry - WATER_Y) / 200)) * z
        c = T(rx, ry)
        cv2.ellipse(L.D, (int(c[0] * 4), int(c[1] * 4)), (int(rad * 4), int(rad * 1.1)), 0, 0, 360, 0.3 * (1 - age), 1, cv2.LINE_AA, 2)
    ps, ang, tilt = pose(t)
    look = 1.0 if 10.9 < t < 13.5 else 0.0
    cormorant(L, *T(*POST), t, z, 51, look)
    jtop = jar(L, *T(JAR_X, GY), 0.95 * z)
    hand = granny(L, *T(GX, GY), t, ps, GS * z)
    cup, rim = ladle(L, hand, ang, tilt, GS * z)
    glow = []
    # weathers glowing softly inside the jars on the shelves
    for j, (jx, jy, jw, jh) in enumerate(S['jars']):
        c = T(jx, jy - jh * 0.45)
        if -50 < c[0] < OW + 50:
            col = JAR_COLS[j % len(JAR_COLS)]
            glow.append((c[0], c[1], jw * 0.45 * z, 0.16 + 0.07 * math.sin(t * 1.3 + j), col))
    if 9.6 < t < 10.5:
        u = (t - 9.6) / 0.9; ys0 = T(0, 402)[1]; yd = ys0 + u ** 2 * (cup[1] - ys0)
        glow.append((cup[0], yd, (4 + 3 * u) * z, 0.9, GLOW))
    fill_l = ease((t - 10.5) / 0.6) * (1 - ease((t - 15.0) / 1.6))
    if fill_l > 0: glow.append((cup[0], cup[1] - 3 * z, 13 * z * fill_l, fill_l, GLOW))
    pour = ease((t - 14.5) / 0.4) * (1 - ease((t - 16.6) / 0.4))
    lip = rim[0] if rim[0][1] > rim[1][1] else rim[1]
    if pour > 0:
        for k in np.linspace(0, 1, 24):
            px = lerp(lip[0], jtop[0], k) + math.sin(k * 3 + t * 9) * 1.2 * z; py = lerp(lip[1], jtop[1], k ** 0.8)
            glow.append((px, py, 2.2 * z, 0.6 * pour, GLOW))
    jglow = ease((t - 15.2) / 1.6)
    if jglow > 0: glow.append((jtop[0], jtop[1] + 22 * z, 24 * z * jglow, 0.5 * jglow, GLOW))
    for k in range(14):
        st0 = 16.0 + k * 0.28
        if t > st0:
            u = (t - st0) / 3.0
            if u < 1: glow.append((jtop[0] + math.sin(k * 2.3 + u * 4) * 12 * z, jtop[1] - u * 80 * z, 1.8 * z, (1 - u) * 0.9, GOLD if k % 3 == 0 else GLOW))
    # fine rain, screen space
    for (rx, ry, rl, rd) in RAIN:
        x = (rx * 0.9 - t * 60) % (OW + 100) - 50; y = (ry + t * 1100) % (OH + 80) - 40
        cv2.line(L.D, (int(x * 4), int(y * 4)), (int((x - rl * 0.2) * 4), int((y - rl) * 4)), rd * 0.32, 1, cv2.LINE_AA, 2)
    for a, c in L.tints: img *= 1 - a[..., None] * (1 - np.asarray(c, np.float32))
    img = img * (1 - L.D[..., None]) + INK * L.D[..., None]
    if glow:
        acc = np.zeros((OH, OW, 3), np.float32)
        for (gx, gy, r, a, col) in glow:
            g = np.zeros((OH, OW), np.float32)
            x0g, y0g = int(gx - r * 8 - 60), int(gy - r * 8 - 60); x1g, y1g = int(gx + r * 8 + 60), int(gy + r * 8 + 60)
            x0g, y0g = max(0, x0g), max(0, y0g); x1g, y1g = min(OW, x1g), min(OH, y1g)
            if x1g <= x0g or y1g <= y0g: continue
            sub = np.zeros((y1g - y0g, x1g - x0g), np.float32)
            cv2.circle(sub, (int((gx - x0g) * 4), int((gy - y0g) * 4)), max(1, int(r * 4)), float(a), -1, cv2.LINE_AA, 2)
            gl = cv2.GaussianBlur(sub, (0, 0), max(1, r * 0.3)) * 0.9 + cv2.GaussianBlur(sub, (0, 0), max(2, r * 1.2)) * 1.3 + cv2.GaussianBlur(sub, (0, 0), max(4, r * 3)) * 1.0
            acc[y0g:y1g, x0g:x1g] += gl[..., None] * np.asarray(col, np.float32)
        img = img + acc * 0.75
    return np.clip(img, 0, 1)

# ---- title card overlay at the end
def title_layer():
    img = Image.new('L', (OW, OH), 0); d = ImageDraw.Draw(img)
    f = ImageFont.truetype(CJK, 120); f2 = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf', 34)
    d.text((300, 190), '雨', font=f, fill=255, anchor='mm'); d.text((300, 320), '铺', font=f, fill=255, anchor='mm')
    t = np.asarray(img, np.float32) / 255
    t = cv2.dilate(t, np.ones((5, 5), np.uint8)); t = cv2.GaussianBlur(t, (0, 0), 1.6)
    t = smooth(t + (vnoise(OH, OW, 4, 9, 2) - 0.5) * 0.55, 0.3, 0.6)
    e = Image.new('L', (OW, OH), 0); ImageDraw.Draw(e).text((300, 420), 'The Rain Shop', font=f2, fill=255, anchor='mm')
    e = cv2.GaussianBlur(np.asarray(e, np.float32) / 255, (0, 0), 0.6)
    seal = np.zeros((OH, OW), np.float32); cv2.rectangle(seal, (372, 360), (408, 396), 1.0, -1)
    seal = wash(seal, 0.9, bleed=1.0, seed=3, gran=0.8, rough=0.3)
    sc = Image.new('L', (OW, OH), 0); ImageDraw.Draw(sc).text((390, 378), '雨', font=ImageFont.truetype(CJK, 26), fill=255, anchor='mm')
    seal *= 1 - np.asarray(sc, np.float32) / 255
    return t, e, seal
TITLE = title_layer()
_b = np.zeros((OH, OW), np.float32); cv2.ellipse(_b, (310, 300), (190, 230), 0, 0, 360, 1.0, -1)
BACK = smooth(cv2.GaussianBlur(_b, (0, 0), 50) + (vnoise(OH, OW, 30, 4, 3) - 0.5) * 0.3, 0.2, 0.8) * 0.93

def frame(t, vig):
    f = render(t) * vig
    a = ease((t - 17.3) / 1.2)
    if a > 0:
        tt, e, seal = TITLE
        f = f * (1 - BACK[..., None] * a) + PAPER * BACK[..., None] * a
        f = f * (1 - tt[..., None] * a * 0.92) + INK * tt[..., None] * a * 0.92
        f = f * (1 - e[..., None] * a * 0.8) + INK * e[..., None] * a * 0.8
        sa = ease((t - 18.2) / 0.4)
        f = f * (1 - seal[..., None] * sa * (1 - np.array(VERMILION, np.float32)))
    fi = ease(t / 1.2); fo = ease((DUR - t) / 0.6)
    f = PAPER * (1 - fi) + f * fi
    return np.clip(f * fo, 0, 1)

if __name__ == '__main__':
    # usage: shot01.py FRAMEDIR worker nworkers  (resumable: skips frames already written)
    outdir = sys.argv[1]; wk = int(sys.argv[2]); nw = int(sys.argv[3]); os.makedirs(outdir, exist_ok=True)
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    vig = (1 - 0.22 * (((xx - OW / 2) / (OW * 0.6)) ** 2 + ((yy - OH / 2) / (OH * 0.7)) ** 2)).clip(0.6, 1)[..., None]
    for i in range(wk, int(DUR * FPS), nw):
        fn = os.path.join(outdir, f'{i:05d}.png')
        if os.path.exists(fn): continue
        f = frame(i / FPS, vig)
        cv2.imwrite(fn + '.tmp.png', (f * 255 + 0.5).astype(np.uint8)); os.replace(fn + '.tmp.png', fn)
        print(i, flush=True)
