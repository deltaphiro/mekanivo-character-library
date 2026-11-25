"""
UCUP rig v0.4 (v0.3 + leg_override for gait) — structural revision of v0.1 (identity, face, cap, palette, hand art unchanged)
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
HIP = (340, 502)
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
    ov = p.get('leg_override')
    if ov:   # walk: legs given directly by the gait driver (st=cos thigh, ss=cos shank, hip height from gait)
        L = {}
        for k in 'RL':
            o = ov[k]; v = dict(th=o['th'], kn=o['kn'], st=o['st'], ss=o['ss'], hy=HIP[1], reach=0, c=1)
            th = math.radians(v['th']); tk = math.radians(v['th'] + v['kn'])
            kx = HIP[0] - THIGH * v['st'] * math.sin(th); ky = v['hy'] + THIGH * v['st'] * math.cos(th)
            ax = kx - SHIN * v['ss'] * math.sin(tk); ay = ky + SHIN * v['ss'] * math.cos(tk)
            if k == 'L': kx, ax = 600 - kx, 600 - ax
            v['knee'], v['ankle'] = (kx, ky), (ax, ay); L[k] = v
        return L, ov['ry']
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
    shoe = (f'<g{gid(ids, "foot-" + k)} data-pivot="ankle" transform="translate(0 {f(SHIN * ss)}) {rot(-(th + kn))} translate(4 0) scale(0.96 1) {rot(-p[k + "_foot"])}">'
            f'<path d="M-40 27 C-44 8 -30 -5 -8 -5 C14 -5 38 -1 48 15 C54 26 49 35 40 36 L-33 36 C-38 36 -40 32 -40 27 Z" fill="{C["shoe"]}"/>'
            f'<path d="M-40 28 C-30 24 -10 24 8 25 C28 26 44 26 52 24 C53 31 48 36 40 37 L-33 37 C-39 37 -41 33 -40 28 Z" fill="{C["sole"]}"/>'
            f'<path d="M-4 7 L8 11 M0 13.5 L13 17.5 M4 20 L17 24" stroke="{C["lace"]}" stroke-width="2.6" stroke-linecap="round" fill="none"/>'
            f'<path d="M-30 12 C-24 6 -14 4 -6 4" stroke="{C["shoe_dk"]}" stroke-width="3" stroke-linecap="round" fill="none" opacity=".6"/></g>')
    out = (f'<g{gid(ids, "leg-" + k)} data-pivot="{HIP[0]},{f(hy)}" transform="translate({HIP[0]} {f(hy)}) {rot(th)}">'
           f'<g transform="scale(0.89 {f(st)})">'
           f'<path d="M-42 8 Q-42 -8 -26 -8 L26 -8 Q42 -8 42 8 C43 60 41 118 39.5 {THIGH + 4} L-39.5 {THIGH + 4} C-41 118 -43 60 -42 8 Z" fill="{pa}"/>'
           f'<path d="M-30 4 C-26 26 -30 44 -36 54" stroke="{pl}" stroke-width="2.4" stroke-linecap="round" fill="none"/>'
           f'<path d="M-3 4 C-5 28 -6 46 -7 62" stroke="{pl}" stroke-width="2.2" stroke-linecap="round" fill="none" opacity=".8"/></g>'
           f'<g{gid(ids, "shin-" + k)} data-pivot="knee" transform="translate(0 {f(THIGH * st)}) {rot(kn)}">'
           f'<g transform="scale(0.89 {f(ss)})">'
           f'<ellipse rx="39.5" ry="9" fill="{pa}"/>'
           f'<path d="M-39.5 -2 L39.5 -2 C39 40 39.5 100 41 {SHIN - 2} L-41 {SHIN - 2} C-39.5 100 -39 40 -39.5 -2 Z" fill="{pa}"/>'
           f'<path d="M-40 {SHIN - 14} L40 {SHIN - 14}" stroke="{pl}" stroke-width="2.2" opacity=".55"/></g>'
           f'{shoe}'
           f'<g transform="translate(0 {f(SHIN * ss)}) {rot(-(th + kn))}"><path d="M-37.5 -8 L37.5 -8 L38 0 Q0 6 -38 0 Z" fill="{pa}"/></g>'
           f'</g></g>')
    if k == 'L':
        out = f'<g transform="translate(600 0) scale(-1 1)">{out}</g>'
    return out



import ucup_rig as _V1
def neck_svg3(ids=True):
    return (f'<g{gid(ids, "neck")}>'
            f'<path d="M275 232 L325 232 L325 296 C314 307 286 307 275 296 Z" fill="{C["skin"]}"/>'
            f'<path d="M264 294 C280 318 320 318 336 294" stroke="{C["blue_dk"]}" stroke-width="4" stroke-linecap="round" fill="none"/>'
            f'</g>')

HEAD_DY = 32            # head seated lower on the neck (v0.2: 18)
CAP_PIV = _V1.CAP_PIV
CAP_LIM_ROT, CAP_LIM_DY = 1.0, 1.0   # cap rigid to head; only +-1 follow-through

def head_svg3(p, ids=True):
    hr = C['hair']; on = p['cap_on']
    cr = max(-CAP_LIM_ROT, min(CAP_LIM_ROT, p['cap_rot'])); cd = max(-CAP_LIM_DY, min(CAP_LIM_DY, p['cap_dy']))
    cap_tf = f'translate(0 {f(cd)}) {rot(cr, *CAP_PIV)}'
    c, dk, hi = C['cap'], C['cap_dk'], C['cap_hi']
    visor = crown = ''
    if on:
        visor = (f'<g{gid(ids, "cap-visor")} transform="{cap_tf}"><path d="M350 116 C376 118 400 140 409 170 C390 174 364 166 346 152 Z" fill="{dk}"/>'
                 f'<path d="M352 124 C372 128 392 142 400 160" stroke="{c}" stroke-width="2" fill="none" opacity=".5"/></g>')
        crown = (f'<g{gid(ids, "cap")} transform="{cap_tf}">'
                 f'<path d="M234 141 C226 98 262 64 300 64 C338 64 374 98 366 141 Q300 152 234 141 Z" fill="{c}"/>'
                 f'<path d="M330 68 C352 84 370 112 366 141 Q350 146 336 146 C343 120 341 92 330 68 Z" fill="{dk}"/>'
                 f'<circle cx="300" cy="64.5" r="5.4" fill="{c}"/>'
                 f'<path d="M279 134 A21 23 0 0 1 321 134 Z" fill="{C["cap_hole"]}"/>'
                 f'<path d="M277 134 L323 134 L322 143 Q300 147 278 143 Z" fill="{hi}"/>'
                 f'<g fill="{C["cap_dot"]}"><circle cx="287" cy="139" r="1.6"/><circle cx="295" cy="139.5" r="1.6"/>'
                 f'<circle cx="303" cy="139.5" r="1.6"/><circle cx="311" cy="139" r="1.6"/></g></g>')
    # hair: with the cap on, the scalp hair is cut INSIDE the crown (top edge y=128) so it can never show above/beside the hat;
    # visible hair = side hair + fringe below the hat edge. Cap off -> full bowl cut.
    if on:
        back = (f'<path{gid(ids, "hair-back")} d="M231 172 C231 204 242 228 262 239 L338 239 C358 228 369 204 369 172 C369 160 367 148 364 141 L364 128 L236 128 L236 141 C233 148 231 160 231 172 Z" fill="{hr}"/>')
        fringe = (f'<path{gid(ids, "hair-fringe")} d="M230 178 C230 160 233 148 235 141 L235 128 L365 128 L365 141 C367 148 370 160 370 178 L358 176 L355 162 L345 151 L335 169 L325 148 L313 167 L301 145 '
                  f'L289 165 L277 146 L266 167 L255 151 L246 162 L244 176 Z" fill="{hr}"/>')
    else:
        back = (f'<path{gid(ids, "hair-back")} d="M231 172 C231 204 242 228 262 239 L338 239 C358 228 369 204 369 172 C369 110 340 76 300 76 C260 76 231 110 231 172 Z" fill="{hr}"/>')
        fringe = (f'<path{gid(ids, "hair-fringe")} d="M229 184 C222 120 250 76 300 76 C350 76 378 120 371 184 L358 176 L355 162 L345 151 L335 169 L325 148 L313 167 L301 145 '
                  f'L289 165 L277 146 L266 167 L255 151 L246 162 L244 176 Z" fill="{hr}"/>')
    ears = ''.join(
        f'<ellipse{gid(ids, "ear-" + ("L" if cx < 300 else "R"))} cx="{cx}" cy="190" rx="14.5" ry="19.5" fill="{C["skin"]}"/>'
        f'<path d="M{cx + s_ * 3} 182 Q{cx - s_ * 4} 188 {cx + s_ * 1} 199" stroke="{C["ear_in"]}" stroke-width="2.4" stroke-linecap="round" fill="none"/>'
        for cx, s_ in ((238, -1), (362, 1)))
    face = (f'<path{gid(ids, "face-base")} d="M240 166 C240 134 264 118 300 118 C336 118 360 134 360 166 L360 192 '
            f'C360 227 334 246 300 246 C266 246 240 227 240 192 Z" fill="{C["skin"]}"/>')
    chin_sh = f'<path d="M280 236 Q300 258 320 236 L320 248 Q300 264 280 248 Z" fill="{C["skin_sh"]}"/>'
    sweat = ''
    if p['sweat'] > 0.05:
        sw = p['sweat']
        sweat = (f'<path d="M352 {f(150 + 14 * sw)} C347 {f(160 + 14 * sw)} 344 {f(168 + 14 * sw)} 352 {f(172 + 14 * sw)} '
                 f'C360 {f(168 + 14 * sw)} 357 {f(160 + 14 * sw)} 352 {f(150 + 14 * sw)} Z" fill="{C["sweat"]}" opacity="{f(min(1, sw * 1.5))}"/>')
    return (f'<g{gid(ids, "head")} data-pivot="{NECK[0]},{NECK[1]}" transform="{rot(p["head"], *NECK)} translate(0 {HEAD_DY}) '
            f'translate(300 296) scale(1.12) translate(-300 -296)">'
            f'{visor}{back}{chin_sh}{face}{_V1.features_svg(p, ids)}{fringe}{ears}{crown}{sweat}</g>')

# ------------------------------------------------------------ torso
def logo(dx=0):
    return (f'<g id="ucup-logo" transform="translate({f(268 + dx)} 372) scale(.92)">'
            f'<path d="M5 38 V12 M5 22 C5 5 27 5 27 22 V38 M27 22 C27 5 49 5 49 22 V38" stroke="{C["white"]}" '
            f'stroke-width="10.5" fill="none" stroke-linejoin="round"/><circle cx="60" cy="35" r="7.3" fill="{C["orange"]}"/></g>')

CHEST = (f'<path d="M221 316 C230 299 266 293 284 293 L316 293 C334 293 370 299 379 316 '
         f'C384 360 386 430 386 484 L386 494 L214 494 L214 484 C214 430 216 360 221 316 Z" fill="{C["blue"]}"/>')
ABDOMEN = (f'<path d="M219 492 L381 492 L380 504 C379 514 374 520 366 520 L234 520 C226 520 221 514 220 504 Z" fill="{C["hem"]}"/>'
           f'<path d="M214 455 L386 455 L386 496 C386 501 382 504 374 504 C340 507 260 507 226 504 C218 504 214 501 214 496 Z" fill="{C["blue"]}"/>')

def pelvis_svg2(p, ids=True):
    return (f'<g transform="{rot(p["hip"] * 0.8, 300, 520)}"><path{gid(ids, "pelvis")} d="M224 480 L376 480 L376 546 C376 562 224 562 224 546 Z" fill="{C["pants"]}"/>'
            f'<path d="M226 516 L374 516 L374 526 Q300 534 226 526 Z" fill="{C["pants_sh"]}" opacity=".85"/>'
            f'<path d="M238 528 C244 536 247 548 248 558 M362 528 C356 536 353 548 352 558" stroke="{C["pants_ln"]}" '
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
    abd_tf = f'{rot(0.35 * tilt - 0.4 * p["hip"], *HEM_P)} translate(300 517) scale({f(math.cos(phi * .85))} 1) translate(-300 -517)'
    art_tf = f'translate({cp[0]} {cp[1]}) scale({f(ct)} {f(1 - 0.30 * bend)}) translate({-cp[0]} {-cp[1]})'
    cont = f'translate(0 {f(drop)})'
    order = ['L', 'R'] if p['arm_top'] == 'R' else ['R', 'L']
    back = ''.join(arm_svg2(k, p, ids) for k in order if p[f'{k}_z'] == 'back')
    front = ''.join(arm_svg2(k, p, ids) for k in order if p[f'{k}_z'] != 'back')
    p2 = dict(p); p2['face_x'] = p['face_x'] + 9 * stw
    hd = (f'<g transform="translate(300 296) scale({f(1 + .06 * bend)}) translate(-300 -296)">{head_svg3(p2, ids)}</g>')
    chest = (f'<g{gid(ids, "torso")} data-pivot="{cp[0]},{cp[1]}" transform="{chest_tf}">'
             f'<g transform="{cont}">{back}</g>'
             f'<g transform="{inv}"><g{gid(ids, "abdomen")} transform="{abd_tf}">{ABDOMEN}</g></g>'
             f'<g{gid(ids, "chest-art")} transform="{art_tf}">{CHEST}{logo(36 * stw / max(ct, .3))}</g>'
             f'<g transform="{cont}">{neck_svg3(ids)}{hd}{front}</g></g>')
    legs = leg_svg2('R', p, L['R'], ids) + leg_svg2('L', p, L['L'], ids)
    return (f'<g{gid(ids, "root")} transform="translate({f(p["root_x"])} {f(ry)})">{pelvis_svg2(p, ids)}{legs}{chest}</g>')


def svg_doc(pose=None, ids=True, bg=None, view=(0, 0, W, H), size=None, extra='', title='Ucup v0.3'):
    vx, vy, vw, vh = view
    w, h = size or (vw, vh)
    bgr = f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {vw} {vh}" width="{w}" height="{h}">'
            f'<title>{title}</title>{bgr}{extra}{character_svg2(pose, ids)}</svg>')
