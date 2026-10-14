# Scene 11 · Every Jar in the Shop · 所有的罐子  (47:00 - 52:00)
import sys, math
from kit import *
from sets_more import MUDFLAT, QIAN_BOAT, depth_s, MUD_HZ, SKY, SKY_W, SKY_H
from figure import dragon, dragon_spine
from s06 import BALD
from s09 import BLUE_MIST
from s10 import dragon_now, DX, DY, MUD_Y, flying_ink, bicycle

DAWN = (0.92, 0.88, 0.88)
MORN = (0.98, 0.96, 0.96)
WEATHERS = [W_DRIZZLE, W_SNOW, W_SUN, W_FOG, W_BREEZE, W_THUNDER]

def draw_spine(ctx, sp, T, s, strength=0.35, eye='calm', jaw=0.0, color=0.0, cols=None):
    x0, y0 = sp.min(0) - 160 * s; x1, y1 = sp.max(0) + 160 * s
    p0 = ctx.T(x0, y0); p1 = ctx.T(x1, y1)
    if p1[0] < 0 or p0[0] > OW or p1[1] < 0 or p0[1] > OH: return
    L = ctx.layer(max(-200, p0[0]), max(-200, p0[1]), min(OW + 200, p1[0]), min(OH + 200, p1[1]))
    spS = (sp - [ctx.left, ctx.top]) * ctx.z
    dragon(L, spS, T, s * ctx.z, strength, eye=eye, jaw=jaw)
    if color > 0 and cols:
        # the drunk weathers shimmer along its body in bands
        n = len(spS)
        for k, c in enumerate(cols):
            i0 = int(n * k / len(cols)); i1 = int(n * (k + 1) / len(cols))
            for i in range(i0, i1, 4):
                ctx.add_glow(spS[i][0], spS[i][1], 9 * s * ctx.z, 0.18 * color, c, world=False)

# ---------------------------------------------------------------- A/B: Granny arrives; "It's you... you're still so small."
def granny_mud(ctx, T, u, x=None, pose=None):
    s = depth_s(MUD_Y + 10)
    if x is None:
        x, ph, f = walk_x([(0, 700), (12, 1500)], u, stride=26, s=s)
    else: ph = None
    p = dict(walk=ph, arm_f=(60, 40), arm_b=(20, 30), lean=10 if ph is not None else 4, mouth='open' if ph is not None else 'flat', look=-6)
    p.update(pose or {})
    r = ctx.fig(x, MUD_Y + 10, s, 'granny', 1, p)
    if r and not (pose or {}).get('no_lantern'): lantern(ctx, r['hand_f'], s * ctx.z * 0.55, 0.6, T)
    return r

def xm_kneel(ctx, T, pose=None):
    p = dict(crouch=0.75, arm_f=(30, 30), arm_b=(20, 30), look=0)
    p.update(pose or {})
    return ctx.fig(1700, MUD_Y, depth_s(MUD_Y), 'xiaoman', 1, p)

def dragon_low(T, u, bow=0.0):
    sp = dragon_now(T, 80)       # the calm, head-lifted pose from the end of scene 10
    sp = sp.copy()
    n = len(sp)
    for i in range(n // 3):      # lower the head and neck toward Granny
        w = (1 - i / (n / 3)) ** 1.5
        sp[i, 1] += 60 * bow * w; sp[i, 0] -= 40 * bow * w
    return sp

def drawA(ctx, lt):
    T = ctx.Tabs; u = T
    bow = ease((u - 8) / 4)
    draw_spine(ctx, dragon_low(T, u, bow), T, 1.6, 0.35, 'calm')
    granny_mud(ctx, T, u, pose=dict(eyes='wide' if 12 < u < 16 else 'open', mouth='open' if u < 12 else 'flat', lean=10 if u < 12 else 6))
    xm_kneel(ctx, T, dict(look=-12 if u > 8 else 0, mouth='open' if 23 < u < 28 else 'flat'))
    ctx.baozi(1780, MUD_Y - 230 + 8 * math.sin(T * 2), 1.3, 'happy')
    ctx.cormorant(1440, MUD_Y - 64, 0.9, look=0.3)

T_B = 40.0
def drawB(ctx, lt):
    T = ctx.Tabs; u = T - T_B
    draw_spine(ctx, dragon_low(T, u, 1.0), T, 1.6, 0.35, 'calm')
    granny_mud(ctx, T, u, x=1500, pose=dict(look=-14 if u < 12 else 0, eyes='closed' if 10 < u < 12.5 else 'open', mouth='flat', arm_f=(30, 40)))
    xm_kneel(ctx, T, dict(look=-12, crouch=0.75 * (1 - ease((u - 16) / 1.5)), eyes='wide' if u > 15 else 'open'))
    ctx.baozi(1780, MUD_Y - 230 + 8 * math.sin(T * 2), 1.3, 'happy')
    ctx.cormorant(1440, MUD_Y - 64, 0.9, look=0.3)

# ---------------------------------------------------------------- C: the whole town carries the jars across the mud
T_C = 62.0
CAST = [('farmer', None), ('bride', None), ('poet', None), ('mother', None), ('ferryman', None), ('twin', None), ('twin', TWIN_B), ('porter', None),
        ('farmer', dict(top=(0.12, (0.62, 0.70, 0.80), 0.6))), ('mother', dict(top=(0.10, (0.60, 0.66, 0.72), 0.6))), ('qian', BALD), ('porter', dict(top=(0.20, (0.66, 0.72, 0.78), 0.6)))]
PATH = [(300, 470), (900, 540), (1300, 620), (1560, 700)]
RING = [(1560, 690), (1660, 735), (1800, 760), (1960, 765), (2120, 755), (2260, 735), (2380, 705), (1480, 650), (2440, 670), (1420, 610), (2480, 630), (1380, 575)]

def path_at(d):
    """point along the procession path, d in pixels from the start"""
    acc = 0.0
    for (a, b) in zip(PATH, PATH[1:]):
        seg = math.hypot(b[0] - a[0], b[1] - a[1])
        if d <= acc + seg:
            v = (d - acc) / seg; return (lerp(a[0], b[0], v), lerp(a[1], b[1], v))
        acc += seg
    return PATH[-1]

def carriers(ctx, T, u, opened=0.0):
    order = []
    for i, (who, spec) in enumerate(CAST):
        start = i * 3.2
        d = (u - start) * 46
        ring = RING[i]
        if d < 0: continue
        arrive = 1500
        if d < arrive:
            x, y = path_at(d * 0.98)
            ph = d / 40.0; f = 1
        else:
            v = ease((d - arrive) / 300)
            x0, y0 = path_at(arrive * 0.98)
            x, y = lerp(x0, ring[0], v), lerp(y0, ring[1], v); ph = None if v >= 1 else d / 40.0
            f = 1 if ring[0] >= x0 else -1
        order.append((y, i, who, spec, x, ph, f))
    order.sort()
    for (y, i, who, spec, x, ph, f) in order:
        s = depth_s(y) * (0.85 if who == 'twin' else 1.0)
        lid = opened > 0 and i < 12
        p = dict(walk=ph, arm_f=(80, 90) if not lid else (lerp(80, 150, opened), lerp(90, 20, opened)), arm_b=(70, 90) if not lid else (60, 60),
                 look=-4 if not lid else -20 * opened, mouth='smile' if who != 'qian' else 'frown', eyes='open' if not lid else 'wide')
        if who == 'qian': p['eyes'] = 'closed' if int(T * 0.7) % 3 == 0 else 'open'
        r = ctx.fig(x, y, s, who, f, p, seed=40 + i, spec=spec)
        if r:
            hx, hy = r['hand_f']
            wx, wy = hx / ctx.z + ctx.left, hy / ctx.z + ctx.top
            col = WEATHERS[i % len(WEATHERS)]
            if opened <= 0:
                big_jar(ctx, wx + 6 * f, wy + 40 * s, 0.5 * s / 1.2, col, 0.25, seed=900 + i)
                if who == 'qian': big_jar(ctx, wx - 20 * f, wy + 44 * s, 0.45 * s / 1.2, WEATHERS[(i + 2) % 6], 0.25, seed=950)
            else:
                big_jar(ctx, x + 30 * f * s, y, 0.5 * s / 1.2, col, 0.3 + 0.4 * opened, seed=900 + i)

def drawC(ctx, lt):
    T = ctx.Tabs; u = T - T_C
    draw_spine(ctx, dragon_low(T, u, 1.0), T, 1.6, 0.35, 'calm')
    carriers(ctx, T, u)
    granny_mud(ctx, T, u, x=1500, pose=dict(look=-14, mouth='smile' if u > 10 else 'flat'))
    xm_kneel(ctx, T, dict(crouch=0.0, look=-14, eyes='happy' if u > 6 else 'wide', mouth='smile'))
    ctx.baozi(1780, MUD_Y - 230 + 8 * math.sin(T * 2), 1.3, 'happy')

# ---------------------------------------------------------------- D: they open them; the colors swirl in; it drinks, grows, starts to rise
T_D = 110.0
def swirl(ctx, T, u, cx, cy, amt, R0=500):
    for i in range(12):
        col = WEATHERS[i % len(WEATHERS)]
        jx, jy = RING[i]
        n = 18
        pts = []
        for k in range(n):
            s_ = k / n
            prog = min(1, max(0, u / 14 - s_ * 0.4))
            a = i * 0.52 + T * (0.6 + 0.1 * (i % 3)) + s_ * 3.0
            r = R0 * (1 - prog * 0.75) * (0.6 + 0.4 * s_)
            px = lerp(jx, cx + math.cos(a) * r, min(1, prog * 2)); py = lerp(jy - 60, cy + math.sin(a) * r * 0.45 - 120 * prog, min(1, prog * 2))
            pts.append((px, py))
        wisp(ctx, pts, amt, col, 10, world=True, t=T + i)

def rising_spine(T, up):
    """the dragon uncoiling and lifting from the mud (up 0..1)"""
    hx = DX - 120 + 80 * up; hy = DY - 100 - 520 * up
    return dragon_spine(hx, hy, T, 1000 + 300 * up, 40 + 30 * up, 1.4, ang=-math.pi / 2 - 0.5 + 0.3 * up, n=80, speed=0.4, coil=max(0, 0.6 - up))

def drawD(ctx, lt):
    T = ctx.Tabs; u = T - T_D
    opened = ease(u / 2.5)
    drink = ease((u - 10) / 30)
    up = ease((u - 46) / 20)
    if up <= 0:
        sp = dragon_low(T, u, 1.0 - drink)
    else:
        sp = rising_spine(T, up * 0.35)
    draw_spine(ctx, sp, T, 1.6 + 0.6 * drink, 0.35 + 0.6 * drink, 'calm', jaw=0.6 * math.sin(T * 3) * (10 < u < 40), color=drink, cols=WEATHERS)
    carriers(ctx, T, 200, opened)
    swirl(ctx, T, u, sp[0][0] + 120, sp[0][1] + 60, 0.28 * opened * (1 - ease((u - 40) / 8)))
    granny_mud(ctx, T, u, x=1500, pose=dict(look=-20, mouth='open' if 20 < u < 30 else 'smile', eyes='wide' if u > 46 else 'open'))
    xm_kneel(ctx, T, dict(crouch=0.0, look=-24, eyes='wide', mouth='open', arm_f=(150, 20) if u > 46 else (30, 30), arm_b=(140, 20) if u > 46 else (20, 30)))
    ctx.baozi(1780, MUD_Y - 230 + 8 * math.sin(T * 2), 1.3, 'happy')

# ---------------------------------------------------------------- E/F: in the sky: it falters; the jar from the day his mother was born; up into the clouds
GROUND = SKY_H - 200
def sky_spine(T, h, falter=0.0, s=1.0):
    """dragon climbing above the ground: h = height of head above ground (pixels)"""
    hx = 1300 + 120 * math.sin(T * 0.3) - 90 * falter
    hy = GROUND - h + 140 * falter
    return dragon_spine(hx, hy, T, 1300, 60 - 25 * falter, 1.5, ang=-math.pi / 2 + 0.15 - 0.5 * falter, n=90, speed=0.5 - 0.3 * falter)

def ground_crowd(ctx, T, look=1.0, raise_=0.0):
    for i, (who, spec) in enumerate(CAST[:10]):
        x = 900 + i * 85 + (i % 2) * 30
        s = 0.42 * (0.85 if who == 'twin' else 1.0)
        ctx.fig(x, GROUND + 40 + (i % 3) * 8, s, who, 1 if i % 2 else -1, dict(look=-24 * look, arm_f=(lerp(20, 160, raise_), 20), arm_b=(lerp(20, 150, raise_), 20), eyes='wide', mouth='open'), seed=40 + i, spec=spec)

T_E = 180.0
def drawE(ctx, lt):      # climbing ... and faltering halfway
    T = ctx.Tabs; u = T - T_E
    h = lerp(500, 1200, ease(u / 10)) - 300 * ease((u - 10) / 6)
    falter = ease((u - 10) / 6)
    draw_spine(ctx, sky_spine(T, h, falter), T, 2.2, 0.9, 'calm' if u < 12 else 'scared', color=1.0 - 0.5 * falter, cols=WEATHERS)
    ground_crowd(ctx, T)

def drawE2(ctx, lt):     # on the mud, close: Granny's tiny jar with the faded red string
    T = ctx.Tabs; u = T - 198
    take = ease((u - 1) / 2.5)
    r = granny_mud(ctx, T, u, x=1500, pose=dict(no_lantern=True, arm_f=(lerp(30, 95, take), lerp(60, 20, take)), arm_b=(lerp(20, 80, take), 30), look=-6 if u < 10 else -24,
                   eyes='closed' if 12 < u < 14 else 'open', mouth='flat' if u < 18 else 'smile'))
    xm = ctx.fig(1640, MUD_Y + 4, depth_s(MUD_Y), 'xiaoman', -1, dict(look=6, eyes='wide' if u > 2 else 'open', mouth='open' if 3 < u < 6 else 'flat', arm_f=(20, 30)))
    if r and take > 0:
        hx, hy = r['hand_f']
        small_jar(ctx, (hx, hy), ctx.z * depth_s(MUD_Y), W_WARM, 0.4 + 0.3 * ease((u - 18) / 2), s=0.35)
        Ls = ctx.layer(hx - 30 * ctx.z, hy - 10 * ctx.z, hx + 30 * ctx.z, hy + 40 * ctx.z)
        line(Ls, [(hx - 8 * ctx.z, hy + 2 * ctx.z), (hx + 2 * ctx.z, hy + 14 * ctx.z), (hx - 4 * ctx.z, hy + 26 * ctx.z)], 1.2, ctx.z, 0.0, 0.2, 1990)
        Ls.tints.append((np.clip(Ls.M + 0, 0, 1) * 0, VERMILION))
        rr = ctx.layer(hx - 30 * ctx.z, hy - 10 * ctx.z, hx + 30 * ctx.z, hy + 40 * ctx.z)
        m = np.zeros(rr.D.shape, np.float32)
        cv2.polylines(m, [np.int32(np.array([(hx - 8 * ctx.z - rr.x0, hy + 2 * ctx.z - rr.y0), (hx + 2 * ctx.z - rr.x0, hy + 14 * ctx.z - rr.y0), (hx - 4 * ctx.z - rr.x0, hy + 26 * ctx.z - rr.y0)]) * 4)],
                      False, 1.0, int(2 * ctx.z * 4), cv2.LINE_AA, 2)
        rr.knock(m); rr.tints.append((m * 0.8, VERMILION))
        if u > 18:      # it opens: a soft warm rain spirals up
            v = u - 18
            for k in range(30):
                s_ = (k / 30 + v * 0.25) % 1.0
                a = s_ * 14 + T * 2
                px = hx + math.cos(a) * 30 * ctx.z * (0.3 + s_) ; py = hy - s_ * 700 * ctx.z
                ctx.add_glow(px, py, 3.5 * ctx.z, 0.7 * min(1, v / 1.5) * (1 - s_ * 0.6), W_WARM, world=False)

T_F = 222.0
def drawF(ctx, lt):      # the warm rain reaches it; it roars and climbs into the clouds
    T = ctx.Tabs; u = T - T_F
    h = lerp(900, 2300, ease((u - 4) / 22))
    jaw = math.exp(-((u - 5) / 1.0) ** 2) * 1.0
    for k in range(40):      # the warm spiral rising from the ground
        s_ = (k / 40 + u * 0.2) % 1.0
        a = s_ * 16 + T * 2
        ctx.add_glow(1300 + math.cos(a) * 80 * (0.4 + s_), GROUND - s_ * h, 6, 0.6 * (1 - ease((u - 14) / 6)), W_WARM)
    draw_spine(ctx, sky_spine(T, h, 0.0), T, 2.4, 1.0, 'calm', jaw=jaw, color=1.0, cols=WEATHERS + [W_WARM])
    ground_crowd(ctx, T, 1.0, ease((u - 10) / 2))

def sky_cam_follow(lt):
    u = lt + 4
    h = lerp(900, 2300, ease((u - 4) / 22))
    return (1300, min(SKY_H - 402, max(402, GROUND - h + 250)), 1.0)

def post_roar_flash(img, lt, ctx):
    u = ctx.Tabs - T_F
    a = math.exp(-((u - 5.2) / 0.5) ** 2) * 0.35 + (math.exp(-((u - 24) / 0.4) ** 2) * 0.5)
    return img * (1 - a) + np.array([1.0, 0.98, 0.95], np.float32) * a

shots = [
    # A · 0  Granny arrives
    dict(dur=14, set=MUDFLAT, cam=camkf([(0, (1300, 450, 1.2)), (14, (1650, 470, 1.35))]), draw=drawA, grade=DAWN, fade_in=(2.0, (0, 0, 0))),
    dict(dur=8, set=MUDFLAT, cam=(1520, 560, 2.6), draw=drawA, grade=DAWN),                          # 14 "It's you..."
    dict(dur=8, set=MUDFLAT, cam=camkf([(0, (1850, 560, 2.4)), (8, (1850, 565, 2.6))]), draw=drawA, grade=DAWN),   # 22 the dragon bows its head
    dict(dur=10, set=MUDFLAT, cam=(1690, 570, 2.6), draw=drawA, grade=DAWN),                         # 30 "Granny, it needs water"
    # B · 40  she looks back at the town
    dict(dur=10, set=MUDFLAT, cam=camkf([(0, (1520, 560, 2.8)), (10, (1520, 560, 3.1))]), draw=drawB, grade=DAWN),
    dict(dur=6, set=MUDFLAT, cam=camkf([(0, (700, 420, 2.2)), (6, (700, 420, 2.4))]), draw=drawB, grade=DAWN),        # 50 the far town
    dict(dur=6, set=MUDFLAT, cam=(1520, 560, 3.0), draw=drawB, grade=DAWN),                          # 56 "Bring the jars."
    # C · 62  the procession
    dict(dur=20, set=MUDFLAT, cam=camkf([(0, (1000, 470, 1.2)), (20, (1300, 480, 1.25))]), draw=drawC, grade=MORN, xfade=1.5),
    dict(dur=12, set=MUDFLAT, cam=camkf([(0, (1250, 560, 1.9)), (12, (1450, 580, 1.9))]), draw=drawC, grade=MORN),
    dict(dur=8, set=MUDFLAT, cam=lambda lt: (lerp(1150, 1350, lt / 8), 560, 2.4), draw=drawC, grade=MORN),   # 94 Qian, sheepish, with two jars
    dict(dur=8, set=MUDFLAT, cam=camkf([(0, (1900, 470, 1.15)), (8, (1950, 450, 1.05))]), draw=drawC, grade=MORN),
    # D · 110  the weathers burst out
    dict(dur=14, set=MUDFLAT, cam=camkf([(0, (1950, 420, 1.05)), (14, (1950, 430, 1.15))]), draw=drawD, grade=MORN),
    dict(dur=20, set=MUDFLAT, cam=camkf([(0, (1950, 430, 1.15)), (20, (2000, 402, 1.0))]), draw=drawD, grade=MORN),
    dict(dur=12, set=MUDFLAT, cam=camkf([(0, (1880, 520, 2.4)), (12, (1880, 500, 2.6))]), draw=drawD, grade=MORN),   # 144 drinking
    dict(dur=10, set=MUDFLAT, cam=(1600, 560, 2.4), draw=drawD, grade=MORN),                                         # 156 faces, colours
    dict(dur=14, set=MUDFLAT, cam=camkf([(0, (1950, 402, 1.0)), (14, (1950, 402, 1.0))]), draw=drawD, grade=MORN),   # 166 it begins to rise
    # E · 180  in the sky; it falters
    dict(dur=18, set=SKY, cam=lambda lt: (1300, min(SKY_H - 402, max(402, GROUND - (lerp(500, 1200, ease(lt / 10)) - 300 * ease((lt - 10) / 6)) + 300)), 1.0), draw=drawE, grade=MORN, xfade=1.5),
    dict(dur=24, set=MUDFLAT, cam=camkf([(0, (1560, 560, 2.5)), (24, (1540, 520, 2.8))]), draw=drawE2, grade=MORN),   # 198 "What's that?"  the warm rain
    # F · 222  it climbs into the clouds
    dict(dur=28, set=SKY, cam=sky_cam_follow, draw=drawF, grade=lambda lt: tuple(lerp(a, b, ease(lt / 26)) for a, b in zip(MORN, (0.72, 0.70, 0.72))), post=post_roar_flash, xfade=1.0),
    dict(dur=12, set=SKY, cam=camkf([(0, (1300, 1900, 1.0)), (12, (1300, 1990, 1.0))]), draw=lambda c, l: ground_crowd(c, c.Tabs, 1.0, 1.0 - ease(l / 6)),
         grade=(0.72, 0.70, 0.72)),
    dict(dur=38, set=MUDFLAT, cam=camkf([(0, (1560, 560, 2.2)), (38, (1600, 470, 1.4))]), draw=lambda c, l: (granny_mud(c, c.Tabs, l, x=1500, pose=dict(no_lantern=True, look=-24, mouth='flat')),
         c.fig(1640, MUD_Y + 4, depth_s(MUD_Y), 'xiaoman', -1, dict(look=-24, eyes='wide', mouth='flat'))), grade=(0.70, 0.68, 0.70), fade_out=(2.0, (0.6, 0.6, 0.62))),
]

subs = [
    (15.0, '是你……你还这么小。', "It's you... you're still so small.", 'granny'),
    (31.0, '外婆，它需要水。很多很多水。', 'Granny, it needs water. Lots and lots of water.', 'xiaoman'),
    (56.5, '把罐子都拿来。全部。', 'Bring the jars. All of them.', 'granny'),
    (200.5, '那是什么？', "What's that?", 'xiaoman'),
    (205.0, '你妈妈出生那天的雨。', 'The rain from the day your mother was born.', 'granny'),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 21)
    m.drips(0, 110, 0.8, 0.03)
    m.steps(0, 12, 2.4, 0.03); m.breath(2, 1.2, 0.06); m.breath(5, 1.2, 0.06); m.breath(8, 1.2, 0.06)
    m.pad(0, 62, [45, 52, 57], 0.025)
    m.melody(14, [(69, 3.0), (67, 1.0), (64, 2.0), (62, 4.0)], 'erhu', 0.05)
    m.breath(22.5, 3.0, 0.06)
    m.add(m.bell(note(69), 5, 0.05), 24)
    m.melody(42, [(57, 4.0), (None, 2.0), (55, 2.0), (57, 6.0)], 'erhu', 0.04)
    m.add(m.drum(48, 0.20, 0.8), 56.2)
    # the procession: a steady walking theme, gathering instruments
    m.pad(62, 48, [50, 57, 62, 66], 0.025)
    m.steps(62, 110, 3.0, 0.03)
    m.zheng_phrase(63, [62, 66, 69, 74, 69, 66, 62, None] * 5 + [62, 66, 69, 74, 76, 74], 0.75, 0.07, 0.5)
    m.melody(80, [(74, 2.0), (76, 1.0), (78, 1.0), (81, 3.0), (78, 1.0), (76, 2.0), (74, 4.0), (None, 2.0), (76, 2.0), (78, 2.0), (81, 6.0)], 'dizi', 0.05)
    m.snort(96.5, 0.04)
    # the weathers burst out: each its own sound
    m.add(m.woodblock(800, 0.06), 110.2)
    m.rain([(110, 0.0), (111, 0.25), (130, 0.25), (140, 0.0)])
    m.add(m.chime(note(100), 0.07), 111.0); m.gliss(111.3, 86, 103, 0.04, 0.04)
    m.add(m.bell(note(88), 4, 0.05), 111.6)
    m.wind(112, 132, 0.03, 400, 2000)
    m.giggle(112.5, 3.0, 0.05)
    m.thunder(113.0, 0.25)
    m.pad(112, 70, [57, 64, 69, 73, 76], 0.035)
    m.melody(118, [(81, 2.0), (83, 1.0), (85, 1.0), (88, 4.0), (None, 1.0), (86, 1.0), (85, 2.0), (83, 2.0), (81, 6.0)], 'dizi', 0.05)
    m.tremolo(140, note(69), 26, 0.03)
    m.roar(156.0, 2.0, 0.10); m.whoosh(166, 4.0, 0.12)
    # it falters; the little jar
    m.pad(180, 42, [45, 52, 56], 0.03)
    m.whoosh(190, 2.0, 0.10, up=False); m.roar(191, 1.5, 0.06)
    m.add(m.guzheng(note(57), 5, 0.10), 199)
    m.melody(206, [(69, 2.0), (72, 1.0), (74, 3.0), (None, 1.0), (76, 1.0), (74, 1.0), (72, 1.0), (69, 4.0)], 'erhu', 0.05)
    m.rain([(216, 0.0), (218, 0.15), (240, 0.15), (246, 0.0)])
    m.gliss(216, 69, 98, 0.10, 0.05)
    # the roar; the climb
    m.roar(226.5, 3.5, 0.40); m.thunder(227.0, 0.35)
    for k in range(18): m.add(m.drum(52 + (k % 3) * 6, 0.16, 0.4), 228 + k * 0.6)
    m.melody(229, [(76, 1.0), (79, 1.0), (81, 1.0), (84, 2.0), (86, 1.0), (88, 4.0), (91, 6.0)], 'dizi', 0.07)
    m.pad(228, 22, [52, 59, 64, 71, 76], 0.04)
    m.thunder(246.0, 0.30)
    m.add(m.gong(8, 0.25, 70), 248)
    # silence on the ground... wind only
    m.wind(250, 300, 0.015, 200, 900)
    m.write(fn, 1.0, 2.0)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
