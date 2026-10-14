# Scene 9 · The Thief · 小偷  (38:00 - 42:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_shop import SHOP, shop_live, FEET, ALTAR, red_jar
from sets_more import ROOFS, SKYLIGHT, roof_y, ROOM, room_live, BED, BRIDGE, BR_CX, MUDFLAT, QIAN_BOAT, depth_s
from figure import baozi as _bz
from s01 import Q
from s06 import BALD, chest

NIGHT = (0.48, 0.40, 0.38)
DARK = (0.38, 0.31, 0.30)
RS = 1.25                     # people on the near roofs
BLUE_MIST = np.array([1.0, 0.78, 0.50], np.float32)

def thunder_baozi(ctx, x, y, s, T, anger=1.0, world=True):
    """Baozi puffed up into a little thundercloud: darker, bigger, crackling"""
    if world: x, y = ctx.T(x, y); s = s * ctx.z
    L = ctx.layer(x - 70 * s, y - 60 * s, x + 70 * s, y + 60 * s)
    _bz(L, x, y, T, s * (1 + 0.5 * anger), 'cross')
    m = np.clip(L.M, 0, 1)
    over(L.D, m * 0.35 * anger)
    for k in range(3):
        if (int(T * 7 + k * 3) % 5) == 0:
            a = k * 2.1 + T
            ctx.add_glow(x + math.cos(a) * 14 * s, y + 16 * s + k * 4 * s, 3 * s, 0.8 * anger, W_THUNDER, world=False)
    if (int(T * 3) % 4) == 0:
        ctx.add_glow(x, y + 30 * s, 2.5 * s, 0.9 * anger, W_THUNDER, world=False)

# ---------------------------------------------------------------- A: shadows on the roofs; the hook goes down
def porters_roof(ctx, T, u):
    sx, sy = SKYLIGHT
    x1, ph1, f1 = walk_x([(0, 700), (12, sx - 110)], u, stride=30, s=RS)
    x2, ph2, f2 = walk_x([(1.2, 600), (13, sx + 90)], u, stride=30, s=RS)
    lower = ease((u - 15) / 2)
    ra = ctx.fig(x1, roof_y(x1), RS, 'porter', 1, dict(walk=ph1, crouch=0.5 + 0.3 * lower, arm_f=(lerp(30, 120, lower), 10), arm_b=(20, 30), lean=12, look=10 * lower), seed=31)
    ctx.fig(x2, roof_y(x2), RS, 'porter', -1 if u > 13 else 1, dict(walk=ph2, crouch=0.5, arm_f=(40, 30), arm_b=(30, 30), lean=10, look=8), seed=32, spec=dict(top=(0.20, (0.66, 0.72, 0.78), 0.6)))
    if ra and u > 15:
        hx, hy = ra['hand_f']
        tx, ty = ctx.T(sx, sy)
        L = ctx.layer(min(hx, tx) - 10, min(hy, ty) - 10, max(hx, tx) + 10, max(hy, ty) + 40)
        line(L, [(hx, hy), (tx, ty + 10 * ctx.z)], 1.2, ctx.z, 0.9, 0.2, 1900, taper=False)

def drawA(ctx, lt):
    T = ctx.Tabs
    porters_roof(ctx, T, T)
    ctx.add_glow(3300, 140, 60, 0.15, W_DRIZZLE)
    for k, (wx, wy) in enumerate([(520, 560), (1890, 573), (2500, 568)]):
        ctx.add_glow(wx, wy, 8, 0.18 * (0.8 + 0.2 * math.sin(T + k)), WARM)

# ---------------------------------------------------------------- B: inside, the red jar rises out of the dark
def drawB(ctx, lt):
    T = ctx.Tabs; u = T - 30
    shop_live(ctx, glow=0.4, night=0.6, red=False, giggle=False, rain_door=0.0, candles=False, empty=0.78)
    hook_y = lerp(-80, ALTAR[1] - 96, ease(u / 7)) if u < 9 else ALTAR[1] - 96 - (ease((u - 10) / 14) * 700)
    lifted = u > 9.5
    x = ALTAR[0] + math.sin(T * 1.3) * (4 if lifted else 1)
    sx, sy = ctx.T(x, hook_y); se = ctx.z
    L = ctx.layer(sx - 20 * se, -10, sx + 20 * se, sy + 20 * se)
    line(L, [(sx, -10), (sx, sy)], 1.2, se, 0.9, 0.2, 1910, taper=False)
    line(L, [(sx, sy), (sx + 6 * se, sy + 8 * se), (sx, sy + 14 * se), (sx - 5 * se, sy + 9 * se)], 1.6, se, 0.95, 0, 1911)
    jy = ALTAR[1] if not lifted else hook_y + 96
    red_jar(ctx, x, jy, glow=0.25 + 0.15 * math.sin(T * 2) if lifted else 0.0)

# ---------------------------------------------------------------- C: Old Ink; Xiaoman wakes; Baozi puffs up
def drawC(ctx, lt):      # Old Ink squawks on his post
    T = ctx.Tabs; u = T - 60
    town_live(ctx, 0.0, False, True, False, jars_glow=0.2, water=0.0, night=0.3, cormorant=False)
    flap = math.sin(u * 22) * (2 < u < 5)
    ctx.cormorant(2092, WATER_Y - 62 - 8 * abs(flap), 1.0, look=-0.5 + 0.5 * flap)

def drawC2(ctx, lt):     # he sits bolt upright
    T = ctx.Tabs; u = T - 66
    room_live(ctx, 0.0, 0.0)
    up = ease((u - 1.5) / 0.5)
    if up < 0.5:
        ctx.fig(1880, BED[2] - 4, 2.0, 'xiaoman', 1, dict(eyes='closed' if u < 1.2 else 'wide', arm_f=(160, 10)), rot=-90)
    else:
        x, ph, f = walk_x([(9, 1700), (14, 900)], u, stride=26, s=2.0)
        r = ctx.fig(x if u > 9 else 1700, ROOM_FEET if u > 9 else BED[2] + 40, 2.0, 'xiaoman', -1, dict(walk=ph, crouch=0.0 if u > 9 else 0.5, eyes='wide', mouth='open' if 9.6 < u < 12 or 2 < u < 3.5 else 'flat',
                    arm_f=(60, 40), arm_b=(40, 40), look=-6))
    anger = ease((u - 4) / 2)
    bx = 1640 + 20 * math.sin(T); by = 420 + 10 * math.sin(T * 1.4)
    if anger <= 0: ctx.baozi(bx, by, 1.8, 'happy')
    else: thunder_baozi(ctx, bx, by, 1.8, T, anger)

from sets_more import ROOM_FEET

# ---------------------------------------------------------------- D: the rooftop chase
T_D = 80.0
def qx_at(u): return walk_x([(0, 900), (34, 3300)], u, stride=40, s=RS)
def drawD(ctx, lt):
    T = ctx.Tabs; u = T - T_D
    x, ph, f = qx_at(u)
    hop = abs(math.sin(u * 3.3)) * 18
    flap = math.sin(T * 9)
    r = ctx.fig(x, roof_y(x) - hop, RS, 'qian', 1, dict(walk=ph, arm_f=(80, 90), arm_b=(150 + 20 * flap, 30), lean=14, mouth='open', eyes='happy' if 12 < u < 20 else 'wide',
                hem=20 + 10 * flap), spec=dict(hem=14 + 8 * abs(flap)))
    if r:
        hx, hy = r['hand_f']
        red_jar(ctx, (hx / ctx.z) + ctx.left + 6, (hy / ctx.z) + ctx.top + 20, 0.75, glow=0.25)
    # Xiaoman leaps the gaps after him; the thundercloud scuds overhead
    xx, xph, xf = walk_x([(3, 600), (36, 3050)], u, stride=26, s=1.1)
    jump = max(0, math.sin((u - 22) * math.pi / 1.4)) * 90 if 22 < u < 23.4 else 0
    ctx.fig(xx, roof_y(xx) - abs(math.sin(u * 4)) * 10 - jump, 1.1, 'xiaoman', 1, dict(walk=xph if not jump else 0.3, arm_f=(150 if jump else 40, 20), arm_b=(140 if jump else 40, 20),
            lean=12, eyes='wide', mouth='open'))
    thunder_baozi(ctx, xx + 80, roof_y(xx) - 230 + 10 * math.sin(T * 2), 1.6, T, 1.0)
    # the porters ahead, running
    for k in range(2):
        px, pph, pf = walk_x([(0, 1500 + k * 90), (30, 3600 + k * 90)], u, stride=40, s=RS)
        ctx.fig(px, roof_y(px), RS, 'porter', 1, dict(walk=pph, arm_f=(70, 50), arm_b=(70, 50), lean=14, mouth='open', eyes='wide'), seed=31 + k,
                spec=None if k == 0 else dict(top=(0.20, (0.66, 0.72, 0.78), 0.6)))

def camD(lt):
    u = lt + 0 if False else lt
    x, _, _ = qx_at(u)
    return (min(3300, max(960, x + 120)), 520, 1.35)

def camD2(lt):
    x, _, _ = qx_at(lt + 16)
    return (x + 30, 520, 2.6)

def camD3(lt):
    xx, _, _ = walk_x([(3, 600), (36, 3050)], lt + 24, stride=26, s=1.1)
    return (xx + 60, 470, 1.9)

# ---------------------------------------------------------------- E: under the bridge, the tug of war
T_E = 125.0
GROUND = 700
def drawE(ctx, lt):
    T = ctx.Tabs; u = T - T_E
    # both hold the jar; it see-saws between them
    cx = 1400 + math.sin(u * 2.2) * 30 * (u < 25)
    lean = math.sin(u * 2.2) * 14 * (u < 25)
    slip = u > 24.5
    v = min(1, max(0, (u - 24.5) / 0.6))
    q_run = u > 50
    qx = cx + 110 if not q_run else walk_x([(50, cx + 110), (65, 2800)], u, stride=40, s=1.6)[0]
    xp = cx - 100
    qp = dict(arm_f=(85, 10), arm_b=(80, 10), lean=-10 - lean, mouth='open' if u < 25 else 'frown', eyes='wide' if u > 24 else 'squint')
    if q_run: qp.update(walk=walk_x([(50, cx + 110), (65, 2800)], u, stride=40, s=1.6)[1], arm_f=(80, 90), arm_b=(70, 90), lean=14)
    ctx.fig(qx, GROUND, 1.6, 'qian', -1 if not q_run else 1, qp, spec=BALD)
    ctx.fig(xp, GROUND, 1.25, 'xiaoman', 1, dict(arm_f=(90, 10), arm_b=(85, 10), lean=-10 + lean, eyes='wide', mouth='open' if u < 25 or 27 < u < 30 else 'flat'))
    if 34 < u < 52: pass
    # the jar
    crack = ease((u - 25.1) / 0.3) if u > 25.1 else 0.0
    if not slip:
        jx, jy = cx, GROUND - 60
    elif u < 46:
        jx, jy = cx + 20 * v, GROUND - 60 + 58 * v * v
    else:      # Qian snatches it up again
        w = ease((u - 46) / 1.2)
        jx, jy = lerp(cx + 20, qx - 40, w), lerp(GROUND - 2, GROUND - 80, w)
    red_jar(ctx, jx, jy, 1.0, crack=crack, glow=0.25 + 0.3 * crack)
    if crack > 0 and u < 60:
        # a thin thread of blue mist leaks out and curls around them both
        amt = ease((u - 25.5) / 3) * (1 - ease((u - 52) / 4))
        pts = []
        for k in range(40):
            s_ = k / 40
            a = s_ * 10 + T * 0.8
            rx = 160 + 40 * math.sin(T * 0.5 + s_ * 4); ry = 90
            px = 1400 + math.cos(a) * rx * s_ * min(1, (u - 25.5) / 6); py = GROUND - 160 + math.sin(a) * ry * s_ - s_ * 60
            pts.append((lerp(jx, px, min(1, s_ * 3)), lerp(jy - 40, py, min(1, s_ * 3))))
        wisp(ctx, pts, amt * 0.9, BLUE_MIST, 7, world=True, t=T)
    thunder_baozi(ctx, xp - 40, GROUND - 330 + 8 * math.sin(T * 2), 1.4, T, 1.0 if u < 25 else 0.4)

# ---------------------------------------------------------------- F: aboard; the empty altar
def drawF(ctx, lt):      # he leaps aboard the painted boat
    T = ctx.Tabs; u = lt
    x, ph, f = walk_x([(0, 1900), (6, 2400)], u, stride=40, s=1.25)
    leap = ease((u - 6) / 0.8)
    y = lerp(672, 600, leap) - math.sin(min(1, leap) * math.pi) * 60
    xx = lerp(x, 2560, leap)
    r = ctx.fig(xx, y, depth_s(672) * 1.04, 'qian', 1, dict(walk=ph if leap == 0 else None, arm_f=(80, 90), arm_b=(150, 30), lean=10, mouth='open' if u < 6 else 'smile', eyes='wide' if u < 6 else 'squint'), spec=BALD)
    if r: red_jar(ctx, (r['hand_f'][0] / ctx.z) + ctx.left + 6, (r['hand_f'][1] / ctx.z) + ctx.top + 20, 0.7, crack=1.0, glow=0.3)
    ctx.add_glow(QIAN_BOAT[0] - 190, QIAN_BOAT[1] - 100, 10, 0.7, WARM)
    ctx.add_glow(QIAN_BOAT[0] + 170, QIAN_BOAT[1] - 70, 10, 0.7, WARM)

def drawG(ctx, lt):      # Granny comes down with a lantern: the altar is empty. She sits on the step.
    T = ctx.Tabs; u = lt
    shop_live(ctx, glow=0.4, night=0.6, red=False, giggle=False, rain_door=0.0, candles=(80,), empty=0.78)
    x, ph, f = walk_x([(2, 2900), (9, 2050)], u, stride=30, s=2.0)
    sit = ease((u - 17) / 2.0)
    r = ctx.fig(x if u < 12 else lerp(2050, 2150, ease((u - 12) / 3)), FEET - 20, 2.0, 'granny', -1 if u < 15 else 1,
                dict(walk=ph, crouch=0.6 * sit, arm_f=(lerp(60, 20, sit), 30), arm_b=(20, 30), look=-6 if u < 15 else 10, eyes='wide' if 9 < u < 13 else 'closed' if 22 < u < 26 else 'open'))
    if r: lantern(ctx, r['hand_f'], 2.0 * ctx.z * 0.55, 1.0, T)
    # Xiaoman in the doorway, out of breath, stops
    if u > 26:
        xx, xph, xf = walk_x([(26, 300), (29, 700)], u, stride=26, s=1.9)
        ctx.fig(xx, FEET, 1.9, 'xiaoman', 1, dict(walk=xph, arm_f=(20, 30), arm_b=(20, 30), look=6, eyes='open', mouth='frown', lean=6))

shots = [
    # A · 0  midnight on the roofs
    dict(dur=14, set=ROOFS, cam=camkf([(0, (1000, 402, 1.0)), (14, (1400, 480, 1.3))]), draw=drawA, grade=NIGHT, fade_in=(2.0, (0, 0, 0))),
    dict(dur=16, set=ROOFS, cam=camkf([(0, (1480, 520, 1.9)), (16, (1500, 530, 2.1))]), draw=drawA, grade=NIGHT),
    # B · 30  the jar rises
    dict(dur=16, set=SHOP, cam=camkf([(0, (1975, 420, 1.8)), (16, (1975, 380, 2.0))]), draw=drawB, grade=DARK),
    dict(dur=14, set=SHOP, cam=lambda lt: (1975, max(201, 380 - lt * 18), 2.0), draw=drawB, grade=DARK),
    # C · 60  Old Ink; Xiaoman; "Thieves!"
    dict(dur=6, set=TOWN, cam=(2092, 480, 2.6), draw=drawC, args=dict(water=0.0, mist=0.2), grade=NIGHT),
    dict(dur=14, set=ROOM, cam=camkf([(0, (1700, 440, 1.5)), (14, (1300, 420, 1.3))]), draw=drawC2, grade=NIGHT),
    # D · 80  over the roofs
    dict(dur=16, set=ROOFS, cam=camD, draw=drawD, grade=NIGHT),
    dict(dur=8, set=ROOFS, cam=camD2, draw=drawD, grade=NIGHT),                          # 96 "The biggest storm in the world!"
    dict(dur=10, set=ROOFS, cam=camD3, draw=drawD, grade=NIGHT),                         # 104 the leap
    dict(dur=11, set=ROOFS, cam=lambda lt: (3240, 402, 1.0), draw=drawD, grade=NIGHT, set_t0=0),
    # E · 125  under the bridge
    dict(dur=15, set=BRIDGE, cam=camkf([(0, (1400, 500, 1.4)), (15, (1400, 520, 1.6))]), draw=drawE, args=dict(water=0.0), grade=NIGHT, xfade=1.0),
    dict(dur=10, set=BRIDGE, cam=camkf([(0, (1400, 552, 2.3)), (10, (1405, 556, 2.4))]), draw=drawE, args=dict(water=0.0), grade=NIGHT),     # 140 hands on the jar
    dict(dur=8, set=BRIDGE, cam=(1420, 560, 2.2), draw=drawE, args=dict(water=0.0), grade=NIGHT),                                         # 150 it slips and cracks
    dict(dur=18, set=BRIDGE, cam=camkf([(0, (1400, 560, 1.8)), (18, (1400, 540, 1.6))]), draw=drawE, args=dict(water=0.0), grade=NIGHT),    # 158 the blue thread
    dict(dur=15, set=BRIDGE, cam=camkf([(0, (1450, 520, 1.5)), (15, (1700, 500, 1.3))]), draw=drawE, args=dict(water=0.0), grade=NIGHT),    # 176 snatched
    # F · 191  aboard; the empty altar
    dict(dur=12, set=MUDFLAT, cam=camkf([(0, (2200, 470, 1.4)), (12, (2450, 470, 1.4))]), draw=drawF, grade=NIGHT, xfade=1.0),
    dict(dur=37, set=SHOP, cam=camkf([(0, (2300, 402, 1.15)), (14, (2080, 430, 1.5)), (24, (2100, 450, 1.7)), (37, (1700, 402, 1.05))]), draw=drawG, grade=DARK,
         xfade=1.5, fade_out=(4.0, (0, 0, 0))),
]

subs = [
    (75.0, '外婆！有贼！', 'Granny! Thieves!', 'xiaoman'),
    (97.0, '世界上最大的风暴！城里人会排队来看！', 'The biggest storm in the world! The city will queue to see it!', 'qian'),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 19)
    m.crickets(0, 60, 0.018)
    m.pad(0, 60, [38, 44, 50], 0.025)      # tense: a tritone under it
    for k in range(12): m.step(2 + k * 0.9, 0.025, True)
    m.creak(14.5, 0.05); m.creak(21.0, 0.04)
    m.tremolo(16, note(62), 14, 0.02)
    m.add(m.woodblock(400, 0.04), 39.5); m.creak(40.0, 0.06)
    m.rumble(41, 3, 0.10, 34); m.add(m.bell(note(74), 3, 0.03), 41.2)
    # Old Ink, the alarm
    m.squawk(61.8, 0.18); m.squawk(62.6, 0.16); m.squawk(63.5, 0.14)
    m.breath(67.5, 0.8, 0.08)
    m.rumble(70.5, 2.0, 0.10, 60); m.thunder(71.0, 0.10)
    m.steps(75, 80, 3.6, 0.05)
    # the chase: drums, dizi, tiles clattering
    for k in range(60): m.add(m.drum(70 if k % 2 else 55, 0.12, 0.25), 80 + k * 0.38)
    m.melody(80, [(69, 0.25), (72, 0.25), (74, 0.25), (76, 0.5), (74, 0.25), (72, 0.25), (69, 0.5)] * 6, 'dizi', 0.05)
    m.steps(80, 125, 4.4, 0.05)
    for t0 in (88.0, 95.0, 103.0, 112.0, 119.0): m.crack(t0, 0.06)
    for t0 in (90.0, 101.0, 116.0): m.thunder(t0, 0.08, far=True)
    m.whoosh(102.5, 1.2, 0.10)
    m.crowd(96.5, 100, 0.0)
    # under the bridge
    m.pad(125, 66, [38, 45, 49], 0.03)
    for k in range(10): m.creak(127 + k * 2.3, 0.05)
    m.shatter(150.1, 0.18); m.crack(150.15, 0.25)
    m.breath(152.0, 6.0, 0.18)       # the deep breath from inside the jar
    m.rumble(152, 6, 0.20, 30)
    m.gliss(156, 50, 74, 0.15, 0.05)
    m.melody(160, [(62, 3.0), (61, 1.0), (62, 2.0), (66, 4.0), (None, 1.0), (67, 3.0)], 'erhu', 0.05)
    m.add(m.drum(50, 0.25, 0.6), 171.0); m.steps(175, 190, 4.0, 0.04)
    # aboard; the empty altar
    m.steps(191, 197, 3.6, 0.04); m.oar(198.0, 0.10)
    m.crickets(203, 240, 0.02)
    m.steps(205, 212, 1.4, 0.03, True)
    m.add(m.guzheng(note(45), 6, 0.12), 213.5)
    m.melody(216, [(57, 4.0), (55, 2.0), (52, 6.0)], 'erhu', 0.05)
    m.steps(229, 232, 3.0, 0.04)
    m.pad(213, 27, [33, 40, 45], 0.03)
    m.write(fn, 1.0, 3.0)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
