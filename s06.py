# Scene 6 · Boss Qian · 钱老板  (23:00 - 27:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_shop import SHOP, shop_live, FEET, ALTAR, red_jar, COUNTER
from sets_more import MUDFLAT, QIAN_BOAT, depth_s, MUD_HZ
from s01 import named_jars, Q, GRAN_IN, GRAN_Y
from s05 import HOT, heat

BALD = dict(hair='bald')
SILVER = np.array([0.95, 0.93, 0.88], np.float32)
PLANK_Y = 672

def chest(ctx, x, by, se, open_=0.0, world=True, over=False):
    """a lacquered chest with brass corners; open_ lifts the lid and silver light spills out"""
    if world: x, by = ctx.T(x, by); se = se * ctx.z
    w, h = 64 * se, 38 * se
    L = ctx.layer(x - w - 20, by - h - 60 * se, x + w + 20, by + 10, over=over)
    body = [(x - w, by - h), (x + w, by - h), (x + w, by), (x - w, by)]
    fill(L, body, 0.25, (0.22, 0.26, 0.62), 0.85, s=se, seed=971, gran=0.5)
    line(L, body + [body[0]], 2.0, se, 0.9, 0.2, 972, taper=False)
    line(L, [(x - w, by - h * 0.5), (x + w, by - h * 0.5)], 1.2, se, 0.6, 0, 973, taper=False)
    for cx in (x - w + 6 * se, x + w - 6 * se):
        fill(L, [(cx - 6 * se, by - h), (cx + 6 * se, by - h), (cx + 6 * se, by - h + 10 * se), (cx - 6 * se, by - h + 10 * se)], 0.05, (0.25, 0.72, 0.92), 0.9, s=se, seed=974)
    a = open_ * 1.9
    lid_back = (x - w, by - h)
    lid = [lid_back, (lid_back[0] + 2 * w * math.cos(a), lid_back[1] - 2 * w * math.sin(a)),
           (lid_back[0] + 2 * w * math.cos(a) + 14 * se * math.sin(a), lid_back[1] - 2 * w * math.sin(a) - 14 * se * math.cos(a)),
           (lid_back[0] + 14 * se * math.sin(a), lid_back[1] - 14 * se * math.cos(a))]
    fill(L, lid, 0.3, (0.22, 0.26, 0.62), 0.85, s=se, seed=975, gran=0.5)
    line(L, lid + [lid[0]], 2.0, se, 0.9, 0.2, 976, taper=False)
    if open_ > 0.2:
        for k in range(7):
            ctx.add_glow(x - w * 0.8 + k * w * 0.27, by - h - 2 * se, 10 * se, 0.5 * open_, SILVER, world=False)
        ctx.add_glow(x, by - h - 10 * se, 70 * se, 0.25 * open_, GOLD, world=False)

def porters_with_chest(ctx, x, y, s, ph, facing, open_=0.0, run=False, over=False):
    """two porters carrying the chest on a pole between them"""
    gap = 230 * s
    xa, xb = x - gap / 2, x + gap / 2
    lean = 14 if run else 4
    pose = dict(walk=ph, arm_f=(100, 10), arm_b=(100, 10), lean=lean * facing * 0 + lean, mouth='open' if run else 'flat', eyes='wide' if run else 'open')
    ra = ctx.fig(xa, y, s, 'porter', facing, pose, seed=31, over=over)
    rb = ctx.fig(xb, y, s, 'porter', facing, dict(pose, walk=(ph + 0.5) if ph is not None else None), seed=32, spec=dict(top=(0.20, (0.66, 0.72, 0.78), 0.6)), over=over)
    if ra and rb:
        ha, hb = ra['hand_f'], rb['hand_f']
        L = ctx.layer(min(ha[0], hb[0]) - 10, min(ha[1], hb[1]) - 10, max(ha[0], hb[0]) + 10, max(ha[1], hb[1]) + 10, over=over)
        line(L, [ha, hb], 2.6, s * ctx.z, 0.85, 0.3, 980, taper=False)
        mx, my = (ha[0] + hb[0]) / 2, (ha[1] + hb[1]) / 2
        chest(ctx, mx, my + 60 * s * ctx.z, s * 0.9, open_, world=False, over=over)

# ---------------------------------------------------------------- A: the painted boat stuck on the mud
def drawA(ctx, lt):
    T = ctx.Tabs
    x, ph, f = walk_x([(4, 2380), (30, 1350)], T, stride=40, s=1.25)
    s = depth_s(PLANK_Y)
    fanning = math.sin(T * 5)
    r = ctx.fig(x, PLANK_Y, s * 1.04, 'qian', f if ph is not None else -1, dict(walk=ph, arm_f=(50 + 10 * fanning, 80), arm_b=(20, 30), look=-4, mouth='smile'))
    fd = f if ph is not None else -1
    if r: fan(ctx, r['hand_f'], fd * (55 + 20 * fanning), s * ctx.z)
    px, pph, pf = walk_x([(7, 2560), (33, 1530)], T, stride=40, s=1.25)
    porters_with_chest(ctx, px, PLANK_Y + 4, s, pph, -1)

# ---------------------------------------------------------------- B: in the shop; the offer
T_B = 30.0
CHEST_X = 690
def granny_counter(ctx, T, pose=None):
    p = dict(arm_f=(15, 20), arm_b=(10, 20), look=-4, mouth='flat')
    p.update(pose or {})
    return ctx.fig(GRAN_IN, GRAN_Y, 2.1, 'granny', -1, p)

def drawB(ctx, lt):
    T = ctx.Tabs; u = T - T_B
    shop_live(ctx, glow=0.6, giggle=False, rain_door=0.0, red=True, empty=0.78)
    named_jars(ctx, 0.5, skip=('梅雨', '虎丘雷'))
    gp = dict(look=-4, eyes='closed' if 18.5 < u < 19.4 else 'open', mouth='frown' if u > 10 else 'flat')
    if 32 < u < 40: gp.update(arm_f=(60, 80), arm_b=(60, 80))       # arms folded
    granny_counter(ctx, T, gp)
    # Xiaoman at the end of the counter, peeking
    ctx.fig(1540, FEET - 10, 1.9, 'xiaoman', -1, dict(look=-6, arm_f=(20, 30), eyes='wide' if 6 < u < 14 else 'open', mouth='open' if 7 < u < 10 else 'flat'))
    # porters carry the chest in and set it down
    px, pph, pf = walk_x([(0, 120), (7, CHEST_X)], u, stride=34, s=2.0)
    if u < 8:
        porters_with_chest(ctx, px, FEET + 30, 2.0, pph, 1, over=True)
    else:
        opn = ease((u - 10) / 1.2)
        chest(ctx, CHEST_X, FEET + 34, 2.0, opn, over=True)
        for k, (xx, spec) in enumerate([(CHEST_X - 200, None), (CHEST_X - 300, dict(top=(0.20, (0.66, 0.72, 0.78), 0.6)))]):
            ctx.fig(xx, FEET + 30, 2.0, 'porter', 1, dict(arm_f=(10, 10), look=6 if k == 0 else -2), seed=31 + k, spec=spec, over=True)
    # Qian sweeps in ahead of them, bows with the fan, then makes his pitch
    x, ph, f = walk_x([(0, 300), (5, 900)], u, stride=36, s=2.1)
    pitch = 22 < u < 32
    bow = math.sin(min(1, max(0, (u - 6) / 1.6)) * math.pi)
    fl = math.sin(T * 3)
    qp = dict(walk=ph, arm_f=(110 + 20 * fl if pitch else 50, 80 if not pitch else 40), arm_b=(20 if not pitch else 120 + 20 * fl, 30 if not pitch else 20), lean=16 * bow + 6 * pitch,
              mouth='smile', eyes='happy' if 6 < u < 9 or pitch else 'open', look=-6 * bow)
    r = ctx.fig(x, FEET + 34, 2.1, 'qian', 1, qp, over=True)
    if r: fan(ctx, r['hand_f'], 40 + 30 * fl if pitch else 55 + 20 * math.sin(T * 5), 2.1 * ctx.z, over=True)

# ---------------------------------------------------------------- C: Qian strolls the shelves; the red jar; the broom
T_C = 80.0
def drawC(ctx, lt):
    T = ctx.Tabs; u = T - T_C
    shop_live(ctx, glow=0.6, giggle=False, rain_door=0.0, red=True, empty=0.78)
    named_jars(ctx, 0.5, skip=('梅雨', '虎丘雷'))
    chest(ctx, CHEST_X, FEET + 34, 2.0, 1.0, over=True)
    for k, (xx, spec) in enumerate([(CHEST_X - 200, None), (CHEST_X - 300, dict(top=(0.20, (0.66, 0.72, 0.78), 0.6)))]):
        ctx.fig(xx, FEET + 30, 2.0, 'porter', 1, dict(arm_f=(10, 10), look=-2), seed=31 + k, spec=spec, over=True)
    # Qian: stroll, tap a jar with the fan, stroll on, stop dead at the altar
    x, ph, f = walk_x([(0, 900), (6, 1150), (9, 1150), (16, 1500), (19, 1500), (26, 1790)], u, stride=36, s=2.1)
    tap = (6.5 < u < 8.5) or (16.5 < u < 18.5)
    stopped = u > 26
    qp = dict(walk=ph, arm_f=(150 if tap else 20 if stopped else 50, -20 if tap else 30 if stopped else 80), arm_b=(20, 30), look=-14 if tap else (-2 if not stopped else 4), mouth='smile' if not stopped else 'open' if 30 < u < 32 else 'smile',
              eyes='wide' if 26 < u < 28 else 'squint' if 28 < u < 36 else 'open', lean=8 if stopped else 0)
    r = ctx.fig(x, FEET + 34, 2.1, 'qian', 1, qp, over=True)
    if r: fan(ctx, r['hand_f'], 10 if tap else 175 if stopped else 55 + 20 * math.sin(T * 5), 2.1 * ctx.z, open_=0.2 if tap or stopped else 1.0, over=True)
    # Granny follows at a distance; at "the red one" she goes for the broom by the stairs
    gx, gph, gf = walk_x([(10, GRAN_IN), (14, 1250), (26, 1500), (36, 1500), (39.5, 1660)], u, stride=30, s=2.1)
    grab = ease((u - 39.5) / 1.0)
    gp = dict(walk=gph, arm_f=(lerp(20, 140, grab), lerp(20, 10, grab)), arm_b=(lerp(10, 130, grab), lerp(20, 10, grab)), mouth='frown', look=4,
              eyes='squint' if u > 36 else 'open')
    rg = ctx.fig(gx, FEET + 20, 2.1, 'granny', 1, gp)
    if rg and grab > 0: broom(ctx, rg['hand_f'], 150 - 40 * grab, 2.1 * ctx.z)
    elif u < 40: broom(ctx, ctx.T(1700, FEET - 70), 172, 2.1 * ctx.z)       # leaning on the wall
    ctx.fig(1300, FEET - 10, 1.9, 'xiaoman', 1, dict(look=4, arm_f=(20, 30), eyes='wide' if u > 26 else 'open'))
    if u > 26: ctx.add_glow(ALTAR[0], ALTAR[1] - 40, 16, 0.10, W_DRAGON)

# ---------------------------------------------------------------- D: the broom chase
T_D = 128.0
def drawD(ctx, lt):      # in the shop: Granny sweeps them out
    T = ctx.Tabs; u = T - T_D
    shop_live(ctx, glow=0.6, giggle=False, rain_door=0.0, red=True, empty=0.78)
    named_jars(ctx, 0.5, skip=('梅雨', '虎丘雷'))
    hop = abs(math.sin(T * 7))
    x, ph, f = walk_x([(0, 1640), (1.0, 1640), (9, 150)], u, stride=34, s=2.1)
    r = ctx.fig(x, FEET + 34 - 20 * hop * (u > 1), 2.1, 'qian', -1, dict(walk=ph, arm_f=(150, 40), arm_b=(150, 60), lean=14, mouth='open', eyes='wide'), over=True)
    if r: fan(ctx, r['hand_f'], -10 + 40 * math.sin(T * 9), 2.1 * ctx.z, over=True)
    px, pph, pf = walk_x([(1.5, 900), (8, -50)], u, stride=34, s=2.0)
    porters_with_chest(ctx, px, FEET + 30, 2.0, pph, -1, run=True, over=True)
    gx, gph, gf = walk_x([(0.5, 1720), (11, 330)], u, stride=30, s=2.1)
    sw = math.sin(T * 6.5)
    rg = ctx.fig(gx, FEET + 20, 2.1, 'granny', -1, dict(walk=gph, arm_f=(100 + 30 * sw, 10), arm_b=(90 + 30 * sw, 10), lean=10, mouth='frown', eyes='squint'))
    if rg: broom(ctx, rg['hand_f'], -60 - 50 * sw, 2.1 * ctx.z)
    ctx.fig(1420, FEET - 10, 1.9, 'xiaoman', -1, dict(look=-4, arm_f=(150 + 20 * math.sin(T * 8), 20), arm_b=(150 - 20 * math.sin(T * 8), 20), eyes='happy', mouth='open', bob=hop * 6))

T_D2 = 150.0
def drawD2(ctx, lt):     # on the quay: Old Ink pecks Qian's hat off
    T = ctx.Tabs; u = T - T_D2
    town_live(ctx, 0.0, False, True, False, jars_glow=0.2, water=0.0, cormorant=False)
    peck = u > 6.2
    x, ph, f = walk_x([(0, 1560), (6.0, 2040), (7.2, 2070), (9.5, 2300), (14, 2800)], u, stride=34, s=1.05)
    stumble = math.exp(-((u - 6.6) / 0.5) ** 2)
    r = ctx.fig(x, Q, 1.05, 'qian', 1, dict(walk=ph, arm_f=(150, 40), arm_b=(150, 60), lean=14 + 20 * stumble, mouth='open', eyes='wide'), spec=BALD if peck else None)
    # Old Ink: lunges at the passing hat
    lunge = math.exp(-((u - 6.0) / 0.35) ** 2)
    ctx.cormorant(2092 - 30 * lunge, WATER_Y - 62 + 10 * lunge, 1.0, look=-0.6 * lunge + 0.3 * (u > 7))
    if peck:      # the hat sails off, spinning, and lands on the mud
        v = min(1, (u - 6.2) / 2.2)
        hx = 2060 - 260 * v; hy = Q - 120 - 160 * math.sin(v * math.pi) + 240 * v * v
        sx, sy = ctx.T(hx, hy)
        flying_hat(ctx, sx, sy, (u - 6.2) * 6 * (1 - v), 0.55 * ctx.z, front=False)
    px, pph, pf = walk_x([(2.5, 1500), (13, 2800)], u, stride=34, s=1.0)
    porters_with_chest(ctx, px, Q, 1.0, pph, 1, run=True)
    # Granny at the door, broom grounded; Xiaoman laughing beside her
    rg = ctx.fig(1600, Q, 1.12, 'granny', 1, dict(arm_f=(70, 20), arm_b=(60, 20), mouth='flat' if u < 8 else 'smile', eyes='squint' if u < 8 else 'happy'))
    if rg: broom(ctx, rg['hand_f'], 10, 1.12 * ctx.z)
    hop = abs(math.sin(T * 8)) * (u > 7)
    ctx.fig(1530, Q, 0.95, 'xiaoman', 1, dict(arm_f=(150, 20), arm_b=(140, 20), eyes='happy' if u > 7 else 'wide', mouth='open', bob=hop * 8))

# ---------------------------------------------------------------- E: back on his boat
def drawE(ctx, lt):      # porters heave the chest aboard; Qian, hatless, climbs up
    T = ctx.Tabs; u = lt
    x, ph, f = walk_x([(0, 1700), (9, 2380)], u, stride=40, s=1.25)
    s = depth_s(PLANK_Y)
    ctx.fig(x, PLANK_Y, s * 1.04, 'qian', f, dict(walk=ph, arm_f=(20, 30), arm_b=(20, 30), look=6, mouth='frown'), spec=BALD)
    px, pph, pf = walk_x([(0, 1980), (10, 2420)], u, stride=40, s=1.25)
    porters_with_chest(ctx, px, PLANK_Y + 4, s, pph, 1)

def drawE2(ctx, lt):     # close: from the deck he looks back, eyes narrowing
    T = ctx.Tabs
    fl = math.sin(T * 1.2)
    r = ctx.fig(2560, 596, 1.5, 'qian', -1, dict(arm_f=(50 + 6 * fl, 80), arm_b=(30, 40), look=4, eyes='squint' if lt > 4 else 'open', mouth='smile' if lt > 8 else 'flat'), spec=BALD)
    if r: fan(ctx, r['hand_f'], -(55 + 12 * fl), 1.5 * ctx.z)

def drawE3(ctx, lt):     # wide at dusk: the painted boat, the little town far away, a lantern lit on the cabin
    T = ctx.Tabs
    ctx.fig(2560, 596, 1.5, 'qian', -1, dict(arm_f=(50, 80), arm_b=(30, 40), look=0, eyes='squint'), spec=BALD)
    ctx.add_glow(QIAN_BOAT[0] - 190, QIAN_BOAT[1] - 100, 10, 0.7 * ease((lt - 6) / 3), WARM)
    ctx.add_glow(QIAN_BOAT[0] + 170, QIAN_BOAT[1] - 70, 10, 0.7 * ease((lt - 8) / 3), WARM)
    for k in range(6):
        ctx.add_glow(200 + k * 160, MUD_HZ - 30 - (k % 3) * 8, 3, 0.5 * ease((lt - 10 - k) / 3), WARM)

def dusk(lt):
    u = ease(lt / 20)
    return (lerp(0.80, 0.50, u), lerp(0.93, 0.55, u), lerp(1.04, 0.90, u))

SUNA = dict(sun=1.0, mist=0.0, water=0.0)
shots = [
    # A · 0  the painted boat, stuck where the water ends
    dict(dur=12, set=MUDFLAT, cam=camkf([(0, (2500, 402, 1.0)), (12, (2350, 402, 1.0))]), draw=drawA, grade=HOT, post=heat, fade_in=(2.0, (0, 0, 0))),
    dict(dur=9, set=MUDFLAT, cam=camkf([(0, (2050, 520, 1.6)), (9, (1850, 520, 1.6))]), draw=drawA, grade=HOT, post=heat),
    dict(dur=9, set=MUDFLAT, cam=camkf([(0, (1700, 420, 1.1)), (9, (1500, 410, 1.05))]), draw=drawA, grade=HOT, post=heat),
    # B · 30  in the shop: a chest of silver
    dict(dur=14, set=SHOP, cam=camkf([(0, (700, 402, 1.2)), (14, (820, 420, 1.3))]), draw=drawB, grade=HOT, xfade=1.0),
    dict(dur=8, set=SHOP, cam=(1110, 470, 2.4), draw=drawB, grade=HOT),                                                       # 44 "Granny Yun!"
    dict(dur=4, set=SHOP, cam=(1110, 470, 2.6), draw=drawB, grade=HOT),                                                       # 52
    dict(dur=12, set=SHOP, cam=camkf([(0, (850, 440, 1.8)), (12, (870, 440, 1.9))]), draw=drawB, grade=HOT),                   # 56 the pitch
    dict(dur=12, set=SHOP, cam=camkf([(0, (1100, 470, 2.4)), (12, (1110, 470, 2.6))]), draw=drawB, grade=HOT),                 # 68 "Weather isn't merchandise."
    # C · 80  he strolls the shelves
    dict(dur=26, set=SHOP, cam=camkf([(0, (950, 402, 1.5)), (26, (1750, 402, 1.5))]), draw=drawC, grade=HOT),
    dict(dur=10, set=SHOP, cam=camkf([(0, (1850, 440, 1.9)), (10, (1870, 450, 2.0))]), draw=drawC, grade=HOT),                 # 106 the red one
    dict(dur=6, set=SHOP, cam=(1520, 460, 2.5), draw=drawC, grade=HOT),                                                       # 116 Granny
    dict(dur=6, set=SHOP, cam=(1690, 450, 2.2), draw=drawC, grade=HOT),                                                       # 122 "Out."
    # D · 128  the broom
    dict(dur=12, set=SHOP, cam=camkf([(0, (1300, 402, 1.05)), (12, (700, 402, 1.05))]), draw=drawD, grade=HOT),
    dict(dur=10, set=SHOP, cam=(400, 402, 1.2), draw=drawD, grade=HOT, set_t0=0),
    dict(dur=16, set=TOWN, cam=camkf([(0, (1800, 440, 1.4)), (16, (2000, 440, 1.4))]), draw=drawD2, args=SUNA, grade=HOT, post=heat),
    dict(dur=7, set=TOWN, cam=(1580, 470, 2.4), draw=drawD2, args=SUNA, grade=HOT, post=heat),                                 # 166 Granny and Xiaoman laugh
    dict(dur=12, set=TOWN, cam=camkf([(0, (2092, 480, 2.6)), (12, (2050, 500, 2.4))]), draw=drawD2, args=SUNA, grade=HOT, post=heat),   # 173 Old Ink, smug
    # E · 185  back on his boat
    dict(dur=14, set=MUDFLAT, cam=camkf([(0, (2100, 430, 1.1)), (14, (2350, 420, 1.1))]), draw=drawE, grade=HOT, post=heat, xfade=1.0),
    dict(dur=14, set=MUDFLAT, cam=camkf([(0, (2570, 440, 2.6)), (14, (2565, 445, 2.9))]), draw=drawE2, grade=(0.70, 0.82, 1.0)),       # 199
    dict(dur=27, set=MUDFLAT, cam=camkf([(0, (2400, 420, 1.3)), (27, (1800, 402, 1.0))]), draw=drawE3, grade=dusk, xfade=1.5, fade_out=(4.0, (0, 0, 0))),
]

subs = [
    (45.0, '云婆婆！久仰！我出一箱银子，买你店里所有的天气。', 'Granny Yun! An honor! A chest of silver for every weather in your shop.', 'qian'),
    (52.5, '不卖。', 'Not for sale.', 'granny'),
    (57.0, '城里人要太阳拍照，要雪办婚礼——你的罐子能发大财！', 'City people want sunshine for photos and snow for weddings. Your jars could make a fortune!', 'qian'),
    (70.0, '天气不是货。', "Weather isn't merchandise.", 'granny'),
    (110.0, '那个红的呢？我出双倍。', "And the red one? I'll pay double.", 'qian'),
    (122.5, '出去。', 'Out.', 'granny'),
    (205.0, '越不卖，越值钱。', 'The more she refuses, the more it’s worth.', 'qian'),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 16)
    m.cicadas(0, 30, 0.03); m.wind(0, 30, 0.02, 300, 1500)
    # Qian's swagger: plucked strings, a little drum, woodblock steps
    for k in range(10): m.add(m.woodblock(600 + 80 * (k % 2), 0.05), 4 + k * 2.6)
    m.zheng_phrase(3, [60, 64, 67, 72, None, 67, 64, None, 60, 64, 67, 72, 76, None, None, None], 0.35, 0.09, 0.5)
    m.steps(7, 30, 1.6, 0.03)
    # in the shop
    m.steps(30, 37, 2.0, 0.04); m.add(m.drum(60, 0.25, 0.5), 38.0)
    m.creak(40.0, 0.08); m.add(m.chime(note(91), 0.07), 40.4); m.add(m.chime(note(95), 0.06), 40.7); m.add(m.chime(note(98), 0.05), 41.0)
    m.pad(44, 36, [43, 50], 0.02)
    m.add(m.woodblock(400, 0.12), 52.6)
    m.zheng_phrase(57, [67, 69, 72, 74, 76, 74, 72, 69], 0.4, 0.08, 0.5)
    m.add(m.guzheng(note(45), 4, 0.12), 70.0)
    # stroll: tap tap on the jars, then silence at the altar
    m.steps(80, 106, 1.6, 0.025)
    m.add(m.chime(note(84), 0.06), 87.0); m.add(m.chime(note(86), 0.05), 97.0)
    m.rumble(106.5, 3.0, 0.12, 36)
    m.add(m.bell(note(62), 4, 0.04), 110.2)
    m.add(m.drum(52, 0.2, 0.6), 119.6); m.add(m.drum(52, 0.25, 0.6), 122.4)
    # the chase: fast drum and dizi, broom swishes
    for k in range(40): m.add(m.drum(80 if k % 2 else 65, 0.10, 0.25), 128 + k * 0.42)
    m.melody(128.3, [(76, 0.25), (79, 0.25), (81, 0.25), (79, 0.25), (76, 0.25), (74, 0.25), (72, 0.5), (74, 0.25), (76, 0.25), (79, 0.5), (81, 0.25), (84, 0.5)] * 3, 'dizi', 0.05)
    for k in range(14): m.sweep(128.6 + k * 0.7, 0.06)
    m.steps(128, 166, 4.0, 0.04)
    m.squawk(156.0, 0.14); m.whoosh(156.3, 0.8, 0.08)
    m.giggle(157.5, 3.0, 0.05)
    m.add(m.woodblock(500, 0.12), 158.6)
    m.cicadas(166, 199, 0.03)
    m.snort(178.0, 0.06)
    # back aboard: low and sly
    m.steps(185, 196, 1.4, 0.03)
    m.pad(199, 41, [38, 45, 49], 0.03)
    m.melody(203, [(57, 1.5), (56, 0.5), (57, 2.0), (None, 1.0), (60, 1.0), (59, 0.5), (57, 3.0)], 'erhu', 0.05)
    m.add(m.drum(45, 0.18, 1.0), 207.0); m.add(m.drum(45, 0.18, 1.0), 209.0)
    m.crickets(214, 240, 0.02)
    m.add(m.gong(6, 0.10, 65), 234)
    m.write(fn, 1.0, 2.5)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
