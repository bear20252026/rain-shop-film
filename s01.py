# Scene 1 · Plum Rain Morning · 梅雨之晨  (0:00 - 5:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_shop import SHOP, shop_live, FEET, ALTAR, GIGGLE_JAR, NAMED, red_jar, COUNTER
from sets_more import PAPER_SET

Q = WATER_Y - 18            # the quay where people stand in the town view
GX, JAR_X = 1500, 1418      # Granny and her jar at the shop front
GRAN_IN = 1110              # Granny behind the counter (inside)
GRAN_Y = 690

# ---------------------------------------------------------------- A: ink spreads, title
BACK = None
def title_back():
    global BACK
    if BACK is None:
        b = np.zeros((OH, OW), np.float32); cv2.ellipse(b, (OW // 2, 300), (420, 190), 0, 0, 360, 1.0, -1)
        BACK = smooth(cv2.GaussianBlur(b, (0, 0), 60) + (vnoise(OH, OW, 30, 4, 3) - 0.5) * 0.3, 0.2, 0.8) * 0.9
    return BACK

def postA(img, lt, ctx):
    img = ink_reveal(img, ease((lt - 1.0) / 8.0))
    a = min(ease((lt - 9.0) / 1.6), ease((23.0 - lt) / 1.5))
    if a > 0:
        img = img * (1 - title_back()[..., None] * a) + screen_paper() * title_back()[..., None] * a
        img = ink_over(img, card([('雨铺', 'The Rain Shop')], 120, 40) * a, 0.92)
        sa = ease((lt - 10.4) / 0.4) * a
        if sa > 0: img = img * (1 - (seal_mask(OW // 2 + 120, 220, 40) * sa)[..., None] * (1 - np.array(VERMILION, np.float32)))
    return img

def drawA(ctx, lt):
    town_live(ctx, rain_amt=0.4 + 0.6 * ease(lt / 12), jars_glow=0.6)

# ---------------------------------------------------------------- B: the long scroll pan to the shop
def drawB(ctx, lt):
    T = ctx.Tabs
    town_live(ctx, rain_amt=1.0, look=1.0 if lt > 30 else 0.0)
    # the ferry slides past on the canal
    bx = 400 + lt * 22
    deck = sampan(ctx, bx, WATER_Y + 52, 0.9, seed=611)
    r = ctx.fig(deck[0], deck[1], 0.85, 'ferryman', 1, dict(arm_f=(150, -30), arm_b=(120, -10), lean=12, bob=False))
    if r: pole(ctx, r['hand_f'], 18 + 6 * math.sin(lt * 0.8), 0.85 * ctx.z)
    # a porter hurries left under a red umbrella; the poet strolls right under an ochre one
    x, ph, f = walk_x([(0, 2100), (44, 1150)], lt, s=1.0)
    r = ctx.fig(x, Q, 1.0, 'porter', -1, dict(walk=ph, arm_f=(25, 105), arm_b=(-10, 10)))
    if r: umbrella(ctx, r['hand_f'], ctx.z, 0, -8)
    x, ph, f = walk_x([(0, 1030), (40, 1330)], lt, s=1.0)
    r = ctx.fig(x, Q, 1.02, 'poet', 1, dict(walk=ph, arm_f=(25, 105), look=-4))
    if r: umbrella(ctx, r['hand_f'], ctx.z, 1, 6)
    granny_catch(ctx, 0.0)

# ---------------------------------------------------------------- C: Granny catches a drop and pours it
def granny_catch(ctx, lt):
    """lt: local time of the catching action (0 = still catching; ~8 glowing drop; 12-18 pour)"""
    a = ease((lt - 11.0) / 2.2); b = ease((lt - 18.6) / 1.6)
    sh = lerp(92, 55, a); sh = lerp(sh, 80, b)
    el = lerp(-6, 25, a); el = lerp(el, 0, b)
    ang = lerp(24, -4, a); ang = lerp(ang, 26, b)
    tilt = -55 * ease((lt - 13.2) / 0.8) * (1 - ease((lt - 16.8) / 0.7))
    look = 14 if lt < 11 else lerp(14, -12, a)
    r = ctx.fig(GX, Q, 1.12, 'granny', -1, dict(arm_f=(sh, el), arm_b=(10, 20), look=look, lean=4 + 10 * a - 8 * b, eyes='open'))
    jt = ctx.T(JAR_X, Q)
    jtop = big_jar(ctx, JAR_X, Q, 0.95)
    if not r: return
    cupc, rim = ladle(ctx, r['hand_f'], ang, tilt, 1.12 * ctx.z)
    z = ctx.z
    if 7.6 < lt < 8.5:
        u = (lt - 7.6) / 0.9; ys0 = ctx.T(0, 402)[1]
        ctx.add_glow(cupc[0], ys0 + u * u * (cupc[1] - ys0), (4 + 3 * u) * z, 0.9, GLOW, world=False)
    fill_l = ease((lt - 8.5) / 0.6) * (1 - ease((lt - 14.0) / 1.6))
    if fill_l > 0: ctx.add_glow(cupc[0], cupc[1] - 3 * z, 13 * z * fill_l, fill_l, GLOW, world=False)
    pour = ease((lt - 13.5) / 0.4) * (1 - ease((lt - 16.6) / 0.4))
    lip = rim[0] if rim[0][1] > rim[1][1] else rim[1]
    stream(ctx, lip, jtop, pour, GLOW, r=2.2 * z, t=ctx.Tabs)
    jg = ease((lt - 14.2) / 1.6)
    if jg > 0: ctx.add_glow(jtop[0], jtop[1] + 22 * z, 24 * z * jg, 0.5 * jg, GLOW, world=False)
    for k in range(14):
        st0 = 15.0 + k * 0.28
        if lt > st0:
            u = (lt - st0) / 3.0
            if u < 1: ctx.add_glow(jtop[0] + math.sin(k * 2.3 + u * 4) * 12 * z, jtop[1] - u * 80 * z, 1.8 * z, (1 - u) * 0.9, GOLD if k % 3 == 0 else GLOW, world=False)

def drawC(ctx, lt):
    town_live(ctx, rain_amt=1.0, look=1.0 if 8.4 < lt < 12 else 0.0)
    granny_catch(ctx, lt)

# ---------------------------------------------------------------- D: the label is written
def drawD(ctx, lt):
    shop_live(ctx, glow=0.6, rain_door=0.6)
    x, y = OW * 0.5, 90
    u = ease((lt - 1.0) / 7.5)
    paper_slip(ctx, x, y, 3.2, '梅雨第三日', reveal=u)
    # the brush follows the writing down the slip, with little dabbing strokes
    n = len('梅雨第三日'); by = y + 22 * 3.2 + u * (n - 0.4) * 26 * 3.2 * 1.08
    tip = (x + 10 + math.sin(lt * 7.0) * 14, by + math.sin(lt * 11.0) * 10)
    brush(ctx, tip, 2.2, 28 + 6 * math.sin(lt * 3))

# ---------------------------------------------------------------- E: inside, the shelves of weather
LABEL_COL = {'虎丘雷': W_THUNDER, '初霜': W_SNOW, '秋雾': W_FOG, '梅雨': W_DRIZZLE, '六月雪': W_SNOW}
def named_jars(ctx, glow=1.0, skip=()):
    for name, (x, sy) in NAMED.items():
        if name in skip: continue
        big_jar(ctx, x, sy - 2, 1.0, LABEL_COL[name], 0.35 * glow * (0.85 + 0.15 * math.sin(ctx.Tabs * 1.7 + x)), label=name, seed=int(x))

def drawE(ctx, lt):
    shop_live(ctx, giggle=False, rain_door=0.8)
    named_jars(ctx)
    big_jar(ctx, GIGGLE_JAR[0], GIGGLE_JAR[1] - 2, 0.8, W_BREEZE, 0.4, label='笑风', seed=77)
    # the red jar answers with the faintest pulse as the camera arrives
    if lt > 22: ctx.add_glow(ALTAR[0], ALTAR[1] - 40, 20, 0.12 * math.sin(min(1, (lt - 22) / 2) * math.pi), W_DRAGON)

camE = camkf([(0, (700, 360, 1.7)), (16, (1600, 360, 1.7)), (21, (1820, 380, 1.6)), (30, (1975, 440, 2.6))])

# ---------------------------------------------------------------- F: the bride and her mother
def shop_people(ctx, lt, T0, cast, granny_pose):
    """common shop view: Granny behind the counter, customers in front"""
    shop_live(ctx, giggle=True, rain_door=0.9, red=True)
    named_jars(ctx, 0.8)
    r = ctx.fig(GRAN_IN, GRAN_Y, 2.1, 'granny', -1, granny_pose)
    for (who, keys, s, pose, extra) in cast:
        x, ph, f = walk_x(keys, ctx.Tabs - T0, s=s)
        p = dict(pose); p['walk'] = ph
        rr = ctx.fig(x, FEET + 30, s, who, f if ph is not None else 1, p, over=True, seed=hash(who) % 50)
        if rr and extra: extra(ctx, rr)
    return r

T_F = 140.0
def drawF(ctx, lt):
    T = ctx.Tabs - T_F
    reach = ease((T - 27) / 1.5) * (1 - ease((T - 31) / 1.5))
    give = ease((T - 36) / 1.0) * (1 - ease((T - 43) / 0.8))
    gp = dict(arm_f=(lerp(lerp(15, 160, reach), 80, give), lerp(20, -10, reach)), look=lerp(0, 25, reach), facing=-1,
              mouth='frown' if T < 25 else 'flat', eyes='closed' if 25.5 < T < 26.6 else 'open')
    gp.pop('facing')
    has_jar_g = 30 < T < 41.5
    bride_jar = T >= 41.5
    def bride_extra(c, rr):
        if bride_jar: small_jar(c, rr['hand_f'], 2.0 * c.z * 0.5, W_SNOW, 0.5)
    cast = [('bride', [(0, 150), (9, 650)], 2.0, dict(arm_f=(lerp(20, 70, give if T < 42 else 1), 30) if T > 35 else (10, 10), eyes='happy' if T > 42 else 'open', mouth='smile' if T > 42 else 'flat', look=-6), bride_extra),
            ('mother', [(1.2, 120), (10, 520)], 2.0, dict(arm_f=(30, 40), look=-4), None)]
    if T > 46:   # they leave together, the bride hugging the jar
        cast = [('bride', [(46, 650), (54, 120)], 2.0, dict(arm_f=(40, 80), eyes='happy', mouth='smile'), bride_extra),
                ('mother', [(46.4, 520), (54, 40)], 2.0, dict(arm_f=(30, 40)), None)]
    r = shop_people(ctx, lt, T_F, cast, gp)
    if r and has_jar_g: small_jar(ctx, r['hand_f'], 1.0 * ctx.z, W_SNOW, 0.6)

# ---------------------------------------------------------------- G: the rice farmer
T_G = 188.0
def drawG(ctx, lt):
    T = ctx.Tabs - T_G
    pour = ease((T - 17) / 0.6) * (1 - ease((T - 22) / 0.6))
    gp = dict(arm_f=(lerp(15, 75, ease((T - 15) / 1.2) * (1 - ease((T - 24) / 1))), 10), look=-5)
    state = {}
    def farmer_extra(c, rr):
        state['cup'] = cup(c, rr['hand_f'], 2.0 * c.z * 0.55)
    keys = [(0, 140), (8, 700)] if T < 26 else [(26, 700), (33, 100)]
    cast = [('farmer', keys, 2.0, dict(arm_f=(70, 10) if 8 < T < 26 else (20, 20), look=-3, mouth='smile' if T > 23 else 'flat'), farmer_extra)]
    r = shop_people(ctx, lt, T_G, cast, gp)
    if r and 14 < T < 25:
        jt = small_jar(ctx, r['hand_f'], 1.0 * ctx.z, W_DRIZZLE, 0.5)
        if 'cup' in state: stream(ctx, jt, state['cup'], pour, W_DRIZZLE, r=2.0 * ctx.z, t=ctx.Tabs)

# ---------------------------------------------------------------- H: the poet
T_H = 222.0
def drawH(ctx, lt):
    T = ctx.Tabs - T_H
    give = ease((T - 18) / 1.2)
    gp = dict(arm_f=(lerp(15, 80, give * (1 - ease((T - 26) / 1))), 10), look=-5)
    holding = T > 26
    def poet_extra(c, rr):
        if holding:
            jt = small_jar(c, rr['hand_f'], 2.0 * c.z * 0.5, W_FOG, 0.45)
            # a curl of autumn fog leaks out
            pts = [(jt[0] + math.sin(k * 0.5 + c.Tabs) * 8 * c.z, jt[1] - k * 9 * c.z) for k in range(10)]
            wisp(c, pts, 0.5 * ease((T - 27) / 2), W_FOG, 5 * c.z, world=False, t=c.Tabs)
    keys = [(0, 140), (8, 690)] if T < 30 else [(30, 690), (38, 80)]
    cast = [('poet', keys, 2.0, dict(arm_f=(60, 40) if T > 26 else (30, 60), look=(-8 if T < 28 else 10), eyes='closed' if 27 < T < 30 else 'open', mouth='smile' if T > 27 else 'flat'), poet_extra)]
    r = shop_people(ctx, lt, T_H, cast, gp)
    if r and 18 < T < 26: small_jar(ctx, r['hand_f'], 1.0 * ctx.z, W_FOG, 0.5)

# ---------------------------------------------------------------- I: dusk; Old Ink; shutters; a glance at the red jar
def drawI1(ctx, lt):
    town_live(ctx, rain_amt=0.7, look=0.0 if lt < 4 else 1.0, night=0.3)

FRONT = (1558, 1862, 406, Q)
def shutters(ctx, n_closed):
    x0, x1, y0, y1 = FRONT; w = (x1 - x0) / 8
    for k in range(8):
        u = min(1, max(0, n_closed - k))
        if u <= 0: continue
        px = x0 + k * w - (1 - u) * 120
        pts = ctx.Tp([(px, y0), (px + w - 2, y0), (px + w - 2, y1), (px, y1)])
        L = ctx.layer(pts[:, 0].min() - 6, pts[:, 1].min() - 6, pts[:, 0].max() + 6, pts[:, 1].max() + 6)
        fill(L, pts, 0.32, (0.45, 0.55, 0.70), 0.6, s=ctx.z, seed=900 + k, gran=0.8)
        line(L, np.vstack([pts, pts[:1]]), 1.4, ctx.z, 0.85, 0.3, 910 + k, taper=False)

def drawI2(ctx, lt):
    town_live(ctx, rain_amt=0.7, night=0.4)
    n = 4 * ease((lt - 2) / 8)
    shutters(ctx, n)
    # Granny carries the boards one by one along the front
    x = 1540 + (n % 1) * 40 + int(n) * 38
    ctx.fig(min(1700, x - 30), Q, 1.12, 'granny', 1, dict(arm_f=(40, 60), arm_b=(30, 50), walk=(lt * 0.8 if lt < 10 else None)))

def drawI3(ctx, lt):
    shop_live(ctx, glow=0.8, candles=True, rain_door=0.5, night=0.5)
    look = 1 if 3 < lt < 7.5 else 0
    ctx.fig(1700, FEET, 2.1, 'granny', 1 if look else -1, dict(look=4 if look else -6, eyes='open', mouth='flat'))
    if 4 < lt < 7: ctx.add_glow(ALTAR[0], ALTAR[1] - 40, 22, 0.1 * math.sin((lt - 4) / 3 * math.pi), W_DRAGON)

NIGHT = (0.70, 0.62, 0.58)
shots = [
    dict(dur=24, set=TOWN, cam=lambda t: (lerp(560, 760, ease(t / 24)), 402, 1.0), draw=drawA, post=postA, fade_in=(1.5, (0, 0, 0)), args=dict(mist=1.2)),
    dict(dur=44, set=TOWN, cam=lambda t: (lerp(760, 1500, ease(t / 44)), 402, 1.0), draw=drawB, xfade=1.0),
    dict(dur=28, set=TOWN, cam=camkf([(0, (1500, 402, 1.0)), (6, (1462, 470, 2.1)), (28, (1462, 480, 2.3))]), draw=drawC),
    dict(dur=14, set=SHOP, cam=(1150, 360, 2.6), draw=drawD, xfade=0.8, args=dict(no_counter=True), post=None),
    dict(dur=30, set=SHOP, cam=camE, draw=drawE, xfade=1.0),
    dict(dur=11, set=SHOP, cam=(900, 402, 1.0), draw=drawF, xfade=0.8),              # 140 wide: they come in
    dict(dur=6, set=SHOP, cam=(760, 420, 1.7), draw=drawF),                           # 151 bride asks
    dict(dur=4, set=SHOP, cam=(1080, 400, 1.8), draw=drawF),                          # 157 granny: expensive
    dict(dur=5, set=SHOP, cam=(760, 420, 1.7), draw=drawF),                           # 161 mother
    dict(dur=22, set=SHOP, cam=camkf([(0, (900, 410, 1.3)), (22, (860, 410, 1.25))]), draw=drawF),   # 166 the tiny jar
    dict(dur=10, set=SHOP, cam=(900, 402, 1.0), draw=drawG, xfade=0.8),               # 188 farmer
    dict(dur=16, set=SHOP, cam=camkf([(0, (900, 420, 1.4)), (16, (920, 420, 1.5))]), draw=drawG),
    dict(dur=8, set=SHOP, cam=(900, 402, 1.0), draw=drawG),
    dict(dur=8, set=SHOP, cam=(900, 402, 1.0), draw=drawH, xfade=0.8),                # 222 poet
    dict(dur=10, set=SHOP, cam=(760, 420, 1.8), draw=drawH),
    dict(dur=22, set=SHOP, cam=camkf([(0, (900, 410, 1.3)), (22, (860, 410, 1.2))]), draw=drawH),
    dict(dur=10, set=TOWN, cam=camkf([(0, (2060, 470, 2.4)), (10, (2060, 480, 2.6))]), draw=drawI1, xfade=1.0, grade=NIGHT),   # 262 Old Ink
    dict(dur=14, set=TOWN, cam=(1690, 470, 1.9), draw=drawI2, grade=NIGHT),                                                    # 272 shutters
    dict(dur=14, set=SHOP, cam=camkf([(0, (1800, 400, 1.6)), (14, (1850, 410, 1.75))]), draw=drawI3, grade=(0.62, 0.55, 0.52), fade_out=(3.0, (0, 0, 0))),
]

subs = [
    (106.0, 110.0, '梅雨　第三日', 'Plum rain · day 3', None),
    (113.0, 116.0, '虎丘雷', 'Thunder over Tiger Hill', None),
    (117.0, 120.0, '初霜', 'First frost', None),
    (121.0, 124.0, '笑风', 'Giggling breeze', None),
    (125.0, 128.0, '秋雾', 'Autumn fog', None),
    (151.5, '婆婆，我的婚礼在六月……能下一点点雪吗？', 'Granny, my wedding is in June... could it snow, just a little?', 'bride'),
    (157.3, '六月雪？贵。', 'Snow in June? Expensive.', 'granny'),
    (161.3, '她从小就想要。', 'She has wanted it since she was little.', 'mother'),
    (177.0, '只够一支舞。别浪费。', "Enough for one dance. Don't waste it.", 'granny'),
    (196.5, '一杯毛毛雨，给秧苗。', 'A cup of drizzle, for the seedlings.', 'farmer'),
    (202.0, '一杯。不是一桶。', 'A cup. Not a bucket.', 'granny'),
    (228.5, '有没有……让人想家的雾？', 'Do you have a fog... that makes you miss home?', 'poet'),
    (236.0, '秋雾。别在屋里开。', "Autumn fog. Don't open it indoors.", 'granny'),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 11)
    m.rain([(0, 0.0), (3, 0.5), (12, 1.0), (96, 1.0), (98, 0.45), (262, 0.45), (264, 0.8), (286, 0.8), (288, 0.4), (300, 0.0)])
    m.drips(20, 96, 1.5); m.drips(262, 286, 1.5)
    # opening: ink blooms on low strings, title on gong
    m.zheng_phrase(1.5, [50, None, 57, None, 62, None, None, 54, None, 57, None, (59, -0.03)], 0.6, 0.26)
    m.add(m.gong(5, 0.38), 9.2, 1, 0.5)
    for n_ in (38, 45, 50, 57): m.add(m.guzheng(note(n_), 4.5, 0.17), 9.25)
    m.add(m.bell(note(86), 3, 0.06), 10.4, 1, 0.7)
    m.melody(12.5, [(81, 1.2), (78, 0.5), (76, 0.5), (74, 1.6), (None, 0.6), (76, 0.5), (78, 0.5), (81, 0.8), (83, 0.6), (81, 2.0)], 'dizi', 0.09)
    # the long pan: a walking guzheng line, dizi answering
    t = 26
    for rep in range(4):
        m.zheng_phrase(t, [62, 66, 69, 66, 71, 69, 66, 64], 0.55, 0.16, 0.35); t += 5.5
        m.melody(t - 2.0, [(81, 0.8), (78, 0.4), (76, 1.2)] if rep % 2 == 0 else [(74, 0.8), (76, 0.4), (78, 1.2)], 'dizi', 0.07)
    m.steps(24, 68, 2.0, 0.025, True)
    for k in range(8): m.oar(25 + k * 5.0, 0.05)
    m.squawk(54, 0.05)
    # the drop
    m.add(m.bell(note(93), 4, 0.12), 76.5, 1, 0.45); m.add(m.bell(note(98), 3, 0.06), 76.55, 1, 0.6)
    for n_ in (62, 66, 69): m.add(m.guzheng(note(n_), 4, 0.12), 76.6)
    m.pour(81.4, 3.0, 0.05); m.gliss(81.5, 62, 93, 0.07, 0.14)
    m.tremolo(82.6, 81, 1.6)
    m.add(m.dizi(note(74), 2.2, 0.08), 82.8, 1, 0.6)
    # the label is written: brush swishes
    for k in range(5): m.sweep(97.5 + k * 1.3, 0.03)
    m.zheng_phrase(97, [74, None, 69, 66, None, 62], 0.7, 0.14)
    # the shelves: each named weather gets its own colour of sound
    m.tremolo(110, 86, 2.0, 0.04)
    m.thunder(113.2, 0.12, far=True); m.add(m.chime(note(98), 0.05), 117.2); m.giggle(121.0, 1.4, 0.04); m.wind(125, 128.5, 0.03, 300, 900)
    m.pad(128, 12, [38, 45], 0.04); m.rumble(132, 3, 0.10, 36)
    # customers: a light hopping tune; bells for the June snow
    m.add(m.bell(note(88), 2, 0.05), 140.2, 1, 0.3)
    m.steps(140, 150, 2.4, 0.03, True)
    m.zheng_phrase(142, [74, 76, 78, 81, None, 78, 76, 74], 0.4, 0.12, 0.6)
    m.breath(166.0, 1.4, 0.03)   # Granny sighs
    m.knock(169.5, 0.05)
    for k in range(6): m.add(m.chime(note(PENT[12 + k]), 0.03), 171 + k * 0.25, 1, 0.3 + 0.08 * k)
    m.melody(182, [(78, 0.4), (81, 0.4), (83, 0.4), (86, 1.2)], 'dizi', 0.07)
    m.steps(186, 194, 2.4, 0.03, True)
    m.steps(188, 196, 1.8, 0.04, True)
    m.pour(205, 2.2, 0.04)
    m.zheng_phrase(200, [62, None, 64, 62, None, 57], 0.6, 0.12, 0.4)
    m.steps(214, 221, 1.8, 0.04, True)
    m.steps(222, 230, 2.0, 0.03, True)
    m.melody(240, [(69, 1.4), (67, 0.6), (65, 1.6), (62, 2.4)], 'erhu', 0.06)
    m.steps(252, 260, 2.0, 0.03, True)
    # dusk, Old Ink, shutters, the glance
    m.snort(266, 0.06)
    for k in range(4): m.knock(275 + k * 2.0, 0.08)
    m.pad(286, 14, [38, 45, 50], 0.035)
    m.rumble(290, 3.5, 0.08, 34)
    m.zheng_phrase(288, [62, None, None, 57, None, None, 50], 0.9, 0.14)
    m.write(fn, 0.3, 3.0)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
