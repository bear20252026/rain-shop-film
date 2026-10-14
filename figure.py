# Parametric ink characters (Feng Zikai-like): a simple skeleton dressed with rounded garment shapes.
# Local coords: feet at (0,0), y up is negative, +x is the direction the character faces.
import numpy as np, cv2, math
from ink import *
from chars import Layer, fill, line, path, SKIN, INDIGO, ease, lerp

def tube(pts, w):
    """polygon around a polyline with per-point half-widths"""
    pts = np.asarray(pts, np.float32); n = len(pts); w = np.broadcast_to(np.asarray(w, np.float32), (n,))
    d = np.gradient(pts, axis=0); d /= (np.linalg.norm(d, axis=1, keepdims=True) + 1e-6)
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    left = pts + nrm * w[:, None]; right = pts - nrm * w[:, None]
    cap0 = [pts[0] - d[0] * w[0] * 0.6]; cap1 = [pts[-1] + d[-1] * w[-1] * 0.6]
    return np.vstack([left, cap1, right[::-1], cap0]), left, right

def limb(a, b, c, n=14):
    """smooth polyline through joint b"""
    return bezier(a, b, c, n=n) if False else np.vstack([bezier(a, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), b, n=n // 2), bezier(b, ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2), c, n=n // 2)[1:]])

def polar(o, ang_deg, L):
    """angle 0 = straight down, positive swings toward the facing direction (+x)"""
    a = math.radians(ang_deg); return (o[0] + math.sin(a) * L, o[1] + math.cos(a) * L)

SPECS = {
    'granny':  dict(leg=52, torso=72, head=19, sh=17, hip=16, arm=58, hump=12, belly=0, garment='long_jacket', hem=50,
                    top=(0.16, INDIGO, 0.75), bottom=(0.58, None, 0), hair='bun', skin=SKIN, shoe=0.92, brow=True, wrinkles=True),
    'xiaoman': dict(leg=44, torso=46, head=21, sh=14, hip=12, arm=40, hump=0, belly=0, garment='tee', hem=None,
                    top=(0.06, (0.62, 0.85, 0.95), 0.8), bottom=(0.35, (0.55, 0.50, 0.45), 0.6), hair='boy', skin=(0.70, 0.82, 0.96), shoe=0.75, extras=('headphones',)),
    'qian':    dict(leg=62, torso=80, head=19, sh=21, hip=22, arm=62, hump=0, belly=16, garment='robe', hem=8,
                    top=(0.10, (0.45, 0.70, 0.82), 0.8), bottom=(0.6, None, 0), hair='cap', skin=(0.70, 0.80, 0.95), shoe=0.9, extras=('moustache',)),
    'ferryman': dict(leg=60, torso=72, head=17, sh=18, hip=15, arm=60, hump=4, belly=0, garment='short_jacket', hem=None,
                    top=(0.22, None, 0), bottom=(0.45, None, 0), hair='strawhat', skin=(0.62, 0.74, 0.90), shoe=0.8, rolled=True),
    'farmer':  dict(leg=60, torso=70, head=17, sh=19, hip=15, arm=60, hump=2, belly=0, garment='short_jacket', hem=None,
                    top=(0.12, (0.70, 0.78, 0.80), 0.6), bottom=(0.30, None, 0), hair='towel', skin=(0.58, 0.70, 0.88), shoe=0.0, rolled=True),
    'poet':    dict(leg=66, torso=76, head=17, sh=15, hip=13, arm=62, hump=0, belly=0, garment='robe', hem=10,
                    top=(0.05, (0.85, 0.85, 0.82), 0.5), bottom=(0.6, None, 0), hair='scholar', skin=SKIN, shoe=0.9, extras=('glasses',)),
    'bride':   dict(leg=60, torso=66, head=17, sh=14, hip=14, arm=56, hump=0, belly=0, garment='qipao', hem=12,
                    top=(0.08, (0.35, 0.40, 0.88), 0.85), bottom=(0.0, None, 0), hair='bride', skin=SKIN, shoe=0.9),
    'mother':  dict(leg=58, torso=68, head=18, sh=16, hip=16, arm=56, hump=2, belly=4, garment='long_jacket', hem=48,
                    top=(0.10, (0.70, 0.72, 0.62), 0.6), bottom=(0.5, None, 0), hair='bun_low', skin=SKIN, shoe=0.9),
    'twin':    dict(leg=40, torso=42, head=19, sh=12, hip=11, arm=36, hump=0, belly=0, garment='tee', hem=None,
                    top=(0.06, (0.62, 0.72, 0.95), 0.7), bottom=(0.3, None, 0), hair='pigtails', skin=(0.70, 0.82, 0.96), shoe=0.8),
    'porter':  dict(leg=62, torso=74, head=17, sh=21, hip=16, arm=64, hump=3, belly=0, garment='short_jacket', hem=None,
                    top=(0.30, None, 0), bottom=(0.5, None, 0), hair='cap_round', skin=(0.60, 0.72, 0.88), shoe=0.85),
}

def figure(L, fx, fy, s, who, t=0.0, facing=1, pose=None, seed=11, spec=None):
    """pose keys: walk (phase or None), arm_f/arm_b (shoulder, elbow) degrees, look (head tilt deg), talk (0/1),
    eyes ('open','closed','happy','wide'), lean (deg), crouch (0..1), mouth ('flat','smile','open','frown')"""
    S = dict(SPECS[who]); S.update(spec or {})
    p = dict(walk=None, arm_f=(10, 10), arm_b=(-8, 8), look=0, talk=0, eyes='open', lean=0, crouch=0, mouth='flat', bob=True)
    p.update(pose or {})
    F = facing
    def W(pts):
        q = np.asarray(pts, np.float32).reshape(-1, 2).copy(); q[:, 0] *= F
        return q * s + [fx, fy]
    br = math.sin(t * 2.0 + seed) * 0.8 if p['bob'] else 0
    # ---- skeleton
    walk = p['walk']; leg = S['leg']; cr = p['crouch']
    if walk is not None:
        ph = walk * 2 * math.pi
        hipy = -leg * (1 - 0.15 * cr) + abs(math.sin(ph)) * -2.0
        thigh = [22 * math.sin(ph), -22 * math.sin(ph)]
        knee = [max(0, 30 * math.sin(ph + 1.2)) + 4, max(0, 30 * math.sin(ph + 1.2 + math.pi)) + 4]
    else:
        thigh = [4 + 62 * cr, -3 + 55 * cr]; knee = [2 + 115 * cr, 2 + 105 * cr]
        hipy = -max(0.52 * math.cos(math.radians(thigh[i])) + 0.5 * math.cos(math.radians(thigh[i] - knee[i])) for i in (0, 1)) * leg
    hip = (0, hipy)
    lean = p['lean'] + S['hump'] * 0.3
    neck = polar(hip, 180 - lean, S['torso']); neck = (neck[0], neck[1] + br)
    head_c = polar(neck, 180 - lean - p['look'] * 0.3, S['head'] * 0.9)
    shf = (neck[0] + 3, neck[1] + 8); shb = (neck[0] - 5, neck[1] + 9)
    def leg_pts(i, sx):
        h = (hip[0] + sx, hip[1]); k = polar(h, thigh[i], leg * 0.52); a = polar(k, thigh[i] - knee[i], leg * 0.5)
        # keep the planted foot on the ground
        return h, k, (a[0], min(a[1], 0))
    def arm_pts(sh, ang):
        e = polar(sh, ang[0], S['arm'] * 0.5); h = polar(e, ang[0] + ang[1], S['arm'] * 0.48); return sh, e, h
    legs = [leg_pts(0, 3), leg_pts(1, -3)]
    arms = {'b': arm_pts(shb, p['arm_b']), 'f': arm_pts(shf, p['arm_f'])}
    td, tcol, tal = S['top']; bd, bcol, bal = S['bottom']
    # ---- back arm
    def draw_arm(k, sleeve_w):
        a, e, h = arms[k]
        pl = limb(a, e, h, 14)
        poly, lft, rgt = tube(pl, np.linspace(sleeve_w, sleeve_w * 0.8, len(pl)))
        fill(L, W(poly), td * 1.05 if k == 'b' else td, tcol, tal, s=s, seed=seed + (1 if k == 'b' else 2), gran=0.2, edge=0.5)
        line(L, W(lft), 1.4, s, 0.85, 0.3, seed + 3); line(L, W(rgt), 1.4, s, 0.85, 0.3, seed + 4)
        hm = W([(h[0] + 4.5 * math.cos(q), h[1] + 2 + 4 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 18)])
        fill(L, hm, 0.03, S['skin'], 0.6, s=s, seed=seed + 5); line(L, hm[3:16], 1.0, s, 0.8, 0, seed + 6)
        return h
    sw = 6.5 if S['garment'] in ('long_jacket', 'robe', 'short_jacket') else 4.5
    hand_b = draw_arm('b', sw)
    # ---- legs and feet
    gar = S['garment']
    for i, (h, k, a) in enumerate(legs):
        if gar in ('robe', 'qipao'):
            continue
        pl = limb(h, k, a, 12)
        lw = 7.5 if gar != 'tee' else 5.5
        if gar == 'tee':   # shorts then bare/socked shin
            poly, lft, rgt = tube(pl[:7], np.full(7, lw + 1.5))
            fill(L, W(poly), bd, bcol, bal, s=s, seed=seed + 20 + i, gran=0.2)
            line(L, W(lft), 1.2, s, 0.8, 0.3, seed + 22); line(L, W(rgt), 1.2, s, 0.8, 0.3, seed + 23)
            poly, lft, rgt = tube(pl[6:], np.full(len(pl) - 6, 3.6))
            fill(L, W(poly), 0.02, S['skin'], 0.5, s=s, seed=seed + 24 + i)
            line(L, W(lft), 1.0, s, 0.75, 0.2, seed + 25); line(L, W(rgt), 1.0, s, 0.75, 0.2, seed + 26)
        else:
            poly, lft, rgt = tube(pl, np.linspace(lw, lw * (0.8 if not S.get('rolled') else 0.6), len(pl)))
            fill(L, W(poly), bd, bcol, bal, s=s, seed=seed + 20 + i, gran=0.15)
            line(L, W(lft), 1.3, s, 0.8, 0.3, seed + 22); line(L, W(rgt), 1.3, s, 0.8, 0.3, seed + 23)
        fx0, fy0 = a
        if S['shoe'] > 0:
            sh = path((fx0 - 7, fy0 - 1), ((fx0 - 7, fy0 - 8), (fx0 + 8, fy0 - 9), (fx0 + 11, fy0 - 4)), ((fx0 + 13, fy0), (fx0 + 6, fy0 + 1), (fx0 - 2, fy0 + 1)), ((fx0 - 7, fy0 + 1), (fx0 - 8, fy0), (fx0 - 7, fy0 - 1)))
            fill(L, W(sh), S['shoe'], s=s, seed=seed + 30 + i)
        else:
            line(L, W([(fx0 - 4, fy0), (fx0 + 9, fy0)]), 3.0, s, 0.7, 0, seed + 32 + i)
    # ---- torso garment
    hx, hy = hip; nx, ny = neck; HW = S['hip']; SW = S['sh']; bel = S['belly']; hump = S['hump']
    if gar in ('long_jacket', 'robe', 'qipao'):
        hem_y = -S['hem'] if gar == 'long_jacket' else -S['hem']
        sway = (math.sin(walk * 2 * math.pi) * 4 if walk is not None else 0)
        flare = 8 if gar == 'long_jacket' else (10 if gar == 'robe' else 4)
        body = path((nx - SW * 0.4, ny + 2),
                    ((nx + SW * 0.9 + bel * 0.2, ny + 10), (hx + HW + bel * 1.2, (ny + hy) / 2 + 6), (hx + HW + flare + sway, hem_y)),
                    ((hx + HW * 0.4, hem_y + 4), (hx - HW * 0.4, hem_y + 4), (hx - HW - flare + sway, hem_y)),
                    ((hx - HW - 2, (ny + hy) / 2), (nx - SW - hump, ny + 18), (nx - SW * 0.4, ny + 2)))
        fill(L, W(body), td, tcol, tal, s=s, seed=seed + 40, gran=0.2, edge=0.5)
        line(L, W(body[:19]), 2.4, s, 0.9, 0.3, seed + 41)
        line(L, W(body[36:]), np.array([3.2, 3.0, 2.2]), s, 0.92, 0.35, seed + 42)
        line(L, W(body[18:37]), 1.6, s, 0.8, 0.4, seed + 43)
        if gar in ('robe', 'qipao'):   # feet peeking out under the hem, stepping
            for i, (h, k, a) in enumerate(legs):
                fx0 = a[0] * 0.8; fy0 = 0
                sh = path((fx0 - 7, fy0 - 1), ((fx0 - 7, fy0 - 7), (fx0 + 8, fy0 - 8), (fx0 + 11, fy0 - 3)), ((fx0 + 12, fy0), (fx0 + 6, fy0 + 1), (fx0 - 2, fy0 + 1)), ((fx0 - 7, fy0 + 1), (fx0 - 8, fy0), (fx0 - 7, fy0 - 1)))
                fill(L, W(sh), S['shoe'], s=s, seed=seed + 44 + i)
            if gar == 'robe':
                line(L, W([(hx + HW * 0.6 + bel * 0.5, (ny + hy) / 2 + 12), (hx + HW * 0.5, hem_y + 2)]), 1.0, s, 0.4, 0.3, seed + 45)
                # sash
                line(L, W([(hx - HW - 1, hy - 14), (hx + HW + bel * 1.1, hy - 16)]), 3.0, s, 0.8, 0.2, seed + 46, taper=False)
        else:   # side-fastened front with two knot buttons
            line(L, W(path((nx + 2, ny + 4), ((nx + 6, ny + 12), (nx + 12, ny + 20), (nx + 10, ny + 30)))), 1.3, s, 0.75, 0.2, seed + 47)
            for by in (ny + 14, ny + 26):
                over(L.D, ellipse_mask(L.D.shape, L.P(W([(nx + 9, by)]))[0], (1.5 * s, 1.5 * s)) * 0.9)
    else:   # tee or short jacket ending at the hip
        hem_y = hy + (4 if gar == 'tee' else 8)
        body = path((nx - SW * 0.4, ny + 2),
                    ((nx + SW, ny + 6), (hx + HW + 2, (ny + hy) / 2), (hx + HW + 3, hem_y)),
                    ((hx + HW * 0.4, hem_y + 2), (hx - HW * 0.4, hem_y + 2), (hx - HW - 3, hem_y)),
                    ((hx - HW - 2, (ny + hy) / 2), (nx - SW - hump, ny + 10), (nx - SW * 0.4, ny + 2)))
        fill(L, W(body), td, tcol, tal, s=s, seed=seed + 40, gran=0.2, edge=0.5)
        line(L, W(body[:19]), 2.0, s, 0.9, 0.3, seed + 41)
        line(L, W(body[36:]), 2.4, s, 0.9, 0.35, seed + 42)
        line(L, W(body[18:37]), 1.4, s, 0.8, 0.4, seed + 43)
        if gar == 'tee':
            line(L, W(path((nx - 4, ny + 3), ((nx - 1, ny + 7), (nx + 4, ny + 7), (nx + 6, ny + 3)))), 1.1, s, 0.7, 0, seed + 48)
        else:
            line(L, W([(nx + 4, ny + 4), (hx + 4, hem_y)]), 1.2, s, 0.7, 0.3, seed + 48)
    if 'backpack' in S.get('extras', ()) or (pose or {}).get('backpack'):
        bp = W(path((nx - SW - 2, ny + 6), ((nx - SW - 22, ny + 6), (nx - SW - 24, hy - 4), (nx - SW - 14, hy + 2)), ((nx - SW - 6, hy + 4), (nx - SW, hy - 2), (nx - SW + 2, ny + 6))))
        fill(L, bp, 0.18, (0.55, 0.62, 0.85), 0.7, s=s, seed=seed + 49)
        line(L, bp, 1.6, s, 0.9, 0.3, seed + 50, taper=False)
    # ---- head
    hcx, hcy = head_c; R = S['head']
    lk = math.radians(p['look'])
    head = W([(hcx + R * math.cos(q), hcy + R * 1.04 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 40)])
    fill(L, head, 0.03, S['skin'], 0.55, s=s, seed=seed + 60, edge=0.2)
    hair = S['hair']
    def hairfill(pts, d=0.55, g=0.4):
        fill(L, W(pts), d, s=s, seed=seed + 61, gran=g, edge=0.3)
    if hair in ('bun', 'bun_low'):
        hairfill(path((hcx + R * 0.95, hcy - R * 0.2), ((hcx + R * 0.9, hcy - R * 1.0), (hcx - R * 0.2, hcy - R * 1.15), (hcx - R * 0.75, hcy - R * 0.8)),
                      ((hcx - R * 1.0, hcy - R * 0.4), (hcx - R * 0.9, hcy + R * 0.4), (hcx - R * 0.6, hcy + R * 0.55)),
                      ((hcx - R * 0.3, hcy + R * 0.1), (hcx + R * 0.3, hcy - R * 0.55), (hcx + R * 0.95, hcy - R * 0.2))), 0.30 if hair == 'bun' else 0.6)
        bx, by = (hcx - R * 0.95, hcy - R * 0.5) if hair == 'bun' else (hcx - R * 1.0, hcy + R * 0.1)
        hairfill([(bx + 8 * math.cos(q), by + 7.5 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 24)], 0.55 if hair == 'bun' else 0.7)
    elif hair == 'boy':
        hairfill(path((hcx + R * 0.95, hcy - R * 0.25), ((hcx + R * 0.9, hcy - R * 1.2), (hcx - R * 0.9, hcy - R * 1.35), (hcx - R * 1.05, hcy + R * 0.1)),
                      ((hcx - R * 0.9, hcy + R * 0.5), (hcx - R * 0.5, hcy + R * 0.1), (hcx - R * 0.2, hcy - R * 0.25)),
                      ((hcx + R * 0.3, hcy - R * 0.5), (hcx + R * 0.7, hcy - R * 0.3), (hcx + R * 0.95, hcy - R * 0.25))), 0.82, 0.3)
        for k in range(4):   # spiky tufts
            ax = hcx - R * 0.6 + k * R * 0.4
            line(L, W([(ax, hcy - R * 0.95), (ax + 3 + k, hcy - R * 1.32 - (k % 2) * 3)]), 2.2, s, 0.85, 0.2, seed + 62 + k)
    elif hair == 'pigtails':
        hairfill(path((hcx + R * 0.9, hcy - R * 0.2), ((hcx + R * 0.8, hcy - R * 1.25), (hcx - R * 0.9, hcy - R * 1.3), (hcx - R * 1.0, hcy + R * 0.2)),
                      ((hcx - R * 0.6, hcy - R * 0.2), (hcx + R * 0.3, hcy - R * 0.55), (hcx + R * 0.9, hcy - R * 0.2))), 0.85, 0.3)
        for sx in (-1.15, 0.95):
            hairfill([(hcx + R * sx + 5 * math.cos(q), hcy - R * 0.4 + 9 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 18)], 0.85)
    elif hair in ('cap', 'cap_round', 'scholar'):
        hairfill(path((hcx - R * 1.0, hcy - R * 0.1), ((hcx - R * 1.05, hcy - R * 0.9), (hcx + R * 1.0, hcy - R * 0.9), (hcx + R * 1.0, hcy - R * 0.2)),
                      ((hcx + R * 0.6, hcy - R * 0.45), (hcx - R * 0.6, hcy - R * 0.45), (hcx - R * 1.0, hcy - R * 0.1))), 0.6, 0.3)
        cap = path((hcx - R * 0.95, hcy - R * 0.55), ((hcx - R * 0.95, hcy - R * 1.45), (hcx + R * 0.95, hcy - R * 1.45), (hcx + R * 0.95, hcy - R * 0.55)),
                   ((hcx + R * 0.4, hcy - R * 0.7), (hcx - R * 0.4, hcy - R * 0.7), (hcx - R * 0.95, hcy - R * 0.55)))
        fill(L, W(cap), 0.85 if hair != 'scholar' else 0.5, s=s, seed=seed + 66, gran=0.3)
        if hair == 'cap':
            over(L.D, ellipse_mask(L.D.shape, L.P(W([(hcx, hcy - R * 1.45)]))[0], (3 * s, 3 * s)) * 0.95)
            L.tints.append((ellipse_mask(L.D.shape, L.P(W([(hcx + R * 0.1, hcy - R * 0.85)]))[0], (4 * s, 3 * s)) * 0.8, (0.30, 0.45, 0.85)))
    elif hair == 'strawhat':
        hat = path((hcx - R * 2.0, hcy - R * 0.5), ((hcx - R * 0.6, hcy - R * 1.9), (hcx + R * 0.6, hcy - R * 1.9), (hcx + R * 2.0, hcy - R * 0.5)),
                   ((hcx + R * 0.8, hcy - R * 0.75), (hcx - R * 0.8, hcy - R * 0.75), (hcx - R * 2.0, hcy - R * 0.5)))
        fill(L, W(hat), 0.15, (0.60, 0.80, 0.90), 0.7, s=s, seed=seed + 67, gran=0.6, edge=0.6)
        line(L, W(hat[:19]), 1.8, s, 0.9, 0.4, seed + 68)
        line(L, W(hat[18:]), 1.4, s, 0.8, 0.4, seed + 69)
    elif hair == 'towel':
        tw = path((hcx - R * 1.05, hcy - R * 0.2), ((hcx - R * 1.1, hcy - R * 1.3), (hcx + R * 1.1, hcy - R * 1.3), (hcx + R * 1.05, hcy - R * 0.3)),
                  ((hcx + R * 0.6, hcy - R * 0.6), (hcx - R * 0.6, hcy - R * 0.6), (hcx - R * 1.05, hcy - R * 0.2)))
        fill(L, W(tw), 0.05, (0.85, 0.85, 0.80), 0.4, s=s, seed=seed + 67)
        line(L, W(tw), 1.4, s, 0.8, 0.3, seed + 68, taper=False)
        line(L, W([(hcx - R * 1.0, hcy - R * 0.3), (hcx - R * 1.4, hcy + R * 0.2)]), 3, s, 0.6, 0.2, seed + 69)
    elif hair == 'bride':
        hairfill(path((hcx - R * 1.0, hcy + R * 0.2), ((hcx - R * 1.05, hcy - R * 1.2), (hcx + R * 1.0, hcy - R * 1.25), (hcx + R * 1.0, hcy - R * 0.1)),
                      ((hcx + R * 0.5, hcy - R * 0.5), (hcx - R * 0.5, hcy - R * 0.5), (hcx - R * 1.0, hcy + R * 0.2))), 0.88, 0.3)
        hairfill([(hcx - R * 0.9 + 8 * math.cos(q), hcy - R * 0.8 + 8 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 18)], 0.9)
        L.tints.append((ellipse_mask(L.D.shape, L.P(W([(hcx - R * 0.5, hcy - R * 1.0)]))[0], (5 * s, 4 * s)) * 0.9, (0.30, 0.35, 0.90)))
    # head outline, broken where the hair is
    line(L, W([(hcx + R * math.cos(q), hcy + R * 1.04 * math.sin(q)) for q in np.linspace(-0.25, math.pi * 0.95, 24)]), 1.6, s, 0.88, 0.2, seed + 70)
    # face, on the facing side (3/4 view)
    ex = hcx + R * 0.42; ey = hcy - R * 0.02
    eyes = p['eyes']
    if t % (4.0 + seed % 3) < 0.12 and eyes == 'open': eyes = 'closed'
    for dx in (0, -R * 0.42):
        cx_, cy_ = ex + dx, ey
        if eyes == 'open':
            over(L.D, ellipse_mask(L.D.shape, L.P(W([(cx_, cy_)]))[0], (1.6 * s, 2.0 * s)) * 0.95)
        elif eyes == 'wide':
            over(L.D, ellipse_mask(L.D.shape, L.P(W([(cx_, cy_)]))[0], (2.2 * s, 2.8 * s)) * 0.95)
            L.knock(ellipse_mask(L.D.shape, L.P(W([(cx_ + 0.6, cy_ - 0.9)]))[0], (0.7 * s, 0.7 * s)), 0.9)
        elif eyes == 'happy':
            line(L, W(path((cx_ - 2.5, cy_ + 0.5), ((cx_ - 1.5, cy_ - 2.2), (cx_ + 1.5, cy_ - 2.2), (cx_ + 2.5, cy_ + 0.5)))), 1.2, s, 0.9, 0, seed + 71)
        elif eyes == 'squint':
            line(L, W(path((cx_ - 2.5, cy_ - 0.5), ((cx_ - 1, cy_ - 1.8), (cx_ + 1, cy_ - 1.8), (cx_ + 2.5, cy_ - 0.5)))), 1.4, s, 0.95, 0, seed + 71)
            over(L.D, ellipse_mask(L.D.shape, L.P(W([(cx_, cy_ + 0.3)]))[0], (1.2 * s, 1.2 * s)) * 0.9)
        else:
            line(L, W([(cx_ - 2.2, cy_), (cx_ + 2.2, cy_)]), 1.1, s, 0.9, 0, seed + 71, taper=False)
    if S.get('brow'):
        line(L, W([(ex - R * 0.62, ey - R * 0.38), (ex - R * 0.32, ey - R * 0.44), (ex + R * 0.1, ey - R * 0.36)]), 1.2, s, 0.85, 0.2, seed + 72)
    if 'glasses' in S.get('extras', ()):
        for dx in (0, -R * 0.42):
            line(L, W([(ex + dx + 4 * math.cos(q), ey + 3.5 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 16)]), 0.9, s, 0.85, 0, seed + 73, taper=False)
    # nose: a little hook on the facing side
    line(L, W(path((hcx + R * 0.86, hcy + R * 0.05), ((hcx + R * 1.06, hcy + R * 0.25), (hcx + R * 1.0, hcy + R * 0.33), (hcx + R * 0.82, hcy + R * 0.32)))), 1.0, s, 0.75, 0, seed + 74)
    # mouth (talking flips open/closed)
    m = p['mouth']
    if p['talk'] and (int(t * 9 + seed) % 3) != 0: m = 'open'
    mx, my = hcx + R * 0.48, hcy + R * 0.55
    if m == 'open':
        mm = W([(mx + 2.4 * math.cos(q), my + 2.2 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 14)])
        fill(L, mm, 0.75, s=s, seed=seed + 75)
    elif m == 'smile':
        line(L, W(path((mx - 4, my - 1), ((mx - 2, my + 2.5), (mx + 2, my + 2.5), (mx + 4, my - 1)))), 1.1, s, 0.85, 0, seed + 75)
    elif m == 'frown':
        line(L, W(path((mx - 4, my + 1.5), ((mx - 2, my - 1), (mx + 2, my - 1), (mx + 4, my + 1.5)))), 1.1, s, 0.85, 0, seed + 75)
    else:
        line(L, W([(mx - 3, my), (mx + 3, my + 0.3)]), 1.0, s, 0.8, 0, seed + 75)
    if 'moustache' in S.get('extras', ()):
        line(L, W(path((mx - 6, my - 3), ((mx - 2, my - 6), (mx + 2, my - 5), (mx + 7, my - 2)))), 1.8, s, 0.9, 0, seed + 76)
        line(L, W([(mx + 7, my - 2), (mx + 11, my + 2)]), 1.2, s, 0.85, 0, seed + 77)
    if S.get('wrinkles'):
        line(L, W([(hcx + R * 0.05, hcy + R * 0.0), (hcx + R * 0.1, hcy + R * 0.25)]), 0.8, s, 0.35, 0, seed + 78)
    L.tints.append((ellipse_mask(L.D.shape, L.P(W([(hcx + R * 0.35, hcy + R * 0.32)]))[0], (4 * s, 2.5 * s)) * 0.28, (0.55, 0.62, 0.92)))
    # ear
    line(L, W(path((hcx - R * 0.05, hcy - R * 0.1), ((hcx - R * 0.3, hcy - R * 0.25), (hcx - R * 0.35, hcy + R * 0.25), (hcx - R * 0.05, hcy + R * 0.2)))), 1.0, s, 0.7, 0, seed + 79)
    if 'headphones' in S.get('extras', ()):
        line(L, W(path((nx - 10, ny + 4), ((nx - 6, ny + 12), (nx + 8, ny + 12), (nx + 12, ny + 4)))), 2.6, s, 0.8, 0, seed + 80)
        for ex_ in (nx - 10, nx + 12):
            fill(L, W([(ex_ + 4 * math.cos(q), ny + 4 + 4 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 14)]), 0.8, s=s, seed=seed + 81)
    # ---- front arm on top
    hand_f = draw_arm('f', sw)
    return dict(hand_f=W([hand_f])[0], hand_b=W([hand_b])[0], head=W([head_c])[0], neck=W([neck])[0], R=R * s)

def baozi(L, x, y, t, s=1.0, mood='happy', seed=91):
    """Xiaoman's dumpling-sized cloud"""
    bob = math.sin(t * 2.4) * 3 * s
    pts = []
    for k, (dx, dy, r) in enumerate([(-12, 2, 9), (-4, -6, 11), (7, -5, 10), (13, 3, 8), (0, 5, 10)]):
        pts.append((x + dx * s, y + dy * s + bob, r * s))
    m = np.zeros(L.D.shape, np.float32)
    for (cx, cy, r) in pts: cv2.circle(m, (int((cx - L.x0) * 4), int((cy - L.y0) * 4)), int(r * 4), 1.0, -1, cv2.LINE_AA, 2)
    m = cv2.GaussianBlur(m, (0, 0), 0.8)
    L.knock(m)
    over(L.D, wash(m, 0.07, bleed=0.8 * s, seed=seed, edge=0.9, rough=0.15))
    L.tints.append((m * 0.25, (0.98, 0.92, 0.85)))
    edge = np.clip(m - cv2.erode(m, np.ones((3, 3), np.uint8), iterations=max(1, int(s))), 0, 1)
    over(L.D, edge * 0.7)
    ex, ey = x - 2 * s, y + bob
    if mood == 'happy':
        for dx in (-4, 4): line(L, [(ex + (dx - 2) * s, ey + 0.5 * s), (ex + dx * s, ey - 1.8 * s), (ex + (dx + 2) * s, ey + 0.5 * s)], 1.0, s, 0.9, 0, seed + 2)
    else:
        for dx in (-4, 4): over(L.D, ellipse_mask(L.D.shape, L.P([(ex + dx * s, ey)])[0], (1.3 * s, 1.6 * s)) * 0.95)
    L.tints.append((ellipse_mask(L.D.shape, L.P([(ex - 7 * s, ey + 3 * s)])[0], (2.5 * s, 1.5 * s)) * 0.4, (0.55, 0.62, 0.95)))
    L.tints.append((ellipse_mask(L.D.shape, L.P([(ex + 7 * s, ey + 3 * s)])[0], (2.5 * s, 1.5 * s)) * 0.4, (0.55, 0.62, 0.95)))

WATER_BLUE = (0.92, 0.80, 0.55)

def dragon_spine(x, y, t, length=600, amp=40, waves=1.5, ang=0.0, n=60, speed=1.2, coil=0.0):
    """spine from head (index 0) to tail; a travelling sine wave, optional coil toward the tail"""
    u = np.linspace(0, 1, n)
    along = u * length
    off = np.sin(u * waves * 2 * math.pi - t * speed * 2 * math.pi) * amp * (0.3 + 0.7 * u)
    ca, sa = math.cos(ang), math.sin(ang)
    pts = np.stack([x - along * ca - off * sa, y - along * sa + off * ca], 1)
    if coil > 0:   # curl the tail around
        for i in range(n):
            k = max(0, (u[i] - 0.55) / 0.45) * coil
            if k > 0:
                th = k * math.pi * 1.6
                c = pts[int(n * 0.55)]
                v = pts[i] - c; r = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
                pts[i] = c + r @ v * (1 - 0.35 * k)
    return pts

def dragon(L, spine, t, s=1.0, strength=1.0, seed=301, eye='scared', jaw=0.0):
    """a dragon made of rain: see-through water body, ink contour, flowing mane, antlers, whiskers, little clawed legs"""
    spine = np.asarray(spine, np.float32); n = len(spine)
    u = np.linspace(0, 1, n)
    w = (22 * (1 - u) ** 0.7 * (0.75 + 0.25 * strength) * (0.75 + 0.35 * np.sin(np.clip(u * 3.2, 0, math.pi))) + 2.5) * s
    w[:6] *= np.linspace(0.7, 1, 6)
    poly, left, right = tube(spine, w)
    m = poly_mask(L.D.shape, [L.P(poly)])
    L.knock(m, 0.45)
    over(L.D, wash(m, 0.05 + 0.05 * strength, bleed=1.0 * s, seed=seed, edge=1.2, rough=0.1, gran=0.2))
    L.tints.append((m * (0.22 + 0.25 * strength), WATER_BLUE))
    # highlight running along the body (water catching light)
    hl = spine + (left - spine) * 0.45
    L.knock(cv2.GaussianBlur(stroke_mask(L.D.shape, L.P(hl[2:int(n * 0.8)]), np.linspace(4, 1, int(n * 0.8) - 2) * s), (0, 0), 1.5), 0.8)
    line(L, left, np.full(n, 1.9), s, 0.85, 0.45, seed + 1)
    line(L, right, np.full(n, 1.5), s, 0.7, 0.5, seed + 2)
    for k in range(2):
        cur = spine + (right - spine) * (0.2 + 0.4 * k)
        seg = cur[int(n * (0.08 + 0.1 * k)): int(n * (0.55 + 0.15 * k))]
        if len(seg) > 3: line(L, seg, 0.8, s, 0.28, 0.6, seed + 3 + k)
    for i in range(5, n - 8, 3):
        a_, b_ = right[i], right[i + 2]; mid = (spine[i + 1] * 0.35 + right[i + 1] * 0.65)
        line(L, bezier(a_, mid, b_, n=6), 0.8, s, 0.32, 0, seed + 10 + i)
    # legs with three claws
    for k, uu in enumerate((0.22, 0.5)):
        i = int(uu * n); base = right[i]; d = right[i] - spine[i]; d /= (np.linalg.norm(d) + 1e-6)
        back = spine[i] - spine[max(0, i - 2)]; back /= (np.linalg.norm(back) + 1e-6)
        swing = math.sin(t * 3 + k * 2) * 0.4
        knee = base + (d * 14 + back * (6 + 6 * swing)) * s
        foot = knee + (d * 10 - back * 8) * s
        lp, ll, lr = tube(np.vstack([bezier(base, (base + knee) / 2, knee, n=6), bezier(knee, (knee + foot) / 2, foot, n=6)[1:]]), np.linspace(5, 3, 11) * s)
        fill(L, lp, 0.08, WATER_BLUE, 0.5, s=s, seed=seed + 20 + k)
        line(L, ll, 1.2, s, 0.8, 0.3, seed + 22 + k); line(L, lr, 1.2, s, 0.8, 0.3, seed + 24 + k)
        for c in (-0.6, 0, 0.6):
            cd = d * math.cos(c) + back * -math.sin(c)
            line(L, [foot, foot + cd * 6 * s - back * 2 * s], np.array([1.6, 0.6]), s, 0.9, 0, seed + 26 + k)
    # mane: flame-like locks sweeping back from the head along the spine
    for i in range(1, int(n * 0.5), 2):
        base = left[i]; d = left[i] - spine[i]; d /= (np.linalg.norm(d) + 1e-6)
        back = spine[min(n - 1, i + 4)] - spine[i]; back /= (np.linalg.norm(back) + 1e-6)
        L_ = (42 - i * 1.0) * s
        wob = math.sin(t * 2.6 + i * 0.5) * 0.3
        tip = base + (d * (0.9 + wob) + back * 0.7) * L_
        mid = base + (d * 0.95 + back * 0.15) * L_ * 0.5
        line(L, [base, mid, tip], np.array([3.0, 2.0, 0.5]), s, 0.85, 0.35, seed + 40 + i)
    # tail tuft
    tt_ = spine[-1]; td = spine[-1] - spine[-3]; td /= (np.linalg.norm(td) + 1e-6); tn = np.array([-td[1], td[0]])
    for k in (-1, 0, 1):
        line(L, [tt_, tt_ + (td * 14 + tn * k * 7 + tn * math.sin(t * 3 + k) * 3) * s], np.array([2, 0.5]), s, 0.7, 0.2, seed + 50 + k)
    # head (bigger, with brow and snout)
    hd = spine[0] - spine[3]; hd /= (np.linalg.norm(hd) + 1e-6); nr = np.array([-hd[1], hd[0]])
    if nr[1] > 0: nr = -nr      # keep the top of the head up
    hs = 2.0 * s
    hc = spine[0] + hd * 4 * hs
    P_ = lambda a, b: hc + hd * a * hs + nr * b * hs
    top = bezier(P_(-10, 13), P_(6, 17), P_(16, 8), n=10).tolist() + bezier(P_(16, 8), P_(26, 9), P_(32, 4), n=8).tolist()[1:]
    nose = bezier(P_(32, 4), P_(36, 1), P_(33, -2), n=6).tolist()[1:]
    jw = jaw * 8
    lower = bezier(P_(33, -2), P_(22, -4 - jw), P_(8, -9 - jw * 0.5), n=10).tolist()[1:] + bezier(P_(8, -9 - jw * 0.5), P_(-2, -12), P_(-10, -11), n=8).tolist()[1:]
    hp = top + nose + lower
    hm = poly_mask(L.D.shape, [L.P(hp)])
    hx_ = np.clip(hm - m, 0, 1)
    over(L.D, wash(hx_, 0.05 + 0.05 * strength, bleed=0.8 * s, seed=seed + 60, edge=0.3))
    L.tints.append((hx_ * (0.22 + 0.25 * strength), WATER_BLUE))
    line(L, top + nose, 2.0, s, 0.9, 0.25, seed + 61)
    line(L, lower, 1.7, s, 0.85, 0.3, seed + 62)
    line(L, [P_(16, 9.5), P_(10, 12), P_(2, 12)], 1.4, s, 0.8, 0, seed + 63)     # brow ridge
    if jaw > 0.2:
        line(L, [P_(31, 0), P_(20, -2 - jw * 0.5), P_(10, -5)], 1.2, s, 0.8, 0, seed + 64)
    # antlers
    for k, sgn in enumerate((0, 1)):
        b0 = P_(-2 - 6 * k, 12); b1 = P_(-20 - 6 * k, 30 - 6 * k); bm = P_(-10 - 6 * k, 24 - 2 * k)
        line(L, [b0, bm, b1], np.array([3.2, 2.4, 1.0]), s, 0.85, 0.3, seed + 65 + k)
        line(L, [bm, P_(-6 - 6 * k, 32 - 4 * k)], np.array([1.8, 0.6]), s, 0.8, 0, seed + 67 + k)
    # whiskers: long, slow S-curves trailing back
    for k, sgn in enumerate((1, -1)):
        w0 = P_(30, 0 + sgn * 2)
        pts = [w0 + (-hd * j * 8 + nr * (-6 - j * 1.5 + math.sin(t * 2.2 + j * 0.8 + k) * 4) * (1 if sgn > 0 else 1.3)) * hs for j in range(9)]
        line(L, pts, np.linspace(1.6, 0.3, 9), s, 0.75, 0.15, seed + 70 + k)
    # eye
    ec = P_(12, 4); er = (5.0 if eye == 'scared' else 4.0) * hs
    em = ellipse_mask(L.D.shape, L.P([ec])[0], (er, er * 0.95)); L.knock(em, 1.0)
    line(L, [(ec[0] + er * math.cos(q), ec[1] + er * 0.95 * math.sin(q)) for q in np.linspace(0, 2 * math.pi, 22)], 1.5, s, 0.9, 0, seed + 75, taper=False)
    pr = er * (0.5 if eye == 'scared' else 0.68)
    pc = ec + hd * er * 0.15
    over(L.D, ellipse_mask(L.D.shape, L.P([pc])[0], (pr, pr)) * 0.95)
    L.knock(ellipse_mask(L.D.shape, L.P([pc + nr * pr * 0.35 + hd * pr * 0.2])[0], (pr * 0.35, pr * 0.35)), 1.0)
    if eye == 'calm':
        line(L, [P_(7, 8.5), P_(12, 9.8), P_(17, 8.5)], 1.2, s, 0.85, 0, seed + 76)
    over(L.D, ellipse_mask(L.D.shape, L.P([P_(33, 2)])[0], (1.5 * s, 1.1 * s)) * 0.85)
    return hc, P_(34, 0)
