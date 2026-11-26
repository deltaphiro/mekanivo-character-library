"""Front-view walk = projection of the SAME sagittal gait (gait.py) onto the existing front rig (ucup_rig4)."""
import math
import gait
import ucup_rig4 as R4

def front_pose(g, expr=None):
    hy = g['hip_y']; tt = math.degrees(math.atan(g['sway'] / 325.0))
    ov = {'ry': hy - 502.0}
    for k, nm in (('R', 'A'), ('L', 'B')):
        L = g[nm]
        st, ss = math.cos(math.radians(L['th1'])), math.cos(math.radians(L['th2']))
        if k == 'R': th, kn = -1.5 + tt, -tt
        else:        th, kn = -1.5 - tt, +tt
        ov[k] = dict(th=th, kn=kn, st=st, ss=ss)
    p = dict(leg_override=ov, root_x=g['sway'], hip=g['tilt'], twist=g['twist'], torso=g['torso_roll'], head=-0.6 * g['torso_roll'])
    for k, nm in (('R', 'A'), ('L', 'B')):
        L = g[nm]; a, e = L['arm'], L['elbow']
        fw = max(0.0, min(1.0, (1 - 0.5 * (math.cos(math.radians(a)) + math.cos(math.radians(a + e)))) / 0.75))
        p[f'{k}_fwd'] = fw; p[f'{k}_abd'] = 9; p[f'{k}_flex'] = 6
    if expr: p.update(expr)
    return p
