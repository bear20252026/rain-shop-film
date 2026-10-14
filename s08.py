# Scene 8 · Sixty Years Ago · 六十年前  (33:00 - 38:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_more import SCREEN, ROOM, room_live, ROOM_FEET, BED, WINDOW
from figure import dragon, dragon_spine
from chars import fill, line
from s01 import Q

NIGHT = (0.50, 0.42, 0.40)
FLASHES = [3.2, 9.5, 21.8, 36.0, 168.5, 204.0, 231.0, 266.5, 281.0]

def flash_amt(T, times=FLASHES):
    a = 0.0
    for t0 in times:
        d = T - t0
        if 0 <= d < 0.9: a = max(a, math.exp(-d * 7) * 0.8 + (0.35 * math.exp(-(d - 0.25) ** 2 * 200)))
    return a

def post_flash(img, lt, ctx):
    a = flash_amt(ctx.Tabs)
    if a <= 0: return img
    return img * (1 - a * 0.5) + np.array([1.0, 0.97, 0.95], np.float32) * a * 0.5 + img * a * 0.4

# ---------------------------------------------------------------- A / C: under the eaves at night
def eaves(ctx, lt, xm_pose=None, gr_pose=None, granny_leaves=None):
    T = ctx.Tabs
    town_live(ctx, 0.0, False, True, False, jars_glow=0.4, water=0.0, night=0.5)
    gp = dict(crouch=0.6, arm_f=(40, 60), arm_b=(30, 60), look=-2, mouth='flat')
    gp.update(gr_pose or {})
    gx = 1700
    if granny_leaves is not None:
        u = T - granny_leaves
        up = ease(u / 1.2)
        gp['crouch'] = 0.6 * (1 - up)
        x, ph, f = walk_x([(1.6, 1700), (6, 1820)], u, stride=30, s=1.12)
        gx = x; gp['walk'] = ph
        op = 1 - ease((u - 5) / 1.5)
        if op > 0: ctx.fig(gx, Q - 4 * (1 - up), 1.12, 'granny', 1 if ph is not None else -1, gp, op=op)
    else:
        ctx.fig(gx, Q - 4, 1.12, 'granny', -1, gp)
    xp = dict(crouch=0.6, arm_f=(70, 80), arm_b=(60, 80), look=6, mouth='flat')
    xp.update(xm_pose or {})
    r = ctx.fig(1620, Q - 4, 0.95, 'xiaoman', 1, xp)
    if r and not (xm_pose or {}).get('no_baozi'):
        ctx.baozi(1636, Q - 52 + 2 * math.sin(T * 0.8), 0.9, 'sleepy')

def drawA(ctx, lt):
    T = ctx.Tabs
    talk_eye = 'wide' if 13 < T < 16 else 'open'
    eaves(ctx, lt, dict(look=8 if T > 12 else -10, eyes=talk_eye), dict(eyes='closed' if 22 < T < 26 else 'open', look=-8 if T < 24 else 2))

# ---------------------------------------------------------------- B: the shadow-puppet flashback
def silhouette(L, red=None, alpha=0.93):
    """turn whatever was drawn on L into a flat puppet shadow"""
    L.D = np.maximum(L.D, L.M * alpha); L.tints = []
    if red is not None: L.tints.append(red)

def sil_fig(ctx, x, y, s, who, facing=1, pose=None, seed=11, spec=None, ribbon=False):
    r = ctx.fig(x, y, s, who, facing, pose, seed, spec=spec)
    if r is None: return None
    L = ctx.stack[-1][0]; silhouette(L)
    if ribbon:     # a red ribbon in the girl's hair: the only colour on her
        hx, hy = r['head']
        m = np.zeros(L.D.shape, np.float32)
        cv2.ellipse(m, (int((hx - L.x0 - 18 * s * ctx.z * facing) * 4), int((hy - L.y0 - 14 * s * ctx.z) * 4)), (int(9 * s * ctx.z * 4), int(5 * s * ctx.z * 4)), 30, 0, 360, 1.0, -1, cv2.LINE_AA, 2)
        m = cv2.GaussianBlur(m, (0, 0), 1.0); L.knock(m); L.tints.append((m * 0.95, VERMILION))
    return r

GIRL = dict(hair='pigtails', top=(0.06, None, 0))
WAVE_Y0, WAVE_Y1 = 700, 470

def river(ctx, level, t, ink=0.85):
    """rising flood: three bands of puppet waves"""
    L = ctx.layer(0, 0, OW, OH)
    for k in range(3):
        base = level + k * 46
        pts = [(x, base + math.sin(x * 0.012 + t * (1.2 + k * 0.3) + k) * 14 + math.sin(x * 0.031 - t * 2) * 5) for x in range(-20, OW + 40, 20)]
        poly = pts + [(OW + 20, OH + 20), (-20, OH + 20)]
        m = poly_mask(L.D.shape, [L.P(poly)])
        over(L.D, m * (0.5 + 0.2 * k) * ink)
        # curling crest strokes
        for j in range(0, OW, 160):
            cx = j + (t * 40 * (k + 1)) % 160; cy = base + math.sin(cx * 0.012 + t * (1.2 + k * 0.3) + k) * 14
            line(L, [(cx + 14 * math.cos(q), cy - 10 + 10 * math.sin(q)) for q in np.linspace(math.pi, 2.6 * math.pi, 10)], 2.0, 1, 0.9 * ink, 0, 2000 + j + k)

def arch_bridge(ctx, cx=960, deck=430, w=520):
    L = ctx.layer(cx - w - 20, deck - 40, cx + w + 20, OH)
    top = [(cx + w * math.cos(q), deck + 70 * (1 - math.sin(q)) ** 1.5 * 3.2 - 0) for q in np.linspace(0, math.pi, 40)]
    top = [(x, min(OH, deck + ((x - cx) / w) ** 2 * 220)) for x, _ in top]
    under = [(cx + 260 * math.cos(q), OH - 20 - 250 * math.sin(q)) for q in np.linspace(math.pi, 0, 30)]
    poly = top + [(cx + w, OH + 10)] + [(cx + 270, OH + 10)] + under + [(cx - 270, OH + 10), (cx - w, OH + 10)]
    m = poly_mask(L.D.shape, [L.P(poly)])
    over(L.D, m * 0.9)
    for k in range(-4, 5):
        x = cx + k * 90; y = deck + ((x - cx) / w) ** 2 * 220
        line(L, [(x, y), (x, y - 34)], 3, 1, 0.9, 0, 2100 + k, taper=False)
    line(L, [(x, deck + ((x - cx) / w) ** 2 * 220 - 30) for x in range(cx - 380, cx + 381, 20)], 2.4, 1, 0.9, 0, 2110, taper=False)
    return lambda x: deck + ((x - cx) / w) ** 2 * 220

def house(ctx, x, y, s, ang=0.0, seed=0):
    L = ctx.layer(x - 90 * s, y - 120 * s, x + 90 * s, y + 30 * s)
    c, sn = math.cos(ang), math.sin(ang)
    R = lambda dx, dy: (x + c * dx - sn * dy, y + sn * dx + c * dy)
    body = [R(-50 * s, 0), R(50 * s, 0), R(50 * s, -60 * s), R(-50 * s, -60 * s)]
    roof = [R(-70 * s, -58 * s), R(70 * s, -58 * s), R(40 * s, -95 * s), R(-40 * s, -95 * s)]
    for p in (body, roof): over(L.D, poly_mask(L.D.shape, [L.P(p)]) * 0.92)
    win = [R(-14 * s, -24 * s), R(14 * s, -24 * s), R(14 * s, -44 * s), R(-14 * s, -44 * s)]
    wm = poly_mask(L.D.shape, [L.P(win)]); L.D *= 1 - wm * 0.9

def clouds(ctx, amt, t, cover=1.0):
    L = ctx.layer(0, 0, OW, OH)
    rr = np.random.default_rng(3)
    for k in range(16):
        x = rr.random() * OW; y = 40 + rr.random() * 200 * cover
        r = 90 + rr.random() * 120
        x += math.sin(t * 0.3 + k) * 40
        m = np.zeros(L.D.shape, np.float32)
        cv2.ellipse(m, (int(x * 4), int(y * 4)), (int(r * 1.6 * 4), int(r * 0.6 * 4)), 0, 0, 360, 1.0, -1, cv2.LINE_AA, 2)
        over(L.D, cv2.GaussianBlur(m, (0, 0), 6) * 0.55 * amt)

def puppet_dragon(ctx, spine, t, s=1.0, alpha=1.0, eye='angry'):
    sp = np.asarray(spine, np.float32)
    x0, y0 = sp.min(0) - 120 * s; x1, y1 = sp.max(0) + 120 * s
    L = ctx.layer(x0, y0, x1, y1)
    dragon(L, sp, t, s, 1.0, eye=eye)
    m = np.clip(L.M + L.D, 0, 1)
    L.D = m * 0.55 * alpha; L.tints = [(m * 0.85 * alpha, VERMILION)]
    L.M = L.M * alpha

def big_jar_sil(ctx, x, by, s=1.0, seal=False):
    L = ctx.layer(x - 70 * s, by - 150 * s, x + 70 * s, by + 10)
    half = [(x + 48 * s * (0.5 + 0.5 * math.sin(a)) + 0, by - 120 * s * (1 - math.cos(a)) / 2) for a in np.linspace(0, math.pi, 24)]
    body = [(x - (px - x), py) for px, py in half[::-1]] + half + [(x + 22 * s, by - 132 * s), (x - 22 * s, by - 132 * s)]
    over(L.D, poly_mask(L.D.shape, [L.P(body)]) * 0.93)
    if seal:
        cap = [(x - 24 * s, by - 132 * s), (x + 24 * s, by - 132 * s), (x + 30 * s, by - 112 * s), (x - 30 * s, by - 112 * s)]
        cm = poly_mask(L.D.shape, [L.P(cap)]); L.knock(cm); L.tints.append((cm * 0.95, VERMILION))
    return (x, by - 132 * s)

T_B = 40.0
def drawB(ctx, lt):
    T = ctx.Tabs; u = T - T_B
    t = T
    rise = ease(u / 20)
    level = lerp(WAVE_Y0, WAVE_Y1, rise)
    drain = ease((u - 108) / 10)
    level = lerp(level, WAVE_Y0 + 40, drain)
    # storm overhead (thicker as the dragon comes)
    storm = ease((u - 18) / 8) * (1 - ease((u - 100) / 6))
    clouds(ctx, 0.4 + 0.6 * storm, t, 1.0)
    deck = arch_bridge(ctx)
    # houses floating past early on
    if u < 40:
        for k in range(3):
            hx = (200 + k * 640 + u * 30) % (OW + 300) - 150
            house(ctx, hx, level + 18, 0.9 + 0.2 * k, math.sin(t * 0.9 + k) * 0.12, k)
    # the dragon inside the storm
    if 18 < u < 106:
        app = ease((u - 18) / 6)
        if u < 70:
            sp = dragon_spine(1300 - (u - 18) * 6, 170 + math.sin(t * 0.6) * 30, t, 900, 60, 1.6, ang=0.15, n=70, speed=0.4)
            puppet_dragon(ctx, sp, t, 2.2, app * 0.9)
        else:     # it swoops down and coils around the jar, shrinking into it
            v = ease((u - 70) / 30)
            jx, jy = 960, deck(960) - 130 - 132 * 1.2
            hx = lerp(1300, jx, v); hy = lerp(200, jy - 30, v)
            sp = dragon_spine(hx, hy, t, lerp(900, 120, v), lerp(60, 10, v), 1.6, ang=lerp(0.15, -1.4, v), n=70, speed=0.6, coil=lerp(0, 1.2, v))
            puppet_dragon(ctx, sp, t, lerp(2.2, 0.5, v), 0.9 * (1 - ease((u - 99) / 2)))
    # the grandmother hands the girl the biggest jar (on the bank, left), then the girl climbs the bridge
    if u < 62:
        gx = 360
        give = ease((u - 46) / 3)
        sil_fig(ctx, gx, 640, 2.0, 'granny', 1, dict(arm_f=(lerp(30, 90, give if u > 40 else 0), 20), arm_b=(20, 30), lean=10), seed=5, spec=dict(hair='bun'))
        has = u > 49
        jx = lerp(gx + 90, 560, ease((u - 49) / 2)) if has else gx + 90
        r = sil_fig(ctx, 560, 640, 1.7, 'twin', -1, dict(arm_f=(lerp(20, 100, give), 40), arm_b=(lerp(20, 100, give), 40), look=-10), seed=6, spec=GIRL, ribbon=True)
        if u > 40:
            big_jar_sil(ctx, jx if not has else 560 - 40, 600 if not has else 560, 1.0)
    else:
        x, ph, f = walk_x([(62, 640), (70, 960)], u, stride=30, s=1.7)
        lift = ease((u - 72) / 2)
        r = sil_fig(ctx, x, deck(x), 1.7, 'twin', 1, dict(walk=ph, arm_f=(lerp(80, 175, lift), 10), arm_b=(lerp(80, 170, lift), 10), look=-14 * lift, lean=-6 * lift), seed=6, spec=GIRL, ribbon=True)
        if r:
            hx = (r['hand_f'][0] + r['hand_b'][0]) / 2; hy = min(r['hand_f'][1], r['hand_b'][1])
            mx, my = hx / ctx.z + ctx.left, hy / ctx.z + ctx.top
            big_jar_sil(ctx, mx, my - 10 + 132 * 1.2 * 0 + 0, 1.2, seal=u > 102)
    river(ctx, level, t)
    # the flash as it goes in, then stillness and a few small clouds
    if u > 100:
        ctx.add_glow(960, deck(960) - 300, 60, 0.6 * math.exp(-(u - 100.5) ** 2 * 2), W_DRAGON)

def post_screen(img, lt, ctx):
    """flicker of the lamp behind the screen + the lightning inside the story"""
    T = ctx.Tabs; u = T - T_B
    fl = 1 + 0.03 * math.sin(T * 11) * math.sin(T * 7.3)
    img = img * fl
    lights = [24.0, 31.0, 44.0, 57.0, 66.0, 78.0, 88.0, 100.4]
    a = max([math.exp(-max(0, u - t0) * 6) * (u >= t0) for t0 in lights] + [0])
    return img * (1 + 0.45 * a)

def zpost(zf):
    """slow push-in on the (screen-space) puppet stage: zf(lt) -> (zoom, cx, cy)"""
    def post(img, lt, ctx):
        z, cx, cy = zf(lt)
        if z != 1.0:
            M = np.float32([[z, 0, OW / 2 - cx * z], [0, z, OH / 2 - cy * z]])
            img = cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return post_screen(img, lt, ctx)
    return post
def zk(keys): return lambda lt: tuple(kf([(t, v) for t, v in keys], lt)) if False else _zk(keys, lt)
def _zk(keys, lt):
    if lt <= keys[0][0]: return keys[0][1]
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if lt <= t1:
            u = ease((lt - t0) / (t1 - t0)); return tuple(lerp(p, q, u) for p, q in zip(a, b))
    return keys[-1][1]

# ---------------------------------------------------------------- C: back under the eaves
T_C = 160.0
def drawC(ctx, lt):
    T = ctx.Tabs; u = T - T_C
    eager = 22 < u < 30
    leave = 214.0 if T > 214 else None
    eaves(ctx, lt, dict(crouch=0.6 * (1 - ease((u - 21.5) / 0.6)) + 0.6 * ease((u - 30) / 1.5) * (u > 30), arm_f=(150, 30) if eager else (70, 80), arm_b=(140, 30) if eager else (60, 80),
          eyes='wide' if eager else 'open', mouth='open' if 22 < u < 25 else 'frown' if u > 30 else 'flat', look=8, no_baozi=eager),
          dict(eyes='closed' if 3 < u < 6 or 44 < u < 48 else 'open', look=-6 if u < 30 else -12, mouth='flat'), granny_leaves=leave)
    if eager:
        ctx.baozi(1600, Q - 160 + 6 * math.sin(T * 3), 0.9, 'happy')

# ---------------------------------------------------------------- D: in bed, awake; three tiny drops
T_D = 215.0
HEAD = (1655, 549)
def drawD(ctx, lt):
    T = ctx.Tabs; u = T - T_D
    room_live(ctx, 0.0, 0.0)
    smile = 34 < u < 40
    frown = u > 41
    look_win = u > 50
    ctx.fig(1880, BED[2] - 4, 2.0, 'xiaoman', 1, dict(eyes='open' if not (30 < u < 31) else 'closed', arm_f=(25, 10), arm_b=(15, 10), mouth='smile' if smile else 'frown' if frown else 'flat', look=-14 if look_win else 0), rot=-90)
    bx = HEAD[0] + 20 + 10 * math.sin(T * 0.7); by = HEAD[1] - 120 + 8 * math.sin(T * 1.1)
    ctx.baozi(bx, by, 1.8, 'happy')
    for k, t0 in enumerate((27.0, 29.5, 32.0)):
        v = (u - t0) / 0.6
        if 0 <= v <= 1: drop_glow(ctx, bx - 6 + k * 6, by + 16, HEAD[0] + 8 + k * 6, HEAD[1] - 26, v, W_DRIZZLE, 3.0)
        if 1 < v < 2: ctx.add_glow(HEAD[0] + 8 + k * 6, HEAD[1] - 26, 4, 0.5 * (2 - v), W_DRIZZLE)
    # the dry lightning comes through the window
    a = flash_amt(T)
    if a > 0:
        ctx.add_glow((WINDOW[0] + WINDOW[2]) / 2, (WINDOW[1] + WINDOW[3]) / 2, 260, 0.35 * a, BLUE)

shots = [
    # A · 0  under the eaves, dry lightning
    dict(dur=12, set=TOWN, cam=camkf([(0, (1600, 430, 1.4)), (12, (1650, 450, 1.6))]), draw=drawA, args=dict(water=0.0, mist=0.2), grade=NIGHT, post=post_flash, fade_in=(2.0, (0, 0, 0))),
    dict(dur=8, set=TOWN, cam=(1660, 500, 2.6), draw=drawA, args=dict(water=0.0, mist=0.2), grade=NIGHT, post=post_flash),        # 12 the question
    dict(dur=14, set=TOWN, cam=camkf([(0, (1700, 495, 3.0)), (14, (1700, 495, 3.3))]), draw=drawA, args=dict(water=0.0, mist=0.2), grade=NIGHT, post=post_flash),   # 20 the long silence
    dict(dur=6, set=TOWN, cam=camkf([(0, (1660, 480, 2.2)), (6, (1660, 470, 2.0))]), draw=drawA, args=dict(water=0.0, mist=0.2), grade=NIGHT, post=post_flash, fade_out=(2.5, (0.05, 0.08, 0.15))),
    # B · 40  the puppet screen
    dict(dur=22, set=SCREEN, cam=(960, 402, 1.0), draw=drawB, post=zpost(zk([(0, (1.0, 960, 402)), (22, (1.05, 960, 402))])), fade_in=(2.5, (0.05, 0.08, 0.15))),
    dict(dur=18, set=SCREEN, cam=(960, 402, 1.0), draw=drawB, post=zpost(zk([(0, (1.1, 900, 380)), (18, (1.2, 760, 420))]))),          # 62 the girl, the jar
    dict(dur=30, set=SCREEN, cam=(960, 402, 1.0), draw=drawB, post=zpost(zk([(0, (1.0, 960, 402)), (30, (1.12, 960, 360))]))),          # 80 the bridge, the dragon
    dict(dur=20, set=SCREEN, cam=(960, 402, 1.0), draw=drawB, post=zpost(zk([(0, (1.4, 960, 300)), (20, (1.55, 960, 300))]))),          # 110 it goes in
    dict(dur=30, set=SCREEN, cam=(960, 402, 1.0), draw=drawB, post=zpost(zk([(0, (1.2, 960, 380)), (30, (1.0, 960, 402))])), fade_out=(3.0, (0.05, 0.08, 0.15))),
    # C · 160  "Since then..."
    dict(dur=12, set=TOWN, cam=camkf([(0, (1660, 470, 2.0)), (12, (1660, 480, 2.2))]), draw=drawC, args=dict(water=0.0, mist=0.2), grade=NIGHT, post=post_flash, fade_in=(2.0, (0.05, 0.08, 0.15))),
    dict(dur=10, set=TOWN, cam=(1700, 495, 3.0), draw=drawC, args=dict(water=0.0, mist=0.2), grade=NIGHT, post=post_flash),         # 172
    dict(dur=6, set=TOWN, cam=(1625, 470, 2.6), draw=drawC, args=dict(water=0.0, mist=0.2), grade=NIGHT, post=post_flash),          # 182 "Then open it!"
    dict(dur=14, set=TOWN, cam=camkf([(0, (1700, 495, 3.0)), (14, (1700, 495, 3.2))]), draw=drawC, args=dict(water=0.0, mist=0.2), grade=NIGHT, post=post_flash),   # 188
    dict(dur=13, set=TOWN, cam=camkf([(0, (1660, 450, 1.6)), (13, (1620, 430, 1.4))]), draw=drawC, args=dict(water=0.0, mist=0.2), grade=NIGHT, post=post_flash, fade_out=(2.0, (0, 0, 0))),
    # D · 215  awake in bed
    dict(dur=12, set=ROOM, cam=camkf([(0, (1700, 420, 1.2)), (12, (1700, 450, 1.5))]), draw=drawD, grade=NIGHT, fade_in=(2.0, (0, 0, 0))),
    dict(dur=24, set=ROOM, cam=camkf([(0, (1665, 480, 2.6)), (24, (1665, 490, 3.0))]), draw=drawD, grade=NIGHT),                  # 227 three drops; smile; frown
    dict(dur=22, set=ROOM, cam=camkf([(0, (1640, 500, 3.0)), (22, (1640, 500, 3.3))]), draw=drawD, grade=NIGHT),                  # 251 thinking
    dict(dur=27, set=ROOM, cam=camkf([(0, (1500, 420, 1.5)), (27, (1300, 402, 1.05))]), draw=drawD, grade=NIGHT, fade_out=(4.0, (0, 0, 0))),
]

subs = [
    (13.5, '红罐子里，是什么？', "What's in the red jar?", 'xiaoman'),
    (27.5, '一场雨。最大的那一场。', 'A rain. The biggest one.', 'granny'),
    (47.0, '那年我十岁。河水漫过了桥。', 'I was ten. The river came over the bridge.', None),
    (83.0, '我外婆把最大的罐子交给我，说：', 'My grandmother gave me the biggest jar and said:', None),
    (89.0, '只有孩子的手，它才肯进去。', "It will only go in for a child's hands.", None),
    (120.0, '我捧着罐子，站在桥上。它进去了。', 'I held up the jar on the bridge. And it went in.', None),
    (163.5, '从那以后，柳湾的雨，都是路过的小云带来的。', "Since then, Willow Bend's rain has only come from small passing clouds.", 'granny'),
    (174.0, '今年，小云不来了。', 'This year, the small clouds stopped coming.', 'granny'),
    (182.5, '那就打开它！', 'Then open it!', 'xiaoman'),
    (190.0, '打开它，洪水就回来了。我答应过的。', 'Open it and the flood comes back. I promised.', 'granny'),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 18)
    m.crickets(0, 40, 0.02); m.crickets(160, 215, 0.02)
    for t0 in FLASHES: m.thunder(t0 + 1.2, 0.28, far=True)
    m.pad(0, 40, [38, 45, 50], 0.022)
    m.add(m.guzheng(note(50), 5, 0.10), 27.6)
    # the puppet story: an erhu tells it, a drum for the flood, the dragon's roar, the jar's bell
    m.pad(40, 120, [38, 45, 50, 57], 0.025)
    m.melody(44, [(62, 2.0), (64, 1.0), (62, 1.0), (57, 3.0), (None, 1.0), (55, 1.0), (57, 1.0), (60, 2.0), (57, 4.0)], 'erhu', 0.05)
    m.rain([(40, 0.0), (52, 0.5), (110, 0.7), (141, 0.0)], heavy=1.2)
    for k in range(24): m.add(m.drum(48, 0.12, 1.0), 58 + k * 1.8)
    for t0 in (64.0, 71.0, 97.0, 118.0, 128.0): m.thunder(t0, 0.35)
    m.roar(70, 3.0, 0.18); m.roar(108, 3.5, 0.22)
    m.melody(84, [(57, 1.5), (60, 0.5), (62, 3.0), (None, 1.0), (64, 1.0), (62, 1.0), (60, 1.0), (57, 4.0)], 'erhu', 0.05)
    m.whoosh(112, 2.0, 0.12, up=False); m.whoosh(126, 2.0, 0.14, up=False)
    m.add(m.gong(7, 0.35, 70), 140.6); m.add(m.bell(note(62), 6, 0.12), 140.7)
    m.zheng_phrase(146, [62, 64, 66, 69, 71, None, 69, 66, 64, 62], 0.6, 0.07, 0.5, 4.0)
    # back to now
    m.pad(160, 55, [38, 45], 0.02)
    m.add(m.drum(60, 0.18, 0.5), 182.3)
    m.melody(192, [(57, 2.0), (55, 1.0), (52, 3.0), (None, 2.0), (50, 4.0)], 'erhu', 0.04)
    m.steps(216, 221, 1.4, 0.02, True); m.creak(220.5, 0.05)
    # in bed
    m.thunder(232.5, 0.15, far=True); m.thunder(267.5, 0.15, far=True); m.thunder(282.0, 0.15, far=True)
    m.pad(215, 85, [45, 52, 57], 0.02)
    for k, t0 in enumerate((242.6, 245.1, 247.6)): m.drip(t0, 0.10, 1300 + k * 120)
    m.zheng_phrase(249, [69, 72, 74, 76], 0.4, 0.07, 0.5)
    m.melody(258, [(64, 3.0), (62, 1.0), (60, 2.0), (57, 4.0), (None, 2.0), (60, 1.0), (62, 1.0), (64, 4.0)], 'erhu', 0.04)
    m.write(fn, 1.0, 3.0)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
