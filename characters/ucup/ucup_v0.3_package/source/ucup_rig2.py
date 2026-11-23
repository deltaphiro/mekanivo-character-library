"""
UCUP rig v0.2 — structural revision of v0.1 (identity, face, cap, palette, hand art unchanged)
Changes (each maps to a diagnosed v0.1 defect):
  * torso split: chest + abdomen/hem (bend, twist, lean without rigid slab)
  * shoulder: lower pivot, scapular rhythm (shoulder lifts when arm rises), per-arm shrug
  * arm: seamless elbow union, flex-driven elbow creases, forward foreshortening (fwd)
  * sleeve cuff: hand now emerges from UNDER the sleeve lip (no cuff patch painted over hand)
  * layering: per-arm z (front/back of torso) + arm_top (which arm overlaps the other)
  * legs: thigh foreshortening + knee-out squat (`squat`), hip tilt for weight shift,
          automatic foot planting (support leg straight, free leg compresses to keep ground contact)
"""
import math
import ucup_rig as V1
from ucup_rig import C, hand_svg, HAND_STATES, head_svg, neck_svg, f, rot, gid, UPPER, FORE, THIGH, SHIN, NECK, W, H

SH = (368, 326)          # right shoulder pivot (v0.1: 372,322)
HIP = (348, 502)
CHEST_P = (300, 470)     # chest pivot (waist seam)
HEM_P = (300, 517)

NEW = dict(twist=0, bend=0, squat=0, hip=0, arm_top='R',
           R_fwd=0, L_fwd=0, R_z='front', L_z='front', R_sh=0, L_sh=0,
           R_fold=0, L_fold=0)
DEFAULT = V1.DEFAULT
DEFAULT.update(NEW)


# ------------------------------------------------------------ shoulder / anchors
def rhythm(abd):
    """scapulohumeral rhythm: shoulder girdle lifts as the arm rises above ~40deg"""
    return min(16.0, max(0.0, abd - 40) * 0.14)

def anchor(p, k, with_rhythm=True):
    phi = math.radians(35 * p['twist'])
    ct, st = math.cos(phi), math.sin(phi)
    lift = rhythm(p[f'{k}_abd']) if with_rhythm else 0
    x = 300 + (SH[0] - 300) * ct - 0.3 * lift
    y = SH[1] + (-6 * st if k == 'R' else 6 * st) - p['shrug'] - p[f'{k}_sh'] - lift
    return x, y


# ------------------------------------------------------------ arm
def arm_svg2(k, p, ids=True):
    abd, flex, wr = p[f'{k}_abd'], p[f'{k}_flex'], p[f'{k}_wrist']
    fw = p[f'{k}_fwd']
    ul, fl, hs, wd = 1 - 0.75 * fw, 1 - 0.75 * fw, 1 + 0.35 * fw, 1 + 0.1 * fw
    b, d = C['blue'], C['blue_dk']
    sx, sy = anchor(p, k)
    a = min(1.0, max(0.0, (flex - 30) / 50))
    crease = (f'<path d="M-25 -5 Q-14 5 -5 3 M-27 6 Q-17 13 -8 11" stroke="{d}" stroke-width="2.4" stroke-linecap="round" '
              f'fill="none" opacity="{f(a * .85)}"/>') if a > 0.02 else ''
    hand = hand_svg(p[f'{k}_hand'])
    g = (f'<g{gid(ids, "arm-" + k)} data-pivot="{f(sx)},{f(sy)}" transform="translate({f(sx)} {f(sy)}) {rot(-abd)}">'
         f'<circle r="28.5" fill="{b}"/>'
         f'<g transform="scale({f(wd)} {f(ul)})">'
         f'<path d="M-28.5 0 C-32 34 -33 70 -31 {UPPER} L31 {UPPER} C33 70 32 34 28.5 0 Z" fill="{b}"/>'
         f'<circle cy="{UPPER}" r="31" fill="{b}"/>'
         f'<path d="M-25.5 12 C-28 46 -28 76 -26 {UPPER - 6}" stroke="{d}" stroke-width="2.6" stroke-linecap="round" fill="none"/></g>'
         f'<g{gid(ids, "forearm-" + k)} data-pivot="elbow" transform="translate(0 {f(UPPER * ul)}) {rot(flex)}">'
         f'<g transform="scale({f(wd)} {f(fl)})">'
         f'<circle r="31" fill="{b}"/>'
         # hand is drawn BEFORE the sleeve body so it emerges from under the lip
         f'<g{gid(ids, "hand-" + k)} data-pivot="wrist" transform="translate(0 {FORE - 14}) scale({f(1.3 * hs / wd)} {f(1.3 * hs / fl)}) {rot(wr)}">'
         f'<rect x="-10" y="-22" width="20" height="28" fill="{C["skin"]}"/>{hand}</g>'
         f'<path d="M-31 0 L31 0 C32 40 29 82 25 100 L23 {FORE - 1} A23 6 0 0 1 -23 {FORE - 1} L-25 100 C-29 82 -32 40 -31 0 Z" fill="{b}"/>'
         f'<path d="M-23 {FORE - 1} A23 6 0 0 0 23 {FORE - 1}" stroke="{d}" stroke-width="2.4" stroke-linecap="round" fill="none" opacity=".7" transform="translate(0 0)"/>'
         f'<path d="M-24 {FORE - 14} Q0 {FORE - 9} 24 {FORE - 14}" stroke="{d}" stroke-width="2.2" stroke-linecap="round" fill="none" opacity=".6"/>'
         f'</g>{crease}</g></g>')
    if k == 'L':
        g = f'<g transform="translate(600 0) scale(-1 1)">{g}</g>'
    return g


# ------------------------------------------------------------ legs
def solve_legs(p):
    sq = min(1.15, max(p['squat'], max(0, p['root_y']) / 80.0))
    ht = math.radians(p['hip'])
    L = {}
    for k, sg in (('R', 1), ('L', -1)):
        fold = min(.7, sq * 0.9 + p[f'{k}_fold'])
        st = 1 - 0.55 * fold
        abd = p[f'{k}_thigh'] + 24 * sq
        kn = p[f'{k}_knee'] + 0.9 * 24 * sq
        ss = 1 + 0.06 * min(1, max(0, -p['root_y'] / 10.0))
        hy = HIP[1] + sg * 40 * math.sin(ht)
        L[k] = dict(th=-abd, kn=kn, st=st, ss=ss, hy=hy)
        L[k]['reach'] = hy + THIGH * st * math.cos(math.radians(-abd)) + SHIN * ss * math.cos(math.radians(-abd + kn))
    Y = min(v['reach'] for v in L.values())
    for k, v in L.items():
        c = max(0.75, min(1.0, (Y - v['hy']) / (v['reach'] - v['hy'])))
        v['st'] *= c; v['ss'] *= c; v['c'] = c
        th = math.radians(v['th']); tk = math.radians(v['th'] + v['kn'])
        kx = HIP[0] - THIGH * v['st'] * math.sin(th)
        ky = v['hy'] + THIGH * v['st'] * math.cos(th)
        ax = kx - SHIN * v['ss'] * math.sin(tk); ay = ky + SHIN * v['ss'] * math.cos(tk)
        if k == 'L':
            kx, ax = 600 - kx, 600 - ax
        v['knee'], v['ankle'] = (kx, ky), (ax, ay)
    ry = (827 - Y) + min(0, p['root_y'] + 10)
    return L, ry


def leg_svg2(k, p, g, ids=True):
    pa, pl = C['pants'], C['pants_ln']
    st, ss, th, kn, hy = g['st'], g['ss'], g['th'], g['kn'], g['hy']
    shoe = (f'<g{gid(ids, "foot-" + k)} data-pivot="ankle" transform="translate(0 {f(SHIN * ss)}) {rot(-(th + kn))} scale(1.08 1) {rot(-p[k + "_foot"])}">'
            f'<path d="M-40 27 C-44 8 -30 -5 -8 -5 C14 -5 38 -1 48 15 C54 26 49 35 40 36 L-33 36 C-38 36 -40 32 -40 27 Z" fill="{C["shoe"]}"/>'
            f'<path d="M-40 28 C-30 24 -10 24 8 25 C28 26 44 26 52 24 C53 31 48 36 40 37 L-33 37 C-39 37 -41 33 -40 28 Z" fill="{C["sole"]}"/>'
            f'<path d="M-4 7 L8 11 M0 13.5 L13 17.5 M4 20 L17 24" stroke="{C["lace"]}" stroke-width="2.6" stroke-linecap="round" fill="none"/>'
            f'<path d="M-30 12 C-24 6 -14 4 -6 4" stroke="{C["shoe_dk"]}" stroke-width="3" stroke-linecap="round" fill="none" opacity=".6"/></g>')
    out = (f'<g{gid(ids, "leg-" + k)} data-pivot="{HIP[0]},{f(hy)}" transform="translate({HIP[0]} {f(hy)}) {rot(th)}">'
           f'<g transform="scale(1.07 {f(st)})">'
           f'<path d="M-42 8 Q-42 -8 -26 -8 L26 -8 Q42 -8 42 8 C43 60 41 118 39.5 {THIGH + 4} L-39.5 {THIGH + 4} C-41 118 -43 60 -42 8 Z" fill="{pa}"/>'
           f'<path d="M-30 4 C-26 26 -30 44 -36 54" stroke="{pl}" stroke-width="2.4" stroke-linecap="round" fill="none"/>'
           f'<path d="M-3 4 C-5 28 -6 46 -7 62" stroke="{pl}" stroke-width="2.2" stroke-linecap="round" fill="none" opacity=".8"/></g>'
           f'<g{gid(ids, "shin-" + k)} data-pivot="knee" transform="translate(0 {f(THIGH * st)}) {rot(kn)}">'
           f'<g transform="scale(1.07 {f(ss)})">'
           f'<ellipse rx="39.5" ry="9" fill="{pa}"/>'
           f'<path d="M-39.5 -2 L39.5 -2 C39 40 39.5 100 41 {SHIN - 2} L-41 {SHIN - 2} C-39.5 100 -39 40 -39.5 -2 Z" fill="{pa}"/>'
           f'<path d="M-40 {SHIN - 14} L40 {SHIN - 14}" stroke="{pl}" stroke-width="2.2" opacity=".55"/></g>'
           f'{shoe}'
           f'<g transform="translate(0 {f(SHIN * ss)}) {rot(-(th + kn))}"><path d="M-44 -8 L44 -8 L44.5 0 Q0 6 -44.5 0 Z" fill="{pa}"/></g>'
           f'</g></g>')
    if k == 'L':
        out = f'<g transform="translate(600 0) scale(-1 1)">{out}</g>'
    return out


# ------------------------------------------------------------ torso
def logo(dx=0):
    return (f'<g id="ucup-logo" transform="translate({f(268 + dx)} 372) scale(.92)">'
            f'<path d="M5 38 V12 M5 22 C5 5 27 5 27 22 V38 M27 22 C27 5 49 5 49 22 V38" stroke="{C["white"]}" '
            f'stroke-width="10.5" fill="none" stroke-linejoin="round"/><circle cx="60" cy="35" r="7.3" fill="{C["orange"]}"/></g>')

CHEST = (f'<path d="M222 316 C231 299 266 293 284 293 L316 293 C334 293 369 299 378 316 L381 480 '
         f'C381 488 378 494 372 494 L228 494 C222 494 219 488 219 480 Z" fill="{C["blue"]}"/>')
ABDOMEN = (f'<path d="M219 455 L381 455 L382 498 C382 509 377 517 367 517 L233 517 C223 517 218 509 218 498 Z" fill="{C["blue"]}"/>'
           f'<path d="M218 494 L382 494 L382 498 C382 509 377 517 367 517 L233 517 C223 517 218 509 218 498 Z" fill="{C["hem"]}"/>')

def pelvis_svg2(p, ids=True):
    return (f'<g transform="{rot(p["hip"] * 0.8, 300, 520)}"><path{gid(ids, "pelvis")} d="M206 480 L394 480 L394 548 C394 566 206 566 206 548 Z" fill="{C["pants"]}"/>'
            f'<path d="M232 524 C240 534 244 548 246 560 M368 524 C360 534 356 548 354 560" stroke="{C["pants_ln"]}" '
            f'stroke-width="2.2" stroke-linecap="round" fill="none"/></g>')


def character_svg2(pose=None, ids=True):
    p = dict(DEFAULT)
    if pose:
        p.update(pose)
    L, ry = solve_legs(p)
    phi = math.radians(35 * p['twist']); ct, stw = math.cos(phi), math.sin(phi)
    bend = p['bend']; drop = 53 * bend
    br = 1 + p['breath']; tilt = p['torso']
    cp = CHEST_P
    chest_tf = f'{rot(tilt, *cp)} translate({cp[0]} {cp[1]}) scale(1 {f(br)}) translate({-cp[0]} {-cp[1]})'
    inv = f'translate({cp[0]} {cp[1]}) scale(1 {f(1 / br)}) translate({-cp[0]} {-cp[1]}) {rot(-tilt, *cp)}'
    abd_tf = f'{rot(0.35 * tilt - 0.4 * p["hip"], *HEM_P)} translate(300 517) scale({f(math.cos(phi * .5))} 1) translate(-300 -517)'
    art_tf = f'translate({cp[0]} {cp[1]}) scale({f(ct)} {f(1 - 0.30 * bend)}) translate({-cp[0]} {-cp[1]})'
    cont = f'translate(0 {f(drop)})'
    order = ['L', 'R'] if p['arm_top'] == 'R' else ['R', 'L']
    back = ''.join(arm_svg2(k, p, ids) for k in order if p[f'{k}_z'] == 'back')
    front = ''.join(arm_svg2(k, p, ids) for k in order if p[f'{k}_z'] != 'back')
    p2 = dict(p); p2['face_x'] = p['face_x'] + 9 * stw
    hd = (f'<g transform="translate(300 296) scale({f(1 + .06 * bend)}) translate(-300 -296)">{head_svg(p2, ids)}</g>')
    chest = (f'<g{gid(ids, "torso")} data-pivot="{cp[0]},{cp[1]}" transform="{chest_tf}">'
             f'<g transform="{cont}">{back}</g>'
             f'<g transform="{inv}"><g{gid(ids, "abdomen")} transform="{abd_tf}">{ABDOMEN}</g></g>'
             f'<g{gid(ids, "chest-art")} transform="{art_tf}">{CHEST}{logo(36 * stw / max(ct, .3))}</g>'
             f'<g transform="{cont}">{neck_svg(ids)}{hd}{front}</g></g>')
    legs = leg_svg2('R', p, L['R'], ids) + leg_svg2('L', p, L['L'], ids)
    return (f'<g{gid(ids, "root")} transform="translate({f(p["root_x"])} {f(ry)})">{pelvis_svg2(p, ids)}{legs}{chest}</g>')


def svg_doc(pose=None, ids=True, bg=None, view=(0, 0, W, H), size=None, extra='', title='Ucup v0.2'):
    vx, vy, vw, vh = view
    w, h = size or (vw, vh)
    bgr = f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {vw} {vh}" width="{w}" height="{h}">'
            f'<title>{title}</title>{bgr}{extra}{character_svg2(pose, ids)}</svg>')
