"""UCUP — expressions, poses, timeline engine, secondary motion (v0.1.0-draft)"""
import math
from ucup_rig import DEFAULT, SHOULDER_R, UPPER, FORE, HAND_STATES

# ------------------------------------------------------------------ IK
def _wrap(a):
    return (a + 180) % 360 - 180

def ik_arm(target, bend='down'):
    """2-bone IK for the screen-right arm. target = sleeve-end point (torso coords).
    returns (abd, flex) in rig convention."""
    sx, sy = SHOULDER_R
    dx, dy = target[0] - sx, target[1] - sy
    D = math.hypot(dx, dy)
    D = max(abs(UPPER - FORE) + 2, min(UPPER + FORE - 0.5, D))
    base = math.atan2(-dx, dy)
    a = math.acos(max(-1, min(1, (UPPER**2 + D**2 - FORE**2) / (2 * UPPER * D))))
    best = None
    for th1 in (base + a, base - a):
        ex, ey = sx - UPPER * math.sin(th1), sy + UPPER * math.cos(th1)
        score = {'down': ey, 'up': -ey, 'out': ex, 'in': -ex}[bend]
        if best is None or score > best[0]:
            best = (score, th1, ex, ey)
    _, th1, ex, ey = best
    # direction elbow->target using clamped distance
    tx, ty = sx + D * (dx / math.hypot(dx, dy)), sy + D * (dy / math.hypot(dx, dy))
    th2 = math.atan2(-(tx - ex), ty - ey)
    return -math.degrees(th1), _wrap(math.degrees(th2 - th1))

def arm(side, target, hand='relaxed', wrist=0, bend='down'):
    x, y = target
    if side == 'L':
        x = 600 - x
    abd, flex = ik_arm((x, y), bend)
    return {f'{side}_abd': abd, f'{side}_flex': flex, f'{side}_wrist': wrist, f'{side}_hand': hand}

# ------------------------------------------------------------------ expressions
# NEW = created beyond the reference sheet; REF = derived from sheet heads
EXPR = {
 'neutral':    dict(tag='REF', p={}),
 'happy':      dict(tag='REF', p=dict(m_open=9, m_w=30, m_smile=1.3, bR_y=-2, bL_y=-2)),
 'surprised':  dict(tag='REF', p=dict(eR_o=1.22, eL_o=1.22, bR_y=-9, bL_y=-9, bR_c=4, bL_c=4, m_w=13, m_open=15, m_smile=0)),
 'wink':       dict(tag='REF', p=dict(eR_o=0, eR_arc=1, m_smile=1.4, m_skew=1.2, m_x=3, bR_y=-1.5)),
 'sad':        dict(tag='REF', p=dict(bR_r=-9, bL_r=-9, bR_y=-1, bL_y=-1, m_smile=-1.3, m_w=22, eR_o=.92, eL_o=.92)),
 'tired':      dict(tag='REF', p=dict(eR_o=.3, eL_o=.3, bR_y=3, bL_y=3, bR_r=-4, bL_r=-4, m_smile=-.6, m_w=20)),
 'eyes_closed':dict(tag='REF', p=dict(eR_o=0, eL_o=0, eR_arc=-1, eL_arc=-1, bR_r=-5, bL_r=-5, m_smile=-.8, m_w=20)),
 'masked':     dict(tag='REF', p=dict(mask=1, eR_o=0, eL_o=0, bR_r=-3, bL_r=-3)),
 'curious':    dict(tag='NEW', p=dict(bR_y=-9, bL_y=1, bL_r=5, bR_c=4, gx=.9, gy=-.7, m_w=16, m_smile=.35, m_skew=.9, m_x=5)),
 'smirk':      dict(tag='NEW', p=dict(bR_y=-5, bL_y=1, eR_o=.85, eL_o=.85, m_smile=1.6, m_skew=1.7, m_w=25, m_x=3)),
 'excited':    dict(tag='NEW', p=dict(eR_o=1.2, eL_o=1.2, bR_y=-8, bL_y=-8, bR_c=3.5, bL_c=3.5, m_open=13, m_w=34, m_smile=1.7)),
 'laugh':      dict(tag='NEW', p=dict(eR_o=0, eL_o=0, eR_arc=1, eL_arc=1, bR_y=-4, bL_y=-4, m_open=16, m_w=38, m_smile=1.9, blush=.35)),
 'confused':   dict(tag='NEW', p=dict(bL_y=-7, bL_r=-6, bR_y=1, bR_r=6, m_w=17, m_smile=-.25, m_skew=-1.3, m_x=-3, gx=-.5, gy=-.4)),
 'focused':    dict(tag='NEW', p=dict(bR_r=7, bL_r=7, bR_y=2, bL_y=2, eR_o=.92, eL_o=.92, m_w=19, m_smile=.1)),
 'skeptical':  dict(tag='NEW', p=dict(eR_o=.5, eL_o=.82, bR_y=-7, bL_r=6, bL_y=2, m_w=18, m_smile=-.2, m_skew=1.6, m_x=3)),
 'embarrassed':dict(tag='NEW', p=dict(blush=1, sweat=.8, bR_r=-7, bL_r=-7, bR_y=-2, bL_y=-2, m_w=18, m_smile=.5, m_skew=-1.2, gx=-.8, gy=.6)),
 'worried':    dict(tag='NEW', p=dict(bR_r=-10, bL_r=-10, bR_y=-3, bL_y=-3, m_smile=-.9, m_w=18, sweat=.6, eR_o=1.1, eL_o=1.1)),
}
VISEMES = {  # mouth-only presets (non-linguistic mapping, for talk/lip-sync later)
 'M': dict(m_w=18, m_open=0, m_smile=.2), 'A': dict(m_w=22, m_open=12, m_smile=.3),
 'E': dict(m_w=32, m_open=6.5, m_smile=1.2), 'O': dict(m_w=12, m_open=12, m_smile=0),
 'U': dict(m_w=9, m_open=8, m_smile=0),
}
FACE_KEYS = ['bR_y','bR_r','bR_c','bL_y','bL_r','bL_c','eR_o','eL_o','eR_arc','eL_arc','gx','gy',
             'm_w','m_open','m_smile','m_skew','m_x','m_y','blush','sweat','mask']

def expr(name):
    return dict(EXPR[name]['p'])

def expr_full(name):
    p = {k: DEFAULT[k] for k in FACE_KEYS}
    p.update(EXPR[name]['p'])
    return p

# ------------------------------------------------------------------ static poses
def pose_library():
    P = {}
    P['rest'] = {}
    pk = arm('R', (350, 530), 'tuck', bend='out'); pk.update(arm('L', (350, 530), 'tuck', bend='out'))
    P['hands_in_pockets'] = dict(pk, torso=0, head=-2, **expr('smirk'))
    ex = arm('R', (432, 400), 'present', wrist=-30, bend='down')
    P['explain'] = dict(ex, L_abd=20, L_flex=22, torso=2, head=3, **expr('happy'))
    pt = arm('R', (530, 316), 'point', wrist=0, bend='down')
    P['point'] = dict(pt, torso=-2, head=-4, **expr('focused'), gx=1)
    tu = arm('R', (402, 298), 'thumbs', wrist=0, bend='down')
    P['thumbs_up'] = dict(tu, torso=1, head=3, **expr('happy'))
    wv = arm('R', (436, 196), 'wave', wrist=10, bend='out')
    P['wave'] = dict(wv, head=4, torso=-1, **expr('happy'))
    th = arm('R', (336, 284), 'fist', wrist=6, bend='down')
    P['think'] = dict(th, L_abd=26, L_flex=70, L_wrist=-10, L_hand='relaxed', head=-5, torso=1, **expr('curious'))
    sh = dict(R_abd=38, R_flex=48, R_wrist=-25, R_hand='present', L_abd=38, L_flex=48, L_wrist=-25, L_hand='present', shrug=10)
    P['shrug'] = dict(sh, head=7, torso=0, **expr('embarrassed'))
    su = dict(R_abd=34, R_flex=62, R_wrist=-18, R_hand='open', L_abd=34, L_flex=62, L_wrist=-18, L_hand='open')
    P['surprised_recoil'] = dict(su, torso=-5, head=-4, root_y=-3, **expr('surprised'))
    ch = arm('R', (452, 168), 'fist', bend='out'); ch.update(arm('L', (148, 168), 'fist', bend='out'))
    P['cheer'] = dict(ch, head=0, root_y=-14, plant=0, **expr('laugh'))
    P['cap_off_scratch'] = dict(arm('R', (352, 212), 'open', wrist=-30, bend='out'), cap_on=0, head=5, **expr('confused'))
    return P

# ------------------------------------------------------------------ easing
def _c(u): return max(0.0, min(1.0, u))
EASE = {
 'lin':  lambda u: u,
 'io':   lambda u: 4*u**3 if u < .5 else 1 - (-2*u + 2)**3 / 2,
 'out':  lambda u: 1 - (1 - u)**3,
 'in':   lambda u: u**3,
 'back': lambda u: 1 + 2.2*(u - 1)**3 + 1.2*(u - 1)**2,
 'spring': lambda u: 1 - math.exp(-6.5*u) * math.cos(13*u) if u < 1 else 1.0,
 'hold': lambda u: 0.0,
}

class Timeline:
    """keys: list of (t, ease, params). Numeric params interpolated per-track with the
    ease of the arriving key; string params switch `lead` seconds before the key."""
    def __init__(self, keys, lead=0.14):
        self.tracks = {}
        for t, ease, params in keys:
            for k, v in params.items():
                self.tracks.setdefault(k, []).append((t, ease, v))
        for k in self.tracks:
            self.tracks[k].sort(key=lambda x: x[0])
        self.lead = lead

    def value(self, k, t):
        tr = self.tracks.get(k)
        if not tr:
            return DEFAULT[k]
        if isinstance(tr[0][2], str):
            cur = tr[0][2]
            for (kt, _, v) in tr:
                if t >= kt - self.lead:
                    cur = v
            return cur
        if t <= tr[0][0]:
            return tr[0][2]
        for (t0, _, v0), (t1, e1, v1) in zip(tr, tr[1:]):
            if t0 <= t <= t1:
                u = (t - t0) / max(1e-6, t1 - t0)
                return v0 + (v1 - v0) * EASE[e1](u)
        return tr[-1][2]

    def pose(self, t):
        return {k: self.value(k, t) for k in self.tracks}

def lag_filter(series, dt, freq=6.0, zeta=0.45):
    """underdamped spring chasing the series -> follow-through / overshoot"""
    x, v, out = series[0], 0.0, []
    w = 2 * math.pi * freq
    for tgt in series:
        for _ in range(4):
            h = dt / 4
            a = w*w*(tgt - x) - 2*zeta*w*v
            v += a*h; x += v*h
        out.append(x)
    return out

def secondary(frames, dt):
    """adds cap lag, head lag behind torso, wrist drag. frames: list of full pose dicts"""
    n = len(frames)
    full = [dict(DEFAULT, **fr) for fr in frames]
    head_tot = [fr['head'] + fr['torso'] for fr in full]
    lh = lag_filter(head_tot, dt, 5.5, 0.32)
    ry = lag_filter([fr['root_y'] for fr in full], dt, 6.0, 0.35)
    lt = lag_filter([fr['torso'] for fr in full], dt, 4.5, 0.5)
    wr = {}
    for s in 'RL':
        ab = [-fr[f'{s}_abd'] + fr[f'{s}_flex'] for fr in full]
        wr[s] = [a - b for a, b in zip(lag_filter(ab, dt, 6.5, 0.3), ab)]
    for i, fr in enumerate(frames):
        fr['cap_rot'] = fr.get('cap_rot', 0) + 0.9 * (lh[i] - head_tot[i])
        fr['cap_dy'] = fr.get('cap_dy', 0) + 0.45 * (ry[i] - full[i]['root_y'])
        fr['head'] = full[i]['head'] + 0.35 * (lt[i] - full[i]['torso'])
        for s in 'RL':
            fr[f'{s}_wrist'] = full[i][f'{s}_wrist'] + 0.7 * wr[s][i]
    return frames

def blink_amount(t, times, dur=0.17):
    for b in times:
        u = (t - b) / dur
        if 0 <= u <= 1:
            return math.sin(math.pi * u) ** 0.8
    return 0.0

def finalize(pose, t, blinks=(), breath_amp=0.007, breath_period=3.4):
    """procedural layers: breathing, blink, feet-plant compensation for root_x"""
    p = dict(pose)
    p['breath'] = p.get('breath', 0) + breath_amp * math.sin(2 * math.pi * t / breath_period)
    b = blink_amount(t, blinks)
    if b > 0:
        for s in 'RL':
            o = p.get(f'e{s}_o', 1)
            if o > 0.5:
                p[f'e{s}_o'] = o * (1 - b)
                if b > .7:
                    p[f'e{s}_arc'] = -1
    rx = p.get('root_x', 0)
    if rx:
        tt = math.degrees(rx / 325.0)
        p['R_thigh'] = p.get('R_thigh', 1.5) - tt; p['L_thigh'] = p.get('L_thigh', 1.5) + tt
        p['R_knee'] = p.get('R_knee', 0) - tt; p['L_knee'] = p.get('L_knee', 0) + tt
    return p
