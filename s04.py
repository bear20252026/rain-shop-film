# Scene 4 · The Red Jar · 红罐子  (14:00 - 18:00)
import sys, math
from kit import *
from sets import TOWN, town_live, WATER_Y
from sets_shop import SHOP, shop_live, FEET, ALTAR, red_jar
from sets_more import ROOM, room_live, ROOM_FEET, DESK, BED
from s01 import named_jars, Q

NIGHT = (0.50, 0.42, 0.40)
DARK = (0.40, 0.33, 0.32)
STAIR = (2910, 438)          # Xiaoman's hiding step

def drawA(ctx, lt):      # he wakes, sits up, creeps out
    T = ctx.Tabs
    room_live(ctx, 0.7, 0.0)
    ctx.add_glow(DESK[0] + 75, DESK[2] - 66, 5, 0.6, W_WARM)        # a candle stub left burning
    ctx.add_glow(DESK[0] + 75, DESK[2] - 66, 80, 0.14, W_WARM)
    if T < 14:
        up = ease((T - 6) / 1.2)
        ctx.fig(1880, BED[2] - 4, 2.0, 'xiaoman', 1, dict(eyes='open' if T > 4 else 'closed', crouch=0.5 * up, arm_f=(160 - 120 * up, 10), look=-6 * up), rot=-90 * (1 - up))
    else:
        x, ph, f = walk_x([(14, 1700), (30, 700)], T, stride=26, s=2.0)
        ctx.fig(x, ROOM_FEET, 2.0, 'xiaoman', -1, dict(walk=ph, lean=10, arm_f=(30, 40), arm_b=(20, 40), look=6))

def granny_altar(ctx, T, turn=False):
    hand_on = 1 - ease((T - 104) / 0.8)
    reach = ease((T - 52) / 3)
    talk = 1 if (60 < T < 96 and int(T * 2.3) % 4 != 0) else 0
    p = dict(crouch=0.85, arm_f=(lerp(30, 128, reach * hand_on), lerp(30, -8, reach * hand_on)), arm_b=(30, 50), look=(16 if not turn else 8),
             talk=talk, eyes='closed' if 70 < T < 90 else 'open')
    if 100 < T < 112: p['eyes'] = 'wide'
    p['lean'] = 10
    return ctx.fig(1835, FEET - 20, 2.0, 'granny', -1 if turn else 1, p)

def drawB(ctx, lt):      # wide: from the stairs, Granny before the altar
    T = ctx.Tabs
    shop_live(ctx, glow=0.6, candles=(80,), rain_door=0.6, night=0.6, red=False)
    pulse = math.sin(min(1, max(0, (T - 100) / 3.0)) * math.pi)
    red_jar(ctx, *ALTAR, glow=0.55 * pulse)
    turn = T > 152
    granny_altar(ctx, T, turn)
    peek = T < 156
    if peek:
        ctx.fig(STAIR[0], STAIR[1], 1.9, 'xiaoman', -1, dict(crouch=0.7, look=-12, eyes='wide' if T > 100 else 'open', arm_f=(80, 30)))

def drawC(ctx, lt):      # close: her hand on the jar like on a child's head
    T = ctx.Tabs
    shop_live(ctx, glow=0.5, candles=(80,), rain_door=0.0, night=0.6, red=False)
    pulse = math.sin(min(1, max(0, (T - 100) / 3.0)) * math.pi)
    red_jar(ctx, *ALTAR, glow=0.55 * pulse)
    granny_altar(ctx, T)

def drawD(ctx, lt):      # Xiaoman's face between the banisters
    T = ctx.Tabs
    shop_live(ctx, glow=0.5, rain_door=0.0, night=0.6, red=True)
    ctx.fig(STAIR[0], STAIR[1], 1.9, 'xiaoman', -1, dict(crouch=0.7, look=-12, eyes='wide' if T > 101 else 'open', arm_f=(80, 30), mouth='open' if T > 101 else 'flat'))

def drawE(ctx, lt):      # the empty stair
    shop_live(ctx, glow=0.5, rain_door=0.0, night=0.6, red=True)

def drawF(ctx, lt):      # in bed, writing the question
    T = ctx.Tabs
    room_live(ctx, 0.5, 0.0)
    ctx.add_glow(OW * 0.5, OH * 0.2, 260, 0.10, W_WARM, world=False)
    x0, y0 = 520, 120
    B = ctx.layer(0, 0, OW, OH)       # the quilt fills the frame: an insert shot
    fill(B, [(-20, -20), (OW + 20, -20), (OW + 20, OH + 20), (-20, OH + 20)], 0.10, (0.62, 0.42, 0.30), 0.85, s=3, seed=78)
    rr = np.random.default_rng(4)
    for k in range(40):
        fx, fy = rr.random() * OW, rr.random() * OH
        line(B, [(fx + 9 * math.cos(q), fy + 9 * math.sin(q)) for q in np.linspace(0, 6.3, 12)], 1.0, 2, 0.35, 0, 90 + k, taper=False)
    L = ctx.layer(x0 - 20, y0 - 20, x0 + 900, y0 + 600)
    page = [(x0, y0), (x0 + 880, y0 + 6), (x0 + 874, y0 + 570), (x0 + 6, y0 + 566)]
    fill(L, page, 0.02, (0.92, 0.95, 0.97), 0.6, s=2, seed=11)
    line(L, page + [page[0]], 1.4, 2, 0.5, 0, 12, taper=False)
    for k in range(8): line(L, [(x0 + 30, y0 + 70 + k * 64), (x0 + 850, y0 + 74 + k * 64)], 0.8, 2, 0.18, 0, 13 + k, taper=False)
    u = ease((lt - 1.0) / 6.0)
    brush_text(L, '红罐子里有什么？', x0 + 60, y0 + 230, 70, False, d=0.75, reveal=u, anchor='lm')
    # (the little doodle of the jar beside it)
    if lt > 7.5:
        jx, jy = x0 + 700, y0 + 420
        line(L, [(jx + 40 * math.cos(q), jy - 50 * (1 - math.cos(q)) / 2 * 2 + 0) for q in np.linspace(0, math.pi, 12)], 1.6, 2, 0.6, 0.3, 30)
        line(L, [(jx - 40 * math.cos(q), jy - 50 * (1 - math.cos(q)) / 2 * 2) for q in np.linspace(0, math.pi, 12)], 1.6, 2, 0.6, 0.3, 31)
        line(L, [(jx - 30, jy - 100), (jx + 30, jy - 100)], 2.0, 2, 0.6, 0, 32, taper=False)
        for k in range(3): line(L, [(jx - 50 + k * 50, jy - 130), (jx - 46 + k * 50, jy - 150)], 1.4, 2, 0.6, 0, 33 + k)
    pen = (x0 + 60 + 680 * u + math.sin(T * 9) * 6, y0 + 230 + math.sin(T * 13) * 8)
    if lt < 7.5: stick(ctx, pen, 35, 200, 1.0, w=7, seed=9)

def drawG(ctx, lt):      # outside: the rain thins and stops; the last drop
    T = ctx.Tabs
    amt = 1 - ease(lt / 14)
    town_live(ctx, rain_amt=amt * 0.8, drips_on=amt > 0.25, ripples_on=amt > 0.25, jars_glow=0.6)

def drawH(ctx, lt):      # the very last drop on the eave, close
    T = ctx.Tabs
    town_live(ctx, rain_amt=0.0, drips_on=False, ripples_on=False, jars_glow=0.0, cormorant=False)
    x, ey = 1700, 400
    if lt < 4.0:
        swell = ease(lt / 3.5)
        ctx.add_glow(x, ey + 2 + 3 * swell, 2.5 + 2 * swell, 0.6, W_DRIZZLE)
    elif lt < 5.2:
        u = (lt - 4.0) / 1.2
        ctx.add_glow(x, ey + 6 + u * u * 200, 3.5, 0.7, W_DRIZZLE)

def post_sun(img, lt, ctx):
    """dissolve into a hard, bright sun"""
    u = ease((lt - 6.0) / 3.0)
    warm = np.array([0.88, 0.96, 1.0], np.float32)
    flash = math.exp(-((lt - 7.5) / 1.2) ** 2) * 0.55
    return img * (1 - flash) + warm * flash

shots = [
    dict(dur=30, set=ROOM, cam=camkf([(0, (1800, 420, 1.6)), (14, (1700, 420, 1.4)), (30, (1000, 420, 1.1))]), draw=drawA, grade=NIGHT, fade_in=(2.0, (0, 0, 0))),
    dict(dur=20, set=SHOP, cam=camkf([(0, (2500, 360, 1.15)), (20, (2420, 370, 1.2))]), draw=drawB, grade=DARK, xfade=1.0),           # 30
    dict(dur=24, set=SHOP, cam=camkf([(0, (1930, 470, 2.4)), (24, (1940, 480, 2.7))]), draw=drawC, grade=DARK),                        # 50
    dict(dur=8, set=SHOP, cam=(2905, 300, 3.0), draw=drawD, grade=DARK),                                                              # 74
    dict(dur=18, set=SHOP, cam=camkf([(0, (1930, 480, 2.7)), (18, (1940, 470, 3.0))]), draw=drawC, grade=DARK),                        # 82
    dict(dur=6, set=SHOP, cam=(2905, 300, 3.0), draw=drawD, grade=DARK),                                                              # 100: the pulse, his face
    dict(dur=16, set=SHOP, cam=camkf([(0, (1950, 460, 2.2)), (16, (1950, 470, 2.4))]), draw=drawC, grade=DARK),                        # 106 "not yet"
    dict(dur=34, set=SHOP, cam=camkf([(0, (2450, 380, 1.2)), (34, (2400, 380, 1.25))]), draw=drawB, grade=DARK),                       # 122 the creak, she turns
    dict(dur=12, set=SHOP, cam=(2905, 300, 2.6), draw=drawE, grade=DARK),                                                             # 156 empty stair
    dict(dur=14, set=ROOM, cam=(960, 402, 1.0), draw=drawF, grade=(0.62, 0.56, 0.52), xfade=1.0),                                      # 168 notebook
    dict(dur=16, set=ROOM, cam=camkf([(0, (1880, 450, 1.6)), (16, (1880, 460, 1.7))]), draw=lambda c, l: (room_live(c, 0.4, 0.0), c.fig(1880, BED[2] - 4, 2.0, 'xiaoman', 1, dict(eyes='open' if l < 9 else 'closed', arm_f=(160, 10)), rot=-90)), grade=NIGHT),  # 182
    dict(dur=24, set=TOWN, cam=camkf([(0, (1300, 402, 1.0)), (24, (1600, 402, 1.0))]), draw=drawG, xfade=2.0, grade=lambda t: tuple(lerp(0.75, 1.0, ease(t / 20)) for _ in range(3))),   # 198 dawn
    dict(dur=6, set=TOWN, cam=(1700, 470, 3.2), draw=drawH),                                                                           # 222 the last drop
    dict(dur=12, set=TOWN, cam=camkf([(0, (1500, 402, 1.0)), (12, (1450, 402, 1.0))]), draw=lambda c, l: town_live(c, 0.0, False, True, False, jars_glow=0.4),
         args=dict(sun=1.0, mist=0.0), post=post_sun, xfade=1.5),                                                                      # 228 bright sun
]

subs = [
    (108.5, '再等等。还不行。', 'Wait a little more. Not yet.', 'granny'),
    (171.0, 178.0, '红罐子里有什么？', "What's in the red jar?", None),
]
scene = Scene(shots, subs)

def sound(fn):
    m = Mix(scene.dur, 14)
    m.rain([(0, 0.0), (2, 0.4), (30, 0.4), (31, 0.3), (168, 0.3), (169, 0.4), (198, 0.6), (212, 0.15), (222, 0.0), (240, 0.0)])
    m.drips(198, 214, 1.2, 0.05)
    m.pad(2, 26, [38, 45], 0.03)
    m.creak(17, 0.04); m.creak(24, 0.05); m.steps(15, 29, 1.4, 0.02, True)
    # Granny's whisper scene: low drones, rain only; a single guzheng note now and then
    m.pad(30, 70, [38, 45, 50], 0.025)
    for at, n_ in [(34, 50), (44, 57), (58, 53), (72, 50), (86, 57)]: m.add(m.guzheng(note(n_), 4, 0.10), at)
    # the pulse
    m.rumble(100.2, 4.0, 0.22, 34); m.add(m.bell(note(74), 4, 0.05), 100.3)
    m.breath(101, 2.5, 0.06)
    m.melody(110, [(62, 2.0), (60, 1.0), (57, 3.0)], 'erhu', 0.04)
    m.creak(150.5, 0.10)
    m.add(m.drum(55, 0.08), 152.2)
    m.steps(156.2, 158.5, 4, 0.02, True)
    m.pencil(169, 176, 0.03)
    m.zheng_phrase(176, [62, None, 64, None, 66, None, None, 69], 0.5, 0.10, 0.6)
    # the rain stops
    m.melody(200, [(74, 2.0), (71, 1.0), (69, 2.0), (66, 3.0), (None, 2.0), (64, 1.0), (62, 4.0)], 'dizi', 0.06)
    m.drip(226.3, 0.18, 1100)
    m.cicadas(229, 240, 0.03)
    m.add(m.gong(5, 0.18, 70), 233.5)
    m.write(fn, 1.0, 1.0)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'frames': run(scene, sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    elif cmd == 'still':
        for t in sys.argv[3:]: still(scene, float(t), f'{sys.argv[2]}_{t}.jpg')
    elif cmd == 'sound': sound(sys.argv[2])
    print('dur', scene.dur)
