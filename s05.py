# Scene 5 · No More Rain · 不再下雨  (18:00 - 23:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_shop import SHOP, shop_live, FEET, ALTAR, red_jar
from s01 import named_jars, Q

HOT = (0.80, 0.93, 1.04)           # BGR: dry, bleached, warm
NIGHT = (0.55, 0.47, 0.44)
MUD_Y = 700                        # where feet stand on the dry canal bed
GROOM = dict(top=(0.10, (0.30, 0.36, 0.82), 0.85), extras=())

def heat(img, lt, ctx, amp=1.6):
    """heat shimmer: the air above the hot stones wobbles"""
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    k = (1 - yy / h) * 0.5 + 0.5
    dx = np.sin(yy * 0.045 + lt * 5.0 + np.sin(xx * 0.01) * 2) * amp * k
    dy = np.sin(xx * 0.03 + lt * 3.7) * amp * 0.4 * k
    return cv2.remap(img, xx + dx, yy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def post_days(lines, t_in, t_out):
    cp = chapter_post(lines, t_in, t_out, 96, 40)
    return lambda img, lt, ctx: cp(heat(img, lt, ctx), lt, ctx)

# ---------------------------------------------------------------- A: the time-lapse, Day 7 / 30 / 45
def drawA(ctx, lt):
    w = ctx.args['water']
    town_live(ctx, 0.0, False, True, False, jars_glow=0.25, water=w)

def water_args(w0, w1, d):
    return lambda lt: dict(water=lerp(w0, w1, ease(lt / d)), sun=1.0, mist=0.0)

# ---------------------------------------------------------------- B: the queue in the heat
QUEUE = [('farmer', 1760, 1.05, None), ('mother', 1860, 1.0, None), ('porter', 1950, 1.0, None), ('poet', 2040, 1.0, None),
         ('twin', 2120, 0.9, None), ('twin', 2165, 0.9, TWIN_B), ('farmer', 2240, 1.0, dict(top=(0.12, (0.62, 0.70, 0.80), 0.6))),
         ('mother', 2320, 1.0, dict(top=(0.10, (0.60, 0.66, 0.72), 0.6))), ('porter', 2400, 1.0, dict(top=(0.20, (0.70, 0.75, 0.80), 0.6)))]
GX = 1660

def queue(ctx, T, shift=0.0, first_gone=False, fans=True):
    for i, (who, x, s, spec) in enumerate(QUEUE):
        if first_gone and i == 0: continue
        xx = x - shift * (90 if i > 0 else 0)
        bob = math.sin(T * 0.7 + i * 1.7)
        p = dict(look=-4 + 3 * bob, arm_f=(20, 30), eyes='closed' if int(T * 0.9 + i * 3) % 9 == 0 else 'open')
        if fans and i in (1, 3, 7):
            p['arm_f'] = (100 + 12 * math.sin(T * 6 + i), 60)
        r = ctx.fig(xx, Q, s, who, -1, p, seed=20 + i, spec=spec, talker='farmer' if i == 0 else 'q%d' % i)
        if r and fans and i in (1, 3, 7): fan(ctx, r['hand_f'], -40 + 25 * math.sin(T * 6 + i), 0.9 * ctx.z)

def granny_door(ctx, T, give=0.0, pose=None):
    p = dict(arm_f=(lerp(20, 85, give), lerp(30, 0, give)), arm_b=(15, 25), look=4, mouth='flat')
    p.update(pose or {})
    return ctx.fig(GX, Q, 1.12, 'granny', 1, p)

def xm_helper(ctx, T, x=1600, pose=None):
    p = dict(arm_f=(60, 70), arm_b=(30, 40), look=6, mouth='flat')
    p.update(pose or {})
    r = ctx.fig(x, Q, 0.95, 'xiaoman', 1, p)
    return r

T_B = 40.0
def drawB(ctx, lt):
    T = ctx.Tabs; u = T - T_B
    town_live(ctx, 0.0, False, True, False, jars_glow=0.2, water=0.0)
    give = ease((u - 21) / 1.2) * (1 - ease((u - 26) / 1.0))
    gone = u > 27
    r = granny_door(ctx, T, give, dict(eyes='closed' if 16.2 < u < 17.0 else 'open'))
    if r and 20 < u < 26.5:
        small_jar(ctx, r['hand_f'], 1.12 * ctx.z, W_DRIZZLE, 0.5)
        if u > 22: small_jar(ctx, (r['hand_f'][0] + 16 * ctx.z, r['hand_f'][1] + 4 * ctx.z), 1.12 * ctx.z, W_DRIZZLE, 0.5)
    xm_helper(ctx, T)
    shift = ease((u - 30) / 2.0)
    queue(ctx, T, shift, first_gone=gone)
    if gone:      # the farmer hurries away hugging the two little jars
        x, ph, f = walk_x([(27, 1760), (40, 900)], u, s=1.05)
        rr = ctx.fig(x, Q, 1.05, 'farmer', f, dict(walk=ph, arm_f=(40, 85), arm_b=(30, 80), look=6, mouth='smile'), seed=20)
        if rr:
            small_jar(ctx, rr['hand_f'], 1.05 * ctx.z, W_DRIZZLE, 0.45)
            small_jar(ctx, (rr['hand_f'][0] - 14 * ctx.z, rr['hand_f'][1] + 2 * ctx.z), 1.05 * ctx.z, W_DRIZZLE, 0.45)

def drawB4(ctx, lt):     # Old Ink pants on his post above the cracked mud
    T = ctx.Tabs
    town_live(ctx, 0.0, False, False, False, jars_glow=0.0, water=0.0, look=0.4 * math.sin(T * 0.5))

# ---------------------------------------------------------------- C: counting the shelves at night
T_C = 100.0
def drawC(ctx, lt):
    T = ctx.Tabs; u = T - T_C
    shop_live(ctx, glow=0.7, night=0.4, empty=0.78, red=True, giggle=False, rain_door=0.0)
    named_jars(ctx, 0.5, skip=('梅雨', '虎丘雷'))
    x, ph, f = walk_x([(0, 560), (6, 760), (8, 760), (13, 1060), (15, 1060), (21, 1440), (22, 1500)], u, stride=26, s=1.9)
    if u > 22: f = 1
    look = -16 if ph is None else -6
    if u > 23: look = 6
    r = ctx.fig(x, FEET, 1.9, 'xiaoman', f, dict(walk=ph, arm_f=(95, 20), arm_b=(25, 40), look=look, mouth='open' if ph is None and int(T * 3) % 2 else 'flat'), over=True)
    if r: lantern(ctx, r['hand_f'], 1.9 * ctx.z * 0.55, 1.0, T, over=True)
    # Granny by the altar, her back half turned
    gp = dict(arm_f=(30, 40), arm_b=(20, 40), look=(12 if u < 32 else 18), eyes='closed' if 33 < u < 36 else 'open')
    ctx.fig(1880, FEET - 20, 2.0, 'granny', -1 if u < 31 else 1, gp)
    ctx.add_glow(ALTAR[0] + 80, ALTAR[1] - 54, 5, 0.8, WARM)

# ---------------------------------------------------------------- D: the wedding in the heat, and the snow
T_D = 160.0
def wedding(ctx, T, snow_amt):
    u = T - T_D
    town_live(ctx, 0.0, False, True, False, jars_glow=0.2, water=0.0)
    look_up = ease((u - 29) / 1.5) if u > 29 else 0.0
    dance = u > 32
    # red lanterns strung along the eave
    for k, lx in enumerate(range(1300, 2060, 95)):
        ly = 470 + 10 * math.sin(k * 1.3)
        sx, sy = ctx.T(lx, ly); L = ctx.box(lx, ly + 12, 16, 22)
        body = [(sx + 9 * ctx.z * math.cos(q), sy + 13 * ctx.z * math.sin(q) + 12 * ctx.z) for q in np.linspace(0, 2 * math.pi, 20)]
        fill(L, body, 0.04, VERMILION, 0.9, s=ctx.z, seed=900 + k, edge=0.5)
    # guests
    guests = [('mother', 1380, 1.0, None), ('poet', 1460, 1.02, None), ('farmer', 1990, 1.0, None), ('twin', 2070, 0.9, None), ('twin', 2110, 0.9, TWIN_B), ('porter', 2190, 1.0, None)]
    for i, (who, x, s, spec) in enumerate(guests):
        lk = lerp(-4, -24, look_up)
        p = dict(look=lk, arm_f=(lerp(20, 60 + 30 * math.sin(T * 2 + i), look_up), lerp(30, 0, look_up)), mouth='open' if look_up > 0.5 else 'smile', eyes='wide' if 0.3 < look_up and u < 40 else 'happy' if u > 40 else 'open')
        if who == 'twin' and dance: p['bob'] = abs(math.sin(T * 4 + i)) * 8
        if not look_up and i in (0, 5):
            p['arm_f'] = (100 + 12 * math.sin(T * 6 + i), 60)
        r = ctx.fig(x, Q, s, who, 1 if x < 1700 else -1, p, seed=40 + i, spec=spec)
        if r and not look_up and i in (0, 5): fan(ctx, r['hand_f'], -40 + 25 * math.sin(T * 6 + i), 0.9 * ctx.z)
    # bride and groom: limp in the heat, then a slow dance in the snow
    if dance:
        a = (T - T_D - 32) * 0.55
        bx = 1660 + math.sin(a) * 30; gx = 1745 + math.sin(a) * 30
        ctx.fig(bx, Q, 1.04, 'bride', 1, dict(arm_f=(90, 40), arm_b=(60, 50), eyes='happy', mouth='smile', look=-14, bob=abs(math.sin(a * 2)) * 4), seed=61)
        ctx.fig(gx, Q, 1.06, 'poet', -1, dict(arm_f=(90, 40), arm_b=(60, 50), eyes='happy', mouth='smile', look=-14, bob=abs(math.sin(a * 2 + 1)) * 4), seed=62, spec=GROOM)
    else:
        ctx.fig(1660, Q, 1.04, 'bride', 1, dict(arm_f=(10, 10), look=lerp(6, -24, look_up), lean=4 * (1 - look_up), mouth='flat' if not look_up else 'open', eyes='wide' if look_up else 'open'), seed=61)
        ctx.fig(1740, Q, 1.06, 'poet', -1, dict(arm_f=(10, 10), look=lerp(6, -24, look_up), lean=4 * (1 - look_up), mouth='flat'), seed=62, spec=GROOM)
    # Granny and Xiaoman at the side, by the shop door
    open_ = ease((u - 23) / 1.5)
    down = 1 - ease((u - 30) / 1.5)
    gp = dict(arm_f=(lerp(20, 95, ease((u - 14) / 1.5) * down), lerp(30, -20, open_ * down)), arm_b=(lerp(15, 80, ease((u - 18) / 1) * down), lerp(25, -10, open_ * down)),
              look=lerp(4, -20, look_up), mouth='smile' if 58 < u < 67 else 'flat', eyes='happy' if 59.5 < u < 65 else 'open')
    r = ctx.fig(1560, Q, 1.12, 'granny', 1, gp)
    if r and 14 < u < 30:
        small_jar(ctx, r['hand_f'], 1.12 * ctx.z, W_SNOW, 0.5 + 0.4 * open_, s=0.4)
        if open_ > 0:    # the seal lifts and a thin white wisp climbs out
            top = (r['hand_f'][0], r['hand_f'][1] - 14 * ctx.z)
            pts = [(top[0] + math.sin(k * 0.6 + T * 2) * 8 * ctx.z, top[1] - k * 22 * ctx.z * open_) for k in range(14)]
            wisp(ctx, pts, open_ * (1 - ease((u - 28) / 2)), W_SNOW, 5 * ctx.z, world=False, t=T)
    ctx.fig(1500, Q, 0.95, 'xiaoman', 1, dict(look=lerp(4, -22, look_up) if not (50 < u < 64) else 10, arm_f=(20, 30), eyes='wide' if 29 < u < 34 else 'open', mouth='open' if 29 < u < 33 else 'flat'))
    if snow_amt > 0: snow(ctx, snow_amt)

def drawD(ctx, lt):
    T = ctx.Tabs
    amt = ease((T - T_D - 25) / 4) * (1 - ease((T - T_D - 68) / 6))
    wedding(ctx, T, amt * 0.9)

# ---------------------------------------------------------------- E: the ferryman on the mud; dusk
T_E = 240.0
def drawE(ctx, lt):
    T = ctx.Tabs; u = T - T_E
    town_live(ctx, 0.0, False, True, False, jars_glow=0.2, water=0.0)
    push = math.sin(min(u, 14) * 1.6) if 8 < u < 16 else 0
    x, ph, f = walk_x([(0, 700), (7, 1050)], u, stride=40, s=1.2)
    r = ctx.fig(x if u < 7 else 1050 + 4 * push, MUD_Y, 1.2, 'ferryman', 1, dict(walk=ph, arm_f=(70 + 20 * push, 30), arm_b=(60 + 20 * push, 30), lean=10 + 12 * max(0, push),
              mouth='flat', eyes='closed' if 17 < u < 19 else 'open', look=-6 if u > 22 else 4), talker='ferryman')
    if r:
        if u < 8: stick(ctx, r['hand_f'], 150, 230, 1.2 * ctx.z, w=3, seed=611)
        elif u < 18: pole(ctx, r['hand_f'], 40, 1.2 * ctx.z)
        else: stick(ctx, (r['hand_f'][0] + 20 * ctx.z, r['hand_f'][1]), 175, 230, 1.2 * ctx.z, w=3, seed=611)
    ctx.fig(1300, Q, 0.95, 'xiaoman', -1, dict(look=14, arm_f=(15, 20), mouth='frown' if u > 24 else 'flat'))

def drawF(ctx, lt):      # dusk: Granny comes and stands with him; the red sun goes down
    T = ctx.Tabs; u = lt
    town_live(ctx, 0.0, False, True, False, jars_glow=0.25 + 0.3 * ease(u / 30), water=0.0, night=0.4 * ease((u - 20) / 15))
    ctx.fig(1520, Q, 0.95, 'xiaoman', -1, dict(look=-2, arm_f=(15, 20)))
    x, ph, f = walk_x([(6, 1720), (14, 1570)], u, stride=30, s=1.12)
    arm = ease((u - 17) / 1.5)
    ctx.fig(x, Q, 1.12, 'granny', f if ph is not None else -1, dict(walk=ph, arm_f=(lerp(15, 70, arm), lerp(25, 60, arm)), arm_b=(20, 40), look=-2))

def dusk(lt):
    u = ease(lt / 26)
    return (lerp(0.80, 0.55, u), lerp(0.93, 0.62, u), lerp(1.04, 0.95, u))

shots = [
    # A · 0  the town bakes; the canal sinks day by day
    dict(dur=13, set=TOWN, cam=camkf([(0, (1100, 402, 1.0)), (13, (1350, 402, 1.0))]), draw=drawA, args=water_args(1.0, 0.7, 13), grade=HOT,
         post=post_days([('第七天', 'Day 7')], 3.0, 10.0), fade_in=(1.5, (1, 1, 1))),
    dict(dur=13, set=TOWN, cam=camkf([(0, (1350, 402, 1.0)), (13, (1600, 402, 1.0))]), draw=drawA, args=water_args(0.7, 0.3, 13), grade=HOT,
         post=post_days([('第三十天', 'Day 30')], 3.0, 10.0), xfade=1.2),
    dict(dur=14, set=TOWN, cam=camkf([(0, (1150, 470, 1.35)), (14, (1180, 480, 1.5))]), draw=drawA, args=water_args(0.3, 0.0, 9), grade=HOT,
         post=post_days([('第四十五天', 'Day 45')], 4.0, 11.0), xfade=1.2),
    # B · 40  a queue outside the Rain Shop
    dict(dur=14, set=TOWN, cam=camkf([(0, (2250, 430, 1.25)), (14, (1900, 440, 1.4))]), draw=drawB, args=dict(sun=1.0, mist=0.0, water=0.0), grade=HOT, post=heat, xfade=1.0),
    dict(dur=12, set=TOWN, cam=camkf([(0, (1700, 470, 2.3)), (12, (1705, 475, 2.45))]), draw=drawB, args=dict(sun=1.0, mist=0.0, water=0.0), grade=HOT, post=heat),
    dict(dur=14, set=TOWN, cam=camkf([(0, (1600, 440, 1.4)), (14, (1450, 440, 1.3))]), draw=drawB, args=dict(sun=1.0, mist=0.0, water=0.0), grade=HOT, post=heat),
    dict(dur=20, set=TOWN, cam=camkf([(0, (2092, 520, 2.4)), (20, (2092, 500, 2.7))]), draw=drawB4, args=dict(sun=1.0, mist=0.0, water=0.0), grade=HOT, post=heat,
         fade_out=(2.5, (0, 0, 0))),
    # C · 100  night, counting the shelves with a lantern
    dict(dur=22, set=SHOP, cam=camkf([(0, (700, 400, 1.6)), (22, (1450, 410, 1.6))]), draw=drawC, grade=NIGHT, fade_in=(2.0, (0, 0, 0))),
    dict(dur=10, set=SHOP, cam=camkf([(0, (1680, 450, 1.5)), (10, (1690, 455, 1.55))]), draw=drawC, grade=NIGHT),
    dict(dur=8, set=SHOP, cam=(1890, 470, 2.6), draw=drawC, grade=NIGHT),
    dict(dur=20, set=SHOP, cam=camkf([(0, (1520, 440, 2.2)), (20, (1300, 402, 1.05))]), draw=drawC, grade=NIGHT, fade_out=(3.0, (0, 0, 0))),
    # D · 160  the wedding in the heat; snow for one dance
    dict(dur=14, set=TOWN, cam=camkf([(0, (1640, 440, 1.35)), (14, (1660, 445, 1.45))]), draw=drawD, args=dict(sun=1.0, mist=0.0, water=0.0), grade=HOT, post=heat, fade_in=(1.5, (0, 0, 0))),
    dict(dur=8, set=TOWN, cam=(1580, 480, 2.6), draw=drawD, args=dict(sun=1.0, mist=0.0, water=0.0), grade=HOT, post=heat),
    dict(dur=7, set=TOWN, cam=camkf([(0, (1585, 470, 3.6)), (7, (1585, 440, 3.2))]), draw=drawD, args=dict(sun=1.0, mist=0.0, water=0.0), grade=HOT),
    dict(dur=23, set=TOWN, cam=camkf([(0, (1660, 430, 1.4)), (23, (1680, 420, 1.25))]), draw=drawD, args=dict(sun=0.5, mist=0.0, water=0.0), grade=(0.95, 0.97, 1.0), xfade=1.0),
    dict(dur=6, set=TOWN, cam=(1500, 480, 2.8), draw=drawD, args=dict(sun=0.5, mist=0.0, water=0.0), grade=(0.95, 0.97, 1.0)),
    dict(dur=8, set=TOWN, cam=(1565, 470, 3.0), draw=drawD, args=dict(sun=0.5, mist=0.0, water=0.0), grade=(0.95, 0.97, 1.0)),
    dict(dur=4, set=TOWN, cam=(1500, 480, 2.8), draw=drawD, args=dict(sun=0.5, mist=0.0, water=0.0), grade=(0.95, 0.97, 1.0)),
    dict(dur=10, set=TOWN, cam=camkf([(0, (1660, 430, 1.3)), (10, (1640, 420, 1.2))]), draw=drawD, args=lambda lt: dict(sun=lerp(0.5, 1.0, ease(lt / 6)), mist=0.0, water=0.0),
         grade=lambda lt: tuple(lerp(a, b, ease(lt / 6)) for a, b in zip((0.95, 0.97, 1.0), HOT)), post=lambda img, lt, ctx: heat(img, lt, ctx, 1.6 * ease(lt / 6))),
    # E · 230  the ferryman can't come any more
    dict(dur=22, set=TOWN, cam=camkf([(0, (900, 520, 1.6)), (22, (1080, 530, 1.75))]), draw=drawE, args=dict(sun=1.0, mist=0.0, water=0.0), grade=HOT, post=heat, xfade=1.5),
    dict(dur=10, set=TOWN, cam=camkf([(0, (1180, 540, 1.9)), (10, (1190, 545, 1.95))]), draw=drawE, args=dict(sun=1.0, mist=0.0, water=0.0), grade=HOT, post=heat),
    dict(dur=28, set=TOWN, cam=camkf([(0, (1560, 470, 1.6)), (28, (1600, 402, 1.0))]), draw=drawF, args=dict(sun=1.0, mist=0.3, water=0.0), grade=dusk, post=heat,
         xfade=2.0, fade_out=(4.0, (0, 0, 0))),
]

subs = [
    (49.0, '秧苗快死了。', 'The seedlings are dying.', 'farmer'),
    (56.5, '拿两杯。别告诉别人。', "Take two cups. Don't tell anyone.", 'granny'),
    (123.5, '还剩四十一个。', 'Forty-one left.', 'xiaoman'),
    (128.0, '够了。', "That's enough.", 'granny'),
    (131.0, '够多久？', 'Enough for how long?', 'xiaoman'),
    (255.0, '船走不了了。', "The boat can't move.", 'ferryman'),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 15)
    # the drought: cicadas everywhere, a dry wind, a slow pulse of days
    m.cicadas(0, 100, 0.03); m.wind(0, 100, 0.02, 300, 1500)
    for k, at in enumerate([3.5, 16.5, 30.5]):
        m.add(m.gong(4, 0.12, 80), at); m.add(m.bell(note(69 - 3 * k), 3, 0.05), at + 0.3)
    m.pad(0, 40, [45, 52, 57], 0.022)
    m.melody(6, [(69, 2.0), (None, 1.0), (67, 1.0), (64, 3.0), (None, 2.0), (62, 2.0), (64, 4.0)], 'erhu', 0.035)
    m.crowd(40, 94, 0.012)
    m.steps(66, 78, 2.2, 0.03)
    m.add(m.woodblock(700, 0.05), 62.0); m.add(m.woodblock(760, 0.05), 63.2)
    m.squawk(88, 0.05)
    # night: crickets, lantern, counting
    m.crickets(100, 160, 0.022)
    m.steps(100, 122, 1.4, 0.02, True)
    for k in range(10): m.add(m.woodblock(1100, 0.012), 104 + k * 1.8)
    m.pad(100, 60, [38, 45], 0.025)
    m.add(m.guzheng(note(57), 5, 0.08), 134.5)
    m.melody(140, [(62, 3.0), (60, 2.0), (57, 6.0)], 'erhu', 0.035)
    # the wedding: thin suona-like dizi in the heat, then the snow hushes everything
    m.cicadas(160, 184, 0.03); m.crowd(160, 184, 0.015)
    m.melody(161, [(72, 0.5), (74, 0.5), (76, 1.0), (74, 0.5), (72, 0.5), (69, 1.5), (None, 1.0), (72, 0.5), (74, 0.5), (76, 1.5), (79, 2.0)], 'dizi', 0.05)
    m.add(m.chime(note(88), 0.05), 183.0); m.whoosh(183.8, 1.5, 0.05)
    m.gliss(185.0, 74, 98, 0.07, 0.06)
    m.zheng_phrase(189, [69, 72, 74, 76, 79, 76, 74, 72, 69, None, 72, 74, 76, None, 74, 72, 69, None, 67, 69], 0.7, 0.10, 0.5, 4.0)
    m.pad(189, 40, [57, 64, 69, 76], 0.03)
    m.crowd(195, 203, 0.012, cheer=True)
    m.melody(218, [(76, 2.0), (74, 1.0), (72, 3.0)], 'dizi', 0.04)
    m.cicadas(232, 300, 0.03); m.wind(232, 300, 0.02, 300, 1500)
    # the ferryman, the mud
    m.steps(240, 247, 1.6, 0.04)
    for at in (248.5, 250.2, 251.8, 253.4): m.creak(at, 0.06)
    m.melody(262, [(62, 3.0), (64, 1.0), (62, 2.0), (57, 4.0), (None, 2.0), (55, 2.0), (57, 6.0)], 'erhu', 0.04)
    m.steps(278, 286, 1.5, 0.025, True)
    m.pad(272, 28, [38, 45, 50], 0.025)
    m.add(m.gong(6, 0.12, 70), 294)
    m.write(fn, 1.0, 2.5)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
