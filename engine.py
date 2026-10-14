# Scene engine: shots = painted set + camera + live drawing (screen space, crisp at any zoom);
# bilingual subtitles (中文 over English) in the lower letterbox bar.
import sys, os, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from ink import *
from chars import Layer, ease, lerp, fill, line, path, jar as _jar, ladle as _ladle, cormorant as _cormorant
from figure import *

FPS = 24; OW, OH = 1920, 804; FH = 1080; BAR = (FH - OH) // 2
CJK = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
BRUSH = os.path.join(HERE, 'MaShanZheng.ttf')
SERIF_I = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
GLOW = np.array([0.98, 0.95, 0.70], np.float32)     # BGR pale jade light
GOLD = np.array([0.55, 0.85, 1.0], np.float32)
WARM = np.array([0.45, 0.72, 1.0], np.float32)      # candle / lantern
BLUE = np.array([1.0, 0.80, 0.50], np.float32)
JAR_COLS = [np.array(c, np.float32) for c in [(0.80, 0.70, 1.0), (0.45, 0.80, 1.0), (1.0, 0.80, 0.55), (0.95, 0.65, 0.85), (0.70, 1.0, 0.75)]]
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)

def kf(keys, t, fn=ease):
    """keyframes [(t, value-or-tuple), ...] -> eased interpolation"""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            u = fn((t - t0) / max(1e-6, t1 - t0))
            if isinstance(v0, tuple): return tuple(a + (b - a) * u for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * u
    return keys[-1][1]

def lin(u): return min(1.0, max(0.0, u))

def C(cx, cy, z=1.0):
    """camera from a centre point"""
    return (cx - OW / 2 / z, cy - OH / 2 / z, z)

def camkf(keys):
    """keys [(t, (cx, cy, z)), ...] -> camera function"""
    return lambda t: kf(keys, t)

_sp = None
def screen_paper():
    global _sp
    if _sp is None:
        f = os.path.join(CACHE, 'screen_paper.npy')
        if os.path.exists(f): _sp = np.load(f).astype(np.float32)
        else: _sp = paper(OH, OW, 7); np.save(f, _sp.astype(np.float16))
    return _sp

class Ctx:
    """what a shot's draw() gets: world->screen transform, a stack of local ink layers, glows"""
    def __init__(self, left, top, z, t, T=0.0, scene=None):
        self.left, self.top, self.z, self.t, self.Tabs, self.scene = left, top, z, t, T, scene
        self.stack = []; self.glow = []; self.front = []; self.over = False
        self.L = self.layer()                  # full-screen back layer
    def T(self, x, y): return ((x - self.left) * self.z, (y - self.top) * self.z)
    def Tp(self, pts): return (np.asarray(pts, np.float32) - [self.left, self.top]) * self.z
    def layer(self, x0=0, y0=0, x1=OW, y1=OH, op=1.0, front=False, over=False):
        """front: after grade and glow (weather); over: in front of the set's foreground pieces"""
        x0, y0 = int(math.floor(x0)), int(math.floor(y0)); x1, y1 = int(math.ceil(x1)), int(math.ceil(y1))
        L = Layer(x0, y0, max(1, x1 - x0), max(1, y1 - y0))
        if front: self.front.append((L, op))
        else: self.stack.append((L, op, over or self.over))
        return L
    def visible(self, sx, sy, r):
        return sx + r > 0 and sx - r < OW and sy + r > 0 and sy - r < OH
    def talking(self, who):
        return self.scene.talking(who, self.Tabs) if self.scene else False
    def fig(self, x, y, s, who, facing=1, pose=None, seed=11, op=1.0, front=False, over=False, rot=0.0, talker=None, spec=None):
        """rot: degrees, turns the whole figure about its feet (lying down, tumbling, flying)"""
        sx, sy = self.T(x, y); se = s * self.z
        if not self.visible(sx, sy - 120 * se, 280 * se): return None
        pose = dict(pose or {})
        if 'talk' not in pose: pose['talk'] = 1 if self.talking(talker or who) else 0
        if not rot:
            L = self.layer(sx - 140 * se, sy - 270 * se, sx + 140 * se, sy + 30 * se, op, front, over)
            return figure(L, sx, sy, se, who, self.t, facing, pose, seed, spec)
        L = self.layer(sx - 290 * se, sy - 290 * se, sx + 290 * se, sy + 290 * se, op, front, over)
        r = figure(L, sx, sy, se, who, self.t, facing, pose, seed, spec)
        cx, cy = sx - L.x0, sy - L.y0
        M = cv2.getRotationMatrix2D((cx, cy), -rot, 1.0); h, w = L.D.shape
        R = lambda a: cv2.warpAffine(a, M, (w, h), flags=cv2.INTER_LINEAR)
        L.D = R(L.D); L.M = R(L.M); L.tints = [(R(a), c) for a, c in L.tints]
        def rp(p): return (M[0, 0] * (p[0] - L.x0) + M[0, 1] * (p[1] - L.y0) + M[0, 2] + L.x0, M[1, 0] * (p[0] - L.x0) + M[1, 1] * (p[1] - L.y0) + M[1, 2] + L.y0)
        for k in ('hand_f', 'hand_b', 'head', 'neck'): r[k] = rp(r[k])
        return r
    def box(self, x, y, rx, ry, op=1.0, front=False, world=True, over=False):
        """a local layer around a world (or screen) point"""
        if world: x, y = self.T(x, y); rx, ry = rx * self.z, ry * self.z
        return self.layer(x - rx, y - ry, x + rx, y + ry, op, front, over)
    def jar(self, x, by, s=1.0, seed=41):
        sx, sy = self.T(x, by); se = s * self.z
        L = self.layer(sx - 40 * se, sy - 80 * se, sx + 40 * se, sy + 10 * se)
        return _jar(L, sx, sy, se, seed)
    def cormorant(self, x, y, s=1.0, look=0.0, seed=51):
        sx, sy = self.T(x, y); se = s * self.z
        L = self.layer(sx - 70 * se, sy - 90 * se, sx + 70 * se, sy + 120 * se)
        _cormorant(L, sx, sy, self.t, se, seed, look)
    def baozi(self, x, y, s=1.0, mood='happy'):
        sx, sy = self.T(x, y); se = s * self.z
        L = self.layer(sx - 40 * se, sy - 40 * se, sx + 40 * se, sy + 40 * se)
        baozi(L, sx, sy, self.t, se, mood)
    def add_glow(self, x, y, r, a, col=GLOW, world=True):
        if world: x, y = self.T(x, y); r = r * self.z
        self.glow.append((x, y, r, a, col))

def comp_layer(img, L, op, P):
    h, w = L.D.shape
    sx0, sy0 = max(0, L.x0), max(0, L.y0); sx1, sy1 = min(OW, L.x0 + w), min(OH, L.y0 + h)
    if sx1 <= sx0 or sy1 <= sy0: return
    ly0, lx0 = sy0 - L.y0, sx0 - L.x0; ly1, lx1 = ly0 + sy1 - sy0, lx0 + sx1 - sx0
    sub = img[sy0:sy1, sx0:sx1]
    M = L.M[ly0:ly1, lx0:lx1, None] * op
    if M.max() > 0: sub[:] = sub * (1 - M) + P[sy0:sy1, sx0:sx1] * M
    for a, c in L.tints:
        sub *= 1 - a[ly0:ly1, lx0:lx1, None] * op * (1 - np.asarray(c, np.float32))
    D = L.D[ly0:ly1, lx0:lx1, None] * op
    sub[:] = sub * (1 - D) + INK * D

def render_glow(img, glow, k=0.75):
    if not glow: return img
    acc = np.zeros((OH, OW, 3), np.float32)
    for (gx, gy, r, a, col) in glow:
        pad = int(r * 8 + 60)
        x0g, y0g = max(0, int(gx - pad)), max(0, int(gy - pad)); x1g, y1g = min(OW, int(gx + pad)), min(OH, int(gy + pad))
        if x1g <= x0g or y1g <= y0g: continue
        h, w = y1g - y0g, x1g - x0g
        # big glows: blur on a smaller grid, then scale up (same look, far faster)
        ds = int(min(16, max(1, r * 0.3 / 2.0)))
        hs, ws = max(1, h // ds), max(1, w // ds); fy, fx = hs / h, ws / w
        sub = np.zeros((hs, ws), np.float32)
        cv2.circle(sub, (int((gx - x0g) * fx * 4), int((gy - y0g) * fy * 4)), max(1, int(r * fx * 4)), float(a), -1, cv2.LINE_AA, 2)
        gl = cv2.GaussianBlur(sub, (0, 0), max(1, r * 0.3) * fx) * 0.9 + cv2.GaussianBlur(sub, (0, 0), max(2, r * 1.2) * fx) * 1.3 + cv2.GaussianBlur(sub, (0, 0), max(4, r * 3) * fx) * 1.0
        if ds > 1: gl = cv2.resize(gl, (w, h), interpolation=cv2.INTER_LINEAR)
        acc[y0g:y1g, x0g:x1g] += gl[..., None] * np.asarray(col, np.float32)
    return img + acc * k

# ---------------- weather drawn in screen space
_R = np.random.default_rng(5)
RAIN = np.column_stack([_R.random(900) * 2200, _R.random(900) * 900, 14 + _R.random(900) * 22, 0.25 + _R.random(900) * 0.45])
def rain(ctx, amount=1.0, L=None, slant=0.2, speed=1100, dens=0.32, wind=60):
    """amount 0..1 scales the number of streaks"""
    if amount <= 0: return
    L = L or ctx.layer(front=True); t = ctx.Tabs
    n = int(len(RAIN) * min(1, amount) * 0.6)
    for (rx, ry, rl, rd) in RAIN[:n]:
        x = (rx * 0.9 - t * wind) % (OW + 100) - 50; y = (ry + t * speed) % (OH + 80) - 40
        cv2.line(L.D, (int(x * 4), int(y * 4)), (int((x - rl * slant) * 4), int((y - rl) * 4)), rd * dens, 1, cv2.LINE_AA, 2)

def ripples(ctx, y0, y1, n=40, L=None):
    L = L or ctx.L; t = ctx.Tabs; z = ctx.z
    rr = np.random.default_rng(int(t * 6))
    for k in range(n):
        rx = ctx.left + rr.random() * OW / z; ry = y0 + 8 + rr.random() ** 1.5 * (y1 - y0 - 10); age = (rr.random() + t * 1.7) % 1
        rad = (3 + age * 14 * (0.6 + (ry - y0) / 200)) * z
        c = ctx.T(rx, ry)
        cv2.ellipse(L.D, (int(c[0] * 4), int(c[1] * 4)), (int(rad * 4), int(rad * 1.1)), 0, 0, 360, 0.3 * (1 - age), 1, cv2.LINE_AA, 2)

def drips(ctx, xs, ey, yb, L=None):
    L = L or ctx.L; t = ctx.Tabs; z = ctx.z
    for i, dxp in enumerate(xs):
        per = 0.9 + (i * 0.37) % 0.8; ph = (t + i * 0.53) % per / per
        e = ey + (i % 3) * 8; yd = e + ph ** 2 * (yb - e)
        p0 = ctx.T(dxp, yd); p1 = ctx.T(dxp, yd + 6)
        if -10 < p0[0] < OW + 10:
            cv2.line(L.D, (int(p0[0] * 4), int(p0[1] * 4)), (int(p1[0] * 4), int(p1[1] * 4)), 0.5, max(1, int(1.6 * z)), cv2.LINE_AA, 2)

def strands(ctx, anchors, L=None, color=0.0):
    """willow strands: anchors [(ax, ay, length, phase, speed)] in world coords"""
    L = L or ctx.L; t = ctx.Tabs; z = ctx.z; T = ctx.T
    for (ax, ay, ln, ph, sp) in anchors:
        sx0, _ = T(ax, ay)
        if sx0 < -400 or sx0 > OW + 400: continue
        k = np.linspace(0, 1, 16)
        sway = (math.sin(t * sp * 1.4 + ph) * 10 + math.sin(t * 0.5 + ph) * 6) * k ** 1.6
        pts = np.array([T(x, y) for x, y in zip(ax + sway + k * 6, ay + k * ln)])
        cv2.polylines(L.D, [np.round(pts * 4).astype(np.int32)], False, 0.45, max(1, int(z * 0.9)), cv2.LINE_AA, 2)
        for i in range(3, 16, 2):
            px, py = pts[i]; cv2.line(L.D, (int(px * 4), int(py * 4)), (int((px + (4 + (i % 3)) * z) * 4), int((py + 7 * z) * 4)), 0.35, max(1, int(z * 1.4)), cv2.LINE_AA, 2)

def snow(ctx, amount=1.0, L=None, seed=3):
    L = L or ctx.layer(front=True); t = ctx.Tabs
    r = np.random.default_rng(seed); n = int(260 * amount)
    xs = r.random(n) * (OW + 200); ys = r.random(n) * OH; sp = 30 + r.random(n) * 50; sz = 1.5 + r.random(n) * 3
    for i in range(n):
        x = (xs[i] + math.sin(t * 0.8 + i) * 30) % (OW + 200) - 100; y = (ys[i] + t * sp[i]) % (OH + 40) - 20
        cv2.circle(L.M, (int(x * 4), int(y * 4)), int(sz[i] * 4), 1.0, -1, cv2.LINE_AA, 2)
    L.M[:] = cv2.GaussianBlur(L.M, (0, 0), 0.8)
    L.tints.append((L.M * 0.0, (1, 1, 1)))
    over(L.D, cv2.GaussianBlur(L.M, (0, 0), 1.5) * 0.06)

# ---------------- subtitles
_subcache = {}
def subtitle_img(zh, en):
    key = (zh, en)
    if key in _subcache: return _subcache[key]
    im = Image.new('L', (OW, BAR), 0); d = ImageDraw.Draw(im)
    fz = 36; fe = 31
    if zh: d.text((OW / 2, 46), zh, font=ImageFont.truetype(BRUSH, 40), fill=255, anchor='mm')
    if en: d.text((OW / 2, 96), en, font=ImageFont.truetype(SERIF_I, fe), fill=255, anchor='mm')
    a = np.asarray(im, np.float32) / 255
    if len(_subcache) > 200: _subcache.clear()
    _subcache[key] = a
    return a

def card_img(lines, size=(OW, OH), fz=64, fe=34, gap=22):
    """centred title / caption: list of (zh, en)"""
    im = Image.new('L', size, 0); d = ImageDraw.Draw(im)
    y = size[1] / 2 - (len(lines) * (fz + fe + gap)) / 2 + fz / 2
    for zh, en in lines:
        if zh: d.text((size[0] / 2, y), zh, font=ImageFont.truetype(BRUSH, fz), fill=255, anchor='mm')
        if en: d.text((size[0] / 2, y + fz * 0.5 + fe * 0.9), en, font=ImageFont.truetype(SERIF_I, fe), fill=255, anchor='mm')
        y += fz + fe + gap * 2
    t = np.asarray(im, np.float32) / 255
    return t

def words(en): return len(en.split())
def sub_dur(zh, en):
    return max(2.0, 1.0 + words(en) / 2.6, len(zh) / 5.0)

class Scene:
    def __init__(self, shots, subs=(), title=None, credits=None):
        self.shots = shots
        t = 0
        for sh in shots: sh['t0'] = t; t += sh['dur']
        self.dur = t
        # subs: (t0, zh, en, who) or (t0, t1, zh, en, who)
        out = []
        for s in subs:
            if len(s) == 4: t0, zh, en, who = s; t1 = t0 + sub_dur(zh, en)
            else: t0, t1, zh, en, who = s
            out.append((t0, t1, zh, en, who))
        out.sort(key=lambda r: r[0])
        for i in range(len(out) - 1):          # never overlap
            if out[i][1] > out[i + 1][0] - 0.1:
                r = out[i]; out[i] = (r[0], out[i + 1][0] - 0.1, r[2], r[3], r[4])
        self.subs = out
    def talking(self, who, T):
        for (t0, t1, zh, en, w) in self.subs:
            if w == who and t0 <= T < t1 - 0.25: return True
        return False
    def shot_at(self, t):
        for i, sh in enumerate(self.shots):
            if sh['t0'] <= t < sh['t0'] + sh['dur']: return i
        return len(self.shots) - 1
    def frame(self, t):
        idx = self.shot_at(t); sh = self.shots[idx]; lt = t - sh['t0']
        img = self.render_shot(sh, lt, t)
        xin = sh.get('xfade', 0)
        if xin and lt < xin and idx > 0:
            pv = self.shots[idx - 1]; img0 = self.render_shot(pv, pv['dur'] + lt, t)
            u = ease(lt / xin); img = img0 * (1 - u) + img * u
        fi = sh.get('fade_in'); fo = sh.get('fade_out')
        if fi:
            d, col = fi; u = ease(lt / d)
            if u < 1: img = img * u + np.asarray(col, np.float32) * (1 - u)
        if fo:
            d, col = fo; u = ease((sh['dur'] - lt) / d)
            if u < 1: img = img * u + np.asarray(col, np.float32) * (1 - u)
        return img
    def render_shot(self, sh, lt, T):
        cam = sh['cam'](lt) if callable(sh['cam']) else sh['cam']
        if len(cam) == 3 and sh.get('center', True) and not sh.get('raw_cam'): left, top, z = C(*cam)
        else: left, top, z = cam
        args = sh.get('args', {})
        if callable(args): args = args(lt)
        img = sh['set'].render(T if sh.get('abs_t') else lt + sh.get('set_t0', 0), left, top, z, args).copy()
        ctx = Ctx(left, top, z, lt, T, self); ctx.args = args
        if sh.get('draw'): sh['draw'](ctx, lt)
        P = screen_paper()
        for L, op, ov in ctx.stack:
            if not ov: comp_layer(img, L, op, P)
        if hasattr(sh['set'], 'fg'):
            fg = sh['set'].fg(lt, left, top, z, args)
            if fg is not None:
                rgb, a = fg; img = img * (1 - a[..., None]) + rgb * a[..., None]
        for L, op, ov in ctx.stack:
            if ov: comp_layer(img, L, op, P)
        g = sh.get('grade')
        if g is not None:
            g = g(lt) if callable(g) else g
            img *= np.asarray(g, np.float32)
        img = render_glow(img, ctx.glow)
        for L, op in ctx.front: comp_layer(img, L, op, P)
        if sh.get('post'): img = sh['post'](img, lt, ctx)
        return np.clip(img, 0, 1)
    def full(self, t, vig):
        f = self.frame(t) * vig
        out = np.zeros((FH, OW, 3), np.float32); out[BAR:BAR + OH] = f
        for (t0, t1, zh, en, who) in self.subs:
            if t0 <= t < t1:
                a = subtitle_img(zh, en) * min(1, (t - t0) / 0.2, (t1 - t) / 0.2)
                out[BAR + OH:] = np.maximum(out[BAR + OH:], a[..., None] * np.array([0.86, 0.90, 0.93], np.float32))
                break
        return out

def make_vig():
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    return (1 - 0.22 * (((xx - OW / 2) / (OW * 0.6)) ** 2 + ((yy - OH / 2) / (OH * 0.7)) ** 2)).clip(0.6, 1)[..., None]

def run(scene, outdir, wk, nw, t_from=0.0, t_to=None):
    os.makedirs(outdir, exist_ok=True); vig = make_vig()
    n = int(round((t_to or scene.dur) * FPS))
    for i in range(int(t_from * FPS) + wk, n, nw):
        fn = os.path.join(outdir, f'{i:05d}.png')
        if os.path.exists(fn): continue
        f = scene.full(i / FPS, vig)
        cv2.imwrite(fn + '.tmp.png', (np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8)); os.replace(fn + '.tmp.png', fn)
        print(i, flush=True)

def still(scene, t, fn):
    f = scene.full(t, make_vig()); cv2.imwrite(fn, (np.clip(f, 0, 1) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 88])
