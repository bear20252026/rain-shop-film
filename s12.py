# Scene 12 · The Rain Returns · 雨回来了  (52:00 - 56:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_more import MUDFLAT, depth_s, SKY, SKY_W, SKY_H
from engine import rain
from s01 import Q
from s06 import BALD
from s10 import MUD_Y
from s11 import draw_spine, granny_mud, carriers, WEATHERS

GREY = (0.70, 0.68, 0.70)
WET = (0.80, 0.80, 0.84)
FULL = (1.0, 0.99, 0.98)
DRAGON_COLS = WEATHERS + [W_WARM]

def ramp(T, a, b): return ease((T - a) / (b - a))

# ---------------------------------------------------------------- rainbow (screen-space bands on an ellipse)
RB_COLS = np.array([(0.25, 0.28, 0.86), (0.22, 0.55, 0.96), (0.35, 0.86, 0.96), (0.45, 0.80, 0.42), (0.86, 0.66, 0.36), (0.78, 0.45, 0.58)], np.float32)
_YY, _XX = np.mgrid[0:OH, 0:OW].astype(np.float32)
_RBN = smooth(vnoise(OH, OW, 40, 313, 3), 0.2, 0.8)

def rainbow(img, X, Y, cx, cy, rx, ry, phi_min, amt, r0=1.06, bw=0.028):
    if amt <= 0: return img
    nx = (X - cx) / rx; ny = (cy - Y) / ry
    rho = np.sqrt(nx * nx + ny * ny); phi = np.arctan2(ny, nx)
    idx = (rho - r0) / bw
    a = np.clip(np.minimum(idx, 6 - idx) * 1.5, 0, 1) * smooth(phi - phi_min, 0, 0.08) * (ny > 0) * smooth(ny, 0, 0.25)
    if a.max() <= 0: return img
    k = np.clip(idx, 0, 5.999)
    col = np.stack([np.interp(k, np.arange(6), RB_COLS[:, c]) for c in range(3)], -1)
    a = (a * amt * (0.55 + 0.45 * _RBN))[..., None]
    return img * (1 - a) + img * col * a * 1.25

# ---------------------------------------------------------------- A: silence; one drop on Granny's cheek; then a thousand
DROP_T = 7.0
def rain_amt(T): return ramp(T, 9.5, 18) * (1 - 0.35 * ramp(T, 184, 200))

def drawA(ctx, lt):
    T = ctx.Tabs
    hit = T > DROP_T
    r = granny_mud(ctx, T, T, x=1500, pose=dict(no_lantern=True, look=-24 if T < DROP_T + 1.5 else -30,
                   eyes='closed' if DROP_T < T < DROP_T + 0.5 or T > DROP_T + 4 else ('wide' if hit else 'open'),
                   mouth='smile' if T > DROP_T + 5 else 'flat', arm_f=(lerp(20, 60, ramp(T, 12, 15)), 30), arm_b=(lerp(20, 50, ramp(T, 12, 15)), 30)))
    ctx.fig(1640, MUD_Y + 4, depth_s(MUD_Y), 'xiaoman', -1, dict(look=-24, eyes='happy' if T > 16 else ('wide' if T > 9 else 'open'),
            mouth='open' if T > 12 else 'flat', arm_f=(lerp(20, 160, ramp(T, 15, 17)), 20), arm_b=(lerp(20, 150, ramp(T, 15.5, 17.5)), 20)))
    ctx.baozi(1720, MUD_Y - 230 + 8 * math.sin(T * 2), 1.3, 'happy' if T > 12 else 'calm')
    if r:      # the single drop falling onto her cheek
        hx, hy = r['head']; hx += 14 * ctx.z; hy += 24 * ctx.z
        if T < DROP_T:
            u = ramp(T, DROP_T - 1.4, DROP_T)
            ctx.add_glow(hx, lerp(-20, hy, u * u), 3 * ctx.z, 0.8 * (u > 0), W_DRIZZLE, world=False)
        elif T < DROP_T + 2.5:
            v = (T - DROP_T) / 2.5
            ctx.add_glow(hx + 2 * ctx.z, hy + 10 * ctx.z * v, 3 * ctx.z, 0.7 * (1 - v), W_DRIZZLE, world=False)
    rain(ctx, rain_amt(T))

def drawA2(ctx, lt):       # wide: the town on the mud, arms up, faces to the sky
    T = ctx.Tabs
    carriers(ctx, T, 200, 1.0)
    granny_mud(ctx, T, T, x=1500, pose=dict(no_lantern=True, look=-30, eyes='closed', mouth='smile', arm_f=(70, 30), arm_b=(60, 30)))
    ctx.fig(1640, MUD_Y + 4, depth_s(MUD_Y), 'xiaoman', 1 if int(T * 1.2) % 2 else -1, dict(look=-24, eyes='happy', mouth='open', arm_f=(160, 20), arm_b=(150, 20), walk=T * 2.5))
    rain(ctx, rain_amt(T))

# ---------------------------------------------------------------- B: color floods the ink town; the canal fills; children dance
T_B = 34.0
def col_amt(T): return ramp(T, T_B + 1, T_B + 16)
def water_amt(T): return ramp(T, T_B, T_B + 26)

def town_args(lt, base):
    T = base + lt
    return dict(water=water_amt(T), color=col_amt(T), mist=0.6)

def dancers(ctx, T, xs=(760, 880, 1000, 1100)):
    crew = [('twin', None, 0.8), ('twin', TWIN_B, 0.8), ('xiaoman', None, 0.95), ('twin', None, 0.8)]
    for i, ((who, spec, s), x0) in enumerate(zip(crew, xs)):
        if who == 'xiaoman' and T < 150: continue      # he is still out on the mud until the end
        if who == 'xiaoman': continue
        sw = math.sin(T * 1.7 + i * 2.1)
        f = 1 if math.sin(T * 0.9 + i * 1.3) > 0 else -1
        x = x0 + 40 * math.sin(T * 0.8 + i)
        ctx.fig(x, Q - 6 * abs(math.sin(T * 4 + i)), s, who, f, dict(walk=T * 3 + i, arm_f=(lerp(110, 170, (sw + 1) / 2), 20), arm_b=(lerp(170, 110, (sw + 1) / 2), 20),
                eyes='happy', mouth='open', look=-14), seed=60 + i, spec=spec)

def watchers(ctx, T):
    ctx.fig(1240, Q, 1.0, 'mother', -1, dict(look=-20, eyes='closed', mouth='smile', arm_f=(70, 20), arm_b=(60, 20)), seed=71)
    ctx.fig(560, Q, 1.05, 'farmer', 1, dict(look=-26, eyes='happy', mouth='open', arm_f=(160, 10), arm_b=(30, 30)), seed=72)
    r = ctx.fig(1380, Q, 1.0, 'bride', -1, dict(look=-10, eyes='happy', mouth='smile', arm_f=(120, 30)), seed=73)
    if r: umbrella(ctx, r['hand_f'], ctx.z, 2, 8, open_=0.0)       # she does not open it

def drawB(ctx, lt):
    T = ctx.Tabs
    town_live(ctx, rain_amt=rain_amt(T), water=water_amt(T), color=col_amt(T), look=-0.5, jars_glow=0.0)
    if T > 62: dancers(ctx, T); watchers(ctx, T)

# ---------------------------------------------------------------- C: Qian, soaked, laughs; "This one... isn't for sale."; helps the ferryman push off
T_C = 90.0
PUSH = T_C + 34

def sleeve_drips(ctx, r, T, s):
    for hand in ('hand_f', 'hand_b'):
        hx, hy = r[hand]
        for k in range(3):
            v = (T * 1.3 + k / 3 + (hand == 'hand_b') * 0.5) % 1.0
            ctx.add_glow(hx + (k - 1) * 4 * ctx.z, hy + v * 140 * s * ctx.z, 2.4 * ctx.z, 0.5 * (1 - v), GOLD, world=False)

def boat_x(T): return lerp(1620, 2450, ease((T - PUSH) / 18) ** 1.2)

def drawC(ctx, lt):
    T = ctx.Tabs; u = T - T_C
    town_live(ctx, rain_amt=0.9, color=1.0, jars_glow=0.0)
    bx = boat_x(T)
    deck = sampan(ctx, bx, WATER_Y + 52, 1.0, seed=611)
    fm = ctx.fig(deck[0], deck[1], 1.0, 'ferryman', -1 if u < 26 else 1, dict(arm_f=(150, -30), arm_b=(120, -10), lean=12, bob=False,
                 eyes='happy' if u > 22 else 'open', mouth='smile' if u > 22 else 'flat', look=0 if u < 30 else 4))
    if fm: pole(ctx, fm['hand_f'], 18 + 8 * math.sin(T * 0.8), ctx.z)
    # the porter offers a jar to catch the rain in (to sell it, of course)
    offer = ramp(u, 2, 4) * (1 - ramp(u, 19, 21))
    pr = ctx.fig(1180, Q, 1.05, 'porter', 1, dict(arm_f=(lerp(30, 80, offer), lerp(40, 90, offer)), arm_b=(lerp(20, 70, offer), lerp(30, 90, offer)), look=-4,
                 eyes='wide' if 15 < u < 22 else 'open', mouth='open' if 16 < u < 19 else 'flat'), seed=81)
    if pr and offer > 0.05:
        hx, hy = pr['hand_f']; wx, wy = hx / ctx.z + ctx.left, hy / ctx.z + ctx.top
        big_jar(ctx, wx + 6, wy + 42, 0.42, W_DRIZZLE, 0.15 * offer, seed=951)
    # Qian
    if T < PUSH:
        x, ph = 1330, None
        if u < 2: x, ph, _ = walk_x([(T_C, 1250), (T_C + 2, 1330)], T, s=1.1)
        push = 0.0
    else:
        x, ph, _ = walk_x([(PUSH - 0.1, 1330), (PUSH + 2.2, 1432)], T, s=1.1)
        push = ramp(T, PUSH + 1.6, PUSH + 2.6) * (1 - ramp(T, PUSH + 9, PUSH + 11))
    laugh = 21 < u < 33 or T > PUSH + 6
    stop = ramp(u, 13, 14.5) * (1 - ramp(u, 19, 21))
    qp = dict(walk=ph, look=-20 if 4 < u < 9 else (-6 if not laugh else -12), eyes='happy' if laugh else ('closed' if 4 < u < 7 else 'open'),
              mouth='open' if laugh or 15 < u < 17 else 'flat', lean=25 * push + (6 if laugh else 0),
              arm_f=(lerp(lerp(20, 70, stop), 85, push), lerp(30, 0, push)), arm_b=(lerp(15, 85, push), lerp(30, 0, push)))
    q = ctx.fig(x, Q, 1.1, 'qian', 1 if T >= PUSH or u < 2 else -1, qp, seed=82, spec=BALD)
    if q: sleeve_drips(ctx, q, T, 1.1)

# ---------------------------------------------------------------- D: the dragon loops once over Willow Bend; its tail draws a rainbow
T_D = 150.0
LOOP = (1300, 1000, 820, 330)
BODY = 2.4

def loop_theta(T):
    return math.pi + 0.7 - (2 * math.pi + 0.7 + BODY + 0.5) * ease((T - T_D) / 19) ** 0.95

def loop_spine(T, n=90):
    cx, cy, rx, ry = LOOP; th0 = loop_theta(T)
    th = th0 + np.linspace(0, BODY, n)
    off = np.sin(np.linspace(0, 1, n) * 3 * math.pi - T * 3) * 30 * np.linspace(0.3, 1, n)
    x = cx + (rx + off) * np.cos(th); y = cy - (ry + off) * np.sin(th)
    return np.stack([x, y], 1)

def rb_phi_min(T):
    return max(0.0, min(math.pi, loop_theta(T) + BODY))

def drawD(ctx, lt):
    T = ctx.Tabs
    draw_spine(ctx, loop_spine(T), T, 1.5, 1.0, 'calm', jaw=0.3 * (math.sin(T * 2) > 0.8), color=1.0, cols=DRAGON_COLS)
    rain(ctx, 0.25)

def postD(img, lt, ctx):
    T = ctx.Tabs
    X = _XX / ctx.z + ctx.left; Y = _YY / ctx.z + ctx.top
    cx, cy, rx, ry = LOOP
    return rainbow(img, X, Y, cx, cy, rx, ry, rb_phi_min(T), 0.85 * (1 - ramp(T, 168, 170)) + 0.0, r0=1.10, bw=0.035)

def post_town_rainbow(amt_fn):
    def post(img, lt, ctx):
        return rainbow(img, _XX, _YY, 960, 980, 1150, 820, 0.0, amt_fn(ctx.Tabs), r0=1.0, bw=0.03)
    return post

def drawD2(ctx, lt):
    T = ctx.Tabs
    town_live(ctx, rain_amt=0.5, color=1.0, look=-1.0, jars_glow=0.0)
    dancers(ctx, T); watchers(ctx, T)

# ---------------------------------------------------------------- E: Granny and Xiaoman stand in the rain, no umbrellas
T_E = 184.0
def drawE(ctx, lt):
    T = ctx.Tabs; u = T - T_E
    town_live(ctx, rain_amt=rain_amt(T), color=1.0, look=0.0, jars_glow=0.0)
    g = ctx.fig(1700, Q, 1.12, 'granny', -1, dict(look=-18 if u < 14 else (-4 if u < 30 else -16), eyes='closed' if 22 < u < 24 or u > 30 else 'open',
                mouth='smile' if u > 23 else 'flat', arm_f=(20, 20), arm_b=(15, 20)), seed=11)
    ctx.fig(1610, Q, 0.95, 'xiaoman', 1, dict(look=-18 if u < 14 else (6 if u < 30 else -16), eyes='happy' if u > 24 else 'open',
            mouth='open' if 16 < u < 18 else ('smile' if u > 24 else 'flat'), arm_f=(20, 30), arm_b=(15, 30)), seed=12)
    ctx.baozi(1655, Q - 210 + 6 * math.sin(T * 2), 1.0, 'happy')
    if u > 26: ctx.add_glow(1660, Q - 200, 40, 0.10 * ramp(u, 26, 30), W_WARM)

# ---------------------------------------------------------------- shots
def tb(fn, base):
    return lambda lt: fn(lt, base)

shots = [
    # A · 0  silence ... one drop ... then a thousand
    dict(dur=14, set=MUDFLAT, cam=camkf([(0, (1520, 565, 2.9)), (14, (1520, 560, 3.1))]), draw=drawA, grade=lambda lt: tuple(lerp(a, b, ramp(lt, 9, 14)) for a, b in zip(GREY, WET)), fade_in=(1.5, (0.6, 0.6, 0.62))),
    dict(dur=8, set=MUDFLAT, cam=(1660, 570, 2.5), draw=drawA, grade=WET),
    dict(dur=12, set=MUDFLAT, cam=camkf([(0, (1700, 470, 1.4)), (12, (1950, 420, 1.05))]), draw=drawA2, grade=WET),
    # B · 34  color floods in; the canal fills
    dict(dur=18, set=TOWN, cam=lambda lt: (lerp(800, 1500, ease(lt / 18)), 402, 1.0), draw=drawB, args=tb(town_args, 34), xfade=1.5,
         grade=lambda lt: tuple(lerp(a, b, ramp(lt, 1, 16)) for a, b in zip(WET, FULL))),
    dict(dur=10, set=TOWN, cam=camkf([(0, (2000, 520, 2.0)), (10, (2000, 540, 2.2))]), draw=drawB, args=tb(town_args, 52), grade=FULL),    # 52 the boat lifts, Old Ink
    dict(dur=14, set=TOWN, cam=camkf([(0, (900, 430, 1.35)), (14, (960, 430, 1.4))]), draw=drawB, args=tb(town_args, 62), grade=FULL, xfade=1.0),   # 62 children dance
    dict(dur=14, set=TOWN, cam=camkf([(0, (900, 480, 2.2)), (14, (980, 480, 2.3))]), draw=drawB, args=tb(town_args, 76), grade=FULL),
    # C · 90  Qian
    dict(dur=14, set=TOWN, cam=camkf([(0, (1330, 450, 1.6)), (14, (1350, 450, 1.7))]), draw=drawC, args=dict(color=1.0, mist=0.5), grade=FULL, xfade=1.0),
    dict(dur=8, set=TOWN, cam=(1370, 470, 2.6), draw=drawC, args=dict(color=1.0, mist=0.5), grade=FULL),         # 104 "This one... isn't for sale."
    dict(dur=10, set=TOWN, cam=camkf([(0, (1300, 470, 2.6)), (10, (1300, 470, 2.8))]), draw=drawC, args=dict(color=1.0, mist=0.5), grade=FULL),   # 112 a real laugh
    dict(dur=28, set=TOWN, cam=camkf([(0, (1400, 440, 1.5)), (14, (1650, 430, 1.4)), (28, (1850, 420, 1.25))]), draw=drawC, args=dict(color=1.0, mist=0.5), grade=FULL),
    # D · 150  the loop; the rainbow
    dict(dur=20, set=SKY, cam=(1300, 900, 1.0), draw=drawD, post=postD, grade=FULL, xfade=1.2),
    dict(dur=14, set=TOWN, cam=camkf([(0, (1350, 402, 1.0)), (14, (1350, 402, 1.0))]), draw=drawD2, args=dict(color=1.0, mist=0.3), grade=FULL,
         post=post_town_rainbow(lambda T: 0.75 * ramp(T, 170, 174)), xfade=1.0),
    # E · 184  in the rain, no umbrellas
    dict(dur=16, set=TOWN, cam=camkf([(0, (1660, 470, 1.8)), (16, (1660, 470, 2.0))]), draw=drawE, args=dict(color=1.0, mist=0.4), grade=FULL, xfade=1.0),
    dict(dur=12, set=TOWN, cam=(1655, 480, 2.7), draw=drawE, args=dict(color=1.0, mist=0.4), grade=FULL),     # 200 the lines
    dict(dur=28, set=TOWN, cam=camkf([(0, (1655, 480, 2.7)), (28, (1500, 402, 1.0))]), draw=drawE, args=dict(color=1.0, mist=0.4), grade=FULL,
         post=post_town_rainbow(lambda T: 0.55 * ramp(T, 222, 232)), fade_out=(2.5, (0.96, 0.96, 0.96))),
]

subs = [
    (105.0, '这个……不卖。', "This one... isn't for sale.", 'qian'),
    (201.0, '罐子都空了。', 'The jars are all empty.', 'xiaoman'),
    (206.5, '嗯。轻多了。', 'Mm. Feels much lighter.', 'granny'),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 22)
    m.wind(0, 10, 0.012, 200, 800)
    m.drip(DROP_T, 0.14, 1100)
    m.add(m.bell(note(81), 6, 0.04), DROP_T + 0.1)
    m.rain([(9, 0.0), (12, 0.25), (18, 0.9), (180, 0.9), (200, 0.55), (240, 0.5)])
    m.drips(14, 240, 2.5, 0.04)
    m.thunder(16.0, 0.20, far=True)
    m.pad(12, 22, [50, 57, 62, 66], 0.03)
    m.crowd(24, 34, 0.04, cheer=True)
    # colour floods in
    m.gliss(35, 62, 98, 0.07, 0.06)
    m.pad(35, 55, [55, 62, 67, 71, 74], 0.035)
    m.zheng_phrase(37, [67, 71, 74, 79, 74, 71, 67, None] * 6, 0.6, 0.07, 0.45)
    m.melody(46, [(79, 2.0), (81, 1.0), (83, 1.0), (86, 3.0), (83, 1.0), (81, 2.0), (79, 4.0), (None, 1.0), (81, 1.0), (83, 2.0), (86, 2.0), (88, 6.0)], 'dizi', 0.06)
    m.creak(53, 0.06); m.splash(55, 0.08); m.squawk(58, 0.08)
    m.giggle(63, 3.0, 0.06); m.giggle(70, 2.5, 0.05); m.giggle(80, 3.0, 0.05)
    m.crowd(62, 90, 0.025)
    for k in range(20): m.add(m.woodblock(700 + 200 * (k % 2), 0.04), 64 + k * 1.2)
    # Qian
    m.pad(90, 60, [52, 59, 64, 68], 0.025)
    m.steps(90, 92, 2.2, 0.04)
    m.melody(93, [(64, 2.0), (66, 1.0), (68, 3.0), (None, 2.0), (71, 2.0), (68, 4.0)], 'erhu', 0.04)
    m.breath(110, 1.5, 0.05)
    m.giggle(108.5, 3.5, 0.06); m.giggle(118, 3.0, 0.05)
    m.zheng_phrase(120, [64, 68, 71, 76, 71, 68] * 3, 0.5, 0.06, 0.5)
    m.oar(PUSH + 2, 0.12); m.splash(PUSH + 2.4, 0.10); m.oar(PUSH + 6, 0.08); m.oar(PUSH + 10, 0.06)
    # the loop; the rainbow
    m.whoosh(151, 4.0, 0.10); m.roar(156, 2.5, 0.12)
    m.pad(150, 34, [57, 64, 69, 73, 76, 81], 0.04)
    m.melody(152, [(81, 2.0), (85, 1.0), (88, 3.0), (93, 4.0), (None, 1.0), (88, 2.0), (85, 2.0), (81, 6.0)], 'dizi', 0.07)
    for k in range(14): m.add(m.chime(note(88 + (k * 5) % 12), 0.04), 160 + k * 0.6)
    m.whoosh(166, 3.0, 0.08, up=False)
    m.crowd(170, 184, 0.03, cheer=True)
    # in the rain, no umbrellas
    m.pad(184, 56, [50, 57, 62], 0.025)
    m.add(m.guzheng(note(62), 5, 0.08), 200.5)
    m.melody(207, [(62, 2.0), (64, 1.0), (66, 2.0), (69, 4.0), (None, 2.0), (71, 2.0), (69, 2.0), (66, 2.0), (62, 8.0)], 'erhu', 0.05)
    m.zheng_phrase(214, [62, 66, 69, 74, 69, 66, 62, None] * 3, 0.9, 0.05, 0.45)
    m.write(fn, 1.5, 2.5)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
