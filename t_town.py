import time, sys
from engine import *
from sets import *
def draw(ctx, lt):
    a = ctx.args
    town_live(ctx, a.get('rain',1), water=a.get('water',1), color=a.get('color',0), night=a.get('night',0))
    ctx.fig(1500, WATER_Y-18, 1.12, 'granny', -1, dict(arm_f=(150, 20)))
    ctx.fig(1420, WATER_Y-18, 1.0, 'xiaoman', 1, dict(walk=lt*1.2, backpack=1))
    ctx.fig(1300, WATER_Y-18, 1.1, 'qian', 1, dict(arm_f=(80, 10)))
shots=[dict(dur=2, set=TOWN, cam=(1400, 402, 1.0), draw=draw, args=dict()),
       dict(dur=2, set=TOWN, cam=(1450, 470, 2.0), draw=draw, args=dict(water=0, rain=0, sun=1, mist=0)),
       dict(dur=2, set=TOWN, cam=(1300, 402, 1.0), draw=draw, args=dict(water=0.5, rain=0.5, color=1)),
       dict(dur=2, set=TOWN, cam=(1300, 402, 1.0), draw=draw, args=dict(night=1, rain=0.3), grade=(0.62,0.48,0.42))]
sc=Scene(shots)
for i,t in enumerate([0.5,2.5,4.5,6.5]):
    t0=time.time(); still(sc, t, f'tt{i}.jpg'); print(i, time.time()-t0)
