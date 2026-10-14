# Scene-writing kit: walking, props held in hands, labels, weather colors, chapter cards.
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
from ink import *
from chars import fill, line, path, ladle as _ladle, jar as _jar
from engine import *
from town import VERMILION, CELADON

W_DRIZZLE = np.array([0.92, 0.90, 0.85], np.float32)
W_SNOW = np.array([1.0, 0.98, 0.95], np.float32)
W_SUN = np.array([0.40, 0.80, 1.0], np.float32)
W_FOG = np.array([0.92, 0.62, 0.80], np.float32)
W_BREEZE = np.array([0.80, 0.62, 1.0], np.float32)
W_THUNDER = np.array([0.55, 0.92, 0.55], np.float32)
W_DRAGON = np.array([1.0, 0.78, 0.45], np.float32)
W_WARM = np.array([0.55, 0.78, 1.0], np.float32)
OILPAPER = [(0.30, 0.38, 0.85), (0.40, 0.70, 0.85), (0.70, 0.55, 0.40), (0.55, 0.75, 0.62)]

def walk_x(keys, t, stride=46.0, s=1.0):
    """keys [(t, x), ...] piecewise linear. returns x, walk phase (None when standing), facing (+1 right / -1 left)"""
    if t <= keys[0][0]: return keys[0][1], None, 1
    for (t0, x0), (t1, x1) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / max(1e-6, t1 - t0); x = x0 + (x1 - x0) * u
            if abs(x1 - x0) < 1: return x, None, 1
            return x, abs(x) / (stride * s), (1 if x1 > x0 else -1)
    return keys[-1][1], None, 1

def walk_xy(keys, t, stride=46.0, s=1.0):
    """keys [(t, (x, y)), ...]"""
    if t <= keys[0][0]: return keys[0][1][0], keys[0][1][1], None, 1
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if t <= t1:
            u = (t - t0) / max(1e-6, t1 - t0); x = p0[0] + (p1[0] - p0[0]) * u; y = p0[1] + (p1[1] - p0[1]) * u
            dist = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            if dist < 1: return x, y, None, 1
            return x, y, (u * dist + t0 * 7) / (stride * s), (1 if p1[0] >= p0[0] else -1)
    return keys[-1][1][0], keys[-1][1][1], None, 1

def arm(keys, t):
    """keyframed arm (shoulder, elbow)"""
    return kf(keys, t)

def blink_pose(**kw): return kw

# ------------------------------------------------------------------ props (screen space, attached to returned hands)
def _L(ctx, x, y, r, over=False):
    return ctx.layer(x - r, y - r, x + r, y + r, over=over)

def umbrella(ctx, hand, se, col=0, tilt=0.0, open_=1.0, over=False):
    """oil-paper umbrella held at hand (screen coords). tilt in degrees."""
    hx, hy = hand; L = _L(ctx, hx, hy - 60 * se, 140 * se, over)
    a = math.radians(tilt); up = np.array([math.sin(a), -math.cos(a)]); rt = np.array([math.cos(a), math.sin(a)])
    top = np.array([hx, hy]) + up * 92 * se
    line(L, [(hx, hy + 8 * se), tuple(top + up * 8 * se)], 2.0, se, 0.9, 0.2, 401, taper=False)
    w = 78 * se * (0.25 + 0.75 * open_); dh = 30 * se * (0.4 + 0.6 * open_)
    rim = [tuple(top + rt * w * math.cos(q) - up * (dh * (1 - math.sin(q)) * 1.0) + up * 0) for q in np.linspace(0, math.pi, 22)]
    dome = [tuple(top + rt * w * math.cos(q) + up * dh * math.sin(q) * 0.35 - up * dh * (1 - math.sin(q))) for q in np.linspace(math.pi, 0, 22)]
    poly = np.array(rim + dome, np.float32)
    canopy = [tuple(top + rt * w * math.cos(q) - up * dh * (1 - math.sin(q)) ) for q in np.linspace(0, math.pi, 22)]
    poly = np.array(canopy + [tuple(top + up * 2 * se)], np.float32)
    fill(L, poly, 0.10, OILPAPER[col % 4], 0.85, s=se, seed=402, edge=0.6)
    line(L, poly[:22], 2.0, se, 0.9, 0.3, 403, taper=False)
    for k in range(1, 8):    # ribs
        q = math.pi * k / 8; p = top + rt * w * math.cos(q) - up * dh * (1 - math.sin(q))
        line(L, [tuple(top), tuple(p)], 0.9, se, 0.5, 0, 404 + k, taper=False)
    return tuple(top)

def cup(ctx, hand, se, over=False):
    hx, hy = hand; L = _L(ctx, hx, hy, 30 * se, over)
    poly = [(hx - 10 * se, hy - 12 * se), (hx + 10 * se, hy - 12 * se), (hx + 7 * se, hy + 2 * se), (hx - 7 * se, hy + 2 * se)]
    fill(L, poly, 0.04, (0.92, 0.92, 0.88), 0.7, s=se, seed=411)
    line(L, poly + [poly[0]], 1.3, se, 0.85, 0, 412, taper=False)
    line(L, [(hx - 6 * se, hy - 5 * se), (hx + 6 * se, hy - 5 * se)], 1.0, se, 0.4, 0, 413, taper=False)
    return (hx, hy - 12 * se)

def small_jar(ctx, hand, se, glow_col=None, glow=0.0, over=False, s=0.55):
    hx, hy = hand; L = _L(ctx, hx, hy, 60 * se, over)
    top = _jar(L, hx, hy + 6 * se, s * se, 433)
    if glow_col is not None and glow > 0: ctx.add_glow(hx, hy - 10 * se, 12 * se, glow, glow_col, world=False)
    return top

def big_jar(ctx, x, by, s=1.0, glow_col=None, glow=0.0, label=None, seed=41, over=False):
    """a jar in world coords with an optional paper label (brush text)"""
    sx, sy = ctx.T(x, by); se = s * ctx.z
    L = ctx.layer(sx - 45 * se, sy - 90 * se, sx + 45 * se, sy + 10 * se, over=over)
    top = _jar(L, sx, sy, se, seed)
    if label:
        lw, lh = 13 * se, (8 + 9 * len(label)) * se; ly = sy - 21 * se
        poly = [(sx - lw / 2, ly - lh / 2), (sx + lw / 2, ly - lh / 2), (sx + lw / 2, ly + lh / 2), (sx - lw / 2, ly + lh / 2)]
        m = poly_mask(L.D.shape, [L.P(poly)]); L.knock(m); L.tints.append((m * 0.5, (0.62, 0.78, 0.88)))
        brush_text(L, label, sx, ly - lh / 2 + 6 * se, 9 * se, vertical=True)
    if glow_col is not None and glow > 0: ctx.add_glow(sx, sy - 22 * se, 16 * se, glow, glow_col, world=False)
    return top

_tf = {}
def brush_text(L, s, x, y, size, vertical=False, d=0.92, reveal=1.0, anchor='mm'):
    """draw brush-font text into a layer at screen coords (x, y = first character centre)"""
    size = max(6, int(size))
    key = (s, size, vertical)
    if key not in _tf:
        f = ImageFont.truetype(BRUSH, size); n = len(s)
        w = int(size * 1.3) if vertical else int(size * 1.1 * n + size)
        h = int(size * 1.1 * n + size) if vertical else int(size * 1.4)
        im = Image.new('L', (w, h), 0); dr = ImageDraw.Draw(im)
        if vertical:
            for i, ch in enumerate(s): dr.text((w / 2, size * 0.6 + i * size * 1.08), ch, font=f, fill=255, anchor='mm')
        else: dr.text((size * 0.5, h / 2), s, font=f, fill=255, anchor='lm')
        a = cv2.GaussianBlur(np.asarray(im, np.float32) / 255, (0, 0), 0.5)
        if len(_tf) > 100: _tf.clear()
        _tf[key] = a
    a = _tf[key].copy()
    h, w = a.shape
    if reveal < 1:
        if vertical: a[int(h * reveal):] = 0
        else: a[:, int(w * reveal):] = 0
    ox = int(x - (w / 2 if vertical else (w / 2 if anchor == 'mm' else size * 0.5))) - L.x0
    oy = int(y - size * 0.6) - L.y0 if vertical else int(y - h / 2) - L.y0
    H_, W_ = L.D.shape
    x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(W_, ox + w), min(H_, oy + h)
    if x1 > x0 and y1 > y0:
        over(L.D[y0:y1, x0:x1], a[y0 - oy:y1 - oy, x0 - ox:x1 - ox] * d)

def ladle(ctx, hand, ang, tilt, se, over=False):
    hx, hy = hand; L = _L(ctx, hx, hy, 140 * se, over)
    return _ladle(L, hand, ang, tilt, se)

def stick(ctx, hand, ang, length, se, w=2.4, over=False, seed=451):
    """a straight pole (broom handle, net pole, lantern stick). ang: degrees from straight up, + leans right"""
    hx, hy = hand; a = math.radians(ang)
    tip = (hx + math.sin(a) * length * se, hy - math.cos(a) * length * se)
    back = (hx - math.sin(a) * 20 * se, hy + math.cos(a) * 20 * se)
    L = ctx.layer(min(tip[0], back[0]) - 30 * se, min(tip[1], back[1]) - 30 * se, max(tip[0], back[0]) + 30 * se, max(tip[1], back[1]) + 30 * se, over=over)
    line(L, [back, tip], w, se, 0.85, 0.3, seed, taper=False)
    return tip, L

def broom(ctx, hand, ang, se, over=False):
    """bamboo broom, held with the head down. ang: degrees from straight down"""
    hx, hy = hand; a = math.radians(ang)
    d = np.array([math.sin(a), math.cos(a)])
    top = np.array([hx, hy]) - d * 40 * se; head = np.array([hx, hy]) + d * 80 * se
    L = ctx.layer(min(top[0], head[0]) - 50 * se, min(top[1], head[1]) - 50 * se, max(top[0], head[0]) + 50 * se, max(top[1], head[1]) + 60 * se, over=over)
    line(L, [tuple(top), tuple(head)], 2.6, se, 0.85, 0.3, 461, taper=False)
    n = np.array([d[1], -d[0]])
    for k in range(-5, 6):
        e = head + d * 40 * se + n * k * 4.5 * se
        line(L, [tuple(head + n * k * 1.2 * se), tuple(e)], 1.1, se, 0.7, 0.4, 470 + k)
    line(L, [tuple(head - n * 8 * se + d * 6 * se), tuple(head + n * 8 * se + d * 6 * se)], 2, se, 0.85, 0, 482, taper=False)
    return tuple(head + d * 40 * se)

def fan(ctx, hand, ang, se, open_=1.0, over=False):
    """folding fan: ang = direction it points (degrees from up)"""
    hx, hy = hand; L = _L(ctx, hx, hy, 70 * se, over)
    a0 = math.radians(ang) - 1.1 * open_; a1 = math.radians(ang) + 1.1 * open_
    R = 46 * se; r0 = 10 * se
    outer = [(hx + R * math.sin(q), hy - R * math.cos(q)) for q in np.linspace(a0, a1, 18)]
    inner = [(hx + r0 * math.sin(q), hy - r0 * math.cos(q)) for q in np.linspace(a1, a0, 8)]
    fill(L, outer + inner, 0.05, (0.75, 0.86, 0.92), 0.6, s=se, seed=491, edge=0.6)
    for q in np.linspace(a0, a1, 9): line(L, [(hx, hy), (hx + R * math.sin(q), hy - R * math.cos(q))], 0.9, se, 0.6, 0, 492, taper=False)
    line(L, outer, 1.4, se, 0.85, 0, 493, taper=False)

def lantern(ctx, hand, se, glow=1.0, t=0.0, over=False):
    """paper lantern hanging below the hand on a short stick"""
    hx, hy = hand; sw = math.sin(t * 2.0) * 3 * se
    L = _L(ctx, hx, hy + 40 * se, 60 * se, over)
    cx, cy = hx + sw, hy + 42 * se
    line(L, [(hx, hy), (cx, cy - 18 * se)], 1.0, se, 0.8, 0, 501, taper=False)
    body = [(cx + 14 * se * math.cos(q), cy + 18 * se * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 24)]
    fill(L, body, 0.03, (0.55, 0.75, 1.0), 0.8, s=se, seed=502, edge=0.4)
    line(L, body, 1.2, se, 0.8, 0, 503, taper=False)
    for k in (-1, 1): line(L, [(cx - 13 * se, cy + k * 8 * se), (cx + 13 * se, cy + k * 8 * se)], 0.8, se, 0.5, 0, 504 + k, taper=False)
    fill(L, [(cx - 7 * se, cy - 18 * se), (cx + 7 * se, cy - 18 * se), (cx + 7 * se, cy - 22 * se), (cx - 7 * se, cy - 22 * se)], 0.8, s=se, seed=506)
    if glow > 0:
        fl = 0.9 + 0.1 * math.sin(t * 12) * math.sin(t * 5.7)
        ctx.add_glow(cx, cy, 10 * se, 0.8 * glow * fl, W_WARM, world=False)
        ctx.add_glow(cx, cy, 70 * se, 0.12 * glow, W_WARM, world=False)
    return (cx, cy)

def net(ctx, hand, ang, se, length=110, over=False):
    """silk catching net on a bamboo pole"""
    tip, L = stick(ctx, hand, ang, length, se, 2.2, over, 511)
    a = math.radians(ang); d = np.array([math.sin(a), -math.cos(a)]); n = np.array([math.cos(a), math.sin(a)])
    c = np.array(tip) + d * 18 * se
    ring = [tuple(c + d * 18 * se * math.cos(q) + n * 22 * se * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 24)]
    L2 = _L(ctx, c[0], c[1], 70 * se, over)
    fill(L2, ring, 0.02, (0.95, 0.95, 0.92), 0.4, s=se, seed=512)
    line(L2, ring, 1.4, se, 0.85, 0, 513, taper=False)
    bag = [tuple(c + n * 22 * se), tuple(c + n * 10 * se + np.array([0, 34 * se])), tuple(c - n * 22 * se)]
    line(L2, bag, 0.9, se, 0.4, 0, 514)
    return tuple(c)

def notebook(ctx, x, y, se, open_=1.0, over=False):
    L = _L(ctx, x, y, 40 * se, over)
    w, h = 30 * se, 22 * se
    for k in (-1, 1):
        poly = [(x, y), (x + k * w * open_, y - 2 * se), (x + k * w * open_, y + h), (x, y + h + 2 * se)]
        fill(L, poly, 0.02, (0.92, 0.94, 0.95), 0.4, s=se, seed=520 + k)
        line(L, poly + [poly[0]], 1.1, se, 0.8, 0, 522 + k, taper=False)
    return L

def paper_slip(ctx, x, y, se, text, reveal=1.0, over=False, vertical=True):
    """a paper label being written: brush text revealed stroke by stroke"""
    n = len(text); w, h = (34 * se, (24 + 30 * n) * se) if vertical else ((24 + 30 * n) * se, 40 * se)
    L = ctx.layer(x - w / 2 - 10, y - 10, x + w / 2 + 10, y + h + 10, over=over)
    poly = [(x - w / 2, y), (x + w / 2, y), (x + w / 2, y + h), (x - w / 2, y + h)]
    fill(L, poly, 0.02, (0.70, 0.85, 0.92), 0.5, s=se, seed=531, edge=0.3)
    if vertical: brush_text(L, text, x, y + 22 * se, 26 * se, True, reveal=reveal)
    else: brush_text(L, text, x, y + h / 2, 26 * se, False, reveal=reveal)
    return L

def drop_glow(ctx, x0, y0, x1, y1, u, col=GLOW, r=4.0, world=True):
    """a single glowing drop falling from (x0,y0) to (x1,y1), u in 0..1 (accelerating)"""
    if 0 <= u <= 1:
        x = lerp(x0, x1, u); y = y0 + (y1 - y0) * u * u
        ctx.add_glow(x, y, r * (1 + 0.5 * u), 0.9, col, world)

def stream(ctx, a, b, amt, col, n=22, r=2.2, t=0.0, wob=1.2, world=False):
    """a glowing pour from a to b (screen coords by default)"""
    if amt <= 0: return
    for k in np.linspace(0, 1, n):
        px = lerp(a[0], b[0], k) + math.sin(k * 3 + t * 9) * wob; py = lerp(a[1], b[1], k ** 0.8)
        ctx.add_glow(px, py, r, 0.6 * amt, col, world)

def wisp(ctx, pts, amt, col, r=6.0, world=True, t=0.0):
    """a ribbon of colored weather along a path of points"""
    for i, (x, y) in enumerate(pts):
        ctx.add_glow(x, y, r * (0.6 + 0.4 * math.sin(i * 0.7 + t * 3)), amt * (0.35 + 0.25 * math.sin(i * 0.9 - t * 4)), col, world)

# ------------------------------------------------------------------ cards
_cards = {}
def card(lines, fz=72, fe=36):
    key = (tuple(lines), fz, fe)
    if key not in _cards:
        t = card_img(lines, (OW, OH), fz, fe)
        t = cv2.GaussianBlur(t, (0, 0), 0.8)
        t = smooth(t + (vnoise(OH, OW, 3, 9, 2) - 0.5) * 0.35, 0.3, 0.6)
        _cards[key] = t
    return _cards[key]

def ink_over(img, a, k=0.92):
    return img * (1 - a[..., None] * k) + INK * a[..., None] * k

_seal = None
_seals = {}
def seal_mask(x, y, size=40, ch='雨'):
    k = (x, y, size, ch)
    if k not in _seals: _seals[k] = _seal_mask(x, y, size, ch)
    return _seals[k]
def _seal_mask(x, y, size=40, ch='雨'):
    m = np.zeros((OH, OW), np.float32); h = size / 2
    cv2.rectangle(m, (int(x - h), int(y - h)), (int(x + h), int(y + h)), 1.0, -1)
    m = wash(m, 0.9, bleed=1.0, seed=3, gran=0.8, rough=0.3)
    im = Image.new('L', (OW, OH), 0); ImageDraw.Draw(im).text((x, y), ch, font=ImageFont.truetype(BRUSH, int(size * 0.75)), fill=255, anchor='mm')
    return m * (1 - np.asarray(im, np.float32) / 255)

def chapter_post(lines, t_in, t_out, fz=64, fe=32):
    """a post function that writes a centred card over the picture between t_in and t_out (shot-local)"""
    def post(img, lt, ctx):
        a = min(ease((lt - t_in) / 0.8), ease((t_out - lt) / 0.8))
        if a <= 0: return img
        return ink_over(img, card(lines, fz, fe) * a)
    return post

def ink_reveal(img, u, seed=12):
    """the picture appears as if ink is soaking into paper (u: 0 blank paper .. 1 full)"""
    if u >= 1: return img
    n = vnoise(OH, OW, 120, seed, 4)
    m = smooth(n - (1 - u * 1.3) + 0.15, 0, 0.15)[..., None]
    return screen_paper() * (1 - m) + img * m

def sampan(ctx, x, wy, s=1.0, awning=True, seed=601, ov=False):
    """a small black-awning boat on the water at world (x, wy). returns the world point of the stern deck"""
    t = ctx.Tabs; bob = math.sin(t * 1.6 + seed) * 1.5
    se = s * ctx.z; cx, cy = ctx.T(x, wy + bob)
    L = ctx.layer(cx - 200 * se, cy - 90 * se, cx + 200 * se, cy + 60 * se, over=ov)
    top = bezier((cx - 160 * se, cy - 26 * se), (cx, cy - 6 * se), (cx + 160 * se, cy - 30 * se), n=30)
    bot = bezier((cx + 160 * se, cy - 30 * se), (cx + 20 * se, cy + 22 * se), (cx - 160 * se, cy - 26 * se), n=30)
    hull = np.vstack([top, bot])
    fill(L, hull, 0.5, s=se, seed=seed, gran=0.6)
    line(L, bot, 4.0, se, 0.9, 0.4, seed + 1, taper=False)
    if awning:
        aw = [(cx - 30 * se + 58 * se * math.cos(a), cy - 14 * se - 40 * se * math.sin(a)) for a in np.linspace(math.pi, 0, 26)]
        fill(L, aw, 0.88, s=se, seed=seed + 2, gran=0.5)
        for k in range(4): line(L, [(cx - 80 * se + 32 * k * se, cy - 16 * se), (cx - 80 * se + 32 * k * se + 2 * se, cy - 46 * se + abs(1.5 - k) * 7 * se)], 1.2, se, 0.3, 0, seed + 3 + k)
    # a dim reflection smear under the hull
    R = ctx.layer(cx - 170 * se, cy + 4 * se, cx + 170 * se, cy + 40 * se, over=ov)
    rm = poly_mask(R.D.shape, [R.P([(cx - 150 * se, cy + 6 * se), (cx + 150 * se, cy + 6 * se), (cx + 110 * se, cy + 30 * se), (cx - 110 * se, cy + 30 * se)])])
    over(R.D, wash(rm, 0.18, bleed=3 * se, seed=seed + 9, rough=0.6))
    return (x + 110 * s, wy + bob - 18 * s)

def pole(ctx, hand, ang, se, length=230, over=False):
    """the ferryman's long punting pole, pushed down into the water"""
    hx, hy = hand; a = math.radians(ang)
    tip = (hx + math.sin(a) * length * se, hy + math.cos(a) * length * se)
    top = (hx - math.sin(a) * 60 * se, hy - math.cos(a) * 60 * se)
    L = ctx.layer(min(tip[0], top[0]) - 20, min(tip[1], top[1]) - 20, max(tip[0], top[0]) + 20, max(tip[1], top[1]) + 20, over=over)
    line(L, [top, tip], 2.6, se, 0.85, 0.3, 611, taper=False)

def brush(ctx, tip, se, ang=25, ink=True):
    """a writing brush: bamboo handle, dark wet tuft at the tip (screen coords). ang: degrees from straight up"""
    a = math.radians(ang); d = np.array([math.sin(a), -math.cos(a)])
    tip = np.array(tip, np.float32); ferrule = tip + d * 26 * se; end = tip + d * 150 * se
    L = ctx.layer(min(tip[0], end[0]) - 20 * se, min(tip[1], end[1]) - 20 * se, max(tip[0], end[0]) + 20 * se, max(tip[1], end[1]) + 20 * se)
    n = np.array([-d[1], d[0]])
    tuft = [tuple(tip), tuple(ferrule + n * 6 * se), tuple(ferrule - n * 6 * se)]
    fill(L, tuft, 0.92 if ink else 0.3, s=se, seed=541)
    hp_ = [tuple(ferrule + n * 4 * se), tuple(end + n * 3.5 * se), tuple(end - n * 3.5 * se), tuple(ferrule - n * 4 * se)]
    fill(L, hp_, 0.08, (0.55, 0.78, 0.85), 0.8, s=se, seed=542)
    line(L, [hp_[0], hp_[1]], 1.2, se, 0.85, 0, 543, taper=False); line(L, [hp_[3], hp_[2]], 1.2, se, 0.85, 0, 544, taper=False)
    for k in (0.3, 0.65): p = ferrule + d * (end - ferrule).dot(d) * k; line(L, [tuple(p + n * 4 * se), tuple(p - n * 4 * se)], 1.0, se, 0.7, 0, 545, taper=False)

TWIN_B = dict(top=(0.06, (0.70, 0.85, 0.62), 0.7))      # the second twin wears green

def breeze_path(t, cx, cy, w=300, h=120, n=40, seed=0, phase=0.0):
    """points of a looping, travelling ribbon of wind around (cx, cy) in world coords"""
    s = np.linspace(0, 1, n)
    a = s * 4 * math.pi + t * 2.3 + phase
    x = cx + np.cos(a) * w * (0.4 + 0.6 * s) + np.sin(t * 0.7 + seed) * 40
    y = cy + np.sin(a * 0.5 + t) * h * (0.5 + 0.5 * s) - s * 30
    return np.stack([x, y], 1)

def breeze(ctx, pts, amt=1.0, col=None, world=True):
    """the giggling breeze: pink light along a ribbon plus curling ink wind-lines"""
    col = W_BREEZE if col is None else col
    P = ctx.Tp(pts) if world else np.asarray(pts, np.float32)
    t = ctx.Tabs; z = ctx.z if world else 1.0
    for i in range(0, len(P), 2):
        ctx.add_glow(P[i][0], P[i][1], 7 * z * (0.6 + 0.4 * math.sin(i * 0.6 + t * 5)), amt * 0.35, col, world=False)
    xs, ys = P[:, 0], P[:, 1]
    L = ctx.layer(xs.min() - 30, ys.min() - 30, xs.max() + 30, ys.max() + 30, front=True)
    for k in range(3):
        off = np.array([math.sin(t * 2 + k * 2), math.cos(t * 1.7 + k)]) * 8 * z * (k + 1)
        seg = P[k * 4: len(P) - k * 3] + off
        if len(seg) > 4: line(L, seg, np.linspace(0.4, 1.8, len(seg)) * amt, max(0.6, z), 0.45, 0.4, 700 + k)
    # little curls at the head of the ribbon
    hx, hy = P[-1]
    curl = [(hx + 14 * z * math.cos(q) * (1 - q / 12), hy + 14 * z * math.sin(q) * (1 - q / 12)) for q in np.linspace(0, 10, 24)]
    line(L, curl, 1.4 * amt, max(0.6, z), 0.5, 0, 710)

def flying_sheet(ctx, x, y, ang, se, col=(0.92, 0.94, 0.95), front=True):
    """a sheet of paper tumbling in the wind (screen coords)"""
    L = ctx.layer(x - 40 * se, y - 40 * se, x + 40 * se, y + 40 * se, front=front)
    c, s_ = math.cos(ang), math.sin(ang)
    w, h = 18 * se, 24 * se * (0.4 + 0.6 * abs(math.cos(ang * 1.7)))
    pts = [(x + c * dx - s_ * dy, y + s_ * dx + c * dy) for dx, dy in ((-w, -h), (w, -h), (w, h), (-w, h))]
    fill(L, pts, 0.02, col, 0.6, s=se, seed=721)
    line(L, pts + [pts[0]], 1.0, se, 0.75, 0, 722, taper=False)
    for k in range(3):
        a = (-w * 0.7, -h * 0.5 + k * h * 0.4); b = (w * 0.6, -h * 0.5 + k * h * 0.4)
        line(L, [(x + c * a[0] - s_ * a[1], y + s_ * a[0] + c * a[1]), (x + c * b[0] - s_ * b[1], y + s_ * b[0] + c * b[1])], 0.7, se, 0.4, 0, 723 + k, taper=False)

def flying_hat(ctx, x, y, ang, se, front=True):
    L = ctx.layer(x - 50 * se, y - 50 * se, x + 50 * se, y + 50 * se, front=front)
    c, s_ = math.cos(ang), math.sin(ang)
    R = lambda dx, dy: (x + c * dx - s_ * dy, y + s_ * dx + c * dy)
    hat = [R(-34 * se, 6 * se)] + [R(34 * se * math.cos(q), 6 * se - 22 * se * math.sin(q)) for q in np.linspace(math.pi, 0, 14)] + [R(34 * se, 6 * se)]
    fill(L, hat, 0.15, (0.60, 0.80, 0.90), 0.7, s=se, seed=731, edge=0.6)
    line(L, hat, 1.4, se, 0.85, 0.3, 732, taper=False)
from sound import Mix, note, PENT
