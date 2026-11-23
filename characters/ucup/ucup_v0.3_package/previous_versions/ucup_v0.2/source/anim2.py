import math
import ucup_rig2 as R2
import ucup_anim as A
from ucup_rig2 import DEFAULT, solve_legs, anchor, UPPER, FORE
from ucup_anim import EXPR, expr, expr_full, VISEMES, Timeline, EASE, lag_filter, blink_amount, finalize, _wrap

def ik2(target, anc, bend='down'):
    sx, sy = anc
    dx, dy = target[0] - sx, target[1] - sy
    D0 = math.hypot(dx, dy); D = max(abs(UPPER - FORE) + 2, min(UPPER + FORE - 0.5, D0))
    base = math.atan2(-dx, dy)
    a = math.acos(max(-1, min(1, (UPPER**2 + D**2 - FORE**2) / (2 * UPPER * D))))
    best = None
    for th1 in (base + a, base - a):
        ex, ey = sx - UPPER * math.sin(th1), sy + UPPER * math.cos(th1)
        sc = {'down': ey, 'up': -ey, 'out': ex, 'in': -ex}[bend]
        if best is None or sc > best[0]:
            best = (sc, th1, ex, ey)
    _, th1, ex, ey = best
    tx, ty = sx + D * dx / D0, sy + D * dy / D0
    th2 = math.atan2(-(tx - ex), ty - ey)
    return -math.degrees(th1), _wrap(math.degrees(th2 - th1))

def arm2(side, target, hand='relaxed', wrist=0, bend='down', ctx=None):
    """target in screen/torso-container coords (screen side). ctx = pose dict being built (twist etc.)"""
    ctx = dict(DEFAULT, **(ctx or {}))
    x, y = target
    if side == 'L': x = 600 - x
    abd = 9
    for _ in range(3):   # converge scapular rhythm
        c = dict(ctx); c[f'{side}_abd'] = abd
        a = anchor(c, side)
        abd, flex = ik2((x, y), a, bend)
    return {f'{side}_abd': abd, f'{side}_flex': flex, f'{side}_wrist': wrist, f'{side}_hand': hand}

def both(ctx, rt, lt, hand='relaxed', wrist=0, bend='down', wr_l=None, hand_l=None, bend_l=None):
    d = dict(ctx)
    d.update(arm2('R', rt, hand, wrist, bend, d)); d.update(arm2('L', lt, hand_l or hand, wrist if wr_l is None else wr_l, bend_l or bend, d))
    return d

def knee_screen(p, side):
    L, ry = solve_legs(dict(DEFAULT, **p)); k = L[side]['knee']
    return (k[0], k[1] + ry), ry

def diag_poses():
    D = {}
    D['01 hands on hips'] = both({}, (356, 488), (244, 488), 'fist', 0, 'out')
    c = dict(arm_top='R')
    D['02 arms crossed'] = both(c, (280, 424), (322, 452), 'fist', 0, 'down', 0, 'fist')
    D['03 one arm up'] = arm2('R', (428, 105), 'point', 0, 'out')
    D['04 both arms up'] = both({}, (436, 150), (164, 150), 'open', 0, 'out')
    D['05 hand on head'] = arm2('R', (366, 206), 'open', 0, 'out')
    D['06 reach forward'] = dict(R_abd=2, R_flex=0, R_fwd=.8, R_hand='open', R_wrist=-165, torso=-2, twist=.15)
    D['07 reach far side'] = dict(R_abd=94, R_flex=0, R_hand='open', torso=5, L_abd=16, L_flex=10)
    D['08 bend forward'] = dict(bend=.85, squat=.12, R_abd=6, R_flex=14, R_fwd=.35, L_abd=6, L_flex=14, L_fwd=.35, head=0)
    sq = dict(squat=.85, torso=0)
    kR, ry = knee_screen(sq, 'R'); kL, _ = knee_screen(sq, 'L')
    tgtR = (kR[0] - 6, kR[1] - ry - 24); tgtL = (kL[0] + 6, kL[1] - ry - 24)
    D['09 squat'] = both(sq, tgtR, tgtL, 'relaxed', 0, 'out')
    t = dict(twist=.8, torso=5, head=-4, hip=2)
    t.update(arm2('R', (240, 350), 'point', 0, 'down', t)); t['L_abd']=22; t['L_flex']=14; t['L_z']='back'
    D['10 twist + arm'] = t
    return D
