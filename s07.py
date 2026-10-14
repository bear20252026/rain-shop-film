# Scene 7 · Learning to Catch Weather · 学捉天气  (27:00 - 33:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_more import BRIDGE, deck_y, BR_STRANDS, BR_CX, LANE, LANE_G, laundry
from s01 import Q
from s05 import heat

DAWN = (0.92, 0.90, 0.94)
DRY = dict(water=0.0, sun=0.6, mist=0.4)
MIST = np.array([0.97, 0.95, 0.93], np.float32)
FIREFLY = np.array([0.45, 1.0, 0.85], np.float32)
STEP = 1620

def mist_blob(ctx, x, y, r, a, t=0.0, seed=0, world=True):
    """a soft lump of morning mist: a few overlapping glows that breathe"""
    for k in range(5):
        ang = seed * 1.7 + k * 1.26
        dx = math.cos(ang + t * 0.3) * r * 0.5; dy = math.sin(ang * 1.3 + t * 0.4) * r * 0.25
        ctx.add_glow(x + dx, y + dy, r * (0.55 + 0.15 * math.sin(t + k)), a * 0.09, MIST, world)

# ---------------------------------------------------------------- A: dawn, on the steps. "Teach me."
T_A = 0.0
def drawA(ctx, lt):
    T = ctx.Tabs; u = T
    town_live(ctx, 0.0, False, True, False, jars_glow=0.2, water=0.0)
    # Granny comes out of the door with the shutter pole, stops when she sees him
    gx, gph, gf = walk_x([(3, 1760), (7, 1690)], u, stride=30, s=1.12)
    leave = u > 46
    if leave:
        gx, gph, gf = walk_x([(46, 1690), (56, 1100)], u, stride=30, s=1.12)
    gp = dict(walk=gph, arm_f=(20, 30), arm_b=(15, 25), look=8 if u < 30 else 14, mouth='flat',
              eyes='closed' if 31 < u < 34.5 else 'open')
    ctx.fig(gx, Q, 1.12, 'granny', gf if gph is not None else -1, gp)
    # Xiaoman: sitting on the step hugging the ladle, jumps up to ask; looks down at his shoes; hops to swap them; runs after her
    stand = ease((u - 13) / 0.8)
    if u < 46:
        hop = abs(math.sin(u * 7)) * 10 if 42 < u < 45.5 else 0
        look = -24 if 38.5 < u < 46 else 8
        p = dict(crouch=0.6 * (1 - stand), arm_f=(60, 80) if u < 13 else (40, 50), arm_b=(40, 70), look=look, eyes='wide' if 38 < u < 41 else 'open',
                 mouth='frown' if 21 < u < 27 else 'flat', bob=hop, lean=-8 * (38.5 < u < 46))
        r = ctx.fig(STEP, Q - 4 * (1 - stand), 0.95, 'xiaoman', 1, p)
        if r: ladle(ctx, r['hand_f'], 150, 0, 0.95 * ctx.z)
    else:
        x, ph, f = walk_x([(47.5, STEP), (56, 1180)], u, stride=26, s=0.95)
        r = ctx.fig(x, Q, 0.95, 'xiaoman', -1, dict(walk=ph, arm_f=(60, 50), arm_b=(40, 50), lean=10, mouth='open'))
        if r: ladle(ctx, r['hand_f'], 150, 0, 0.95 * ctx.z)

# ---------------------------------------------------------------- B: lesson one, mist on the bridge
T_B = 56.0
XM_B, GR_B = 1260, 1520
def bridge_mist(ctx, T, u, flee=0.0, settle=0.0):
    rr = np.random.default_rng(7)
    nx = GR_B + 110; ny = deck_y(GR_B) - 140
    for k in range(14):
        bx = 700 + rr.random() * 1400; by = 200 + rr.random() * 260
        bx += math.sin(T * 0.15 + k) * 40
        if flee > 0 and abs(bx - XM_B) < 420:
            d = 1 if bx > XM_B else -1
            bx += d * flee * (300 + 200 * rr.random()); by -= flee * 120 * rr.random()
        a = 0.9 * (1 - 0.6 * flee * (abs(bx - XM_B) < 600))
        if settle > 0 and k < 6:      # these drift down into Granny's net and curl up
            s_ = ease(min(1, settle * (1.2 - k * 0.08)))
            bx = lerp(bx, nx + math.cos(k + T) * 14 * (1 - s_), s_); by = lerp(by, ny + math.sin(k + T) * 8, s_)
        mist_blob(ctx, bx, by, 70 - 40 * (settle > 0 and k < 6) * ease(settle), a, T, k)

def drawB(ctx, lt):
    T = ctx.Tabs; u = T - T_B
    strands(ctx, BR_STRANDS)
    flee = ease((u - 17) / 1.4) * (1 - ease((u - 26) / 4))
    settle = ease((u - 34) / 10) if u > 34 else 0.0
    bridge_mist(ctx, T, u, flee, settle)
    # they climb up from the left
    xx, ph, f = walk_x([(0, 700), (10, XM_B)], u, stride=26, s=1.8)
    swing = math.sin((u - 14) * 6) if 14 < u < 19 else 0
    r = ctx.fig(xx, deck_y(xx) + 2, 1.8, 'xiaoman', 1, dict(walk=ph, arm_f=(90 + 70 * swing, 20), arm_b=(80 + 70 * swing, 30), lean=6 + 10 * abs(swing),
                eyes='wide' if 18 < u < 24 else 'open', mouth='open' if 17.5 < u < 21 else 'frown' if 21 < u < 30 else 'flat', look=-10 if u > 30 else 0))
    if r: net(ctx, r['hand_f'], 30 + 80 * swing, 1.8 * ctx.z, 130)
    gx, gph, gf = walk_x([(1, 800), (12, GR_B)], u, stride=30, s=1.9)
    slow = ease((u - 30) / 6)
    rg = ctx.fig(gx, deck_y(gx) + 2, 1.9, 'granny', 1, dict(walk=gph, arm_f=(lerp(30, 120, slow), lerp(20, 10, slow)), arm_b=(lerp(20, 110, slow), 20), look=-6 * slow,
                 eyes='closed' if 36 < u < 46 else 'open', mouth='smile' if u > 46 else 'flat'))
    if rg and u > 24: net(ctx, rg['hand_f'], lerp(10, 60, slow), 1.9 * ctx.z, 130)
    if settle > 0.6:
        ctx.add_glow(GR_B + 110, deck_y(GR_B) - 140, 24, 0.25 * (settle - 0.6) / 0.4, MIST)

# ---------------------------------------------------------------- C: lesson two, a sunbeam in a teacup
T_C = 126.0
def drawC(ctx, lt):
    T = ctx.Tabs; u = T - T_C
    town_live(ctx, 0.0, False, True, False, jars_glow=0.15, water=0.0)
    shake = min(1, max(0, (u - 12) / 22)) * (1 if u < 34 else 0)
    jit = (math.sin(T * 37) + math.sin(T * 23)) * 5 * shake
    spill = u > 35.2
    tilt = ease((u - 35.2) / 0.4)
    r = ctx.fig(1560, Q, 0.95, 'xiaoman', 1, dict(arm_f=(100 + jit, 60 + jit * 0.5), arm_b=(95 - jit, 60), look=-14 if u < 33 else 4, eyes='wide' if 33.5 < u < 38 else 'open',
                mouth='open' if 33.5 < u < 37 else 'frown' if 38 < u < 45 else 'flat', lean=-4 * tilt))
    if r:
        hx, hy = r['hand_f']; se = 0.95 * ctx.z
        top = cup(ctx, (hx + 4 * se, hy + 2 * se + tilt * 4 * se), 0.95 * ctx.z * 1.3)
        beam = ease((u - 31) / 1.2) * (1 - tilt)
        if beam > 0:
            bx, by = top
            stream(ctx, (bx - 120 * se * (1 - beam), by - 900), (bx, by), beam, W_SUN, n=40, r=2.6 * ctx.z / 2.4 + 1.2, t=T, wob=0.6)
            ctx.add_glow(bx, by + 2 * se, 8 * se, 0.6 * beam, W_SUN, world=False)
        if spill:      # gold droplets splash out and fade on the stones
            v = u - 35.2
            for k in range(7):
                dx = (k - 3) * 9 * se * v * 2.4; dy = -30 * se * math.sin(min(1, v * 1.6) * math.pi * 0.7) + v * v * 120 * se
                if v < 1.8: ctx.add_glow(top[0] + dx, top[1] + dy, 3 * se, 0.7 * (1 - v / 1.8), W_SUN, world=False)
    # Granny on a stool by the door, sipping tea, watching
    sip = math.sin(min(1, max(0, (u - 6) / 3)) * math.pi)
    ctx.fig(1700, Q, 1.12, 'granny', -1, dict(crouch=0.6, arm_f=(lerp(60, 130, sip), lerp(80, 40, sip)), arm_b=(40, 60), look=8, eyes='happy' if 38 < u < 44 else 'open',
            mouth='smile' if 38 < u < 46 else 'flat'))

# ---------------------------------------------------------------- D: lesson three, fireflies in the lane
T_D = 186.0
def fireflies(ctx, T, cx, cy, n=24, spread=600, pull=0.0, target=None):
    for k in range(n):
        ph = k * 2.39
        x = cx + math.sin(T * 0.4 + ph) * spread * (0.4 + 0.6 * ((k * 37) % 10) / 10) + math.sin(T * 1.3 + ph * 2) * 30
        y = cy + math.cos(T * 0.33 + ph * 1.3) * 120 + math.sin(T * 1.7 + ph) * 20
        if target is not None and k < 9:
            s_ = ease(min(1, pull * (1.3 - k * 0.07)))
            x = lerp(x, target[0], s_); y = lerp(y, target[1], s_)
            if s_ > 0.98: continue
        blink = 0.5 + 0.5 * math.sin(T * 3 + ph * 3)
        ctx.add_glow(x, y, 3.5, 0.7 * blink, FIREFLY)
        ctx.add_glow(x, y, 14, 0.12 * blink, FIREFLY)

def drawD(ctx, lt):
    T = ctx.Tabs; u = T - T_D
    laundry(ctx, 0.05, 0.0)
    pull = ease((u - 14) / 14) if u > 14 else 0.0
    xm = 1700
    r = ctx.fig(xm, LANE_G, 1.8, 'xiaoman', 1, dict(arm_f=(100, 40), arm_b=(30, 40), look=-8, eyes='closed' if 18 < u < 26 else 'wide' if u > 30 else 'open',
                mouth='smile' if u > 31 else 'flat'))
    tgt = None
    if r:
        c = lantern(ctx, r['hand_f'], 1.8 * ctx.z * 0.6, 0.0, T)
        tgt = ((c[0] / ctx.z) + ctx.left, (c[1] / ctx.z) + ctx.top)
        cool = ease((u - 26) / 4)
        if cool > 0:
            ctx.add_glow(c[0], c[1], 10 * ctx.z, 0.7 * cool, BLUE, world=False)
            ctx.add_glow(c[0], c[1], 60 * ctx.z, 0.15 * cool, BLUE, world=False)
    fireflies(ctx, T, 1750, 520, 26, 700, pull, tgt)
    nod = math.sin(min(1, max(0, (u - 38) / 1.2)) * math.pi)
    ctx.fig(2050, LANE_G, 1.9, 'granny', -1, dict(arm_f=(30, 40), arm_b=(20, 30), look=6 + 14 * nod, eyes='closed' if 38 < u < 39.5 else 'open', mouth='smile' if u > 39 else 'flat'))

# ---------------------------------------------------------------- E: alone on the bridge; a tiny cloud
T_E = 236.0
def drawE(ctx, lt):
    T = ctx.Tabs; u = T - T_E
    strands(ctx, BR_STRANDS)
    xm = BR_CX
    breathe = math.sin(T * 0.9)
    hands = ease((u - 6) / 3)
    form = ease((u - 14) / 10)
    walking = u > 46
    if not walking:
        r = ctx.fig(xm, deck_y(xm) + 2, 1.8, 'xiaoman', 1, dict(arm_f=(lerp(15, 95, hands), lerp(20, 60, hands)), arm_b=(lerp(10, 90, hands), 60), look=lerp(0, -12, hands),
                    eyes='closed' if 8 < u < 22 else 'wide' if 22 < u < 30 else 'happy' if u > 30 else 'open', mouth='open' if 22 < u < 28 else 'smile' if u > 28 else 'flat',
                    bob=breathe * 2))
        if r and u > 12:
            px, py = r['hand_f']; se = 1.8 * ctx.z
            cx, cy = px + 8 * se, py - 34 * se
            if form < 1:     # little wisps drawn in from the evening air
                for k in range(8):
                    a = k * 0.785 + T * 0.8; d = (1 - form) * 160 * se
                    ctx.add_glow(cx + math.cos(a) * d, cy + math.sin(a) * d * 0.6, 6 * se, 0.35 * min(1, (u - 12) / 2) * (1 - form), MIST, world=False)
            if form > 0.2:
                L = ctx.layer(cx - 60 * se, cy - 60 * se, cx + 60 * se, cy + 60 * se)
                from figure import baozi as _bz
                _bz(L, cx, cy, T, se * 1.3 * ease((form - 0.2) / 0.8), 'happy' if u > 26 else 'sleepy')
    else:
        x, ph, f = walk_x([(46, xm), (64, 2300)], u, stride=26, s=1.8)
        r = ctx.fig(x, deck_y(x) + 2, 1.8, 'xiaoman', 1, dict(walk=ph, arm_f=(30, 40), arm_b=(30, 40), look=-14 if int(u) % 4 < 2 else 0, eyes='happy', mouth='smile'))
        bx = x - 60 - 30 * math.sin(T * 1.3); by = deck_y(x) - 250 + 20 * math.sin(T * 2.4)
        ctx.baozi(bx, by, 2.3, 'happy')

# ---------------------------------------------------------------- F: home. "It's following me!"  "Baozi."
T_F = 300.0
def drawF(ctx, lt):
    T = ctx.Tabs; u = T - T_F
    town_live(ctx, 0.0, False, True, False, jars_glow=0.35, water=0.0, night=0.3)
    x, ph, f = walk_x([(0, 1100), (4.5, 1580)], u, stride=26, s=0.95)
    jump = abs(math.sin(T * 6)) * 8 if 5 < u < 9 else 0
    r = ctx.fig(x, Q, 0.95, 'xiaoman', 1, dict(walk=ph, arm_f=(150 if 5 < u < 9 else 40, 20), arm_b=(30, 40), look=-10, eyes='happy', mouth='open' if u < 10 else 'smile', bob=jump))
    bx = x - 40 + 15 * math.sin(T * 1.3) + (30 if u > 5 else 0); by = Q - 150 + 10 * math.sin(T * 2.4)
    ctx.baozi(bx, by, 1.25, 'happy')
    laugh = 24 < u < 33
    lb = abs(math.sin(T * 9)) * 6 if laugh else 0
    ctx.fig(1690, Q, 1.12, 'granny', -1, dict(arm_f=(lerp(20, 60, laugh), 70 if laugh else 30), arm_b=(lerp(15, 60, laugh), 70 if laugh else 25),
            look=-6 if laugh else 2, eyes='happy' if laugh else 'open', mouth='open' if laugh else ('smile' if u > 31 else 'flat'), bob=lb, lean=-8 if laugh else 0))
    # the twins walking past on the quay; they freeze, mid-step, mouths open
    for k, spec in enumerate((None, TWIN_B)):
        tx, tph, tf = walk_x([(14, 2350 + k * 45), (24, 1960 + k * 45)], u, stride=22, s=0.9)
        frozen = 24 < u
        ctx.fig(tx, Q, 0.9, 'twin', -1, dict(walk=tph if not frozen else 0.25, arm_f=(40, 20) if not frozen else (120, 10), arm_b=(40, 20) if not frozen else (110, 10),
                eyes='wide' if frozen else 'open', mouth='open' if frozen else 'smile', look=-4), spec=spec, seed=30 + k)

def warm_dusk(lt):
    return (0.82, 0.86, 0.98)

shots = [
    # A · 0  dawn: the steps
    dict(dur=14, set=TOWN, cam=camkf([(0, (1640, 430, 1.5)), (14, (1650, 450, 1.7))]), draw=drawA, args=DRY, grade=DAWN, fade_in=(2.0, (0, 0, 0))),
    dict(dur=6, set=TOWN, cam=(1620, 490, 2.8), draw=drawA, args=DRY, grade=DAWN),                       # 14 "Teach me."
    dict(dur=6, set=TOWN, cam=(1690, 470, 2.6), draw=drawA, args=DRY, grade=DAWN),                       # 20 "You'll break it."
    dict(dur=7, set=TOWN, cam=(1620, 490, 2.8), draw=drawA, args=DRY, grade=DAWN),                       # 26
    dict(dur=9, set=TOWN, cam=camkf([(0, (1690, 470, 2.6)), (9, (1690, 475, 2.8))]), draw=drawA, args=DRY, grade=DAWN),   # 33 the long pause
    dict(dur=4, set=TOWN, cam=(1625, 560, 3.2), draw=drawA, args=DRY, grade=DAWN),                       # 42 his feet
    dict(dur=10, set=TOWN, cam=camkf([(0, (1600, 440, 1.5)), (10, (1300, 430, 1.4))]), draw=drawA, args=DRY, grade=DAWN),   # 46 he runs after her
    # B · 56  the mist on the bridge
    dict(dur=12, set=BRIDGE, cam=camkf([(0, (1200, 402, 1.0)), (12, (1300, 380, 1.06))]), draw=drawB, args=dict(water=0.0), grade=DAWN, xfade=1.5),
    dict(dur=16, set=BRIDGE, cam=camkf([(0, (1300, 290, 1.4)), (16, (1330, 285, 1.42))]), draw=drawB, args=dict(water=0.0), grade=DAWN),       # 68 he swings
    dict(dur=16, set=BRIDGE, cam=camkf([(0, (1520, 290, 1.4)), (16, (1560, 275, 1.48))]), draw=drawB, args=dict(water=0.0), grade=DAWN),       # 84 she waits
    dict(dur=12, set=BRIDGE, cam=camkf([(0, (1560, 262, 1.55)), (12, (1560, 258, 1.6))]), draw=drawB, args=dict(water=0.0), grade=DAWN),       # 100 the line
    dict(dur=14, set=BRIDGE, cam=camkf([(0, (1400, 310, 1.3)), (14, (1400, 330, 1.22))]), draw=drawB, args=dict(water=0.0), grade=DAWN),       # 112
    # C · 126  the teacup
    dict(dur=12, set=TOWN, cam=camkf([(0, (1640, 440, 1.6)), (12, (1630, 450, 1.8))]), draw=drawC, args=dict(DRY, sun=1.0), grade=(0.84, 0.94, 1.04), post=heat, xfade=1.5),
    dict(dur=18, set=TOWN, cam=camkf([(0, (1590, 480, 2.6)), (18, (1590, 485, 3.3))]), draw=drawC, args=dict(DRY, sun=1.0), grade=(0.84, 0.94, 1.04)),   # 138 shaking arms
    dict(dur=10, set=TOWN, cam=(1600, 470, 2.6), draw=drawC, args=dict(DRY, sun=1.0), grade=(0.84, 0.94, 1.04)),                                         # 156 the beam
    dict(dur=10, set=TOWN, cam=camkf([(0, (1620, 450, 1.8)), (10, (1640, 440, 1.6))]), draw=drawC, args=dict(DRY, sun=1.0), grade=(0.84, 0.94, 1.04)),   # 166 spill; she chuckles
    dict(dur=10, set=TOWN, cam=camkf([(0, (1640, 440, 1.6)), (10, (1640, 402, 1.0))]), draw=drawC, args=dict(DRY, sun=1.0), grade=(0.84, 0.94, 1.04), fade_out=(1.5, (0, 0, 0))),
    # D · 186  fireflies
    dict(dur=16, set=LANE, cam=camkf([(0, (1600, 402, 1.0)), (16, (1800, 420, 1.15))]), draw=drawD, grade=(0.62, 0.52, 0.48), fade_in=(1.5, (0, 0, 0))),
    dict(dur=18, set=LANE, cam=camkf([(0, (1720, 480, 2.0)), (18, (1730, 470, 2.3))]), draw=drawD, grade=(0.60, 0.50, 0.46)),
    dict(dur=8, set=LANE, cam=(2040, 470, 2.4), draw=drawD, grade=(0.60, 0.50, 0.46)),                                         # 220 she nods
    dict(dur=8, set=LANE, cam=camkf([(0, (1850, 450, 1.6)), (8, (1850, 420, 1.3))]), draw=drawD, grade=(0.60, 0.50, 0.46), fade_out=(1.5, (0, 0, 0))),
    # E · 236  the tiny cloud
    dict(dur=12, set=BRIDGE, cam=camkf([(0, (1400, 402, 1.0)), (12, (1400, 330, 1.25))]), draw=drawE, args=dict(water=0.0), grade=(0.66, 0.80, 0.98), fade_in=(1.5, (0, 0, 0))),
    dict(dur=16, set=BRIDGE, cam=camkf([(0, (1430, 190, 3.0)), (16, (1430, 180, 3.4))]), draw=drawE, args=dict(water=0.0), grade=(0.66, 0.80, 0.98)),   # 248 hands; it forms
    dict(dur=10, set=BRIDGE, cam=(1405, 185, 3.0), draw=drawE, args=dict(water=0.0), grade=(0.66, 0.80, 0.98)),                                       # 264 his face
    dict(dur=8, set=BRIDGE, cam=(1430, 200, 2.6), draw=drawE, args=dict(water=0.0), grade=(0.66, 0.80, 0.98)),                                        # 274 it stays
    dict(dur=18, set=BRIDGE, cam=lambda t: (lerp(1500, 2050, ease(t / 18)), 260, 1.6), draw=drawE, args=dict(water=0.0), grade=(0.66, 0.80, 0.98)),   # 282 it follows him
    # F · 300  home
    dict(dur=12, set=TOWN, cam=camkf([(0, (1350, 440, 1.5)), (12, (1600, 450, 1.6))]), draw=drawF, args=dict(DRY, sun=0.8), grade=(0.66, 0.78, 0.96), xfade=1.5),
    dict(dur=8, set=TOWN, cam=(1680, 480, 2.6), draw=drawF, args=dict(DRY, sun=0.8), grade=(0.66, 0.78, 0.96)),                                        # 312 "give it a name"
    dict(dur=6, set=TOWN, cam=(1580, 470, 2.6), draw=drawF, args=dict(DRY, sun=0.8), grade=(0.66, 0.78, 0.96)),                                        # 320 "...Baozi."
    dict(dur=8, set=TOWN, cam=camkf([(0, (1690, 470, 2.4)), (8, (1690, 470, 2.7))]), draw=drawF, args=dict(DRY, sun=0.8), grade=(0.66, 0.78, 0.96)),   # 326 she laughs
    dict(dur=8, set=TOWN, cam=(1990, 480, 2.4), draw=drawF, args=dict(DRY, sun=0.8), grade=(0.66, 0.78, 0.96)),                                        # 334 the twins freeze
    dict(dur=18, set=TOWN, cam=camkf([(0, (1750, 440, 1.4)), (18, (1700, 402, 1.0))]), draw=drawF, args=dict(DRY, sun=0.8),
         grade=lambda lt: (lerp(0.66, 0.50, lt / 18), lerp(0.78, 0.55, lt / 18), lerp(0.96, 0.80, lt / 18)), fade_out=(3.0, (0, 0, 0))),
]

subs = [
    (15.0, '教我。', 'Teach me.', 'xiaoman'),
    (21.0, '你会打碎。', "You'll break it.", 'granny'),
    (27.0, '那就教我别打碎。', 'Then teach me not to.', 'xiaoman'),
    (36.0, '……鞋子穿反了。', '...Your shoes are on the wrong feet.', 'granny'),
    (101.0, '天气不喜欢被追。要等它来。', "Weather doesn't like to be chased. Let it come to you.", 'granny'),
    (305.5, '外婆！它跟着我！', "Granny! It's following me!", 'xiaoman'),
    (313.0, '那就给它起个名字。', 'Then give it a name.', 'granny'),
    (321.5, '……包子。', '...Baozi.', 'xiaoman'),
]
scene = Scene(shots, subs)

def strands(ctx, anchors):
    from engine import strands as _s
    _s(ctx, anchors)

def sound(fn):
    m = Mix(scene.dur, 17)
    # dawn: a few birds even in the drought, cicadas starting
    m.birds(0, 56, 0.02); m.cicadas(10, 56, 0.015)
    m.creak(3.0, 0.07); m.steps(3, 7, 1.4, 0.025, True)
    m.pad(0, 56, [50, 57, 62], 0.02)
    m.add(m.guzheng(note(62), 3, 0.08), 15.2); m.add(m.guzheng(note(57), 3, 0.08), 21.2); m.add(m.guzheng(note(64), 3, 0.08), 27.3)
    m.add(m.woodblock(900, 0.05), 38.6)
    m.zheng_phrase(42, [74, 72, 74, 72, 69], 0.3, 0.07, 0.6)
    m.steps(46, 56, 3.6, 0.03)
    # the mist lesson
    m.pad(56, 70, [55, 62, 67, 71], 0.022)
    m.steps(56, 68, 1.6, 0.025)
    for k in range(4): m.whoosh(70 + k * 1.2, 0.7, 0.05)
    m.giggle(73.5, 3.0, 0.06)
    m.melody(90, [(79, 3.0), (76, 2.0), (74, 3.0), (71, 2.0), (74, 6.0)], 'dizi', 0.045)
    m.gliss(99, 67, 86, 0.09, 0.05)
    m.zheng_phrase(114, [67, 71, 74, 79, None, 74, 71], 0.5, 0.08, 0.5)
    # the teacup
    m.cicadas(126, 186, 0.025)
    m.tremolo(140, note(81), 17, 0.02)
    m.add(m.chime(note(93), 0.07), 157.0); m.gliss(157.2, 81, 96, 0.05, 0.05)
    m.breath(159.5, 1.2, 0.08)
    m.splash(161.3, 0.06); m.add(m.woodblock(1300, 0.05), 161.4)
    m.add(m.drum(60, 0.08, 0.4), 164.5)
    m.zheng_phrase(167, [64, None, 62, None, 60], 0.4, 0.07, 0.6)
    # fireflies: crickets and a slow zheng
    m.crickets(186, 236, 0.022)
    m.zheng_phrase(188, [69, None, 72, None, 76, None, None, 74, None, 72, None, None, 69, None, 76, None, 79, None, None, None, 76, None, 74, None, 72], 0.75, 0.07, 0.5, 4.0)
    m.pad(212, 24, [57, 64, 69], 0.025)
    m.add(m.bell(note(81), 4, 0.04), 216.5)
    # the tiny cloud
    m.pad(236, 64, [50, 57, 62, 66], 0.025)
    m.breath(244, 3.0, 0.04); m.breath(249, 3.0, 0.04); m.breath(254, 3.0, 0.04)
    m.gliss(252, 74, 98, 0.12, 0.04)
    m.add(m.chime(note(91), 0.06), 262.5); m.add(m.chime(note(95), 0.05), 263.0)
    m.melody(266, [(74, 1.0), (76, 1.0), (79, 2.0), (81, 1.0), (79, 1.0), (76, 2.0), (74, 4.0)], 'dizi', 0.05)
    m.zheng_phrase(282, [74, 76, 79, 76, 74, 76, 79, 81, 79, 76, 74, None, 74, 76, 79, 76], 0.4, 0.07, 0.5)
    m.steps(282, 300, 2.4, 0.02)
    # home: the laugh
    m.steps(300, 305, 4.0, 0.03)
    m.crickets(300, 360, 0.018)
    m.giggle(321.5, 2.0, 0.02)
    m.melody(323, [(79, 0.5), (81, 0.5), (84, 1.0), (81, 0.5), (79, 0.5), (76, 1.0), (79, 2.0)], 'dizi', 0.05)
    m.add(m.woodblock(800, 0.08), 334.2); m.add(m.woodblock(800, 0.08), 334.5)
    m.pad(334, 26, [55, 62, 67], 0.02)
    m.add(m.gong(5, 0.10, 75), 354)
    m.write(fn, 1.0, 2.5)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
