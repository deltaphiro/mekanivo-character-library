import os as _o
HERE = _o.path.dirname(_o.path.abspath(__file__))
import sys, os, io, json, math, shutil, subprocess, html
sys.path.insert(0, HERE)
import numpy as np, cairosvg
import gait, ucup_side as S, ucup_rig4 as R4, walk_front as WF, ucup_anim as A
from PIL import Image, ImageDraw, ImageFont
OUT = os.environ.get('UCUP_OUT', os.path.join(HERE, '..', 'rebuilt')); PV = OUT + '/preview'; os.makedirs(PV, exist_ok=True)
BG = '#F4F1EA'; FPS = 30; CYCLES = 4
def font(sz, b=False): return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if b else ''), sz)
FB, FS, FT = font(15, True), font(13), font(20, True)
SIDE_VIEW = (110, 0, 380, 900); FRONT_VIEW = (60, 0, 480, 900)
def png(svg, scale=1.0, w=None):
    cairosvg.svg2png(bytestring=svg.encode(), write_to='/tmp/_w.png', scale=scale) if w is None else cairosvg.svg2png(bytestring=svg.encode(), write_to='/tmp/_w.png', output_width=w)
    return Image.open('/tmp/_w.png').convert('RGBA').copy()
rep = {}
# ------------------------------------------------ 1. verification: rendered rig == IK intent (markers) + foot slide
S.DEBUG = True
rows = []; N = 60
def expected(g):
    a = g['A']; au, av, al = a['ankle_u'], a['ankle_v'], a['foot']
    hu = gait._R(al, *gait.HEEL); bu = gait._R(al, *gait.BALL)
    return dict(ankle=(300 - au, av), heel=(300 - (au + hu[0]), av + hu[1]), ball=(300 - (au + bu[0]), av + bu[1]))
def find(img, rgb, tol=40):
    a = np.array(img.convert('RGB')).astype(int)
    m = (abs(a[:, :, 0] - rgb[0]) < tol) & (abs(a[:, :, 1] - rgb[1]) < tol) & (abs(a[:, :, 2] - rgb[2]) < tol)
    ys, xs = np.where(m)
    return (xs.mean(), ys.mean()) if len(xs) else None
meas = []
for i in range(N):
    t = i / N * gait.T; g = gait.state(t)
    im = png(S.svg_side(S.pose_from_gait(g), ids=False, bg='#FFFFFF', view=(0, 0, 600, 900)), scale=2)
    ex = expected(g)
    got = {k: find(im, c) for k, c in (('ankle', (255, 0, 255)), ('heel', (0, 255, 0)), ('ball', (0, 255, 255)))}
    meas.append((g['A']['ph'], got, ex))
S.DEBUG = False
err = []
for ph, got, ex in meas:
    for k in ('ankle', 'heel', 'ball'):
        if got[k] is None: continue
        gx, gy = got[k][0] / 2, got[k][1] / 2
        err.append(math.hypot(gx - ex[k][0], gy - ex[k][1]))
rep['rig_vs_ik_marker_error_px'] = {'max': round(max(err), 2), 'mean': round(float(np.mean(err)), 2), 'samples': len(err)}
slide = []
dt = gait.T / N; expect_dx = gait.V * dt
for j in range(1, N):
    ph0, g0, _ = meas[j - 1]; ph1, g1, _ = meas[j]
    if ph1 < gait.PH_HEELOFF and ph0 < gait.PH_HEELOFF and g0['heel'] and g1['heel']:
        slide.append(abs((g1['heel'][0] - g0['heel'][0]) / 2 - expect_dx))
    elif gait.PH_HEELOFF + 0.02 < ph0 and ph1 < gait.STANCE and g0['ball'] and g1['ball']:
        slide.append(abs((g1['ball'][0] - g0['ball'][0]) / 2 - expect_dx))
rep['foot_slide_px_per_frame(60/cycle) vs expected %.2f' % expect_dx] = {'max': round(max(slide), 2), 'mean': round(float(np.mean(slide)), 2), 'stance_samples': len(slide)}
# ------------------------------------------------ 2. front/side consistency (same gait -> same vertical foot/hip positions)
dA, dB, dH = [], [], []; curves = {'ph': [], 'gait': [], 'side': [], 'front': [], 'hip': []}
for i in range(200):
    t = i / 200 * gait.T; g = gait.state(t)
    L, ry = R4.solve_legs(dict(R4.DEFAULT, **WF.front_pose(g)))
    fA, fB = L['R']['ankle'][1] + ry, L['L']['ankle'][1] + ry
    sA = 502 + (g['hip_y'] - 502) + gait.L1 * math.cos(math.radians(g['A']['th1'])) + gait.L2 * math.cos(math.radians(g['A']['th2']))
    dA.append(abs(fA - g['A']['ankle_v'])); dB.append(abs(fB - g['B']['ankle_v'])); dH.append(abs(502 + ry - g['hip_y']))
    curves['ph'].append(g['phase']); curves['gait'].append(g['A']['ankle_v']); curves['side'].append(sA); curves['front'].append(fA); curves['hip'].append(g['hip_y'])
rep['front_vs_side_ankle_y_error_px'] = {'legA_max': round(max(dA), 3), 'legB_max': round(max(dB), 3), 'hip_y_max': round(max(dH), 3)}
mg = [min(gait.state(i / 400)['A']['margin'], gait.state(i / 400)['B']['margin']) for i in range(400)]
rep['gait'] = {'cycle_s': gait.T, 'stance_fraction': gait.STANCE, 'step_px': gait.V * gait.T / 2, 'stride_px': gait.V * gait.T, 'ground_speed_px_s': gait.V,
               'min_leg_reach_margin_px': round(min(mg), 2),
               'knee_flex_deg': [round(min(gait.state(i / 400)['A']['knee'] for i in range(400)), 1), round(max(gait.state(i / 400)['A']['knee'] for i in range(400)), 1)],
               'hip_bob_px': round(max(c for c in curves['hip']) - min(curves['hip']), 1),
               'loop_closure_pose_diff_max': round(max(abs(a - b) for a, b in zip(S.pose_from_gait(gait.state(0)).values() if False else [0], [0])), 3)}
p0, p1 = S.pose_from_gait(gait.state(0.0)), S.pose_from_gait(gait.state(gait.T - 1e-9))
rep['gait']['loop_closure_pose_diff_max'] = round(max(abs(p0[k] - p1[k]) for k in p0 if isinstance(p0[k], (int, float))), 4)
# ------------------------------------------------ 3. frames + videos
def ground_side(t):
    sp = 70; off = (gait.V * t) % sp; ticks = ''.join(f'<rect x="{x - 2:.1f}" y="872" width="4" height="14" fill="#D6CDB9"/>' for x in np.arange(60 - sp + off, 560, sp))
    return f'<rect x="0" y="866" width="600" height="40" fill="#E9E3D6"/>{ticks}<ellipse cx="300" cy="866" rx="120" ry="9" fill="#000" opacity=".12"/>'
def ground_front(t):
    return '<rect x="0" y="866" width="600" height="40" fill="#E9E3D6"/><ellipse cx="300" cy="868" rx="125" ry="10" fill="#000" opacity=".12"/>'
n = CYCLES * int(gait.T * FPS)
exprs = A.expr_full('happy')
def banner(im, txt):
    d = ImageDraw.Draw(im); d.rectangle([0, 0, im.width, 40], fill='#1A3A9C'); d.text((14, 10), txt, font=FB, fill='white')
frames = []
for i in range(n):
    t = i / FPS; g = gait.state(t)
    sv = png(S.svg_side(S.pose_from_gait(g, A.expr_full('neutral')), ids=False, bg=BG, view=SIDE_VIEW, extra=ground_side(t)), 1.0)
    fp = WF.front_pose(g, {k: v for k, v in A.expr_full('neutral').items() if k in ('bR_y','bR_r','bL_y','bL_r','eR_o','eL_o','m_w','m_open','m_smile','m_skew','gx','gy')})
    fv = png(R4.svg_doc(fp, ids=False, bg=BG, view=FRONT_VIEW, extra=ground_front(t)), 1.0)
    frames.append((sv.convert('RGB'), fv.convert('RGB'), g))
def video(name, make):
    d = f'/tmp/fr_{name}'; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    for i, fr in enumerate(frames): make(fr, i).save(f'{d}/f{i:04d}.png')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{d}/f%04d.png', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', f'{PV}/{name}.mp4'], check=True)
def mk_side(fr, i):
    sv, fv, g = fr; im = Image.new('RGB', (sv.width, sv.height + 40 + 40), BG); im.paste(sv, (0, 40)); banner(im, 'UCUP side walk · loop 1.0s'); d = ImageDraw.Draw(im)
    d.text((12, sv.height + 50), f'phase {g["phase"]:.2f}   hip y {g["hip_y"]:.1f}', font=FS, fill='#1A3A9C'); return im
def mk_front(fr, i):
    sv, fv, g = fr; im = Image.new('RGB', (fv.width, fv.height + 80), BG); im.paste(fv, (0, 40)); banner(im, 'UCUP front walk · same gait · loop 1.0s'); d = ImageDraw.Draw(im)
    d.text((12, fv.height + 50), f'phase {g["phase"]:.2f}   hip y {g["hip_y"]:.1f}', font=FS, fill='#1A3A9C'); return im
def mk_sync(fr, i):
    sv, fv, g = fr; im = Image.new('RGB', (sv.width + fv.width + 10, sv.height + 120), BG); im.paste(sv, (0, 40)); im.paste(fv, (sv.width + 10, 40)); banner(im, 'UCUP walk · SIDE (left) and FRONT (right) driven by ONE gait · same phase'); d = ImageDraw.Draw(im)
    a, b = g['A'], g['B']
    d.text((12, sv.height + 50), f'phase {g["phase"]:.3f}   hip y {g["hip_y"]:.1f}   leg A ankle y {a["ankle_v"]:.1f} ({"stance" if a["stance"] else "swing"})   leg B ankle y {b["ankle_v"]:.1f} ({"stance" if b["stance"] else "swing"})', font=FS, fill='#1A3A9C')
    d.text((12, sv.height + 76), f'side: thigh {a["th1"]:.0f}° knee {a["knee"]:.0f}° foot {a["foot"]:.0f}°   front: thigh scale {math.cos(math.radians(a["th1"])):.2f} shank scale {math.cos(math.radians(a["th2"])):.2f}', font=FS, fill='#555'); return im
video('walk_side', mk_side); video('walk_front', mk_front); video('walk_sync_side_front', mk_sync)
# ------------------------------------------------ 4. cycle sheet (8 phases, side over front)
labels = ['A heel strike', 'A loading', 'A mid-stance (B swing)', 'A late stance', 'B heel strike', 'B loading', 'B mid-stance (A swing)', 'A late swing']
cells = []
for k, ph in enumerate([0, .125, .25, .375, .5, .625, .75, .875]):
    g = gait.state(ph * gait.T)
    s_ = png(S.svg_side(S.pose_from_gait(g), ids=False, bg=BG, view=SIDE_VIEW), 0.62).convert('RGB')
    f_ = png(R4.svg_doc(WF.front_pose(g), ids=False, bg=BG, view=FRONT_VIEW), 0.62).convert('RGB')
    cells.append((s_, f_, ph, labels[k], g))
cw = max(cells[0][0].width, cells[0][1].width) + 12; sh = Image.new('RGB', (8 * cw, 40 + cells[0][0].height + cells[0][1].height + 70), BG); d = ImageDraw.Draw(sh)
d.rectangle([0, 0, sh.width, 36], fill='#1A3A9C'); d.text((14, 9), 'Walk cycle — 8 key phases. Top: SIDE rig · Bottom: FRONT rig · both from the same gait state', font=FB, fill='white')
for i, (s_, f_, ph, lab, g) in enumerate(cells):
    x = i * cw; sh.paste(s_, (x + (cw - s_.width) // 2, 40)); sh.paste(f_, (x + (cw - f_.width) // 2, 40 + s_.height + 6))
    d.text((x + 6, 40 + s_.height + f_.height + 10), f'φ={ph:.3f} {lab}', font=FS, fill='#1A3A9C'); d.text((x + 6, 40 + s_.height + f_.height + 30), f'hip y {g["hip_y"]:.1f}  A {g["A"]["ankle_v"]:.0f}  B {g["B"]["ankle_v"]:.0f}', font=FS, fill='#555')
sh.save(PV + '/walk_cycle_sheet.png')
# ------------------------------------------------ 5. consistency plot
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(1, 2, figsize=(13, 4.2))
ph = np.array(curves['ph']); o = np.argsort(ph)
ax[0].plot(ph[o], np.array(curves['gait'])[o], lw=5, alpha=.35, label='gait target'); ax[0].plot(ph[o], np.array(curves['side'])[o], '--', lw=2, label='side rig (FK from angles)'); ax[0].plot(ph[o], np.array(curves['front'])[o], ':', lw=2.5, label='front rig (solve_legs)')
ax[0].invert_yaxis(); ax[0].set_title('Leg A ankle height over the cycle (screen y, lower = higher foot)'); ax[0].set_xlabel('phase'); ax[0].legend(); ax[0].grid(alpha=.3)
ax[1].plot(ph[o], np.array(curves['hip'])[o], lw=2); ax[1].invert_yaxis(); ax[1].set_title('Hip height (bob) shared by both views'); ax[1].set_xlabel('phase'); ax[1].grid(alpha=.3)
fig.suptitle(f"front-vs-side ankle y error: leg A max {rep['front_vs_side_ankle_y_error_px']['legA_max']} px, leg B max {rep['front_vs_side_ankle_y_error_px']['legB_max']} px", fontsize=11)
fig.tight_layout(); fig.savefig(PV + '/consistency_front_vs_side.png', dpi=110); plt.close(fig)
# ------------------------------------------------ 6. side expressions (profile face reuses the front expression library)
names = ['neutral', 'happy', 'surprised', 'sad', 'curious', 'smirk', 'laugh', 'worried']
cells = []
for nme in names:
    p = A.expr_full(nme); im = png(S.svg_side(p, ids=False, bg=BG, view=(205, 25, 240, 300)), 1.0).convert('RGB'); cells.append((im, nme))
cap_off = png(S.svg_side(dict(A.expr_full('neutral'), cap_on=0), ids=False, bg=BG, view=(205, 25, 240, 300)), 1.0).convert('RGB'); cells.append((cap_off, 'cap off (bowl cut)'))
w, h = cells[0][0].size; sh = Image.new('RGB', (5 * w, 2 * (h + 26) + 40), BG); d = ImageDraw.Draw(sh)
d.rectangle([0, 0, sh.width, 34], fill='#1A3A9C'); d.text((14, 8), 'Side-view face: same expression parameters as the front rig, drawn in profile', font=FB, fill='white')
for i, (im, nme) in enumerate(cells): x, y = (i % 5) * w, (i // 5) * (h + 26) + 40; sh.paste(im, (x, y)); d.text((x + 6, y + h + 3), nme, font=FB, fill='#1A3A9C')
sh.save(PV + '/side_expressions_sheet.png')
# ------------------------------------------------ 7. side rig sheet with skeleton + mapping table
sx, sy = S.SHOULDER; pts = [('head/neck', (300, 296)), ('cap', (300, 112)), ('chest/waist', (300, 470)), ('shoulder', (300, 326)), ('hip', (300, 502)), ('knee', (300, 675)), ('ankle', (300, 827))]
ov = ''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="#D8213F" stroke="#fff" stroke-width="2"/><text x="{x + 160 if False else 340}" y="{y + 5}" font-family="DejaVu Sans" font-size="15" fill="#1A3A9C">{nm}</text>' for nm, (x, y) in pts)
lines = ['SHARED DIMENSIONS (side = front)', 'hip y 502 · knee y 675 · ankle y 827 · ground 860 · shoulder y 326', 'thigh 173 · shank 152 · upper arm 100 · forearm 108 · head x1.12, seat +32', '',
         'ONE GAIT DRIVER  (gait.py, sagittal plane)', 'leg A = near leg (side) = screen-RIGHT leg (front)', 'leg B = far leg (side) = screen-LEFT leg (front)', 'arm A: same side as leg A, opposite phase', '',
         'SIDE rig  <-  gait', 'N_hip = thigh θ1 · N_knee = flex k · N_foot = pitch α', 'N_arm / N_elbow · root_y = hip_y - 502 · lean · head', 'angles drawn directly (true profile)', '',
         'FRONT rig  <-  same gait', 'thigh scale = cos θ1 · shank scale = cos θ2', 'ry = hip_y - 502 · hip tilt · root_x sway · twist', 'arm foreshortening R_fwd/L_fwd = 1 - cos(arm angle)', 'front is a PROJECTION of the same skeleton', '',
         'IDENTICAL BY CONSTRUCTION: ankle y, hip y, phase, loop', 'verified numerically: see validation report']
tx = ''.join(f'<text x="560" y="{70 + i * 27}" font-family="DejaVu Sans" font-size="{17 if (l.isupper() or l.startswith(("SHARED","ONE","SIDE rig","FRONT rig","IDENT"))) else 15}" font-weight="{700 if l.startswith(("SHARED","ONE","SIDE rig","FRONT rig","IDENT")) else 400}" fill="#1A3A9C">{html.escape(l)}</text>' for i, l in enumerate(lines))
svg = S.svg_side({}, ids=False, bg=BG, view=(0, 0, 1180, 900), extra=''); svg = svg.replace('</svg>', ov + tx + '</svg>')
png(svg, 1.0).convert('RGB').save(PV + '/side_rig_sheet.png')
json.dump(rep, open(os.path.join(HERE, 'metrics_walk.json'), 'w'), indent=1)
print(json.dumps(rep, indent=1))
