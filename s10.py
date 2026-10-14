# Scene 10 · The Chase · 追  (42:00 - 47:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_more import LANE, LANE_G, laundry, MUDFLAT, QIAN_BOAT, depth_s, MUD_HZ
from figure import dragon, dragon_spine
from s01 import Q
from s06 import BALD
from s09 import thunder_baozi, BLUE_MIST
from sets_shop import red_jar

PREDAWN = (0.72, 0.60, 0.55)
DAWN = (0.86, 0.80, 0.80)
MUD_Y = 700

def flying_ink(ctx, x, y, s, T, seed=0):
    """Old Ink in flight: dark body, long neck forward, hooked beak, flapping wings"""
    sx, sy = ctx.T(x, y); se = s * ctx.z
    L = ctx.layer(sx - 90 * se, sy - 70 * se, sx + 90 * se, sy + 70 * se)
    fl = math.sin(T * 9 + seed)
    body = [(sx + 26 * se * math.cos(q), sy + 9 * se * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 20)]
    fill(L, body, 0.85, s=se, seed=740, gran=0.4)
    line(L, [(sx + 22 * se, sy - 2 * se), (sx + 44 * se, sy - 8 * se), (sx + 56 * se, sy - 6 * se)], 3.0, se, 0.9, 0.2, 741)
    line(L, [(sx + 56 * se, sy - 6 * se), (sx + 68 * se, sy - 4 * se), (sx + 70 * se, sy + 1 * se)], 1.6, se, 0.9, 0, 742)
    ctx.add_glow(sx + 54 * se, sy - 7 * se, 1.2 * se, 0.6, W_SUN, world=False)
    for side in (-1, 1):
        tip = (sx - 6 * se, sy - side * 0 + (-48 * fl if side < 0 else -40 * fl) * se)
        wing = [(sx + 10 * se, sy - 2 * se), (sx - 4 * se, sy - 20 * se * fl - 4 * se), tip, (sx - 26 * se, sy - 22 * se * fl), (sx - 14 * se, sy)]
        fill(L, wing, 0.8 if side > 0 else 0.55, s=se, seed=744 + side, gran=0.5)
    line(L, [(sx - 26 * se, sy), (sx - 44 * se, sy + 4 * se)], 3.5, se, 0.85, 0.2, 746)

def bicycle(ctx, x, y, s, T, front=False):
    """an old black bicycle with the twins: one pedals, one rides on the rack"""
    sx, sy = ctx.T(x, y); se = s * ctx.z
    L = ctx.layer(sx - 80 * se, sy - 70 * se, sx + 80 * se, sy + 6 * se, front=front)
    rw = 24 * se
    wa, wb = (sx - 40 * se, sy - rw), (sx + 40 * se, sy - rw)
    for (cx, cy) in (wa, wb):
        line(L, [(cx + rw * math.cos(q), cy + rw * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 28)], 2.2, se, 0.9, 0.2, 760, taper=False)
        for k in range(4):
            a = T * 8 + k * math.pi / 4
            line(L, [(cx - rw * math.cos(a), cy - rw * math.sin(a)), (cx + rw * math.cos(a), cy + rw * math.sin(a))], 0.6, se, 0.5, 0, 761 + k, taper=False)
    crank = (sx - 4 * se, sy - rw)
    seat = (sx - 14 * se, sy - rw - 34 * se); bar = (sx + 30 * se, sy - rw - 40 * se)
    for a_, b_ in [(wa, crank), (crank, seat), (seat, wa), (crank, (sx + 26 * se, sy - rw - 30 * se)), ((sx + 26 * se, sy - rw - 30 * se), seat), ((sx + 26 * se, sy - rw - 30 * se), wb), (bar, (sx + 26 * se, sy - rw - 30 * se))]:
        line(L, [a_, b_], 2.0, se, 0.9, 0.2, 765, taper=False)
    line(L, [(bar[0] - 8 * se, bar[1]), (bar[0] + 6 * se, bar[1] - 2 * se)], 2.4, se, 0.9, 0, 766, taper=False)
    line(L, [(seat[0] - 26 * se, seat[1] + 2 * se), (seat[0] - 6 * se, seat[1] + 2 * se)], 2.4, se, 0.9, 0, 767, taper=False)

def twins_bike(ctx, x, y, s, T, surprised=False):
    bicycle(ctx, x, y, s, T)
    ph = T * 2.2
    ctx.fig(x - 14 * s, y - 40 * s, s * 0.9, 'twin', 1, dict(walk=ph, arm_f=(70, 20), arm_b=(70, 20), lean=14, eyes='wide' if surprised else 'happy', mouth='open'), seed=30)
    ctx.fig(x - 40 * s, y - 34 * s, s * 0.9, 'twin', 1, dict(crouch=0.6, arm_f=(150 if not surprised else 100, 10), arm_b=(140, 10), eyes='wide' if surprised else 'happy', mouth='open'), seed=31, spec=TWIN_B)

# ---------------------------------------------------------------- A: the chase
def drawA(ctx, lt):      # across the dry canal bed
    T = ctx.Tabs; u = lt
    town_live(ctx, 0.0, False, True, False, jars_glow=0.25, water=0.0, night=0.3, cormorant=False)
    x, ph, f = walk_x([(0, 300), (20, 2600)], u, stride=30, s=1.2)
    ctx.fig(x, MUD_Y, 1.2, 'xiaoman', 1, dict(walk=ph, arm_f=(60, 50), arm_b=(60, 50), lean=14, mouth='open', eyes='wide'))
    thunder_baozi(ctx, x + 60, MUD_Y - 300 + 14 * math.sin(T * 3), 1.4, T, 0.8)
    flying_ink(ctx, x + 180 + 40 * math.sin(T * 0.7), MUD_Y - 380 + 30 * math.sin(T * 1.1), 1.2, T)
    rr = np.random.default_rng(2)
    for k in range(int(u * 4)):      # little puffs of dust behind his heels
        t0 = k / 4.0; age = u - t0
        if age < 1.5:
            px, _, _ = walk_x([(0, 300), (20, 2600)], t0, stride=30, s=1.2)
            ctx.add_glow(px - 10, MUD_Y - 4 - age * 10, 6 + age * 10, 0.12 * (1 - age / 1.5), np.array([0.70, 0.80, 0.88], np.float32))

T_A2 = 20.0
def drawA2(ctx, lt):     # through the laundry and over a stall; the twins on their bicycle
    T = ctx.Tabs; u = T - T_A2
    gust = 0.6 + 0.4 * math.sin(T * 2)
    laundry(ctx, 0.4, gust * (u < 14))
    x, ph, f = walk_x([(0, 600), (25, 3400)], u, stride=30, s=1.8)
    jump = max(0, math.sin((u - 8.2) * math.pi / 1.2)) * 140 if 8.2 < u < 9.4 else 0
    duck = 0.5 if 3 < u < 5 else 0.0
    ctx.fig(x, LANE_G - jump, 1.8, 'xiaoman', 1, dict(walk=ph if not jump else 0.3, crouch=duck, arm_f=(150 if jump else 60, 20 if jump else 50), arm_b=(140 if jump else 60, 20 if jump else 50),
            lean=14, mouth='open', eyes='wide'))
    thunder_baozi(ctx, x + 60, LANE_G - 420, 1.6, T, 0.8)
    flying_ink(ctx, x + 220, LANE_G - 520 + 30 * math.sin(T * 1.1), 1.6, T)
    if u > 12:
        bx, _, _ = walk_x([(12, 300), (25, 3000)], u, stride=30, s=1.8)
        twins_bike(ctx, bx, LANE_G, 1.8, T)

T_A3 = 45.0
def drawA3(ctx, lt):     # past the shop: Granny on the step stands up with her lantern
    T = ctx.Tabs; u = T - T_A3
    town_live(ctx, 0.0, False, True, False, jars_glow=0.2, water=0.0, night=0.25, cormorant=False)
    x, ph, f = walk_x([(0, 1000), (12, 2600)], u, stride=30, s=0.95)
    ctx.fig(x, Q, 0.95, 'xiaoman', 1, dict(walk=ph, arm_f=(60, 50), arm_b=(60, 50), lean=14, mouth='open', eyes='wide'))
    thunder_baozi(ctx, x + 40, Q - 220, 1.0, T, 0.8)
    bx, _, _ = walk_x([(1, 800), (12, 2500)], u, stride=30, s=0.95)
    twins_bike(ctx, bx, Q, 0.95, T)
    flying_ink(ctx, x + 120, Q - 260, 0.9, T)
    up = ease((u - 4) / 2)
    r = ctx.fig(1700, Q - 4 * (1 - up), 1.12, 'granny', 1, dict(crouch=0.6 * (1 - up), arm_f=(lerp(20, 60, up), 40), arm_b=(20, 30), look=-4, eyes='wide' if u > 4 else 'closed'))
    if r: lantern(ctx, r['hand_f'], 1.12 * ctx.z * 0.55, 1.0, T)

# ---------------------------------------------------------------- B: the boat stuck; "Push!"; the jar breaks
T_B = 60.0
def drawB(ctx, lt):
    T = ctx.Tabs; u = T - T_B
    shout = math.sin(T * 6)
    s = depth_s(672)
    for k, px in enumerate((2240, 2330)):
        heave = abs(math.sin(T * 1.8 + k))
        ctx.fig(px, 672, s, 'porter', 1, dict(arm_f=(100, 0), arm_b=(95, 0), lean=26 + 6 * heave, crouch=0.3 + 0.2 * heave, mouth='open', eyes='closed' if heave > 0.6 else 'open'),
                seed=31 + k, spec=None if k == 0 else dict(top=(0.20, (0.66, 0.72, 0.78), 0.6)))
    broke = u > 30.0
    qp = dict(arm_f=(80, 90), arm_b=(150 + 15 * shout, 20) if 8 < u < 16 else (70, 90), look=-10 if u < 20 else 14, mouth='open' if 8 < u < 16 or 30 < u < 36 else 'frown',
              eyes='wide' if u > 24 else 'squint', lean=-6)
    if broke: qp.update(arm_f=(130, 40), arm_b=(130, 40), lean=-14)
    r = ctx.fig(2560, 596, 1.5, 'qian', -1, qp, spec=BALD)
    if r and not broke:
        crack = 1.0 + ease((u - 18) / 10) * 2.0
        hx, hy = r['hand_f']
        ctx.add_glow(hx, hy - 30 * ctx.z, 12 * ctx.z, 0.3 * ease((u - 18) / 10), BLUE_MIST, world=False)
        red_jar(ctx, hx / ctx.z + ctx.left - 4, hy / ctx.z + ctx.top + 22, 0.8, crack=min(1.0, crack), glow=0.2 + 0.4 * ease((u - 18) / 10) + 0.3 * abs(math.sin(T * 7)) * (u > 24))
    if broke:
        v = u - 30
        ctx.add_glow(2540, 520, 200 * min(1, v * 3), 0.9 * math.exp(-v * 1.2), BLUE_MIST)
        for k in range(8):       # shards falling to the mud
            a = k * 0.8
            px = 2540 + math.cos(a) * 60 * min(1, v * 2); py = 520 + v * v * 300 * (0.6 + 0.1 * k)
            if py < 700:
                sx, sy = ctx.T(px, py); L = ctx.box(px, py, 12, 12)
                fill(L, [(sx, sy - 5 * ctx.z), (sx + 7 * ctx.z, sy), (sx, sy + 4 * ctx.z), (sx - 6 * ctx.z, sy)], 0.06, VERMILION if k % 3 == 0 else CELADON, 0.7, s=ctx.z, seed=880 + k)

# ---------------------------------------------------------------- C: the dragon
T_C = 110.0
DX, DY = 2050, 660

def dragon_now(T, u):
    """spine of the stranded dragon: coiled, shivering; tries to rise at ~u 8 and falls back; later lifts its head to the boy"""
    shiver = math.sin(T * 17) * 2.0
    rise = math.sin(min(1, max(0, (u - 7) / 3.5)) * math.pi) * (1 if u < 11 else 0)
    lift = ease((u - 56) / 6) * 0.6 + ease((u - 72) / 4) * 0.25
    hx = DX - 180 + 60 * lift + 60 * rise; hy = DY - 30 - 180 * rise - 80 * lift + shiver
    sp = dragon_spine(hx, hy, T, 980, 22 + 10 * rise, 1.4, ang=math.pi + 0.15 - 0.6 * rise - 0.35 * lift, n=80, speed=0.15, coil=0.9 - 0.3 * rise)
    sp[:, 1] = np.minimum(sp[:, 1], DY + 30)
    return sp

def draw_dragon(ctx, T, u, s=1.6, eye='scared', jaw=0.0, op=1.0):
    sp = dragon_now(T, u)
    x0, y0 = sp.min(0) - 150 * s; x1, y1 = sp.max(0) + 150 * s
    p0 = ctx.T(x0, y0); p1 = ctx.T(x1, y1)
    L = ctx.layer(p0[0], p0[1], p1[0], p1[1])
    spS = (sp - [ctx.left, ctx.top]) * ctx.z
    dragon(L, spS, T, s * ctx.z, 0.35, eye=eye, jaw=jaw)
    # glints of water running off it
    for k in range(6):
        i = (int(T * 12) + k * 13) % len(sp)
        ctx.add_glow(sp[i][0], sp[i][1] + 10, 3, 0.4, BLUE_MIST)
    return sp

def drawC(ctx, lt):
    T = ctx.Tabs; u = T - T_C
    sp = draw_dragon(ctx, T, u, eye='scared' if u < 66 else 'calm')
    # Qian backing away along the deck
    qx = lerp(2560, 2700, ease((u - 10) / 6))
    ctx.fig(qx, 596, 1.5, 'qian', -1, dict(arm_f=(130, 40), arm_b=(120, 40), lean=-14, eyes='wide', mouth='open' if 14 < u < 20 else 'frown'), spec=BALD)
    for k, px in enumerate((2240, 2330)):
        ctx.fig(px + 140 + 30 * k, 672, depth_s(672), 'porter', 1, dict(arm_f=(130, 30), arm_b=(120, 30), lean=-10, eyes='wide', mouth='open'), seed=31 + k,
                spec=None if k == 0 else dict(top=(0.20, (0.66, 0.72, 0.78), 0.6)))
    # Xiaoman arrives, slows, kneels; reaches out; touches its nose
    s = depth_s(MUD_Y)
    x, ph, f = walk_x([(18, 1100), (26, 1560), (30, 1620), (42, 1700)], u, stride=26, s=s)
    kneel = ease((u - 43) / 3)
    reach = ease((u - 58) / 5)
    hx, hy = sp[0]
    r = ctx.fig(x, MUD_Y, s, 'xiaoman', 1, dict(walk=ph if u < 42 else None, crouch=0.75 * kneel, arm_f=(lerp(20, 95, reach), lerp(30, 10, reach)), arm_b=(20, 30),
                look=-6 if u < 70 else 4, eyes='closed' if 47 < u < 50 else 'open', mouth='smile' if u > 66 else 'flat', lean=6 * reach))
    if u > 64 and r:
        ctx.add_glow(r['hand_f'][0], r['hand_f'][1], 22 * ctx.z, 0.35 * ease((u - 64) / 2), BLUE_MIST, world=False)
    # Baozi, no longer angry, drifts over and rains a few drops on its nose; Old Ink lands on a stone
    if u > 18:
        bz_x = lerp(x + 40, hx + 20, ease((u - 88) / 4)); bz_y = lerp(MUD_Y - 260, hy - 120, ease((u - 88) / 4)) + 8 * math.sin(T * 2)
        if u < 40: thunder_baozi(ctx, bz_x, bz_y, 1.4, T, max(0, 1 - (u - 30) / 6))
        else: ctx.baozi(bz_x, bz_y, 1.4, 'happy' if u < 96 else 'sleepy')
        if 93 < u < 99:
            for k in range(3):
                v = ((u - 93) - k * 1.6) / 0.6
                if 0 <= v <= 1: drop_glow(ctx, bz_x, bz_y + 20, hx + 6, hy - 4, v, W_DRIZZLE, 3.0)
    if u > 30:
        ix = lerp(1500, 1440, ease((u - 30) / 2)); iy = lerp(MUD_Y - 320, MUD_Y - 60, ease((u - 30) / 2))
        if u < 32: flying_ink(ctx, ix, iy, 1.2, T)
        else: ctx.cormorant(1440, MUD_Y - 64, 0.9, look=0.3)
    # the twins arrive on their bicycle and skid to a stop
    if u > 122:
        bx = lerp(600, 1150, ease((u - 122) / 3))
        twins_bike(ctx, bx, MUD_Y + 20, depth_s(MUD_Y + 20), T if u < 125 else 0.0, surprised=u > 125)

shots = [
    # A · 0  the chase
    dict(dur=20, set=TOWN, cam=lambda lt: (lerp(700, 2300, ease(lt / 20)), 520, 1.5), draw=drawA, args=dict(water=0.0, mist=0.4), grade=PREDAWN, fade_in=(1.0, (0, 0, 0))),
    dict(dur=13, set=LANE, cam=lambda lt: (lerp(900, 1600, lt / 13), 430, 1.2), draw=drawA2, grade=PREDAWN, xfade=0.6),
    dict(dur=12, set=LANE, cam=lambda lt: (lerp(1600, 2700, lt / 12), 440, 1.2), draw=drawA2, grade=PREDAWN, set_t0=13),
    dict(dur=15, set=TOWN, cam=camkf([(0, (1500, 440, 1.3)), (15, (2300, 430, 1.3))]), draw=drawA3, args=dict(water=0.0, mist=0.4), grade=PREDAWN, xfade=0.6),
    # B · 60  the stuck boat
    dict(dur=14, set=MUDFLAT, cam=camkf([(0, (2300, 402, 1.0)), (14, (2350, 420, 1.15))]), draw=drawB, grade=PREDAWN, xfade=1.0),
    dict(dur=8, set=MUDFLAT, cam=(2560, 470, 2.5), draw=drawB, grade=PREDAWN),                                         # 74 "Push!"
    dict(dur=8, set=MUDFLAT, cam=camkf([(0, (2400, 450, 1.6)), (8, (2400, 450, 1.7))]), draw=drawB, grade=PREDAWN),      # 82 heave
    dict(dur=12, set=MUDFLAT, cam=camkf([(0, (2540, 390, 3.0)), (12, (2540, 390, 3.3))]), draw=drawB, grade=PREDAWN),    # 90 the crack runs; it breaks at 90
    dict(dur=8, set=MUDFLAT, cam=camkf([(0, (2450, 430, 1.6)), (8, (2300, 420, 1.3))]), draw=drawB, grade=PREDAWN),      # 102 blue flash
    # C · 110  the dragon
    dict(dur=14, set=MUDFLAT, cam=camkf([(0, (2050, 450, 1.2)), (14, (2050, 470, 1.35))]), draw=drawC, grade=DAWN, xfade=1.5),
    dict(dur=8, set=MUDFLAT, cam=(2640, 470, 2.6), draw=drawC, grade=DAWN),                                            # 124 "This is the storm?"
    dict(dur=16, set=MUDFLAT, cam=camkf([(0, (1500, 470, 1.4)), (16, (1700, 480, 1.5))]), draw=drawC, grade=DAWN),       # 132 he arrives, slows
    dict(dur=14, set=MUDFLAT, cam=camkf([(0, (1760, 540, 2.2)), (14, (1770, 545, 2.4))]), draw=drawC, grade=DAWN),       # 148 kneels; "Don't be afraid"
    dict(dur=14, set=MUDFLAT, cam=camkf([(0, (1880, 560, 2.6)), (14, (1880, 560, 2.9))]), draw=drawC, grade=DAWN),       # 162 the dragon's eye
    dict(dur=16, set=MUDFLAT, cam=camkf([(0, (1800, 540, 2.0)), (16, (1820, 545, 2.2))]), draw=drawC, grade=DAWN),       # 176 he touches its nose
    dict(dur=12, set=MUDFLAT, cam=(1720, 540, 2.6), draw=drawC, grade=DAWN),                                           # 192 "It's been locked up"
    dict(dur=14, set=MUDFLAT, cam=camkf([(0, (1880, 520, 2.2)), (14, (1880, 520, 2.3))]), draw=drawC, grade=DAWN),       # 204 Baozi's three drops
    dict(dur=14, set=MUDFLAT, cam=(1720, 540, 2.6), draw=drawC, grade=DAWN),                                           # 218
    dict(dur=24, set=MUDFLAT, cam=camkf([(0, (1500, 470, 1.5)), (24, (1600, 420, 1.1))]), draw=drawC, grade=DAWN),       # 232 the twins
    dict(dur=44, set=MUDFLAT, cam=camkf([(0, (1700, 420, 1.1)), (44, (1800, 402, 1.0))]), draw=drawC, grade=lambda lt: tuple(lerp(a, b, ease(lt / 40)) for a, b in zip(DAWN, (0.92, 0.88, 0.88))),
         fade_out=(3.0, (0, 0, 0))),
]

subs = [
    (75.5, '推！用力推！', 'Push! Push harder!', 'qian'),
    (126.0, '这……这就是风暴？', 'This... this is the storm?', 'qian'),
    (155.0, '别怕。我不追你。', "Don't be afraid. I won't chase you.", 'xiaoman'),
    (194.0, '它不是洪水……它是被关起来了。它要回家。', "It's not a flood... it's been locked up. It wants to go home.", 'xiaoman'),
    (222.0, '它太渴了，飞不起来。', "It's too thirsty to fly.", 'xiaoman'),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 20)
    # chase music: driving drums, dizi, wood blocks; footsteps; laundry snaps; bicycle bell
    for k in range(150): m.add(m.drum(72 if k % 2 else 56, 0.11, 0.22), 0.5 + k * 0.4)
    m.melody(1, [(74, 0.25), (76, 0.25), (79, 0.5), (76, 0.25), (74, 0.25), (72, 0.5), (69, 0.5), (72, 0.25), (74, 0.25), (76, 1.0)] * 8, 'dizi', 0.05)
    m.steps(0, 60, 4.4, 0.04)
    for t0 in (23.5, 25.0, 27.2): m.whoosh(t0, 0.5, 0.06)
    m.add(m.woodblock(700, 0.10), 28.6)
    for t0 in (32.0, 32.4, 47.0, 47.4, 232.6, 233.0): m.add(m.chime(note(96), 0.08), t0)
    m.giggle(33, 2.0, 0.03)
    m.squawk(50.0, 0.10)
    # the stuck boat
    m.pad(60, 50, [40, 47, 52], 0.025)
    for k in range(10): m.creak(63 + k * 2.6, 0.06); m.breath(63.5 + k * 2.6, 0.8, 0.05)
    m.add(m.drum(50, 0.20, 0.5), 75.4); m.add(m.drum(50, 0.20, 0.5), 76.6)
    for t0 in (78.0, 81.5, 84.0, 86.0, 87.5, 88.6, 89.4): m.crack(t0, 0.06 + 0.02 * (t0 - 78) / 4)
    m.shatter(90.0, 0.4); m.whoosh(90.05, 2.0, 0.2); m.rumble(90.1, 4.0, 0.3, 32)
    m.gliss(90.2, 62, 98, 0.03, 0.08)
    # the dragon: a thin whimper of strings, slow drips, a frightened heartbeat
    m.pad(100, 200, [45, 52, 57, 64], 0.028)
    m.drips(104, 300, 1.2, 0.04)
    for k in range(20): m.add(m.drum(44, 0.10, 0.6), 110 + k * 0.9)
    m.melody(118, [(64, 2.0), (63, 1.0), (64, 3.0), (None, 2.0), (67, 1.0), (66, 1.0), (64, 4.0)], 'erhu', 0.05)
    m.breath(117, 3.0, 0.10); m.breath(119.5, 1.5, 0.12)
    m.roar(118.5, 1.6, 0.06)
    m.melody(150, [(69, 2.0), (71, 1.0), (72, 3.0), (None, 2.0), (71, 1.0), (69, 1.0), (67, 4.0)], 'dizi', 0.04)
    m.gliss(174, 72, 93, 0.10, 0.04)
    m.add(m.bell(note(81), 5, 0.05), 175.5)
    m.zheng_phrase(178, [69, 72, 76, 79, 76, 72, 69, None, 72, 76, 81, None, 79, 76], 0.6, 0.08, 0.5, 4.0)
    m.melody(196, [(64, 3.0), (67, 1.0), (69, 2.0), (72, 4.0), (None, 2.0), (71, 2.0), (69, 4.0)], 'erhu', 0.045)
    for k, t0 in enumerate((203.2, 204.8, 206.4)): m.drip(t0, 0.10, 1200 + 100 * k)
    m.melody(240, [(69, 3.0), (67, 1.0), (64, 2.0), (62, 6.0), (None, 2.0), (64, 2.0), (67, 2.0), (69, 8.0)], 'dizi', 0.04)
    m.add(m.gong(7, 0.12, 70), 290)
    m.write(fn, 0.5, 3.0)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
