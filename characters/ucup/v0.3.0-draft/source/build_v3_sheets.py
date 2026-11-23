import os as _o
HERE=_o.path.dirname(_o.path.abspath(__file__))
import sys, os, json
sys.path.insert(0,HERE)
import numpy as np, cairosvg
from scipy import ndimage
import ucup_rig2 as R2, ucup_rig3 as R3, anim3 as A3
from hatprobe import probe_local
from PIL import Image, ImageDraw, ImageFont
OUT=os.environ.get('UCUP_OUT', os.path.join(HERE,'..','rebuilt')); PV=OUT+'/preview'; os.makedirs(PV,exist_ok=True)
BG='#F4F1EA'
def font(sz,b=False): return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),sz)
FB,FS,FT=font(16,True),font(13),font(22,True)
def rend(M,pose,view,w,bg=BG):
    cairosvg.svg2png(bytestring=M.svg_doc(pose,ids=False,bg=bg,view=view).encode(),write_to='/tmp/_r.png',output_width=w)
    return Image.open('/tmp/_r.png').convert('RGB').copy()
def alpha(M,pose,view=(0,0,600,900),w=600):
    cairosvg.svg2png(bytestring=M.svg_doc(pose,ids=False,view=view).encode(),write_to='/tmp/_a.png',output_width=w)
    return np.array(Image.open('/tmp/_a.png').convert('RGBA'))
def title(im,txt,h=46):
    out=Image.new('RGB',(im.width,im.height+h),BG); d=ImageDraw.Draw(out); d.rectangle([0,0,im.width,h],fill='#1A3A9C'); d.text((14,11),txt,font=FB,fill='white'); out.paste(im,(0,h)); return out
rep={}
# ---------- 1 widths (arms raised so the torso/pants are not hidden)
UP=dict(R_abd=150,L_abd=150,R_flex=0,L_flex=0)
rows=[(420,'chest'),(480,'sweater low'),(505,'hem'),(530,'pants top'),(570,'hip'),(620,'thigh'),(760,'shin')]
W={}
for M,n in ((R2,'v0.2'),(R3,'v0.3')):
    a=alpha(M,UP)[:,:,3]>40; W[n]={}
    for y,l in rows:
        xs=np.where(a[y])[0]; W[n][l]=int(xs.max()-xs.min()+1)
rep['widths_px_arms_raised']=W
rep['pants_to_chest_ratio']={n:round(W[n]['pants top']/W[n]['chest'],2) for n in W}
# ---------- 2 waist comparison
z=(140,380,320,330); cells=[]
for M,n in ((R2,'v0.2'),(R3,'v0.3')):
    cells.append((rend(M,UP,z,330),f'{n} · arms raised'))
for M,n in ((R2,'v0.2'),(R3,'v0.3')):
    cells.append((rend(M,{},z,330),f'{n} · rest'))
w,h=cells[0][0].size
sh=Image.new('RGB',(4*w+30,h+40+190),BG); d=ImageDraw.Draw(sh)
for i,(im,l) in enumerate(cells): sh.paste(im,(i*(w+10),30)); d.text((i*(w+10)+4,6),l,font=FB,fill='#1A3A9C' if 'v0.3' in l else '#888')
y0=h+44; d.text((6,y0),'Silhouette width (px, arms raised)     '+'   '.join(f'{l}' for _,l in rows),font=FS,fill='#222')
for k,n in enumerate(('v0.2','v0.3')):
    d.text((6,y0+28+k*26),f'{n}:  '+'      '.join(f"{W[n][l]:>3d}" for _,l in rows),font=FB,fill='#1A3A9C' if n=='v0.3' else '#888')
d.text((6,y0+84),f"pants-top / chest ratio:  v0.2 = {rep['pants_to_chest_ratio']['v0.2']}   v0.3 = {rep['pants_to_chest_ratio']['v0.3']}   (target: pants narrower than sweater, ratio < 1)",font=FB,fill='#D8213F')
d.text((6,y0+112),'v0.3: sweater 172 wide with curved relaxed sides and bloused hem over a 164 rib band; pants waist 152, legs 75 each, small gap.',font=FS,fill='#222')
title(sh,'Waist · sweater · pants — before / after').save(PV+'/waist_comparison.png')
# ---------- 3 neutral silhouette comparison
v=(120,15,360,880); a2=alpha(R2,{},v,420); a3=alpha(R3,{},v,420)
def tint(a,c): o=np.zeros_like(a); m=a[:,:,3]>40; o[m]=list(c)+[170]; return Image.fromarray(o)
ov=Image.new('RGBA',(420,int(420*880/360)),BG); ov.alpha_composite(tint(a2,(216,33,63))); ov.alpha_composite(tint(a3,(36,83,189)))
s2=rend(R2,{},v,420); s3=rend(R3,{},v,420)
sh=Image.new('RGB',(3*430,s2.height+30),BG); d=ImageDraw.Draw(sh)
for i,(im,l) in enumerate(((s2,'v0.2 (previous)'),(s3,'v0.3 (revised)'),(ov.convert('RGB'),'overlay: red=v0.2 only · blue=v0.3 only'))): sh.paste(im,(i*430,30)); d.text((i*430+6,6),l,font=FB,fill='#1A3A9C')
title(sh,'Neutral silhouette comparison').save(PV+'/neutral_silhouette_comparison.png')
# ---------- 4 hat & hair attachment test
cases=[('neutral',{}),('head +15',dict(head=15)),('head −15',dict(head=-15)),('head +15 + face turn +12',dict(head=15,face_x=12)),
       ('torso +12 (head follows)',dict(torso=12)),('bend 1.0',dict(bend=1.0)),
       ('STRESS cap up 6px, rot −3°',dict(cap_dy=-6,cap_rot=-3)),('STRESS cap down 6px, rot +3°',dict(cap_dy=6,cap_rot=3))]
res={}; lim=(R3.CAP_LIM_DY,R3.CAP_LIM_ROT); cells=[]
for n,p in cases:
    b2=probe_local(R2,p); b3=probe_local(R3,p)
    stress=n.startswith('STRESS')
    if stress: R3.CAP_LIM_DY,R3.CAP_LIM_ROT=6,3
    b3s=probe_local(R3,p); img3=rend(R3,p,(170,15,260,260),220); img2=rend(R2,p,(170,15,260,260),220)
    R3.CAP_LIM_DY,R3.CAP_LIM_ROT=lim
    res[n]={'v0.2_px':b2,'v0.3_px_real_behaviour(clamped)':b3,'v0.3_px_clamp_lifted':b3s}
    cells.append((img2,img3,n,b2,b3s if stress else b3))
rep['hair_above_hat_line_px (head-local, lower = better)']=res
w,h=cells[0][0].size
sh=Image.new('RGB',(4*(2*w+16),2*(h+64)),BG); d=ImageDraw.Draw(sh)
for i,(a_,b_,n,b2,b3) in enumerate(cells):
    x,y=(i%4)*(2*w+16),(i//4)*(h+64); d.text((x+4,y+4),n,font=FB,fill='#1A3A9C')
    sh.paste(a_,(x,y+30)); sh.paste(b_,(x+w,y+30))
    d.text((x+4,y+h+34),f'v0.2: {b2} px hair above hat line',font=FS,fill='#D8213F' if b2>100 else '#2E8B57'); d.text((x+w+4,y+h+34),f'v0.3: {b3} px',font=FS,fill='#2E8B57')
title(sh,'Hat & hair attachment (left v0.2, right v0.3). Metric: hair pixels visible above the hat lower-edge line, measured in head-local frame').save(PV+'/hat_hair_attachment_test.png')
# cap-off integrity + hair coverage close-up
cells=[(rend(R3,dict(cap_on=0),(170,15,260,260),260),'cap off (bowl cut intact)'),(rend(R3,{},(170,15,260,260),260),'cap on · neutral'),(rend(R3,dict(head=15,face_x=12),(170,15,260,260),260),'cap on · head+15 · turn')]
sh=Image.new('RGB',(3*270,260+30),BG); d=ImageDraw.Draw(sh)
for i,(im,l) in enumerate(cells): sh.paste(im,(i*270,30)); d.text((i*270+6,6),l,font=FB,fill='#1A3A9C')
title(sh,'v0.3 hair states').save(PV+'/hair_states_v03.png')
# ---------- 5 head & neck comparison + neck metric
def neck_len(M,pose):
    a=alpha(M,pose,(0,0,600,900),600); col=a[:,300,:].astype(int)
    shy=[y for y in range(240,360) if col[y,3]>200 and abs(col[y,0]-0xE4)+abs(col[y,1]-0x56)+abs(col[y,2]-0x6B)<30]
    blu=[y for y in range(240,420) if col[y,3]>200 and col[y,2]>150 and col[y,0]<120]
    return (min(blu)-min(shy)) if shy and blu else None
nk={'v0.2':neck_len(R2,{}),'v0.3':neck_len(R3,{})}; rep['chin_shadow_to_sweater_px']=nk
cells=[]
for M,n in ((R2,'v0.2'),(R3,'v0.3')):
    row=[rend(M,p,(180,10,240,340),230) for p in ({},dict(head=15,face_x=10),dict(head=-15,face_x=-10),dict(head=0,bend=.6))]
    cells.append((n,row))
w,h=cells[0][1][0].size; sh=Image.new('RGB',(4*(w+6),2*(h+30)+44),BG); d=ImageDraw.Draw(sh)
for r,(n,row) in enumerate(cells):
    for c,im in enumerate(row): sh.paste(im,(c*(w+6),r*(h+30)+30)); d.text((c*(w+6)+4,r*(h+30)+6),f'{n} · '+['neutral','tilt +15 / turn','tilt −15 / turn','bend .6'][c],font=FB,fill='#1A3A9C' if n=='v0.3' else '#888')
d.text((6,2*(h+30)+36-4),f"visible neck (chin shadow → sweater, px at x=300):  v0.2 = {nk['v0.2']}   v0.3 = {nk['v0.3']}",font=FB,fill='#D8213F')
title(sh,'Head & neck proportion comparison').save(PV+'/head_neck_comparison.png')
# ---------- 6 articulation regression: all 10 diagnostic poses on v0.3 + connectivity
D=A3.diag_poses(); cells=[]; comp={}
for n,p in D.items():
    a=alpha(R3,p,(-40,-10,680,900),340)[:,:,3]>40; lab,k=ndimage.label(a); ar=ndimage.sum(a,lab,range(1,k+1)) if k else []
    comp[n]=int(sum(1 for x in ar if x>80)); cells.append((rend(R3,p,(-40,-10,680,900),300),n))
rep['diag_components_v0.3']=comp
w,h=cells[0][0].size; sh=Image.new('RGB',(5*w,2*(h+28)),BG); d=ImageDraw.Draw(sh)
for i,(im,n) in enumerate(cells): x,y=(i%5)*w,(i//5)*(h+28); sh.paste(im,(x,y+28)); d.text((x+6,y+4),n,font=FB,fill='#1A3A9C')
title(sh,'Articulation regression — 10 diagnostic poses on v0.3').save(PV+'/articulation_regression_v03.png')
v=[]
for n,vw in (('01 hands on hips',(60,10,480,640)),('02 arms crossed',(60,10,480,640)),('04 both arms up',(40,0,520,640)),('07 reach far side',(60,10,540,640)),('09 squat',(60,230,480,640)),('10 twist + arm',(60,10,480,640))):
    v.append((rend(R3,D[n],vw,380),n))
w,h=v[0][0].size; sh=Image.new('RGB',(3*w,2*(h+28)),BG); d=ImageDraw.Draw(sh)
for i,(im,n) in enumerate(v): x,y=(i%3)*w,(i//3)*(h+28); sh.paste(im,(x,y+28)); d.text((x+6,y+4),n,font=FB,fill='#1A3A9C')
title(sh,'v0.3 closeups — arm/sleeve/hand/torso interaction').save(PV+'/articulation_closeups_v03.png')
json.dump(rep,open(os.path.join(HERE,'metrics3.json'),'w'),indent=1)
print(json.dumps({k:rep[k] for k in ('widths_px_arms_raised','pants_to_chest_ratio','chin_shadow_to_sweater_px','diag_components_v0.3')},indent=0))
pass
