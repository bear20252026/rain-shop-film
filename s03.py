# Scene 3 · The Giggling Breeze · 笑风  (10:00 - 14:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_shop import SHOP, shop_live, FEET, ALTAR, GIGGLE_JAR, COUNTER
from sets_more import LANE, LANE_G, laundry, BRIDGE, deck_y, BR_STRANDS
from s01 import named_jars, Q

GJX, GJY = GIGGLE_JAR
XM_BEHIND = 1080          # Xiaoman sweeping behind the counter
MORNING = (1.0, 1.0, 1.0)

def jar_fall(T, t0=24.5):
    """the giggling-breeze jar tips, falls and breaks: returns (x, y, rot, broken)"""
    if T < t0: return GJX, GJY - 2, 0.0, False
    u = (T - t0)
    if u < 0.5: return GJX + u * 20, GJY - 2, -u * 30, False         # wobble, tipping
    v = min(1.0, (u - 0.5) / 0.55)
    return GJX + 10 + v * 50, GJY - 2 + v * v * (FEET - 30 - GJY), -15 - v * 160, v >= 1.0

def shards(ctx, x, y, n=7, spread=1.0):
    t = ctx.Tabs; L = ctx.box(x, y, 90, 30)
    for k in range(n):
        dx = (k - n / 2) * 12 * spread + math.sin(k * 3.1) * 8; dy = math.cos(k * 2.3) * 4
        sx, sy = ctx.T(x + dx, y + dy); se = ctx.z
        poly = [(sx, sy - 6 * se), (sx + 9 * se, sy - 2 * se), (sx + 4 * se, sy + 3 * se), (sx - 5 * se, sy + 2 * se)]
        fill(L, poly, 0.06, CELADON, 0.7, s=se, seed=800 + k)
        line(L, poly + [poly[0]], 1.0, se, 0.85, 0, 810 + k, taper=False)

# ---------------------------------------------------------------- A: sweeping; the jar falls; the breeze escapes
def drawA(ctx, lt):
    T = ctx.Tabs
    shop_live(ctx, giggle=False, rain_door=0.0, glow=0.8)
    named_jars(ctx, 0.8)
    jx, jy, rot, broken = jar_fall(T)
    if not broken:
        L = ctx.box(jx, jy - 20, 40, 40)
        sx, sy = ctx.T(jx, jy)
        from chars import jar as _j
        _j(L, sx, sy, 0.75 * ctx.z, 77)
        if rot:
            M = cv2.getRotationMatrix2D((sx - L.x0, sy - L.y0 - 15 * ctx.z), rot, 1.0); h, w = L.D.shape
            L.D = cv2.warpAffine(L.D, M, (w, h)); L.M = cv2.warpAffine(L.M, M, (w, h)); L.tints = [(cv2.warpAffine(a, M, (w, h)), c) for a, c in L.tints]
        ctx.add_glow(jx, jy - 15, 9, 0.35, W_BREEZE)
    else:
        shards(ctx, jx, FEET - 30)
    # Xiaoman sweeping with big, eager strokes; the handle swings up into the shelf
    sw = math.sin(T * 2.6) if T < 24 else math.sin(24 * 2.6) * (1 - ease((T - 24) / 1.0))
    x, ph, f = walk_x([(0, 900), (10, 980), (14, 980), (22, XM_BEHIND)], T, s=1.9)
    eyes = 'wide' if 25 < T < 33 else 'open'
    r = ctx.fig(x, 690, 1.9, 'xiaoman', 1, dict(arm_f=(40 + 25 * sw, 20), arm_b=(30 + 25 * sw, 30), walk=ph, eyes=eyes, mouth='open' if 25.5 < T < 32 else 'flat', look=10 if T > 24.5 else -6))
    if r:
        swing = (-30 + 45 * sw) if T < 23 else lerp(-30 + 45 * math.sin(23 * 2.6), 150, ease((T - 23) / 0.9)) * (1 - ease((T - 26) / 1.5)) + (-10) * ease((T - 26) / 1.5)
        broom_long(ctx, r['hand_f'], swing, 1.9 * ctx.z)
    if broken:
        u = T - 25.6
        for k in range(3):
            pts = breeze_path(T, jx + u * 60 * (1 + k * 0.3), FEET - 60 - u * 25 - k * 30, 60 + u * 30, 30 + u * 10, 30, k, k * 2)
            breeze(ctx, pts, min(1, u / 0.8) * 0.9)
    gx = 380 if T < 30 else 380
    ctx.fig(330, FEET + 30, 2.0, 'granny', 1, dict(look=6 if T > 25.3 else -4, eyes='wide' if 25.3 < T < 30 else 'open', arm_f=(30, 40)), over=True)

def broom_long(ctx, hand, ang, se):
    """the shop broom, long handle: ang = handle angle from straight up (head end swings opposite)"""
    a = math.radians(ang); d = np.array([math.sin(a), -math.cos(a)])
    top = np.array(hand) + d * 110 * se; head = np.array(hand) - d * 60 * se
    L = ctx.layer(min(top[0], head[0]) - 60 * se, min(top[1], head[1]) - 60 * se, max(top[0], head[0]) + 60 * se, max(top[1], head[1]) + 60 * se)
    line(L, [tuple(top), tuple(head)], 2.6, se, 0.85, 0.3, 461, taper=False)
    n = np.array([d[1], -d[0]])
    for k in range(-5, 6):
        e = head - d * 40 * se + n * k * 4.5 * se
        line(L, [tuple(head + n * k * 1.2 * se), tuple(e)], 1.1, se, 0.7, 0.4, 470 + k)

# ---------------------------------------------------------------- B: chaos in the lane
def drawB(ctx, lt):
    T = ctx.Tabs; u = T - 33
    gust = 0.5 + 0.5 * math.sin(u * 1.3)
    laundry(ctx, 0.6, gust)
    head_x = 900 + u * 70
    pts = breeze_path(T, head_x, 470, 260, 110, 44, 1)
    breeze(ctx, pts, 1.0)
    # the poet's pages swirl down the lane; his hat goes too
    for k in range(9):
        ph = k * 0.7
        px = head_x - 120 + math.cos(T * 2.0 + ph) * 160 + k * 30; py = 430 + math.sin(T * 2.6 + ph) * 90 - k * 6
        flying_sheet(ctx, *ctx.T(px, py), T * 3 + ph, 1.5 * ctx.z)
    px, ph, f = walk_x([(33, 1250), (40, 1450)], T, s=1.8)
    r = ctx.fig(px, LANE_G, 1.8, 'poet', 1, dict(walk=ph, arm_f=(150, -20), arm_b=(140, 10), eyes='wide', mouth='open', lean=-6))
    flying_hat(ctx, *ctx.T(head_x + 80 + math.sin(T * 3) * 40, 380 + math.cos(T * 2.4) * 40), T * 4, 1.6 * ctx.z)
    # the lotus-seed twins, lifted off their feet, laughing
    for k, (bx, spec) in enumerate(((1700, None), (1790, TWIN_B))):
        lift = max(0, math.sin(min(1, max(0, (T - 36 - k * 0.4) / 9)) * math.pi)) * 90
        ctx.fig(bx + math.sin(T * 2 + k) * 20, LANE_G - lift, 1.8, 'twin', 1 - 2 * k, dict(eyes='happy', mouth='open', arm_f=(160, 0), arm_b=(150, 0)),
                rot=math.sin(T * 3 + k) * 25 * (lift / 90), spec=spec, seed=30 + k)
    # a vendor's straw basket lid spins away
    flying_hat(ctx, *ctx.T(head_x - 200 + math.sin(T * 2.2) * 30, 520 - (u * 12) % 160), -T * 5, 1.2 * ctx.z)

def drawB2(ctx, lt):    # Old Ink spun round his post
    T = ctx.Tabs
    town_live(ctx, rain_amt=0.0, drips_on=False, ripples_on=False, cormorant=False)
    u = ease(lt / 4.0)
    a = u * 2 * math.pi
    px, py = 2092, WATER_Y - 62
    x = px + math.sin(a) * 60; y = py - math.sin(a * 0.5) * 50
    ctx.cormorant(x, y, 1.0, look=1.0 if math.cos(a) > 0 else 0.0)
    pts = breeze_path(T, px, py - 60, 120, 60, 36, 3)
    breeze(ctx, pts, 0.9)
    for k in range(5):
        ctx.add_glow(*ctx.T(px + math.sin(T * 4 + k) * 70, py - 40 + math.cos(T * 3 + k) * 30), 3, 0.4, W_BREEZE, world=False)

# ---------------------------------------------------------------- C: Granny coaxes the breeze back with a fan
T_C = 60.0
def drawC(ctx, lt):
    T = ctx.Tabs; u = T - T_C
    town_live(ctx, rain_amt=0.0, drips_on=False, ripples_on=False)
    # Granny moves slowly along the quay, the fan swaying like a cat's tail
    gx, ph, f = walk_x([(0, 1250), (6, 1250), (16, 1360)], u, stride=30, s=1.12)
    sway = math.sin(T * 1.2)
    r = ctx.fig(gx, Q, 1.12, 'granny', 1 if u < 18 else -1, dict(walk=ph, arm_f=(70 + 20 * sway, 30), arm_b=(40, 70), look=6, mouth='flat'))
    jar_x = gx + 70
    jt = big_jar(ctx, jar_x, Q, 0.9, W_BREEZE, 0.25 * ease((u - 22) / 3))
    if r:
        fan(ctx, r['hand_f'], 60 + 25 * sway, 1.12 * ctx.z)
    # the breeze ribbon: wild at first, then calmer, then pouring into the new jar
    calm = ease((u - 6) / 12); into = ease((u - 18) / 6)
    cx = lerp(1150 + math.sin(T) * 80, jar_x, into); cy = lerp(400 + math.cos(T * 1.3) * 40, Q - 50, into)
    pts = breeze_path(T * (1 - 0.6 * calm), cx, cy, lerp(220, 40, max(calm, into)) * (1 - 0.8 * into) + 6, lerp(90, 20, calm) * (1 - 0.8 * into) + 4, 40, 4)
    breeze(ctx, pts, 1.0 - 0.9 * ease((u - 25) / 3))
    # Xiaoman watches from the doorway, the broom still in his hand
    ctx.fig(1720, Q, 0.95, 'xiaoman', -1, dict(look=4, arm_f=(10, 20)))

# ---------------------------------------------------------------- D: "Three years!"
def drawD(ctx, lt):
    T = ctx.Tabs
    town_live(ctx, rain_amt=0.0, drips_on=False, ripples_on=False)
    angry = 100 < T < 108
    r = ctx.fig(1420, Q, 1.12, 'granny', 1, dict(look=-6, mouth='frown' if not ctx.talking('granny') else 'flat', arm_f=(50, 60) if angry else (20, 30), arm_b=(30, 60)))
    if r: small_jar(ctx, r['hand_b'], 1.12 * ctx.z, W_BREEZE, 0.3)
    sad = T > 118
    ctx.fig(1520, Q, 0.95, 'xiaoman', -1, dict(look=(-10 if sad else 8), mouth='frown' if sad else 'flat', eyes='open', arm_f=(10, 20)))

# ---------------------------------------------------------------- E: the bridge; the twins
T_E = 132.0
def drawE(ctx, lt):
    T = ctx.Tabs; u = T - T_E
    strands(ctx, BR_STRANDS)
    xm = 1400
    pen = math.sin(T * 8) * 0.5 + 0.5
    r = ctx.fig(xm, deck_y(xm) + 4, 1.8, 'xiaoman', 1, dict(crouch=0.6, arm_f=(70 + 8 * pen * (u < 30), 40), look=(-14 if u < 30 else 6)))
    if r: notebook(ctx, r['hand_f'][0] + 6 * ctx.z, r['hand_f'][1] - 2 * ctx.z, 1.0 * ctx.z)
    # the twins arrive from the left, one after the other, and sit down beside him
    for k, (spec, sx) in enumerate(((None, 1290), (TWIN_B, 1330))):
        x, ph, f = walk_x([(14 + k * 1.2, 900 - k * 60), (26 + k * 1.2, sx)], u, s=1.8)
        sit = ease((u - 27 - k) / 1.0)
        talk_as = 'twinA' if k == 0 else 'twinB'
        both = ctx.talking('twins')
        ctx.fig(x, deck_y(x) + 2, 1.8, 'twin', 1, dict(walk=ph, crouch=0.6 * sit, look=4, talk=1 if (ctx.talking(talk_as) or both) else 0,
                                                       eyes='happy' if u > 92 else 'open'), spec=spec, seed=30 + k)

shots = [
    dict(dur=14, set=SHOP, cam=camkf([(0, (900, 402, 1.0)), (14, (950, 420, 1.15))]), draw=drawA, fade_in=(1.5, (0, 0, 0))),
    dict(dur=10, set=SHOP, cam=camkf([(0, (1030, 450, 1.7)), (10, (1080, 450, 1.8))]), draw=drawA),
    dict(dur=9, set=SHOP, cam=camkf([(0, (1100, 430, 1.6)), (9, (900, 420, 1.2))]), draw=drawA),       # 24 crash!
    dict(dur=22, set=LANE, cam=lambda t: (1100 + t * 55, 420, 1.15), draw=drawB, xfade=0.5),             # 33
    dict(dur=5, set=TOWN, cam=(2080, 470, 2.4), draw=drawB2),                                            # 55
    dict(dur=30, set=TOWN, cam=camkf([(0, (1250, 450, 1.7)), (30, (1400, 480, 2.0))]), draw=drawC, xfade=1.0),   # 60
    dict(dur=12, set=TOWN, cam=(1450, 480, 2.3), draw=drawD),                                            # 90
    dict(dur=8, set=TOWN, cam=(1520, 485, 2.8), draw=drawD),                                             # 102
    dict(dur=8, set=TOWN, cam=(1440, 485, 2.8), draw=drawD),                                             # 110
    dict(dur=14, set=TOWN, cam=camkf([(0, (1470, 480, 2.3)), (14, (1500, 470, 2.0))]), draw=drawD),     # 118
    dict(dur=108, set=BRIDGE, cam=camkf([(0, (1400, 240, 1.9)), (24, (1370, 235, 2.0)), (40, (1350, 225, 2.3)), (70, (1360, 230, 2.1)), (95, (1350, 235, 2.2)), (108, (1400, 402, 1.0))]), draw=drawE, xfade=1.5, fade_out=(3.0, (0, 0, 0))),   # 132
]

subs = [
    (99.5, '你知道一阵笑风要等多久吗？三年！', 'Do you know how long it takes to catch a giggling breeze? Three years!', 'granny'),
    (106.5, '我只是想帮忙……', 'I was only trying to help...', 'xiaoman'),
    (112.0, '不用帮。', "I don't need help.", 'granny'),
    (196.0, '你外婆凶吧？', "Your granny's scary, huh?", 'twinA'),
    (201.0, '她以前不这样。我奶奶说的。', "She wasn't always like that. My grandma said so.", 'twinB'),
    (208.0, '以前是怎样？', 'What was she like before?', 'xiaoman'),
    (216.0, '会笑。', 'She used to laugh.', 'twins'),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 13)
    m.birds(0, 33, 0.02); m.birds(132, 240, 0.025)
    # sweeping
    for k in range(9): m.sweep(2 + k * 2.4, 0.05)
    m.zheng_phrase(1, [74, 76, 78, None, 74, 76, 81, None, 78, 76, 74, None], 0.5, 0.10, 0.6)
    m.knock(24.3, 0.12); m.add(m.woodblock(700, 0.06), 24.6)
    m.shatter(25.6, 0.3)
    m.giggle(25.8, 7.0, 0.07); m.whoosh(26, 2.0, 0.12)
    # chaos: fast plucked run, wind, laughter-chimes
    m.wind(33, 60, 0.07, 300, 1500)
    for k in range(6): m.gliss(33.5 + k * 4.0, 66, 90, 0.05, 0.10, down=(k % 2 == 1))
    m.giggle(34, 20, 0.05)
    m.crowd(36, 50, 0.03, cheer=True)
    m.squawk(56, 0.12); m.squawk(57.6, 0.08)
    # the fan: slow, calm music, the breeze quiets
    m.wind(60, 80, 0.04, 200, 900)
    m.melody(62, [(74, 1.6), (71, 0.8), (69, 1.6), (66, 2.4), (None, 1), (69, 1.2), (66, 0.8), (64, 2.4)], 'dizi', 0.07)
    m.giggle(64, 14, 0.025)
    m.gliss(80, 62, 86, 0.09, 0.08, down=True)
    m.add(m.bell(note(86), 3, 0.05), 85)
    m.knock(86.2, 0.06)
    # the scolding: silence, then a sad erhu
    m.add(m.drum(60, 0.1), 101.5)
    m.melody(119, [(62, 1.4), (60, 0.6), (57, 2.0), (None, 0.5), (55, 0.8), (57, 2.8)], 'erhu', 0.05)
    # the bridge: water, willow, twins
    m.zheng_phrase(134, [62, None, 66, 69, None, 66, 64, None, 62, None, None, 57], 0.7, 0.12, 0.35)
    m.steps(146, 160, 3, 0.03, True)
    m.melody(170, [(69, 1.0), (71, 0.5), (74, 1.5), (71, 0.5), (69, 1.0), (66, 2.0)], 'dizi', 0.06)
    m.zheng_phrase(216.5, [74, 78, 81, 86], 0.15, 0.10)      # "She used to laugh"
    m.melody(222, [(81, 1.2), (78, 0.6), (76, 0.6), (74, 2.0), (None, 0.5), (69, 0.8), (71, 0.8), (74, 3.0)], 'dizi', 0.06)
    m.write(fn, 0.5, 3.0)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
