"""
UCUP gait driver (single source of truth for side AND front walking)
-------------------------------------------------------------------
Everything is computed in the SAGITTAL plane with forward-positive angles (deg):
  thigh θ1 (from vertical), shank θ2 (from vertical), knee flex k = θ1-θ2, foot pitch α (toe up +).
Side rig draws these angles directly.  Front rig is a projection of the SAME skeleton
along the walking axis: vertical positions are identical (hip_y, ankle_y), the sagittal
swing shows up as foreshortening  (thigh scale cos θ1, shank scale cos θ2, arm scale cos θ).
Legs: A = near leg in side view = screen-RIGHT leg in front view.  B = far / screen-LEFT.
Arm A is on the same side as leg A and swings opposite to it.
"""
import math
L1, L2 = 173.0, 152.0          # thigh, shank (hip -> ankle), same as front rig THIGH/SHIN
GROUND = 860.0                 # sole level
ANKLE_STAND = 827.0            # ankle height when standing (sole 33 px below)
HIP_STAND = 502.0
T = 1.0                        # seconds per full cycle (2 steps)
STANCE = 0.60                  # stance fraction (walk duty factor)
V = 280.0                      # ground speed px/s  (stride 280, step 140)
HEEL = (-30.0, 33.0)           # contact pivots in foot-local forward-positive coords (u fwd, v down)
BALL = (45.0, 33.0)
PH_FLAT0, PH_HEELOFF = 0.08, 0.45
ALPHA_STRIKE, ALPHA_OFF = 18.0, -32.0

def _R(a, u, v):
    a = math.radians(a)
    return (u * math.cos(a) + v * math.sin(a), -u * math.sin(a) + v * math.cos(a))

def _ss(u): return u * u * (3 - 2 * u)

def foot_pitch(ph):
    if ph < PH_FLAT0:
        return ALPHA_STRIKE * (1 - _ss(ph / PH_FLAT0))
    if ph < PH_HEELOFF:
        return 0.0
    if ph < STANCE:
        return ALPHA_OFF * _ss((ph - PH_HEELOFF) / (STANCE - PH_HEELOFF))
    u = (ph - STANCE) / (1 - STANCE)
    if u < 0.5:
        return ALPHA_OFF + (-5 - ALPHA_OFF) * _ss(u / 0.5)
    return -5 + (ALPHA_STRIKE + 5) * _ss((u - 0.5) / 0.5)

# stance: contact point moves back at V; heel contact first, ball contact for push-off
_P_H0 = 66.0   # heel contact point (forward of hip) at heel strike -> ankle ~ +84

def _stance_ankle(ph):
    t = ph * T
    if ph < PH_HEELOFF:
        P = _P_H0 - V * t; r = HEEL
    else:
        Pb0 = (_P_H0 - V * PH_HEELOFF * T) + (BALL[0] - HEEL[0])
        P = Pb0 - V * (ph - PH_HEELOFF) * T; r = BALL
    a = foot_pitch(ph); ru, rv = _R(a, *r)
    return P - ru, GROUND - rv, a

def ankle_target(ph):
    """ankle position (u forward of hip, v down in px) and foot pitch for phase ph in [0,1)"""
    if ph < STANCE:
        return _stance_ankle(ph)
    u0, v0, a0 = _stance_ankle(STANCE)
    u1, v1, a1 = _stance_ankle(0.0)
    s = (ph - STANCE) / (1 - STANCE)
    k = _ss(s)
    u = u0 + (u1 - u0) * k
    v = v0 + (v1 - v0) * k - 34.0 * math.sin(math.pi * s ** 0.85)
    return u, v, foot_pitch(ph)

def hip_y(phc):
    return 512.0 + 4.0 * math.cos(4 * math.pi * phc)

def leg_ik(du, dv):
    """du forward, dv down (ankle relative to hip). knee forward. returns θ1, θ2 (deg, fwd+), k, reach margin"""
    D0 = math.hypot(du, dv); D = min(D0, L1 + L2 - 0.01)
    base = math.atan2(du, dv)
    al = math.acos(max(-1, min(1, (L1**2 + D**2 - L2**2) / (2 * L1 * D))))
    be = math.acos(max(-1, min(1, (L2**2 + D**2 - L1**2) / (2 * L2 * D))))
    return math.degrees(base + al), math.degrees(base - be), math.degrees(al + be), (L1 + L2) - D0

def state(t):
    """full gait state at time t (seconds). Pure function of t."""
    phc = (t / T) % 1.0
    hy = hip_y(phc)
    g = {'t': t, 'phase': phc, 'hip_y': hy, 'v': V}
    for name, off in (('A', 0.0), ('B', 0.5)):
        ph = (phc + off) % 1.0
        u, v, a = ankle_target(ph)
        th1, th2, k, margin = leg_ik(u, v - hy)
        g[name] = dict(ph=ph, ankle_u=u, ankle_v=v, foot=a, th1=th1, th2=th2, knee=k, margin=margin,
                       stance=ph < STANCE)
        # arm of the same side swings opposite to the leg
        sw = -24.0 * math.cos(2 * math.pi * ph) - 3.0
        el = 16.0 + 14.0 * (sw / 24.0 + 1) / 2
        g[name].update(arm=sw, elbow=el, wrist=-0.4 * sw)
    g['lean'] = 4.0 + 0.8 * math.cos(4 * math.pi * phc)
    g['head_pitch'] = -0.7 * g['lean'] + 0.8 * math.sin(4 * math.pi * phc)
    g['sway'] = 6.0 * math.sin(2 * math.pi * phc)       # front view lateral sway (toward leg A when A is stance)
    g['tilt'] = -2.5 * math.sin(2 * math.pi * phc)      # front view hip tilt (free-leg side drops)
    g['twist'] = 0.18 * math.cos(2 * math.pi * phc)     # front view shoulders counter-rotate
    g['torso_roll'] = 1.2 * math.sin(2 * math.pi * phc)
    return g
