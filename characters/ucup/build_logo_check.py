import os as _o
HERE = _o.path.dirname(_o.path.abspath(__file__))
import sys, os, json
sys.path.insert(0, HERE)
import numpy as np, cairosvg
import ucup_logo as L, ucup_rig3 as R3, ucup_side as S
from PIL import Image, ImageDraw, ImageFont
OUT = os.environ.get('UCUP_OUT', os.path.join(HERE, '..', 'rebuilt')); PV = OUT + '/preview'; os.makedirs(PV, exist_ok=True)
REF = os.path.join(HERE, 'reference', 'ucup_character_sheet.jpg')
def font(sz): return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', sz)
im = Image.open(REF).convert('RGB')
# --- measure reference logo (hero figure) and compare with the vector
c = im.crop((140, 235, 225, 290)).resize((850, 550), Image.LANCZOS); a = np.array(c).astype(int)
white = (a[:, :, 0] > 190) & (a[:, :, 1] > 190) & (a[:, :, 2] > 190); ys, xs = np.where(white); x0, y0 = xs.min(), ys.min(); W = xs.max() - x0 + 1
ref = white[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
refm = np.array(Image.fromarray((ref * 255).astype('uint8')).resize((505, 365), Image.LANCZOS)) > 127
def mask(p=L.P):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 505 365" width="505" height="365"><rect width="505" height="365" fill="#000"/><path d="{L.m_path(p)}" fill="#fff"/></svg>'
    cairosvg.svg2png(bytestring=svg.encode(), write_to='/tmp/_lm.png'); return np.array(Image.open('/tmp/_lm.png').convert('L')) > 127
mine = mask(); iou = float((mine & refm).sum() / (mine | refm).sum())
org = ((a[:, :, 0] - a[:, :, 2]) > 80) & (a[:, :, 0] > 170); oy, ox = np.where(org)
dot_ref = ((ox.mean() - x0) * 505 / W, (oy.mean() - y0) * 505 / W, ((ox.max() - ox.min() + 1) + (oy.max() - oy.min() + 1)) / 4 * 505 / W)
rep = {'m_shape_IoU_vs_reference': round(iou, 4), 'dot_reference(cx,cy,r)': [round(v, 1) for v in dot_ref], 'dot_vector(cx,cy,r)': [L.P['dot'][0], L.P['dot'][1], L.P['dr']],
       'logo_width_on_chest_units': 60, 'logo_aspect_w_over_h': round(L.LW / L.LH, 3)}
# --- comparison sheet
BG = '#2453BD'
def r(svg, w): cairosvg.svg2png(bytestring=svg.encode(), write_to='/tmp/_q.png', output_width=w); return Image.open('/tmp/_q.png').convert('RGB').copy()
old = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-30 -30 618 425"><rect x="-30" y="-30" width="618" height="425" fill="{BG}"/>'
       '<g transform="translate(28 -10) scale(5.8)"><path d="M5 38 V12 M5 22 C5 5 27 5 27 22 V38 M27 22 C27 5 49 5 49 22 V38" stroke="#fff" stroke-width="10.5" fill="none" stroke-linejoin="round"/><circle cx="60" cy="35" r="7.3" fill="#FA9112"/></g></svg>')
new = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-30 -30 625 425"><rect x="-30" y="-30" width="625" height="425" fill="{BG}"/>' + L.logo_group(282.5, 182.5, 565) + '</svg>'
t1 = im.crop((140, 235, 225, 290)).resize((560, 362), Image.LANCZOS); t2 = r(old, 560); t3 = r(new, 560)
ovl = np.zeros((365, 505, 3), 'uint8'); ovl[refm & mine] = (255, 255, 255); ovl[refm & ~mine] = (216, 33, 63); ovl[~refm & mine] = (80, 140, 255)
t4 = Image.fromarray(ovl).resize((560, 405))
fF = r(R3.svg_doc({}, ids=False, bg='#fff', view=(210, 280, 180, 230)), 330); fS = r(S.svg_side({}, ids=False, bg='#fff', view=(215, 280, 170, 230)), 310)
rF = im.crop((52, 190, 310, 400)).resize((330, 268)); rS = im.crop((500, 330, 600, 470)).resize((310, 434))
sh = Image.new('RGB', (4 * 580 + 20, 520 + 40 + 470), '#fff'); d = ImageDraw.Draw(sh); F = font(17); FS = font(14)
d.rectangle([0, 0, sh.width, 34], fill='#1A3A9C'); d.text((14, 8), 'Logo check — reference vs previous (v0.1–v0.4) vs fixed (v0.4.1)', font=F, fill='white')
for i, (t, l, col) in enumerate(((t1, 'REFERENCE sheet (hero figure)', '#222'), (t2, 'BEFORE: stroke "m", 3 full legs, small dot', '#D8213F'), (t3, 'AFTER: vector rebuild', '#1A3A9C'), (t4, f'overlay m shape  IoU {iou:.3f}  (white=match, red=ref only, blue=mine only)', '#222'))):
    sh.paste(t, (i * 580 + 10, 70)); d.text((i * 580 + 10, 44), l, font=FS, fill=col)
y2 = 70 + 420
for i, (t, l) in enumerate(((rF, 'reference · chest, front'), (fF, 'v0.4.1 · chest, front'), (rS, 'reference · chest, side'), (fS, 'v0.4.1 · chest, side (logo clipped by the silhouette)'))):
    sh.paste(t, (i * 580 + 10, y2 + 26)); d.text((i * 580 + 10, y2), l, font=FS, fill='#1A3A9C' if i % 2 else '#222')
sh.save(PV + '/logo_check.png')
json.dump(rep, open(os.path.join(HERE, 'logo_metrics.json'), 'w'), indent=1); print(json.dumps(rep, indent=1))
