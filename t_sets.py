import time, sys
from engine import *
from sets_more import *
def d_room(ctx, lt):
    room_live(ctx, 1, 1)
    ctx.fig(560, ROOM_FEET, 2.0, 'xiaoman', 1, dict(crouch=0.6, arm_f=(70, 30)))
    ctx.fig(1900, 545, 2.0, 'xiaoman', 1, dict(eyes='closed'), rot=-90)
def d_br(ctx, lt):
    strands(ctx, BR_STRANDS)
    for x, who in ((1300, 'twin'), (1360, 'xiaoman'), (1420, 'twin')): ctx.fig(x, deck_y(x), 1.8, who, 1)
def d_lane(ctx, lt):
    laundry(ctx, 0.4, 0.0)
    ctx.fig(1300, LANE_G, 1.8, 'poet', 1)
def d_mud(ctx, lt):
    ctx.fig(1800, 700, depth_s(700), 'xiaoman', 1)
    ctx.fig(2300, 560, depth_s(560), 'qian', -1)
def d_city(ctx, lt): city_live(ctx)
shots=[dict(dur=1, set=ROOM, cam=(1200, 402, 1.0), draw=d_room, grade=(0.6,0.5,0.45)),
 dict(dur=1, set=BRIDGE, cam=(1400, 402, 1.0), draw=d_br),
 dict(dur=1, set=LANE, cam=(1300, 402, 1.0), draw=d_lane),
 dict(dur=1, set=MUDFLAT, cam=(2200, 402, 1.0), draw=d_mud),
 dict(dur=1, set=SKY, cam=(1300, 1500, 1.0)),
 dict(dur=1, set=ROOFS, cam=(1400, 402, 1.0)),
 dict(dur=1, set=SCREEN, cam=(960, 402, 1.0)),
 dict(dur=1, set=CITY, cam=(960, 402, 1.0), draw=d_city)]
sc=Scene(shots)
for i in range(8):
    t0=time.time(); still(sc, i+0.5, f'tq{i}.jpg'); print(i, time.time()-t0, flush=True)
