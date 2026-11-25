"""
UCUP — MEKANIVO character, procedural SVG rig  (v0.1.0-draft)
-------------------------------------------------------------
Rebuilt from scratch as vector geometry (no raster, no sheet crops).
Coordinate system : viewBox 0 0 600 900, centre-line x=300, ground y=860, y down.
Side naming       : R / L = SCREEN right / SCREEN left (character's left / right).
Angle conventions : arm_abd   = upper-arm abduction, outward +  (deg)
                    arm_flex  = elbow flex toward body-midline, inward +
                    wrist     = hand rotation, same sense as flex (inward +)
                    thigh/knee/foot analogous.  Head/torso = SVG clockwise +.
Every movable group is authored in its own local frame (origin = pivot),
parents drive children via nested translate/rotate.  Left side = mirrored R.
"""
import math

W, H = 600, 900
GROUND = 860

C = dict(
    skin='#F9727A', skin_sh='#E4566B', skin_dk='#C93847', ear_in='#E2606D',
    hair='#170708',
    cap='#F8941E', cap_dk='#F26D1D', cap_hi='#FBB040', cap_hole='#130F1A', cap_dot='#FDC15A',
    blue='#2453BD', blue_dk='#1A3A9C', hem='#1E3EA3', white='#FFFFFF', orange='#FA9112',
    pants='#F0D2BA', pants_ln='#D6B091', pants_sh='#E6C3A8',
    shoe='#D8213F', shoe_dk='#B52338', sole='#F8E6D4', lace='#FFFFFF',
    mouth_ln='#C8374A', mouth_in='#9E2037', tongue='#EA6A7E',
    mask='#AADDF0', mask_ln='#7FBFD9', sweat='#8FD6F0',
)

# ---- skeleton dimensions (rest pose) -------------------------------------
SHOULDER_R = (372, 322)
UPPER, FORE = 100, 108           # upper-arm length, forearm (to sleeve end)
HIP_R = (348, 502)
THIGH, SHIN = 173, 152           # hip->knee, knee->ankle(pants hem)
NECK = (300, 296)
WAIST = (300, 505)
CAP_PIV = (300, 112)

DEFAULT = dict(
    # body
    root_x=0, root_y=0, plant=1, torso=0, breath=0, head=0, face_x=0, face_y=0,
    cap_on=1, cap_rot=0, cap_dy=0, shrug=0,
    # arms  (abd outward+, flex inward+)
    R_abd=9, R_flex=6, R_wrist=0, R_hand='relaxed',
    L_abd=9, L_flex=6, L_wrist=0, L_hand='relaxed',
    # legs
    R_thigh=1.5, R_knee=0, R_foot=0, L_thigh=1.5, L_knee=0, L_foot=0,
    # face
    bR_y=0, bR_r=0, bR_c=2.5, bL_y=0, bL_r=0, bL_c=2.5,
    eR_o=1, eL_o=1, eR_arc=-1, eL_arc=-1, gx=0, gy=0,
    m_w=26, m_open=0, m_smile=1.0, m_skew=0, m_x=0, m_y=0,
    blush=0, sweat=0, mask=0,
)


def f(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def rot(a, px=0, py=0):
    return f'rotate({f(a)} {f(px)} {f(py)})' if abs(a) > 1e-6 else ''


def gid(ids, name):
    return f' id="ucup-{name}"' if ids else ''


# ======================= HANDS (right-hand, local frame) ===================
def _fing(x0, y0, x1, y1, w=9.0, col=None):
    col = col or C['skin']
    return (f'<path d="M{f(x0)} {f(y0)} L{f(x1)} {f(y1)}" stroke="{col}" '
            f'stroke-width="{f(w)}" stroke-linecap="round" fill="none"/>')


def _fan(spread=1.0, curl=1.0, lens=(30, 34, 31, 24), xs=(-10.5, -3.5, 3.5, 10.5),
         base=(-5, -1.5, 2.5, 7)):
    out = []
    for x, a, L in zip(xs, base, lens):
        ar = math.radians(a * spread)
        out.append(_fing(x, 34, x + math.sin(ar) * L * curl, 34 + math.cos(ar) * L * curl, 8.8))
    return ''.join(out)


_BLOCK = 'M-15 -4 L15 -4 C18.5 12 18.5 28 14 39 C8 44 -8 44 -14 39 C-18.5 28 -18.5 12 -15 -4 Z'
_PALM = 'M-16 -4 L16 -4 C19.5 12 19.5 28 15.5 40 L-15.5 40 C-19.5 28 -19.5 12 -16 -4 Z'


def hand_svg(state):
    s, d = C['skin'], C['skin_dk']
    if state == 'relaxed':
        return (_fing(-13, 6, -17.5, 32, 10.5) +
                f'<path d="M-15 -4 C-18.5 14 -17.5 36 -12.5 54 C-9 65 3 67 10 58 C17.5 48 17.5 20 15 -4 Z" fill="{s}"/>'
                f'<path d="M-3 42 L-4 58 M5.5 41 L5.5 56" stroke="{d}" stroke-width="2" stroke-linecap="round" fill="none"/>')
    if state in ('open', 'wave', 'present'):
        sp, cu = {'open': (1.0, 1.0), 'wave': (2.2, 1.0), 'present': (0.35, 0.93)}[state]
        return (_fing(-13, 20, -13 - math.sin(math.radians(46)) * 24, 20 + math.cos(math.radians(46)) * 24, 10) +
                f'<path d="{_PALM}" fill="{s}"/>' + _fan(sp, cu) +
                f'<path d="M-14 12 C-8 20 -3 24 -2 36" stroke="{d}" stroke-width="1.8" stroke-linecap="round" fill="none" opacity=".55"/>')
    if state == 'point':
        return (f'<path d="{_BLOCK}" fill="{s}"/>' +
                _fing(-9.5, 34, -10.5, 76, 9.2) +
                _fing(-1, 36, -1, 42, 9) + _fing(6.5, 36, 6.5, 41, 9) + _fing(13, 34, 13, 38, 8.5) +
                _fing(-12.5, 12, -3, 27, 9.5) +
                f'<path d="M-2 30 L14 30" stroke="{d}" stroke-width="2" stroke-linecap="round"/>')
    if state == 'thumbs':
        return (f'<path d="{_BLOCK}" fill="{s}"/>' +
                _fing(-3.5, 34, -3.5, 64, 13.5) +
                f'<path d="M-14 15 L14 15 M-14 25 L14 25 M-13 35 L13 35" stroke="{d}" stroke-width="2" stroke-linecap="round" opacity=".7"/>')
    if state == 'fist':
        return (f'<path d="{_BLOCK}" fill="{s}"/>' +
                ''.join(_fing(x, 35, x, 44, 9) for x in (-10, -3.5, 3.5, 10)) +
                _fing(-13, 24, 6, 30, 10.5) +
                f'<path d="M0 36 L0 44" stroke="{d}" stroke-width="1.8" opacity=".6"/>')
    if state == 'peace':
        return (f'<path d="{_BLOCK}" fill="{s}"/>' +
                _fing(-8, 34, -14.5, 72, 9) + _fing(2.5, 34, 8.5, 72, 9) +
                _fing(9.5, 36, 9.5, 42, 8.5) + _fing(14.5, 34, 14.5, 38, 8) +
                _fing(-12.5, 23, 6, 31, 10))
    if state == 'tuck':
        return f'<path d="M-15 -2 H15 V14 C15 24 -15 24 -15 14 Z" fill="{s}"/>'
    raise ValueError(state)


HAND_STATES = ['relaxed', 'open', 'wave', 'present', 'point', 'thumbs', 'fist', 'peace', 'tuck']


# ======================= ARM ================================================
def arm_svg(side, p, ids=True):
    k = side
    abd, flex, wr = p[f'{k}_abd'], p[f'{k}_flex'], p[f'{k}_wrist']
    b, d = C['blue'], C['blue_dk']
    sx, sy = SHOULDER_R
    sy = sy - p['shrug']
    hand = hand_svg(p[f'{k}_hand'])
    g = (f'<g{gid(ids, "arm-" + k)} data-pivot="{sx},{sy}" transform="translate({f(sx)} {f(sy)}) {rot(-abd)}">'
         # upper sleeve
         f'<path d="M-29 0 C-32 36 -32 72 -30 {UPPER} L30 {UPPER} C32 72 32 36 29 0 A29 29 0 0 0 -29 0 Z" fill="{b}"/>'
         f'<path d="M-26 12 C-28 46 -28 76 -26 {UPPER - 4}" stroke="{d}" stroke-width="2.6" stroke-linecap="round" fill="none"/>'
         # forearm
         f'<g{gid(ids, "forearm-" + k)} data-pivot="elbow" transform="translate(0 {UPPER}) {rot(flex)}">'
         f'<circle r="31" fill="{b}"/>'
         f'<path d="M-31 0 L31 0 C32 40 28 82 25 {FORE - 5} Q27 {FORE + 2} 18 {FORE + 2.5} L-18 {FORE + 2.5} Q-27 {FORE + 2} -27.5 {FORE - 5} C-30 82 -32 40 -31 0 Z" fill="{b}"/>'
         f'<path d="M-24 {FORE - 12} Q0 {FORE - 7} 24 {FORE - 12}" stroke="{d}" stroke-width="2.4" stroke-linecap="round" fill="none" opacity=".75"/>'
         f'<path d="M-22 8 Q-12 14 -2 12 M-20 20 Q-11 24 -3 23" stroke="{d}" stroke-width="2.4" stroke-linecap="round" fill="none" opacity=".8"/>'
         f'<g{gid(ids, "hand-" + k)} data-pivot="wrist" transform="translate(0 {FORE - 6}) {rot(wr)} scale(1.3)">{hand}</g>'
         f'<path d="M-27.5 {FORE - 5} Q-27 {FORE + 2} -18 {FORE + 2.5} L18 {FORE + 2.5} Q27 {FORE + 2} 27.5 {FORE - 5} L26 {FORE - 9} L-26 {FORE - 9} Z" fill="{b}"/>'
         f'</g></g>')
    if k == 'L':
        g = f'<g transform="translate(600 0) scale(-1 1)">{g}</g>'
    return g


# ======================= LEG ================================================
def leg_svg(side, p, ids=True):
    k = side
    th, kn, ft = p[f'{k}_thigh'], p[f'{k}_knee'], p[f'{k}_foot']
    hx, hy = HIP_R
    s = 1.0
    if p['plant']:
        s = max(0.78, min(1.05, 1 - p['root_y'] / (GROUND - hy)))
    pa, pl, ps = C['pants'], C['pants_ln'], C['pants_sh']
    shoe = (f'<g{gid(ids, "foot-" + k)} data-pivot="ankle" transform="translate(0 {SHIN}) scale(1.08 {f(1 / s)}) {rot(-ft)}">'
            f'<path d="M-40 27 C-44 8 -30 -5 -8 -5 C14 -5 38 -1 48 15 C54 26 49 35 40 36 L-33 36 C-38 36 -40 32 -40 27 Z" fill="{C["shoe"]}"/>'
            f'<path d="M-40 28 C-30 24 -10 24 8 25 C28 26 44 26 52 24 C53 31 48 36 40 37 L-33 37 C-39 37 -41 33 -40 28 Z" fill="{C["sole"]}"/>'
            f'<path d="M-4 7 L8 11 M0 13.5 L13 17.5 M4 20 L17 24" stroke="{C["lace"]}" stroke-width="2.6" stroke-linecap="round" fill="none"/>'
            f'<path d="M-30 12 C-24 6 -14 4 -6 4" stroke="{C["shoe_dk"]}" stroke-width="3" stroke-linecap="round" fill="none" opacity=".6"/></g>')
    g = (f'<g{gid(ids, "leg-" + k)} data-pivot="{hx},{hy}" transform="translate({hx} {hy}) scale(1.07 {f(s)}) {rot(-th)}">'
         f'<path d="M-42 -4 L42 -4 C43 60 41 118 39.5 {THIGH} L-39.5 {THIGH} C-41 118 -43 60 -42 -4 Z" fill="{pa}"/>'
         f'<path d="M-30 4 C-26 26 -30 44 -36 54" stroke="{pl}" stroke-width="2.4" stroke-linecap="round" fill="none"/>'
         f'<path d="M-3 4 C-5 28 -6 46 -7 62" stroke="{pl}" stroke-width="2.2" stroke-linecap="round" fill="none" opacity=".8"/>'
         f'<g{gid(ids, "shin-" + k)} data-pivot="knee" transform="translate(0 {THIGH}) {rot(kn)}">'
         f'<ellipse cx="0" cy="0" rx="39.5" ry="9" fill="{pa}"/>'
         f'<path d="M-39.5 -2 L39.5 -2 C39 40 39.5 100 41 {SHIN - 2} L-41 {SHIN - 2} C-39.5 100 -39 40 -39.5 -2 Z" fill="{pa}"/>'
         f'<path d="M-40 {SHIN - 14} L40 {SHIN - 14}" stroke="{pl}" stroke-width="2.2" opacity=".55"/>'
         f'{shoe}'
         f'<path d="M-41 {SHIN - 8} L41 {SHIN - 8} L41.5 {SHIN} Q0 {SHIN + 5} -41.5 {SHIN} Z" fill="{pa}"/>'
         f'</g></g>')
    if k == 'L':
        g = f'<g transform="translate(600 0) scale(-1 1)">{g}</g>'
    return g


# ======================= TORSO / HEAD =======================================
LOGO = (f'<g id="ucup-logo" transform="translate(268 372) scale(.92)">'
        f'<path d="M5 38 V12 M5 22 C5 5 27 5 27 22 V38 M27 22 C27 5 49 5 49 22 V38" stroke="{C["white"]}" '
        f'stroke-width="10.5" fill="none" stroke-linejoin="round"/>'
        f'<circle cx="60" cy="35" r="7.3" fill="{C["orange"]}"/></g>')


def torso_body(ids=True):
    b, h, d = C['blue'], C['hem'], C['blue_dk']
    return (f'<g{gid(ids, "torso-art")}>'
            f'<path d="M222 316 C231 299 266 293 284 293 L316 293 C334 293 369 299 378 316 L382 498 '
            f'C382 509 377 517 367 517 L233 517 C223 517 218 509 218 498 Z" fill="{b}"/>'
            f'<path d="M218 494 L382 494 L382 498 C382 509 377 517 367 517 L233 517 C223 517 218 509 218 498 Z" fill="{h}"/>'
            f'<path d="M232 318 C236 400 236 450 237 492 M368 318 C364 400 364 450 363 492" stroke="{d}" stroke-width="2" opacity=".0" fill="none"/>'
            f'</g>')


def neck_svg(ids=True):
    return (f'<g{gid(ids, "neck")}>'
            f'<path d="M278 224 L322 224 L322 297 C312 314 288 314 278 297 Z" fill="{C["skin"]}"/>'
            f'<path d="M268 296 C282 324 318 324 332 296" stroke="{C["blue_dk"]}" stroke-width="3.4" stroke-linecap="round" fill="none"/>'
            f'</g>')


def brow(cx, cy, y, r, c, side):
    rr = -r if side == 'R' else r
    return (f'<g transform="translate({f(cx)} {f(cy + y)}) {rot(rr)}">'
            f'<path d="M-11.5 1.5 Q0 {f(1.5 - 2 * c)} 11.5 1.5" stroke="{C["hair"]}" stroke-width="3.2" '
            f'stroke-linecap="round" fill="none"/></g>')


def eye(cx, cy, o, arc, gx, gy):
    ex, ey = cx + gx * 3.6, cy + gy * 2.8
    if o < 0.22:
        if arc >= 0:   # happy ^
            return (f'<path d="M{f(cx - 8)} {f(cy + 3)} Q{f(cx)} {f(cy - 9)} {f(cx + 8)} {f(cy + 3)}" '
                    f'stroke="{C["hair"]}" stroke-width="3.4" stroke-linecap="round" fill="none"/>')
        return (f'<path d="M{f(cx - 8)} {f(cy - 1.5)} Q{f(cx)} {f(cy + 6)} {f(cx + 8)} {f(cy - 1.5)}" '
                f'stroke="{C["hair"]}" stroke-width="3.2" stroke-linecap="round" fill="none"/>')
    return f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="5.4" ry="{f(5.7 * min(o, 1.25))}" fill="{C["hair"]}"/>'


def mouth_svg(p, ids=True):
    w, op, sm, sk = p['m_w'], p['m_open'], p['m_smile'], p['m_skew']
    mx, my = 300 + p['m_x'], 223 + p['m_y']
    yl, yr = my - sm * 4 + sk * 3, my - sm * 4 - sk * 3
    cl, cr = (mx - w / 2, yl), (mx + w / 2, yr)
    cy_ctrl = my + sm * 14 + (sk * 0)
    if op < 1.6:
        return (f'<path d="M{f(cl[0])} {f(cl[1])} Q{f(mx)} {f(cy_ctrl)} {f(cr[0])} {f(cr[1])}" '
                f'stroke="{C["mouth_ln"]}" stroke-width="3.6" stroke-linecap="round" fill="none"/>')
    depth = op * 1.6
    path = (f'M{f(cl[0])} {f(cl[1])} Q{f(mx)} {f(cy_ctrl - 6 * sm * 0.3)} {f(cr[0])} {f(cr[1])} '
            f'C{f(cr[0])} {f(cr[1] + depth)} {f(cl[0])} {f(cl[1] + depth)} {f(cl[0])} {f(cl[1])} Z')
    tongue = ''
    if op > 7 and w > 16:
        ty = (cl[1] + cr[1]) / 2 + op * 0.78
        tongue = (f'<ellipse cx="{f(mx)}" cy="{f(ty)}" rx="{f(w * 0.24)}" ry="{f(min(op * 0.2, 5.5))}" fill="{C["tongue"]}"/>')
    return (f'<path d="{path}" fill="{C["mouth_in"]}" stroke="{C["mouth_in"]}" stroke-width="1.6" stroke-linejoin="round"/>' + tongue)


def features_svg(p, ids=True):
    cxr, cxl, ey = 323.5, 276.5, 192
    parts = [
        brow(cxl, 178, p['bL_y'], p['bL_r'], p['bL_c'], 'L'),
        brow(cxr, 178, p['bR_y'], p['bR_r'], p['bR_c'], 'R'),
        eye(cxl, ey, p['eL_o'], p['eL_arc'], p['gx'], p['gy']),
        eye(cxr, ey, p['eR_o'], p['eR_arc'], p['gx'], p['gy']),
        f'<path d="M299 199 C295 204.5 296.5 210 302 209" stroke="{C["skin_dk"]}" stroke-width="2.6" stroke-linecap="round" fill="none"/>',
    ]
    if p['blush'] > 0.01:
        a = f(min(1, p['blush']) * 0.55)
        parts.append(f'<ellipse cx="266" cy="213" rx="10" ry="5.5" fill="{C["skin_dk"]}" opacity="{a}"/>'
                     f'<ellipse cx="334" cy="213" rx="10" ry="5.5" fill="{C["skin_dk"]}" opacity="{a}"/>')
    parts.append(mouth_svg(p, ids))
    if p['mask'] > 0.5:
        parts.append(f'<path d="M247 199 Q300 190 353 199 L347 232 Q300 254 253 232 Z" fill="{C["mask"]}"/>'
                     f'<path d="M256 211 Q300 220 344 211 M255 222 Q300 232 345 222" stroke="{C["mask_ln"]}" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
                     f'<path d="M247 199 Q238 195 236 188 M353 199 Q362 195 364 188" stroke="{C["mask"]}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    return f'<g{gid(ids, "face")} transform="translate({f(p["face_x"])} {f(p["face_y"])})">{"".join(parts)}</g>'


def cap_svg(p, ids=True):
    c, dk, hi = C['cap'], C['cap_dk'], C['cap_hi']
    if not p['cap_on']:
        return '', ''
    visor = (f'<path{gid(ids, "cap-visor")} d="M350 116 C376 118 400 140 409 170 C390 174 364 166 346 152 Z" fill="{dk}"/>'
             f'<path d="M352 124 C372 128 392 142 400 160" stroke="{c}" stroke-width="2" fill="none" opacity=".5"/>')
    crown = (f'<g{gid(ids, "cap")} transform="translate({f(CAP_PIV[0])} {f(CAP_PIV[1] + p["cap_dy"])}) {rot(p["cap_rot"])} translate({-CAP_PIV[0]} {-CAP_PIV[1]})">'
             f'<path d="M234 141 C226 98 262 64 300 64 C338 64 374 98 366 141 Q300 152 234 141 Z" fill="{c}"/>'
             f'<path d="M330 68 C352 84 370 112 366 141 Q350 146 336 146 C343 120 341 92 330 68 Z" fill="{dk}"/>'
             f'<circle cx="300" cy="64.5" r="5.4" fill="{c}"/>'
             f'<path d="M279 134 A21 23 0 0 1 321 134 Z" fill="{C["cap_hole"]}"/>'
             f'<path d="M277 134 L323 134 L322 143 Q300 147 278 143 Z" fill="{hi}"/>'
             f'<g fill="{C["cap_dot"]}"><circle cx="287" cy="139" r="1.6"/><circle cx="295" cy="139.5" r="1.6"/>'
             f'<circle cx="303" cy="139.5" r="1.6"/><circle cx="311" cy="139" r="1.6"/></g>'
             f'</g>')
    return visor, crown


def head_svg(p, ids=True):
    hr = C['hair']
    visor, crown = cap_svg(p, ids)
    back_hair = (f'<path{gid(ids, "hair-back")} d="M231 172 C231 204 242 228 262 239 L338 239 C358 228 369 204 369 172 '
                 f'C369 110 340 76 300 76 C260 76 231 110 231 172 Z" fill="{hr}"/>')
    ears = ''.join(
        f'<ellipse{gid(ids, "ear-" + ("L" if cx < 300 else "R"))} cx="{cx}" cy="190" rx="14.5" ry="19.5" fill="{C["skin"]}"/>'
        f'<path d="M{cx + s * 3} 182 Q{cx - s * 4} 188 {cx + s * 1} 199" stroke="{C["ear_in"]}" stroke-width="2.4" stroke-linecap="round" fill="none"/>'
        for cx, s in ((238, -1), (362, 1)))
    ears_pre = ''
    face = (f'<path{gid(ids, "face-base")} d="M240 166 C240 134 264 118 300 118 C336 118 360 134 360 166 L360 192 '
            f'C360 227 334 246 300 246 C266 246 240 227 240 192 Z" fill="{C["skin"]}"/>')
    chin_sh = f'<path d="M278 236 Q300 262 322 236 L322 252 Q300 270 278 252 Z" fill="{C["skin_sh"]}"/>'
    fringe = (f'<path{gid(ids, "hair-fringe")} d="M229 184 C222 120 250 76 300 76 C350 76 378 120 371 184 L358 176 L355 162 '
              f'L345 151 L335 169 L325 148 L313 167 L301 145 L289 165 L277 146 L266 167 L255 151 L246 162 L244 176 Z" fill="{hr}"/>')
    sweat = ''
    if p['sweat'] > 0.05:
        s = p['sweat']
        sweat = (f'<path d="M352 {f(150 + 14 * s)} C347 {f(160 + 14 * s)} 344 {f(168 + 14 * s)} 352 {f(172 + 14 * s)} '
                 f'C360 {f(168 + 14 * s)} 357 {f(160 + 14 * s)} 352 {f(150 + 14 * s)} Z" fill="{C["sweat"]}" opacity="{f(min(1, s * 1.5))}"/>')
    return (f'<g{gid(ids, "head")} data-pivot="{NECK[0]},{NECK[1]}" transform="{rot(p["head"], *NECK)} translate(0 18) translate(300 296) scale(1.12) translate(-300 -296)">'
            f'{visor}{back_hair}{chin_sh}{face}{features_svg(p, ids)}{ears_pre}{fringe}{ears}{crown}{sweat}</g>')


# ======================= ASSEMBLY ===========================================
def pelvis_svg(ids=True):
    return (f'<path{gid(ids, "pelvis")} d="M206 480 L394 480 L394 548 C394 566 206 566 206 548 Z" fill="{C["pants"]}"/>'
            f'<path d="M232 524 C240 534 244 548 246 560 M368 524 C360 534 356 548 354 560" stroke="{C["pants_ln"]}" '
            f'stroke-width="2.2" stroke-linecap="round" fill="none"/>')


def character_svg(pose=None, ids=True):
    p = dict(DEFAULT)
    if pose:
        p.update(pose)
    br = 1 + p['breath']
    ty = -p['shrug']
    torso = (f'<g{gid(ids, "torso")} data-pivot="{WAIST[0]},{WAIST[1]}" '
             f'transform="{rot(p["torso"], *WAIST)} translate({WAIST[0]} {WAIST[1]}) scale(1 {f(br)}) translate({-WAIST[0]} {-WAIST[1]})">'
             f'{torso_body(ids)}{neck_svg(ids)}{LOGO}'
             f'{head_svg(p, ids)}'
             f'{arm_svg("R", p, ids)}{arm_svg("L", p, ids)}</g>')
    legs = leg_svg('R', p, ids) + leg_svg('L', p, ids)
    return (f'<g{gid(ids, "root")} transform="translate({f(p["root_x"])} {f(p["root_y"])})">'
            f'{pelvis_svg(ids)}{legs}{torso}</g>')


def svg_doc(pose=None, ids=True, bg=None, view=(0, 0, W, H), size=None, extra='', title='Ucup'):
    vx, vy, vw, vh = view
    w, h = size or (vw, vh)
    bgr = f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {vw} {vh}" width="{w}" height="{h}">'
            f'<title>{title}</title>{bgr}{extra}{character_svg(pose, ids)}</svg>')
