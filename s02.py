# Scene 2 · The Boy on the Boat · 船上的男孩  (5:00 - 10:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_shop import SHOP, shop_live, FEET, ALTAR, red_jar
from sets_more import ROOM, room_live, ROOM_FEET, DESK, BED
from s01 import named_jars, Q

STEP_X = 1600          # where the ferry ties up below the shop
NIGHT = (0.62, 0.55, 0.52)

def ferry(ctx, x, talkers=(), xm_pose=None, fm_pose=None, laugh=False):
    deck = sampan(ctx, x, WATER_Y + 52, 1.0, seed=611)
    t = ctx.Tabs
    fp = dict(arm_f=(150, -30), arm_b=(120, -10), lean=12, bob=False, mouth='smile' if laugh else 'flat', eyes='happy' if laugh else 'open')
    fp.update(fm_pose or {})
    r = ctx.fig(deck[0], deck[1], 1.0, 'ferryman', -1 if fm_pose and fm_pose.get('turn') else 1, {k: v for k, v in fp.items() if k != 'turn'})
    if r: pole(ctx, r['hand_f'], 18 + 6 * math.sin(t * 0.8), ctx.z)
    xp = dict(backpack=1, look=4, arm_f=(10, 20)); xp.update(xm_pose or {})
    ctx.fig(x - 70, WATER_Y + 52 - 20, 0.95, 'xiaoman', 1, xp)
    return deck

# ---------------------------------------------------------------- A/B: the ferry comes through the rain
def drawA(ctx, lt):
    town_live(ctx, rain_amt=1.0)
    ferry(ctx, 500 + lt * 26)
def drawB(ctx, lt):
    town_live(ctx, rain_amt=1.0)
    T = ctx.Tabs
    x = 500 + 20 * 26 + (T - 20) * 22
    ferry(ctx, x, fm_pose=dict(turn=1, look=-6) if 21.5 < T < 26 or 30 < T < 34 else None, laugh=30 < T < 34,
          xm_pose=dict(look=10 if T < 27 else 0, arm_f=(30, 40) if 26.5 < T < 30 else (10, 20)))

# ---------------------------------------------------------------- C/D: the steps; Granny with an umbrella
def granny_steps(ctx, lt, pose=None):
    p = dict(arm_f=(25, 105), look=-8); p.update(pose or {})
    r = ctx.fig(1680, Q, 1.12, 'granny', -1, p)
    if r: umbrella(ctx, r['hand_f'], 1.12 * ctx.z, 3, -6)

def xm_path(T):
    """Xiaoman from the boat up onto the quay"""
    if T < 44: return STEP_X - 70, WATER_Y + 32, None
    u = ease((T - 44) / 1.2)
    if T < 45.2:
        x = lerp(STEP_X - 70, STEP_X - 20, u); y = lerp(WATER_Y + 32, Q, u) - math.sin(u * math.pi) * 30
        return x, y, None
    x, ph, f = walk_x([(45.2, STEP_X - 20), (48, STEP_X + 30)], T, s=0.95)
    return x, Q, ph

def drawC(ctx, lt):
    T = ctx.Tabs
    town_live(ctx, rain_amt=1.0, look=0.0)
    x = min(STEP_X, 500 + 20 * 26 + 14 * 22 + (T - 34) * 30)
    deck = sampan(ctx, x, WATER_Y + 52, 1.0, seed=611)
    r = ctx.fig(deck[0], deck[1], 1.0, 'ferryman', 1, dict(arm_f=(150, -30), arm_b=(120, -10), lean=12, bob=False))
    if r: pole(ctx, r['hand_f'], 10, ctx.z)
    xx, yy, ph = xm_path(T)
    ctx.fig(xx, yy, 0.95, 'xiaoman', 1, dict(backpack=1, walk=ph, look=6))
    granny_steps(ctx, lt)

def drawD(ctx, lt):
    T = ctx.Tabs
    town_live(ctx, rain_amt=1.0, look=1.0 if T > 70 else 0.0)
    deck = sampan(ctx, STEP_X, WATER_Y + 52, 1.0, seed=611)
    ctx.fig(deck[0], deck[1], 1.0, 'ferryman', 1, dict(arm_f=(150, -30), arm_b=(120, -10), lean=12, bob=False, eyes='happy' if T > 72 else 'open'))
    ctx.fig(STEP_X + 30, Q, 0.95, 'xiaoman', 1, dict(backpack=1, look=8, mouth='frown' if T > 70 else 'flat'))
    granny_steps(ctx, lt, dict(mouth='flat'))

def drawD2(ctx, lt):      # Old Ink snorts
    town_live(ctx, rain_amt=1.0, look=1.0)
    if 1.0 < lt < 1.4: ctx.add_glow(*ctx.T(2108, WATER_Y - 146), 3, 0.3, W_DRIZZLE, world=False)

def drawE(ctx, lt):       # they go in
    T = ctx.Tabs
    town_live(ctx, rain_amt=1.0)
    x, ph, f = walk_x([(78, 1680), (81, 1700), (86, 1760)], T, s=1.12)
    r = ctx.fig(x, Q, 1.12, 'granny', 1 if ph is not None else -1, dict(walk=ph, arm_f=(25, 105)))
    if r and T < 82: umbrella(ctx, r['hand_f'], 1.12 * ctx.z, 3, -6, open_=1 - ease((T - 80) / 1.5))
    x, ph, f = walk_x([(80, STEP_X + 30), (88, 1760)], T, s=0.95)
    ctx.fig(x, Q, 0.95, 'xiaoman', 1, dict(backpack=1, walk=ph))

# ---------------------------------------------------------------- F: the rules board
BOARD = (2290, 330)
def drawF(ctx, lt):
    T = ctx.Tabs
    shop_live(ctx, rain_door=0.8)
    tap = 0
    for tt0 in (93.5, 94.3, 95.1): tap = max(tap, math.sin(min(1, max(0, (T - tt0) / 0.3)) * math.pi))
    gp = dict(arm_f=(lerp(20, 150, ease((T - 92) / 1.0) * (1 - ease((T - 97) / 1.0))) - 12 * tap, 10), look=8 if T < 99 else -6)
    gx = 2200 if T < 120 else lerp(2200, 2060, ease((T - 128) / 2.0))
    ctx.fig(gx, FEET, 2.0, 'granny', 1 if T < 99 else -1, gp)
    lookjar = 118 < T < 132
    ctx.fig(2400, FEET + 20, 1.85, 'xiaoman', -1, dict(backpack=1, look=(4 if not lookjar else -2), mouth='flat', eyes='wide' if 120 < T < 124 else 'open'), over=True)

def drawF2(ctx, lt):    # what Xiaoman sees: the altar, the red jar
    T = ctx.Tabs
    shop_live(ctx, rain_door=0.8)
    if T > 121.5: ctx.add_glow(ALTAR[0], ALTAR[1] - 40, 20, 0.10 * math.sin(min(1, (T - 121.5) / 2.5) * math.pi), W_DRAGON)
    # Granny steps into frame, blocking it
    x = lerp(2300, 2010, ease((T - 126) / 1.4))
    ctx.fig(x, FEET, 2.0, 'granny', -1, dict(look=-4, walk=(x / 90 if 126 < T < 127.4 else None)))

# ---------------------------------------------------------------- G: supper
def bowl(ctx, x, y, s=1.0, rice=True):
    sx, sy = ctx.T(x, y); se = s * ctx.z
    L = ctx.layer(sx - 30 * se, sy - 30 * se, sx + 30 * se, sy + 10 * se)
    b = [(sx + 18 * se * math.cos(q), sy - 2 * se + 12 * se * math.sin(q)) for q in np.linspace(0, math.pi, 16)]
    fill(L, b, 0.04, (0.90, 0.88, 0.80), 0.7, s=se, seed=int(x))
    line(L, b + [b[0]], 1.2, se, 0.85, 0, int(x) + 1, taper=False)
    if rice:
        top = [(sx + 16 * se * math.cos(q), sy - 2 * se - 8 * se * math.sin(q)) for q in np.linspace(0, math.pi, 12)]
        fill(L, top, 0.02, (0.95, 0.96, 0.96), 0.6, s=se, seed=int(x) + 2)
        line(L, top, 0.9, se, 0.5, 0, int(x) + 3, taper=False)

def greens(ctx, x, y, s=1.0):
    sx, sy = ctx.T(x, y); se = s * ctx.z
    L = ctx.layer(sx - 40 * se, sy - 24 * se, sx + 40 * se, sy + 10 * se)
    pl = [(sx + 30 * se * math.cos(q), sy + 6 * se * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 20)]
    fill(L, pl, 0.03, (0.90, 0.90, 0.85), 0.6, s=se, seed=5)
    for k in range(6):
        cx = sx - 18 * se + k * 7 * se; cy = sy - 4 * se - (k % 2) * 3 * se
        lf = [(cx + 6 * se * math.cos(q), cy + 3.5 * se * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 12)]
        fill(L, lf, 0.10, (0.40, 0.70, 0.45), 0.8, s=se, seed=10 + k)

def chopsticks(ctx, hand, se, up):
    hx, hy = hand
    L = ctx.layer(hx - 50 * se, hy - 50 * se, hx + 50 * se, hy + 50 * se)
    for k in (0, 1):
        line(L, [(hx, hy), (hx - 34 * se, hy + (8 - 16 * up) * se + k * 3 * se)], 1.4, se, 0.9, 0, 700 + k, taper=False)

TAB_Y = 610
def drawG(ctx, lt):
    T = ctx.Tabs
    shop_live(ctx, glow=0.8, rain_door=0.6, night=0.4)
    ctx.add_glow(2660, TAB_Y - 44, 6, 0.85 * (0.92 + 0.08 * math.sin(T * 11)), W_WARM)
    ctx.add_glow(2660, TAB_Y - 44, 120, 0.16, W_WARM)
    for side, (x, who, f) in enumerate([(2470, 'granny', 1), (2860, 'xiaoman', -1)]):
        ph = (T * (0.55 if who == 'granny' else 0.4) + side * 0.3) % 1
        eat = math.sin(ph * 2 * math.pi) * 0.5 + 0.5
        if who == 'xiaoman' and 190 < T < 210: eat = 0.2
        r = ctx.fig(x, FEET - 6, 2.0, who, f, dict(crouch=0.55, arm_f=(60 + 40 * eat, 50 - 20 * eat), arm_b=(55, 60), look=-4 + 6 * eat,
                                                   eyes='closed' if (who == 'granny' and 205 < T < 207) else 'open'))
        if r: chopsticks(ctx, r['hand_f'], 2.0 * ctx.z * (1 if f > 0 else -1) * f, eat)
    bowl(ctx, 2580, TAB_Y, 1.6); bowl(ctx, 2745, TAB_Y, 1.6); greens(ctx, 2662, TAB_Y, 1.5)
    # a small oil lamp on the table
    L = ctx.box(2660, TAB_Y - 20, 20, 30)
    sx, sy = ctx.T(2660, TAB_Y); se = 1.6 * ctx.z
    fill(L, [(sx - 7 * se, sy), (sx + 7 * se, sy), (sx + 4 * se, sy - 14 * se), (sx - 4 * se, sy - 14 * se)], 0.3, s=se, seed=3)

# ---------------------------------------------------------------- H: the room upstairs, the comic, sleep
def comic(ctx, x, y, w, reveal, t):
    """Xiaoman's comic: Granny as a dragon, breathing rain clouds"""
    L = ctx.layer(x - 10, y - 10, x + w + 10, y + w * 0.75 + 10)
    page = [(x, y), (x + w, y + 4), (x + w - 3, y + w * 0.75), (x + 2, y + w * 0.75 - 2)]
    fill(L, page, 0.02, (0.92, 0.95, 0.97), 0.6, s=2, seed=1)
    line(L, page + [page[0]], 1.4, 2, 0.6, 0, 2, taper=False)
    def ok(u): return reveal > u
    s = w / 600
    hx, hy = x + w * 0.52, y + w * 0.30
    if ok(0.05):
        head = [(hx + 46 * s * math.cos(q), hy + 44 * s * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 30)]
        line(L, head, 2.0, s * 2, 0.85, 0.2, 3, taper=False)
        line(L, [(hx - 50 * s + 22 * s * math.cos(q), hy - 50 * s + 22 * s * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 20)], 2.0, s * 2, 0.85, 0.2, 4, taper=False)
    if ok(0.2):
        line(L, [(hx + 10 * s, hy - 6 * s), (hx + 22 * s, hy - 10 * s)], 2.2, s * 2, 0.9, 0, 5, taper=False)
        line(L, [(hx - 16 * s, hy - 6 * s), (hx - 4 * s, hy - 10 * s)], 2.2, s * 2, 0.9, 0, 6, taper=False)
        line(L, [(hx - 2 * s, hy + 18 * s), (hx + 14 * s, hy + 14 * s)], 1.8, s * 2, 0.9, 0, 7, taper=False)
        for k in (-1, 1): line(L, [(hx + k * 20 * s, hy - 40 * s), (hx + k * 34 * s, hy - 80 * s), (hx + k * 24 * s, hy - 92 * s)], 2.0, s * 2, 0.85, 0, 8 + k)
    if ok(0.4):     # long dragon body behind
        body = [(hx - 50 * s - k * 22 * s, hy + 30 * s + math.sin(k * 0.8) * 34 * s) for k in range(14)]
        line(L, body, np.linspace(9, 2, 14) * s, 2, 0.85, 0.3, 11)
        line(L, [(p[0], p[1] + 30 * s * (1 - i / 14)) for i, p in enumerate(body)], np.linspace(5, 1, 14) * s, 2, 0.7, 0.3, 12)
    if ok(0.6):     # clouds from her mouth, rain below
        for k in range(3):
            cx = hx + 90 * s + k * 70 * s; cy = hy + 10 * s - k * 20 * s
            pts = [(cx + (24 + 6 * math.sin(q * 5)) * s * math.cos(q), cy + (14 + 4 * math.sin(q * 5)) * s * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 30)]
            line(L, pts, 1.8, s * 2, 0.8, 0.2, 20 + k, taper=False)
            if ok(0.75):
                for j in range(4): line(L, [(cx - 15 * s + j * 10 * s, cy + 22 * s), (cx - 19 * s + j * 10 * s, cy + 46 * s)], 1.4, s * 2, 0.8, 0, 30 + j)
    if ok(0.9):
        brush_text(L, '雨龙外婆', x + w * 0.18, y + w * 0.62, 34 * s * 2, False, anchor='lm')

def drawH(ctx, lt):
    T = ctx.Tabs
    room_live(ctx, 1.0, 1.0)
    pen = math.sin(T * 9) * 0.5 + 0.5
    r = ctx.fig(DESK[0] + 230, ROOM_FEET, 2.0, 'xiaoman', -1, dict(crouch=0.5, arm_f=(70 + 10 * pen, 40), look=-18, lean=6))
    notebook(ctx, *ctx.T(DESK[0] + 170, DESK[2] - 6), 1.6 * ctx.z)

def drawH2(ctx, lt):    # close: the comic page
    T = ctx.Tabs
    room_live(ctx, 0.6, 1.2)
    D = ctx.layer(0, 0, OW, 804)      # the desk top fills the frame: this is an insert shot
    fill(D, [(-20, -20), (OW + 20, -20), (OW + 20, 824), (-20, 824)], 0.05, (0.40, 0.30, 0.20), 0.9, s=3, seed=77)
    for k in range(9):
        yy = 40 + k * 92 + math.sin(k * 2.3) * 20
        line(D, [(-10, yy), (OW * 0.4, yy + 8 * math.sin(k)), (OW + 10, yy - 6)], 1.0, 2, 0.25, 0.4, 80 + k, taper=False)
    comic(ctx, 520, 90, 880, ease((lt - 0.5) / 14), T)
    pen_x = 520 + 880 * (0.3 + 0.5 * ease((lt - 0.5) / 14)) + math.sin(T * 7) * 20
    pen_y = 90 + 880 * 0.75 * (0.3 + 0.4 * ease((lt - 0.5) / 14)) + math.sin(T * 11) * 14
    stick(ctx, (pen_x, pen_y), 30, 180, 1.0, w=6, seed=9)
    ctx.add_glow(OW * 0.15, 80, 200, 0.12, W_WARM, world=False)

def drawH3(ctx, lt):    # asleep in bed; the lamp goes out
    T = ctx.Tabs
    room_live(ctx, 1.0, 1.0 - ease((lt - 9) / 1.0))
    ctx.fig(1880, BED[2] - 4, 2.0, 'xiaoman', 1, dict(eyes='closed', arm_f=(160, 10), mouth='smile' if lt > 14 else 'flat'), rot=-90)

shots = [
    dict(dur=20, set=TOWN, cam=lambda t: (lerp(700, 1150, ease(t / 20)), 402, 1.0), draw=drawA, fade_in=(1.5, (0, 0, 0))),
    dict(dur=14, set=TOWN, cam=lambda t: (500 + 20 * 26 + t * 22 + 40, 500, 2.0), draw=drawB),
    dict(dur=26, set=TOWN, cam=camkf([(0, (1350, 470, 1.6)), (8, (1560, 470, 1.6)), (26, (1640, 480, 1.9))]), draw=drawC),
    dict(dur=12, set=TOWN, cam=camkf([(0, (1640, 480, 2.2)), (12, (1650, 485, 2.4))]), draw=drawD),
    dict(dur=6, set=TOWN, cam=(2085, 470, 3.0), draw=drawD2),
    dict(dur=12, set=TOWN, cam=(1700, 470, 1.8), draw=drawE),
    dict(dur=28, set=SHOP, cam=camkf([(0, (2250, 360, 1.5)), (28, (2270, 350, 1.6))]), draw=drawF, xfade=1.0),     # 90
    dict(dur=12, set=SHOP, cam=camkf([(0, (1975, 420, 2.4)), (12, (1975, 430, 2.7))]), draw=drawF2),            # 118
    dict(dur=20, set=SHOP, cam=(2200, 380, 1.4), draw=drawF),                                                    # 130
    dict(dur=40, set=SHOP, cam=camkf([(0, (2660, 430, 1.25)), (40, (2660, 440, 1.35))]), draw=drawG, xfade=1.5, grade=NIGHT),   # 150
    dict(dur=10, set=SHOP, cam=(2840, 420, 2.2), draw=drawG, grade=NIGHT),                                       # 190 Xiaoman asks
    dict(dur=8, set=SHOP, cam=(2480, 420, 2.2), draw=drawG, grade=NIGHT),                                        # 200 "Eat."
    dict(dur=32, set=SHOP, cam=camkf([(0, (2660, 430, 1.25)), (32, (2660, 420, 1.15))]), draw=drawG, grade=NIGHT),  # 208
    dict(dur=16, set=ROOM, cam=camkf([(0, (900, 400, 1.2)), (16, (700, 430, 1.5))]), draw=drawH, xfade=1.5, grade=(0.6, 0.52, 0.48)),   # 240
    dict(dur=18, set=ROOM, cam=(960, 402, 1.0), draw=drawH2, args=dict(), grade=(0.66, 0.76, 0.86)),            # 256 the comic (drawn over a dim room)
    dict(dur=26, set=ROOM, cam=camkf([(0, (1700, 420, 1.25)), (26, (1880, 450, 1.6))]), draw=drawH3, xfade=1.5, grade=(0.55, 0.47, 0.43), fade_out=(4.0, (0, 0, 0))),  # 274
]

subs = [
    (22.0, '柳湾到了。你外婆的店就在桥边。', "Willow Bend. Your granny's shop is by the bridge.", 'ferryman'),
    (27.0, '这里有WiFi吗？', 'Is there WiFi here?', 'xiaoman'),
    (30.3, '这里有雨。', "There's rain here.", 'ferryman'),
    (62.0, '你妈说你会洗碗。', 'Your mother says you can wash dishes.', 'granny'),
    (67.0, '……我妈说你会做饭。', '...My mother says you can cook.', 'xiaoman'),
    (96.0, 102.5, '一、不准碰罐子。二、不准碰罐子。三、红的那个，永远不准。', "1. Don't touch the jars.  2. Don't touch the jars.  3. NEVER the red one.", None),
    (108.0, '第一条和第二条一样。', 'Rules one and two are the same.', 'xiaoman'),
    (113.0, '因为很重要。', "Because it's important.", 'granny'),
    (193.0, '罐子里……真的是天气？', 'Is there... really weather in the jars?', 'xiaoman'),
    (201.0, '吃饭。', 'Eat.', 'granny'),
    (266.0, 271.0, '雨龙外婆', 'Rain-Dragon Granny', None),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 12)
    m.rain([(0, 0.0), (2, 1.0), (90, 1.0), (91, 0.45), (150, 0.45), (151, 0.35), (240, 0.35), (241, 0.6), (296, 0.5), (300, 0.0)])
    m.drips(0, 90, 1.6)
    for k in range(12): m.oar(2 + k * 4.0, 0.06)
    m.zheng_phrase(3, [57, None, 62, 64, None, 62, 57, None], 0.7, 0.14, 0.35)
    m.melody(9, [(69, 0.8), (71, 0.4), (74, 1.4), (None, 0.5), (71, 0.5), (69, 0.5), (66, 1.6)], 'dizi', 0.07)
    m.add(m.woodblock(1300, 0.04), 27.4)       # a little "ping" for WiFi
    m.add(m.chime(note(93), 0.04), 27.6)
    m.zheng_phrase(31, [74, 76, 74, 71], 0.18, 0.10)      # the ferryman's laugh
    m.splash(44.2, 0.08); m.step(45.3, 0.06)
    m.pad(48, 12, [50, 57], 0.03)      # the long look
    m.snort(73.2, 0.10)
    m.steps(78, 88, 2.2, 0.04)
    # the board
    for tt0 in (93.5, 94.3, 95.1): m.knock(tt0 + 0.25, 0.09)
    m.zheng_phrase(96, [62, None, 62, None, (66, 0.04)], 0.6, 0.12)
    m.rumble(121, 3, 0.08, 36); m.pad(121, 6, [38, 45], 0.03)
    m.steps(126, 127.6, 3, 0.04)
    # supper: just rain, chopsticks, a lonely erhu
    m.chopsticks(150, 240, 0.05)
    m.melody(156, [(62, 2.0), (64, 0.8), (66, 1.2), (62, 2.8), (None, 2), (57, 1.6), (59, 0.8), (62, 3.0)], 'erhu', 0.05)
    m.melody(214, [(69, 1.6), (66, 0.8), (64, 1.2), (62, 3.2)], 'erhu', 0.045)
    # the comic: pencil, a playful tune
    m.pencil(244, 272, 0.02)
    m.zheng_phrase(256, [74, 78, 81, 78, 74, None, 76, 78, 76, 74, 71, None, 74], 0.45, 0.12, 0.6)
    m.add(m.bell(note(86), 2.5, 0.05), 266)
    # sleep
    m.zheng_phrase(276, [62, None, 57, None, 54, None, None, 50], 0.9, 0.12)
    m.pad(280, 18, [38, 45, 50], 0.03)
    m.write(fn, 1.0, 4.0)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
