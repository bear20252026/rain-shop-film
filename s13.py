# Scene 13 · Autumn · 秋  (56:00 - 60:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_shop import SHOP, shop_live, FEET, COUNTER
from sets_more import CITY, city_live, BRIDGE, LANE, LANE_G, laundry, deck_y
from engine import rain
from s01 import Q, GRAN_IN, GRAN_Y
from s02 import ferry, STEP_X

AUTUMN = (0.84, 0.93, 1.04)
CITYG = (0.92, 0.86, 0.82)
LEAF_COLS = [(0.20, 0.45, 0.86), (0.25, 0.65, 0.95), (0.30, 0.55, 0.80), (0.25, 0.75, 0.92)]

def ramp(T, a, b): return ease((T - a) / (b - a))

def leaves(ctx, T, n=22, seed=3, amt=1.0):
    """falling autumn leaves in the foreground (screen space)"""
    L = ctx.layer(front=True); r = np.random.default_rng(seed)
    ms = [np.zeros(L.D.shape, np.float32) for _ in LEAF_COLS]
    for k in range(int(n * amt)):
        vx = 20 + r.random() * 40; vy = 35 + r.random() * 40; ph = r.random() * 6.28
        x = (r.random() * (OW + 200) + T * vx + 40 * math.sin(T * 0.9 + ph)) % (OW + 200) - 100
        y = (r.random() * (OH + 100) + T * vy) % (OH + 100) - 50
        sz = (7 + r.random() * 7) * (0.7 + 0.3 * ctx.z)
        ang = (T * (60 + r.random() * 90) + ph * 57) % 360
        squash = 0.25 + 0.25 * abs(math.sin(T * 2 + ph))
        cv2.ellipse(ms[k % len(ms)], (int(x * 4), int(y * 4)), (int(sz * 4), int(sz * squash * 4)), ang, 0, 360, 1.0, -1, cv2.LINE_AA, 2)
    for m, c in zip(ms, LEAF_COLS):
        if m.max() > 0:
            L.knock(m * 0.9); over(L.D, m * 0.12); L.tints.append((m * 0.9, c))

def town_autumn(ctx, look=0.0, leaves_on=True, rain_amt=0.0):
    town_live(ctx, rain_amt=rain_amt, water=1.0, color=1.0, look=look, jars_glow=0.25)
    new_sign(ctx)
    if leaves_on: leaves(ctx, ctx.Tabs)

def new_sign(ctx):
    sx, sy = ctx.T(1960, 398)
    paper_slip(ctx, sx, sy, ctx.z * 0.84, '婆婆与小满')

# ---------------------------------------------------------------- A: autumn; the new sign; the shop with few jars
def drawA(ctx, lt):
    T = ctx.Tabs
    town_autumn(ctx)
    sw = math.sin(T * 2.2)
    r = ctx.fig(1650, Q, 1.12, 'granny', -1, dict(lean=14, arm_f=(40 + 12 * sw, 50), arm_b=(30 + 12 * sw, 40), look=6), seed=11)
    if r: broom(ctx, r['hand_f'], 20 + 14 * sw, ctx.z * 1.12)
    ctx.fig(1560, Q, 0.95, 'xiaoman', 1, dict(look=0 if T < 16 else -16, arm_f=(20, 30), mouth='smile' if T > 18 else 'flat'), seed=12)
    ctx.baozi(1560, Q - 205 + 6 * math.sin(T * 2), 0.9, 'happy')

def drawB(ctx, lt):         # inside: few jars; a new sign; the farmer brings one back
    T = ctx.Tabs; u = T - 26
    shop_live(ctx, glow=0.8, red=False, giggle=True, empty=0.82, rain_door=0.0)
    sx, sy = ctx.T(1360, 432)
    paper_slip(ctx, sx, sy, ctx.z * 1.1, '借天气，记得还', vertical=False)
    put = ramp(u, 9, 10.5)
    gp = dict(look=6 if u < 8 else 0, eyes='happy' if u > 11 else 'open', mouth='smile' if u > 11 else 'flat', arm_f=(30, 40))
    ctx.fig(GRAN_IN, GRAN_Y, 2.1, 'granny', -1, gp)
    x, ph, f = walk_x([(0, 150), (8, 700)], u, s=2.0) if u < 13 else walk_x([(14, 700), (22, 120)], u, s=2.0)
    if u >= 13 and u < 14: x, ph, f = 700, None, 1
    fr = ctx.fig(x, FEET, 2.0, 'farmer', 1 if u < 13.5 else -1, dict(walk=ph, arm_f=(lerp(70, 85, put), 80) if u < 11 else (20, 20), arm_b=(60, 80) if u < 11 else (15, 20),
                 eyes='happy' if u > 10 else 'open', mouth='smile', lean=lerp(0, 18, put) * (u < 12)), seed=72)
    if fr and u < 10.5:
        hx, hy = fr['hand_f']; wx, wy = hx / ctx.z + ctx.left, hy / ctx.z + ctx.top
        big_jar(ctx, wx + 8, wy + 60, 0.9, W_SUN, 0.05, seed=961)
    elif u >= 10.5:
        big_jar(ctx, 860, COUNTER[2], 0.9, W_SUN, 0.05, seed=961)

# ---------------------------------------------------------------- C: the ferry on full water; goodbye on the steps
T_C = 50.0
FERRY_X = 1300
GIVE = T_C + 34

def drawC(ctx, lt):
    T = ctx.Tabs; u = T - T_C
    town_live(ctx, rain_amt=0.0, water=1.0, color=1.0, look=0.4, jars_glow=0.25)
    leaves(ctx, T, 14)
    deck = sampan(ctx, FERRY_X, WATER_Y + 52, 1.0, seed=611)
    fm = ctx.fig(deck[0], deck[1], 1.0, 'ferryman', 1, dict(arm_f=(150, -30), arm_b=(120, -10), lean=12, bob=False, look=-4), seed=31)
    if fm: pole(ctx, fm['hand_f'], 10, ctx.z)
    take = ramp(T, GIVE, GIVE + 1.5)
    hold = ramp(T, GIVE + 1.0, GIVE + 2.2)
    gp = dict(look=10 if u < 4 else 8, arm_f=(lerp(20, 70, take), lerp(40, 20, take)), arm_b=(lerp(15, 60, hold), 30),
              eyes='closed' if 24 < u < 25.5 else 'open', mouth='smile' if 6 < u < 12 else 'flat')
    g = ctx.fig(1700, Q, 1.12, 'granny', -1, gp, seed=11)
    xp = dict(backpack=1, look=-6, eyes='happy' if 12 < u < 18 else 'open', mouth='smile' if 12 < u < 20 else 'flat',
              arm_f=(lerp(10, 60, hold), lerp(20, 70, hold)), arm_b=(lerp(10, 55, hold), lerp(20, 70, hold)))
    xm = ctx.fig(1620, Q, 0.95, 'xiaoman', 1, xp, seed=12)
    ctx.baozi(1560, Q - 205 + 6 * math.sin(T * 2), 0.9, 'calm')
    if T > GIVE - 2 and g and xm:
        a = g['hand_f']; b = xm['hand_f']
        p = (lerp(a[0], b[0], take), lerp(a[1], b[1], take))
        small_jar(ctx, p, ctx.z * 1.0, W_DRIZZLE, 0.35, s=0.45)

# ---------------------------------------------------------------- D: the ferry pulls away; she doesn't wave... then waves with both arms
T_D = 106.0
def boat_out(T): return FERRY_X - 900 * ease((T - T_D - 2) / 34) ** 1.1

def ink_wings(ctx, x, y, s, open_, T):
    """Old Ink spreads his wings on the post"""
    if open_ <= 0: return
    sx, sy = ctx.T(x, y); se = s * ctx.z
    L = ctx.layer(sx - 160 * se, sy - 140 * se, sx + 160 * se, sy + 40 * se)
    flap = 6 * math.sin(T * 2.5) * open_
    for k in (-1, 1):
        tip = (sx + k * 120 * se * open_, sy - (60 + flap) * se)
        poly = [(sx + k * 6 * se, sy - 70 * se), (sx + k * 50 * se * open_, sy - (100 + flap) * se), tip,
                (sx + k * 90 * se * open_, sy - 40 * se), (sx + k * 50 * se * open_, sy - 30 * se), (sx + k * 8 * se, sy - 34 * se)]
        fill(L, poly, 0.82, s=se, seed=1500 + k, gran=0.5)
        for f in range(4):
            fx = sx + k * (70 + f * 14) * se * open_
            line(L, [(fx, sy - (50 + f * 4) * se), (fx + k * 6 * se, sy - (34 + f * 2) * se)], 1.2, se, 0.8, 0.2, 1510 + f + k)

def drawD(ctx, lt):
    T = ctx.Tabs; u = T - T_D
    town_live(ctx, rain_amt=0.0, water=1.0, color=1.0, look=0.0 if u < 27 else 0.6, cormorant=True, jars_glow=0.25)
    new_sign(ctx)
    leaves(ctx, T, 14)
    bx = boat_out(T)
    ferry(ctx, bx, xm_pose=dict(look=8, arm_f=(lerp(20, 160, ramp(u, 26, 27)), 20 + 10 * math.sin(T * 6) * (u > 27)), mouth='open' if u > 27 else 'flat', eyes='happy' if u > 28 else 'open'))
    ctx.baozi(bx - 70, WATER_Y - 160 + 6 * math.sin(T * 2), 0.9, 'happy')
    wave = ramp(u, 24.5, 26)
    sw = math.sin(T * 5)
    g = ctx.fig(1700, Q, 1.12, 'granny', -1, dict(look=-2 if u < 24 else -8, arm_f=(lerp(20, 155 + 15 * sw, wave), 20), arm_b=(lerp(15, 150 - 15 * sw, wave), 20),
                eyes='happy' if u > 26 else 'open', mouth='open' if u > 25.5 else 'flat', lean=-4 * wave), seed=11)
    if 0 < u: small_jar(ctx, ctx.T(bx - 40, WATER_Y + 12), ctx.z, W_DRIZZLE, 0.25, s=0.40)
    ink_wings(ctx, 2092, WATER_Y - 62, 1.0, ramp(u, 27, 28.5), T)

# ---------------------------------------------------------------- E: the city; he opens the jar; rain on Willow Bend's tiles; Baozi; three drops
T_E = 150.0
OPEN = T_E + 12

def drawE(ctx, lt):
    T = ctx.Tabs; u = T - T_E
    city_live(ctx, 1.0)
    opened = ramp(T, OPEN, OPEN + 1.5)
    if opened > 0:     # the warm light of the jar and of the shop it remembers
        ctx.add_glow(960, 520, 260, 0.20 * opened, W_WARM, world=False)
    xp = dict(look=10 if u < 8 else 16, eyes='closed' if OPEN + 4 < T < OPEN + 7 else ('happy' if T > OPEN + 18 else 'open'),
              mouth='smile' if T > OPEN + 16 else 'flat', arm_f=(70, 70), arm_b=(65, 75))
    r = ctx.fig(960, 890, 2.6, 'xiaoman', 1, xp, seed=12)
    if r:
        hx, hy = r['hand_f']
        small_jar(ctx, (hx, hy), ctx.z * 2.6, W_DRIZZLE, 0.15 + 0.2 * opened, s=0.45)
        if opened > 0:
            b = ramp(T, OPEN + 2, OPEN + 6)
            bx = hx + 40 * b; by = hy - 60 - 230 * b + 8 * math.sin(T * 2)
            if b > 0: ctx.baozi(bx / ctx.z + ctx.left, by / ctx.z + ctx.top, 1.7 * min(1, b * 1.4), 'happy')
            hd = r['head']
            for k in range(3):     # three drops on his nose
                t0 = OPEN + 9 + k * 1.6
                if t0 < T < t0 + 0.7:
                    v = (T - t0) / 0.7
                    ctx.add_glow(lerp(bx, hd[0] + 22, v), lerp(by + 40, hd[1] + 8, v), 7, 0.9, W_DRIZZLE, world=False)
                elif t0 + 0.7 <= T < t0 + 1.2:
                    ctx.add_glow(hd[0] + 22, hd[1] + 8, 9, 0.6 * (1 - (T - t0 - 0.7) / 0.5), W_DRIZZLE, world=False)

def gradeE(lt):
    a = ramp(lt, 12, 16)
    return tuple(lerp(c0, c1, a) for c0, c1 in zip(CITYG, (0.86, 0.92, 1.00)))

# ---------------------------------------------------------------- F: credits over hand-scroll paintings in colour
T_F = 190.0
CREDITS = [
    (2.0, 11.0, [('雨铺', 'The Rain Shop')], 120, 40),
    (12.0, 21.0, [('婆婆　小满　包子　老墨', 'Granny · Xiaoman · Baozi · Old Ink')], 56, 30),
    (22.0, 31.0, [('故事　画　音乐', 'Story · Pictures · Music'), ('Claude', 'made in code, frame by frame')], 52, 30),
    (32.0, 41.0, [('为 bear 而作', 'Made for bear')], 64, 34),
    (42.0, 49.0, [('借天气，记得还', 'Borrow weather. Remember to bring it back.')], 60, 32),
]

_halo = {}
def credits_post(base):
    def post(img, lt, ctx):
        T = ctx.Tabs - T_F
        for (a, b, lines, fz, fe) in CREDITS:
            if a - 1 < T < b + 1:
                k = min(ease((T - a) / 1.0), ease((b - T) / 1.0))
                if k > 0:
                    m0 = card(lines, fz, fe)
                    key = (tuple(lines), fz, fe)
                    if key not in _halo:
                        h = cv2.GaussianBlur(cv2.dilate(m0, np.ones((15, 15), np.uint8)), (0, 0), 28)
                        _halo[key] = np.clip(h / max(1e-3, h.max()) * 1.6, 0, 1)
                    h = _halo[key] * k * 0.75
                    img = img * (1 - h[..., None]) + np.array([0.90, 0.93, 0.95], np.float32) * h[..., None]
                    img = ink_over(img, m0 * k, 0.88)
        return img
    return post

def drawF_town(ctx, lt):
    town_autumn(ctx, leaves_on=True)
    T = ctx.Tabs
    for i, (who, x) in enumerate([('mother', 600), ('farmer', 900), ('twin', 1180), ('twin', 1240), ('poet', 1420), ('bride', 2300)]):
        ctx.fig(x + 20 * math.sin(T * 0.3 + i), Q, 0.85 if who == 'twin' else 1.0, who, 1 if i % 2 else -1, dict(walk=T * 1.5 + i if who == 'twin' else None, eyes='happy', mouth='smile'),
                seed=60 + i, spec=TWIN_B if (who == 'twin' and i == 3) else None)

def drawF_lane(ctx, lt):
    laundry(ctx, 0.3)
    leaves(ctx, ctx.Tabs, 12)

def drawF_bridge(ctx, lt):
    leaves(ctx, ctx.Tabs, 12)

shots = [
    # A · 0  autumn; the sign
    dict(dur=14, set=TOWN, cam=lambda lt: (lerp(900, 1500, ease(lt / 14)), 402, 1.0), draw=drawA, args=dict(color=1.0, mist=0.4), grade=AUTUMN, fade_in=(2.0, (0.96, 0.96, 0.96))),
    dict(dur=12, set=TOWN, cam=camkf([(0, (1900, 470, 2.4)), (12, (1930, 470, 2.6))]), draw=drawA, args=dict(color=1.0, mist=0.4), grade=AUTUMN),
    # B · 26  inside
    dict(dur=24, set=SHOP, cam=camkf([(0, (900, 402, 1.0)), (24, (900, 410, 1.12))]), draw=drawB, grade=AUTUMN, xfade=1.0),
    # C · 50  the ferry on full water; goodbye
    dict(dur=12, set=TOWN, cam=camkf([(0, (1500, 402, 1.0)), (12, (1620, 440, 1.4))]), draw=drawC, args=dict(color=1.0, mist=0.3), grade=AUTUMN, xfade=1.2),
    dict(dur=8, set=TOWN, cam=(1690, 470, 2.6), draw=drawC, args=dict(color=1.0, mist=0.3), grade=AUTUMN),       # 62 "Your mother says..."
    dict(dur=8, set=TOWN, cam=(1625, 490, 2.9), draw=drawC, args=dict(color=1.0, mist=0.3), grade=AUTUMN),       # 70 "I can catch weather."
    dict(dur=12, set=TOWN, cam=camkf([(0, (1665, 490, 2.4)), (12, (1665, 495, 2.7))]), draw=drawC, args=dict(color=1.0, mist=0.3), grade=AUTUMN),   # 78 the jar
    dict(dur=16, set=TOWN, cam=(1690, 470, 2.7), draw=drawC, args=dict(color=1.0, mist=0.3), grade=AUTUMN),      # 90 "Open it when you miss me."
    # D · 106  the ferry pulls away
    dict(dur=14, set=TOWN, cam=camkf([(0, (1450, 430, 1.4)), (14, (1300, 410, 1.2))]), draw=drawD, args=dict(color=1.0, mist=0.3), grade=AUTUMN),
    dict(dur=10, set=TOWN, cam=camkf([(0, (1700, 480, 2.3)), (10, (1700, 480, 2.4))]), draw=drawD, args=dict(color=1.0, mist=0.3), grade=AUTUMN),   # 120 she does not wave
    dict(dur=10, set=TOWN, cam=camkf([(0, (1750, 450, 1.7)), (10, (1800, 440, 1.6))]), draw=drawD, args=dict(color=1.0, mist=0.3), grade=AUTUMN),   # 130 both arms; Old Ink's wings
    dict(dur=10, set=TOWN, cam=camkf([(0, (1350, 402, 1.0)), (10, (1350, 402, 1.0))]), draw=drawD, args=dict(color=1.0, mist=0.5), grade=AUTUMN, fade_out=(1.5, (0.6, 0.6, 0.62))),
    # E · 150  the city window
    dict(dur=40, set=CITY, cam=camkf([(0, (960, 402, 1.0)), (40, (960, 420, 1.1))]), draw=drawE, grade=gradeE, fade_in=(1.5, (0.6, 0.6, 0.62)), fade_out=(2.0, (0.96, 0.96, 0.96))),
    # F · 190  credits: the hand-scroll
    dict(dur=20, set=TOWN, cam=lambda lt: (lerp(960, 1740, lt / 20), 402, 1.0), draw=drawF_town, args=dict(color=1.0, mist=0.6), grade=AUTUMN, post=credits_post(0), fade_in=(2.0, (0.96, 0.96, 0.96))),
    dict(dur=14, set=LANE, cam=lambda lt: (lerp(1200, 2400, lt / 14), 402, 1.0), draw=drawF_lane, grade=AUTUMN, post=credits_post(0), xfade=2.0),
    dict(dur=16, set=BRIDGE, cam=lambda lt: (lerp(1000, 1800, lt / 16), 402, 1.0), draw=drawF_bridge, args=dict(water=1.0), grade=AUTUMN, post=credits_post(0), xfade=2.0,
         fade_out=(3.0, (0, 0, 0))),
]

subs = [
    (14.5, 24.0, '雨铺　婆婆与小满', 'The Rain Shop · Granny & Xiaoman', 'sign'),
    (30.0, 38.0, '借天气，记得还', 'Borrow weather. Remember to bring it back.', 'sign'),
    (63.0, '你妈说你会洗碗。', 'Your mother says you can wash dishes.', 'granny'),
    (71.0, '我会捉天气。', 'I can catch weather.', 'xiaoman'),
    (92.0, '想我的时候，再打开。', 'Open it when you miss me.', 'granny'),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 23)
    # autumn morning
    m.wind(0, 50, 0.015, 300, 1500); m.birds(0, 26, 0.02)
    for k in range(10): m.sweep(2 + k * 1.45, 0.04)
    m.pad(0, 50, [55, 62, 67, 71], 0.025)
    m.zheng_phrase(2, [67, 71, 74, 79, 74, 71, 67, None] * 4, 0.8, 0.06, 0.45)
    m.melody(16, [(74, 2.0), (76, 1.0), (79, 3.0), (None, 1.0), (81, 1.0), (79, 2.0), (76, 2.0), (74, 4.0)], 'dizi', 0.05)
    m.steps(26, 34, 2.2, 0.04); m.knock(36.6, 0.08); m.steps(40, 48, 2.2, 0.04)
    m.add(m.bell(note(79), 4, 0.04), 37)
    # goodbye on the steps
    m.oar(50, 0.06)
    m.pad(50, 56, [50, 57, 62], 0.025)
    m.melody(56, [(62, 3.0), (64, 1.0), (66, 2.0), (69, 4.0), (None, 3.0), (66, 2.0), (64, 2.0), (62, 6.0)], 'erhu', 0.04)
    m.giggle(63.5, 1.2, 0.03)
    m.add(m.guzheng(note(69), 5, 0.08), GIVE)
    m.melody(93, [(69, 2.0), (71, 1.0), (74, 3.0), (None, 1.0), (76, 2.0), (74, 2.0), (69, 4.0)], 'erhu', 0.05)
    # the ferry pulls away
    for k in range(9): m.oar(T_D + 2 + k * 3.6, 0.08 - k * 0.006)
    m.pad(106, 44, [45, 52, 57, 61], 0.03)
    m.melody(110, [(69, 4.0), (67, 2.0), (64, 2.0), (62, 6.0)], 'erhu', 0.05)
    m.squawk(T_D + 27.5, 0.10); m.whoosh(T_D + 27.6, 0.8, 0.05)
    m.zheng_phrase(T_D + 25, [62, 66, 69, 74, 76, 74, 69, 66, 62, None] * 2, 0.45, 0.07, 0.5)
    m.melody(T_D + 29, [(74, 2.0), (76, 1.0), (78, 1.0), (81, 4.0), (78, 2.0), (76, 2.0), (74, 6.0)], 'dizi', 0.06)
    # the city: traffic hum and rain on glass, then the rain of Willow Bend's tiles
    m.rumble(150, 12, 0.05, 55)
    m.rain([(150, 0.15), (OPEN, 0.15), (OPEN + 1.5, 0.6), (188, 0.6), (192, 0.0)], heavy=0.6)
    m.drips(OPEN + 1, 188, 2.0, 0.05)
    m.add(m.chime(note(93), 0.06), OPEN + 0.5)
    m.giggle(OPEN + 5, 2.0, 0.04)
    for k in range(3): m.drip(OPEN + 9.7 + k * 1.6, 0.12, 1000 + 120 * k)
    m.melody(OPEN + 14, [(74, 2.0), (76, 1.0), (79, 2.0), (81, 4.0), (79, 2.0), (76, 2.0), (74, 6.0)], 'dizi', 0.05)
    m.pad(OPEN + 2, 26, [50, 57, 62, 66], 0.03)
    # credits: the main theme, full
    m.pad(190, 50, [55, 62, 67, 71, 74], 0.035)
    m.zheng_phrase(190, [67, 71, 74, 79, 74, 71, 67, None] * 8, 0.75, 0.07, 0.45)
    m.melody(194, [(79, 2.0), (81, 1.0), (83, 1.0), (86, 3.0), (83, 1.0), (81, 2.0), (79, 4.0), (None, 1.0), (81, 1.0), (83, 2.0), (86, 2.0), (88, 6.0),
                   (86, 2.0), (83, 2.0), (81, 2.0), (79, 8.0)], 'dizi', 0.06)
    m.melody(214, [(67, 4.0), (71, 2.0), (74, 4.0), (72, 2.0), (71, 4.0), (67, 8.0)], 'erhu', 0.04)
    m.add(m.gong(8, 0.12, 70), 232)
    m.write(fn, 1.5, 4.0)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
