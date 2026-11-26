"""
UCUP side-view rig (profile, facing screen-LEFT like the reference sheet; facing='R' mirrors it).
Same skeleton dimensions, joint heights, palette and parameter semantics as the front rig (ucup_rig3).
Authoring frame: x=300 centre line, ground y=860, y down.  Forward = -x.
Angles (deg): limbs hanging from a pivot: forward-positive == SVG-positive rotation.
              torso/head (parts ABOVE their pivot): forward-positive == SVG-negative rotation.
              foot pitch: toe-up positive == SVG-positive rotation.
Legs are driven by IK targets from gait.py; the rig itself takes plain joint angles.
"""
import math
from ucup_rig import C, f, rot, gid
import ucup_rig3 as R3
from ucup_rig3 import NECK, CAP_PIV, HEAD_DY, THIGH, SHIN, UPPER, FORE, W, H

DEBUG = False
SHOULDER = (300, 326)
HIP = (300, 502)
CHEST_P, HEM_P = (300, 470), (300, 517)

SIDE_DEFAULT = dict(
    root_x=0, root_y=0, lean=0, head=0, cap_on=1,
    N_hip=0, N_knee=0, N_foot=0, F_hip=0, F_knee=0, F_foot=0,
    N_arm=-3, N_elbow=14, N_wrist=0, F_arm=-3, F_elbow=14, F_wrist=0,
    N_hand='relaxed', F_hand='relaxed',
    # face (same names/semantics as the front rig; profile shows one eye -> averages)
    bR_y=0, bR_r=0, bR_c=2.5, bL_y=0, bL_r=0, bL_c=2.5, eR_o=1, eL_o=1, eR_arc=-1, eL_arc=-1, gx=0, gy=0,
    m_w=26, m_open=0, m_smile=1.0, m_skew=0, m_x=0, m_y=0, blush=0, sweat=0,
)

def shade(hexcol, k):
    h = hexcol.lstrip('#'); r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02X%02X%02X' % (int(r * k), int(g * k), int(b * k))

# ---------------------------------------------------------------- hand (side)
def hand_side(state, far=False):
    s = shade(C['skin'], .90) if far else C['skin']; d = C['skin_dk']
    if state == 'relaxed':
        return (f'<path d="M-15 -4 C-20 12 -20 32 -14 48 C-6 62 10 62 16 50 C20 30 18 10 14 -4 Z" fill="{s}"/>'
                f'<path d="M-14 4 C-24 12 -27 26 -22 36" stroke="{s}" stroke-width="10.5" stroke-linecap="round" fill="none"/>'
                f'<path d="M-2 40 L-4 57 M5 39 L5 58 M11 38 L12 55" stroke="{d}" stroke-width="2.2" stroke-linecap="round" fill="none"/>')
    if state == 'fist':
        return (f'<path d="M-15 -4 C-19 12 -18 30 -14 40 C-6 48 8 48 15 40 C19 28 18 10 14 -4 Z" fill="{s}"/>'
                f'<path d="M-14 8 C-22 14 -22 26 -14 30" stroke="{s}" stroke-width="10" stroke-linecap="round" fill="none"/>'
                f'<path d="M-4 38 L-4 46 M4 38 L4 46 M10 36 L10 44" stroke="{d}" stroke-width="2" stroke-linecap="round" fill="none"/>')
    raise ValueError(state)

# ---------------------------------------------------------------- arm (side)
def arm_side(k, p, far, ids):
    sx, sy = SHOULDER; sx += 4 if far else 0
    a, e, w = p[f'{k}_arm'], p[f'{k}_elbow'], p[f'{k}_wrist']
    b = shade(C['blue'], .84) if far else C['blue']; dk = C['blue_dk']
    hand = hand_side(p[f'{k}_hand'], far)
    return (f'<g{gid(ids, "arm-" + k)} data-pivot="{sx},{sy}" transform="translate({sx} {sy}) {rot(a)}">'
            f'<circle r="25" fill="{b}"/>'
            f'<path d="M-25 0 C-27 34 -27 70 -25 {UPPER} L25 {UPPER} C27 70 27 34 25 0 Z" fill="{b}"/>'
            f'<circle cy="{UPPER}" r="26.5" fill="{b}"/>'
            + ('' if far else f'<path d="M-21 8 C-23 46 -23 78 -21 {UPPER - 4}" stroke="{dk}" stroke-width="2.6" stroke-linecap="round" fill="none"/>') +
            f'<g{gid(ids, "forearm-" + k)} data-pivot="elbow" transform="translate(0 {UPPER}) {rot(e)}">'
            f'<circle r="26.5" fill="{b}"/>'
            f'<g{gid(ids, "hand-" + k)} data-pivot="wrist" transform="translate(0 {FORE - 14}) {rot(w)} scale(1.25)">'
            f'<rect x="-9" y="-22" width="18" height="28" fill="{shade(C["skin"], .9) if far else C["skin"]}"/>{hand}</g>'
            f'<path d="M-26 0 L26 0 C27 40 24 82 21 {FORE - 6} L19 {FORE - 1} A19 5 0 0 1 -19 {FORE - 1} L-21 {FORE - 6} C-24 82 -27 40 -26 0 Z" fill="{b}"/>'
            f'<path d="M-19 {FORE - 1} A19 5 0 0 0 19 {FORE - 1}" stroke="{dk}" stroke-width="2.2" fill="none" opacity=".7"/>'
            + ('' if far else f'<path d="M-21 8 C-23 40 -23 78 -21 {FORE - 8}" stroke="{dk}" stroke-width="2.4" stroke-linecap="round" fill="none"/>') +
            f'</g></g>')

# ---------------------------------------------------------------- leg (side)
def leg_side(k, p, far, ids):
    th1, kn, al = p[f'{k}_hip'], p[f'{k}_knee'], p[f'{k}_foot']
    th2 = th1 - kn
    pa = shade(C['pants'], .88) if far else C['pants']; pl = C['pants_ln']
    shoe_c = shade(C['shoe'], .80) if far else C['shoe']
    hx, hy = HIP[0] + (2 if far else 0), HIP[1]
    shoe = (f'<g{gid(ids, "foot-" + k)} data-pivot="ankle" transform="translate(0 {SHIN}) {rot(al - th2)}">'
            f'<path d="M36 -6 C38 6 38 22 36 33 L-52 33 C-66 33 -72 26 -66 18 C-60 6 -40 2 -28 -4 Z" fill="{shoe_c}"/>'
            f'<path d="M-70 28 C-72 35 -66 38 -52 38 L34 38 C38 38 38 32 36 29 Z" fill="{C["sole"]}"/>'
            f'<path d="M-30 4 L-14 12 M-24 -2 L-8 6 M-36 10 L-22 17" stroke="{C["lace"]}" stroke-width="2.8" stroke-linecap="round" fill="none"/>'
            f'<path d="M-64 24 C-52 26 -40 24 -30 20" stroke="{C["shoe_dk"]}" stroke-width="3" stroke-linecap="round" fill="none" opacity=".6"/>'
            + ('<circle cx="0" cy="0" r="3" fill="#FF00FF"/><circle cx="30" cy="33" r="3" fill="#00FF00"/><circle cx="-45" cy="33" r="3" fill="#00FFFF"/>' if (DEBUG and k == "N") else '') + '</g>')
    return (f'<g{gid(ids, "leg-" + k)} data-pivot="{hx},{hy}" transform="translate({hx} {hy}) {rot(th1)}">'
            f'<path d="M-37 8 Q-37 -8 -22 -8 L22 -8 Q37 -8 37 8 C38 60 36 118 35 {THIGH} L-35 {THIGH} C-36 118 -38 60 -37 8 Z" fill="{pa}"/>'
            f'<circle cy="{THIGH}" r="35.5" fill="{pa}"/>'
            f'<path d="M-32 6 C-33 60 -33 118 -32 {THIGH}" stroke="{pl}" stroke-width="2.2" stroke-linecap="round" fill="none" opacity=".8"/>'
            f'<g{gid(ids, "shin-" + k)} data-pivot="knee" transform="translate(0 {THIGH}) {rot(-kn)}">'
            f'<circle r="35.5" fill="{pa}"/>'
            f'<path d="M-35 -2 L35 -2 C34 40 34 100 36 {SHIN - 2} L-36 {SHIN - 2} C-34 100 -34 40 -35 -2 Z" fill="{pa}"/>'
            f'<path d="M-35 {SHIN - 14} L35 {SHIN - 14}" stroke="{pl}" stroke-width="2.2" opacity=".5"/>'
            f'{shoe}'
            f'<g transform="translate(0 {SHIN}) {rot(-th2)}"><path d="M-38 -8 L38 -8 L38.5 0 Q0 6 -38.5 0 Z" fill="{pa}"/></g>'
            f'</g></g>')

# ---------------------------------------------------------------- torso
CHEST_D = "M276 296 C264 300 254 310 251 324 C246 352 246 402 248 440 C249 466 250 484 252 494 L352 494 C355 470 357 440 357 400 C357 360 352 328 342 312 C336 302 326 296 324 296 Z"
CHEST = f'<path d="{CHEST_D}" fill="{C["blue"]}"/>'
ABDOMEN = (f'<path d="M255 492 L349 492 L348 504 C347 514 342 520 336 520 L266 520 C260 520 255 514 254 504 Z" fill="{C["hem"]}"/>'
           f'<path d="M250 455 L355 455 L356 496 C356 501 352 504 346 504 C322 507 282 507 258 504 C252 504 249 501 249 496 Z" fill="{C["blue"]}"/>')
def _logo_part():
    """the chest logo as seen from the side: the real logo clipped by the chest silhouette,
    so only its right part (right arch + dot) shows at the front edge, like the reference"""
    from ucup_logo import logo_group
    return (f'<defs><clipPath id="chestclip"><path d="{CHEST_D}"/></clipPath></defs>'
            + logo_group(242, 372, 60, gid='ucup-logo', clip='chestclip'))
LOGO_PART = _logo_part()

def neck_side(ids):
    return (f'<g{gid(ids, "neck")}><path d="M276 228 L332 224 L328 298 C314 309 292 309 280 298 Z" fill="{C["skin"]}"/>'
            f'<path d="M273 297 C286 316 320 316 333 297" stroke="{C["blue_dk"]}" stroke-width="4" stroke-linecap="round" fill="none"/></g>')

# ---------------------------------------------------------------- head (profile)
def face_features(p):
    bY = (p['bR_y'] + p['bL_y']) / 2; bR = (p['bR_r'] + p['bL_r']) / 2; bC = (p['bR_c'] + p['bL_c']) / 2
    o = (p['eR_o'] + p['eL_o']) / 2; arc = p['eL_arc']
    ex, ey = 263 + p['gx'] * -3.4, 192 + p['gy'] * 2.8
    hr = C['hair']
    if o < 0.22:
        eye = (f'<path d="M255 195 Q263 183 271 195" stroke="{hr}" stroke-width="3.4" stroke-linecap="round" fill="none"/>' if arc >= 0 else
               f'<path d="M255 190 Q263 198 271 190" stroke="{hr}" stroke-width="3.2" stroke-linecap="round" fill="none"/>')
    else:
        eye = f'<ellipse cx="{f(ex)}" cy="{f(ey)}" rx="5.2" ry="{f(5.8 * min(o, 1.25))}" fill="{hr}"/>'
    brow = (f'<g transform="translate(263 {f(177 + bY)}) {rot(-bR)}"><path d="M-10 2 Q0 {f(2 - 2 * bC)} 10 1" stroke="{hr}" '
            f'stroke-width="3.2" stroke-linecap="round" fill="none"/></g>')
    w, op, sm = p['m_w'] * 0.62, p['m_open'], p['m_smile']
    mx, my = 247 + p['m_x'] * 0.4, 225 + p['m_y']
    cx2, cy2 = mx + w, my - sm * 3.2 + p['m_skew'] * 2
    if op < 1.6:
        mouth = (f'<path d="M{f(mx)} {f(my)} Q{f(mx + w * .45)} {f(my + 4 + sm * 6)} {f(cx2)} {f(cy2)}" stroke="{C["mouth_ln"]}" '
                 f'stroke-width="3.5" stroke-linecap="round" fill="none"/>')
    else:
        d_ = op * 1.2
        mouth = (f'<path d="M{f(mx)} {f(my)} Q{f(mx + w * .5)} {f(my + 1)} {f(cx2)} {f(cy2)} C{f(cx2)} {f(cy2 + d_)} {f(mx + 2)} {f(my + d_)} {f(mx)} {f(my)} Z" '
                 f'fill="{C["mouth_in"]}" stroke="{C["mouth_in"]}" stroke-width="1.5" stroke-linejoin="round"/>')
    bl = ''
    if p['blush'] > .01:
        bl = f'<ellipse cx="281" cy="212" rx="10" ry="5.5" fill="{C["skin_dk"]}" opacity="{f(min(1, p["blush"]) * .55)}"/>'
    sw = ''
    if p['sweat'] > .05:
        s_ = p['sweat']
        sw = (f'<path d="M290 {f(146 + 14 * s_)} C285 {f(156 + 14 * s_)} 282 {f(164 + 14 * s_)} 290 {f(168 + 14 * s_)} '
              f'C298 {f(164 + 14 * s_)} 295 {f(156 + 14 * s_)} 290 {f(146 + 14 * s_)} Z" fill="{C["sweat"]}" opacity="{f(min(1, s_ * 1.5))}"/>')
    return bl + brow + eye + mouth + sw

def head_side(p, ids):
    hr, on = C['hair'], p['cap_on']
    cr = max(-1.0, min(1.0, p.get('cap_rot', 0))); cd = max(-1.0, min(1.0, p.get('cap_dy', 0)))
    cap_tf = f'translate(0 {f(cd)}) {rot(cr, *CAP_PIV)}'
    c, dk, hi = C['cap'], C['cap_dk'], C['cap_hi']
    skin = (f'<path{gid(ids, "face-base")} d="M254 124 C242 132 238 152 241 170 C242 178 241 186 243 190 C240 196 235 203 236 208 '
            f'C237 212 241 214 244 213 C243 218 244 222 246 225 C244 229 246 233 247 236 C246 242 253 248 266 247 '
            f'C292 245 322 236 338 214 C348 196 352 166 346 140 L330 120 Z" fill="{C["skin"]}"/>')
    chin_sh = f'<path d="M272 244 C288 254 310 250 328 232 L330 246 C312 262 288 264 272 254 Z" fill="{C["skin_sh"]}"/>'
    hair_back = (f'<path{gid(ids, "hair-back")} d="M262 136 C282 142 298 158 304 176 C306 186 308 196 308 204 L312 214 C316 226 326 236 336 240 '
                 f'C352 236 366 214 366 168 L366 140 Z" fill="{hr}"/>')
    ear = (f'<g{gid(ids, "ear")}><ellipse cx="318" cy="196" rx="11" ry="17" fill="{C["skin"]}"/>'
           f'<path d="M313 188 Q322 192 316 206" stroke="{C["ear_in"]}" stroke-width="2.4" stroke-linecap="round" fill="none"/></g>')
    bangs = f'<path{gid(ids, "hair-fringe")} d="M240 150 L254 145 L264 150 L260 162 L253 156 L246 164 Z" fill="{hr}"/>'
    if not on:
        hair_back = (f'<path{gid(ids, "hair-back")} d="M262 100 C284 78 340 74 362 120 C372 150 368 214 340 240 C326 236 316 226 312 214 '
                     f'L308 204 C308 190 306 176 300 162 C286 146 268 140 254 140 C250 120 252 108 262 100 Z" fill="{hr}"/>')
        bangs = (f'<path{gid(ids, "hair-fringe")} d="M240 160 C236 120 262 92 296 92 C330 92 354 112 358 146 L300 138 L270 150 L262 142 L254 154 L246 166 Z" fill="{hr}"/>')
    cap = visor = ''
    if on:
        cap = (f'<g{gid(ids, "cap")} transform="{cap_tf}">'
               f'<path d="M236 148 C228 104 262 62 304 62 C348 62 374 104 368 162 Q300 160 236 148 Z" fill="{c}"/>'
               f'<path d="M332 66 C354 82 372 116 368 162 L350 160 C356 120 348 92 332 66 Z" fill="{dk}"/>'
               f'<circle cx="304" cy="62.5" r="5.4" fill="{c}"/>'
               f'<path d="M236 148 C233 128 238 112 252 106 C259 118 259 134 257 150 Z" fill="{C["cap_hole"]}"/>'
               f'<path d="M236 131 L258 134 L258 143 L237 140 Z" fill="{hi}"/>'
               f'<g fill="{C["cap_dot"]}"><circle cx="242" cy="136" r="1.6"/><circle cx="249" cy="137.5" r="1.6"/><circle cx="255" cy="139" r="1.6"/></g>'
               f'<path d="M366 150 C384 154 404 164 410 174 C412 180 406 182 400 180 C386 176 372 170 364 164 Z" fill="{dk}"/></g>')
    return (f'<g{gid(ids, "head")} data-pivot="{NECK[0]},{NECK[1]}" transform="{rot(-p["head"], *NECK)} translate(0 {HEAD_DY}) '
            f'translate(300 296) scale(1.12) translate(-300 -296)">{chin_sh}{skin}{hair_back}{ear}{bangs}{face_features(p)}{cap}</g>')

# ---------------------------------------------------------------- assembly
def character_side(pose=None, ids=True):
    p = dict(SIDE_DEFAULT)
    if pose: p.update(pose)
    cp = CHEST_P
    chest_tf = f'{rot(-p["lean"], *cp)}'
    inv = f'{rot(p["lean"], *cp)}'
    abd_tf = f'{rot(-0.35 * p["lean"], *HEM_P)}'
    pelvis = f'<path{gid(ids, "pelvis")} d="M258 480 L346 480 L346 546 C346 562 258 562 258 546 Z" fill="{C["pants"]}"/>'
    legs = leg_side('F', p, True, ids) + leg_side('N', p, False, ids)
    chest = (f'<g{gid(ids, "torso")} data-pivot="{cp[0]},{cp[1]}" transform="{chest_tf}">'
             f'{arm_side("F", p, True, ids)}'
             f'<g transform="{inv}"><g{gid(ids, "abdomen")} transform="{abd_tf}">{ABDOMEN}</g></g>'
             f'<g{gid(ids, "chest-art")}>{CHEST}{LOGO_PART}</g>'
             f'{neck_side(ids)}{head_side(p, ids)}{arm_side("N", p, False, ids)}</g>')
    return f'<g{gid(ids, "root")} transform="translate({f(p["root_x"])} {f(p["root_y"])})">{pelvis}{legs}{chest}</g>'

def svg_side(pose=None, ids=True, bg=None, view=(0, 0, W, H), size=None, extra='', facing='L', title='Ucup side'):
    vx, vy, vw, vh = view; w, h = size or (vw, vh)
    body = character_side(pose, ids)
    if facing == 'R': body = f'<g transform="translate(600 0) scale(-1 1)">{body}</g>'
    bgr = f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" fill="{bg}"/>' if bg else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vx} {vy} {vw} {vh}" width="{w}" height="{h}">'
            f'<title>{title}</title>{bgr}{extra}{body}</svg>')

def pose_from_gait(g, expr=None):
    """sagittal gait state -> side rig pose dict"""
    p = dict(root_y=g['hip_y'] - 502.0, lean=g['lean'], head=g['head_pitch'])
    for side, nm in (('N', 'A'), ('F', 'B')):
        L = g[nm]
        p.update({f'{side}_hip': L['th1'], f'{side}_knee': L['knee'], f'{side}_foot': L['foot'],
                  f'{side}_arm': L['arm'], f'{side}_elbow': L['elbow'], f'{side}_wrist': L['wrist']})
    if expr: p.update(expr)
    return p
