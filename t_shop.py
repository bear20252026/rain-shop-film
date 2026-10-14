import time
from engine import *
from sets_shop import *
def draw(ctx, lt):
    shop_live(ctx, candles=True)
    ctx.fig(1100, 690, 2.1, 'granny', -1, dict(arm_f=(60, 30)))
    ctx.fig(700, FEET+30, 2.1, 'bride', 1, dict(), over=True)
    ctx.fig(560, FEET+40, 2.1, 'mother', 1, dict(), over=True)
    ctx.fig(2300, FEET, 2.0, 'xiaoman', -1, dict(look=10))
shots=[dict(dur=2, set=SHOP, cam=(1500, 402, 0.64), draw=draw),
       dict(dur=2, set=SHOP, cam=(1000, 402, 1.0), draw=draw),
       dict(dur=2, set=SHOP, cam=(2200, 360, 1.3), draw=draw, grade=(0.55,0.45,0.42))]
sc=Scene(shots)
for i,t in enumerate([0.5,2.5,4.5]):
    t0=time.time(); still(sc, t, f'ts{i}.jpg'); print(i, time.time()-t0)
