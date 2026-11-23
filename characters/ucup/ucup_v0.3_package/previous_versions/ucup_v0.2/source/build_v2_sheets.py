import sys, os, json, io, math
sys.path.insert(0,'/home/claude/ucup2')
import numpy as np, cairosvg
from scipy import ndimage
import ucup_rig as R1, ucup_rig2 as R2, anim2 as A2, reel2, diag_v1
from ucup_rig2 import solve_legs, DEFAULT
from PIL import Image, ImageDraw, ImageFont
OUT='/mnt/user-data/outputs/ucup_v0.2'; PV=OUT+'/preview'; os.makedirs(PV,exist_ok=True)
BG='#F4F1EA'
def font(sz,b=False): return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),sz)
FB,FS=font(16,True),font(13)
VIEW=(-40,-10,680,900)
def img(mod,pose,view=VIEW,w=220,bg=BG):
    cairosvg.svg2png(bytestring=mod.svg_doc(pose,ids=False,bg=bg,view=view).encode(),write_to='/tmp/_i.png',output_width=w)
    return Image.open('/tmp/_i.png').convert('RGB').copy()
def comps(mod,pose,view=VIEW):
    cairosvg.svg2png(bytestring=mod.svg_doc(pose,ids=False,view=view).encode(),write_to='/tmp/_a.png',output_width=340)
    a=np.array(Image.open('/tmp/_a.png').convert('RGBA'))[:,:,3]>40
    lab,n=ndimage.label(a); areas=ndimage.sum(a,lab,range(1,n+1)) if n else []
    return int(sum(1 for x in areas if x>80)), [int(x) for x in sorted(areas,reverse=True)[:4]]
DB=diag_v1.D; DA=A2.diag_poses()
metrics={}
cells=[]
for (nb,pb),(na,pa) in zip(DB.items(),DA.items()):
    cb,_=comps(R1,pb); ca,_=comps(R2,pa); metrics[na]={'v0.1_components':cb,'v0.2_components':ca}
    cells.append((img(R1,pb),img(R2,pa),na))
W2,H2=220,cells[0][0].height
sh=Image.new('RGB',(5*(2*W2+14),2*(H2+34)+54),BG); d=ImageDraw.Draw(sh)
d.rectangle([0,0,sh.width,50],fill='#1A3A9C'); d.text((16,14),'Diagnostic pose tests — LEFT: v0.1 (original construction)   RIGHT: v0.2 (revised)',font=FB,fill='white')
for i,(b,a,n) in enumerate(cells):
    x,y=(i%5)*(2*W2+14),(i//5)*(H2+34)+54; sh.paste(b,(x,y+28)); sh.paste(a,(x+W2,y+28))
    d.text((x+6,y+4),n,font=FB,fill='#1A3A9C'); d.text((x+W2-70,y+10),'v0.1',font=FS,fill='#999'); d.text((x+2*W2-70,y+10),'v0.2',font=FS,fill='#1A3A9C')
sh.save(PV+'/diag_before_after.png')
# ---- construction comparison: silhouette overlay + cuff + shoulder/elbow zoom
def rgba(mod,pose,view,w):
    cairosvg.svg2png(bytestring=mod.svg_doc(pose,ids=False,view=view).encode(),write_to='/tmp/_o.png',output_width=w); return Image.open('/tmp/_o.png').convert('RGBA').copy()
v=(130,10,340,880); a1=rgba(R1,{},v,420); a2=rgba(R2,{},v,420)
def tint(im,col,al):
    arr=np.array(im); m=arr[:,:,3]>40; out=np.zeros_like(arr); out[m]=list(col)+[al]; return Image.fromarray(out)
ov=Image.new('RGBA',a1.size,BG); ov.alpha_composite(tint(a1,(216,33,63),150)); ov.alpha_composite(tint(a2,(36,83,189),150))
zs=[]
for mod,lab in ((R1,'v0.1'),(R2,'v0.2')):
    row=[]
    for p,vw in (({},(180,360,330,260)),(dict(R_abd=100,R_flex=20),(190,230,330,260)),(dict(R_abd=40,R_flex=130),(190,230,330,260)),(dict(R_hand='open'),(180,460,330,260))):
        row.append(img(mod,p,vw,300))
    zs.append(row)
W=300; cmp=Image.new('RGB',(420+4*W+30,2*(zs[0][0].height+30)+54+10),BG); d=ImageDraw.Draw(cmp)
d.rectangle([0,0,cmp.width,50],fill='#1A3A9C'); d.text((16,14),'Construction comparison — silhouette overlay (red v0.1 / blue v0.2) and joint close-ups',font=FB,fill='white')
ovr=ov.convert('RGB'); ovr=ovr.resize((int(ovr.width*(cmp.height-80)/ovr.height),cmp.height-80)); cmp.paste(ovr,(10+(420-ovr.width)//2,64)); d.text((10,54),'',font=FS)
d.text((12,cmp.height-18),'overlap = purple · red edge = v0.1 only · blue edge = v0.2 only',font=FS,fill='#444')

heads=['rest: shoulder + cuff','arm raised 100°','elbow flex 130°','hand under sleeve lip']
for r,(row,lab) in enumerate(zip(zs,('v0.1','v0.2'))):
    for c,im in enumerate(row):
        x,y=440+c*(W+6),60+r*(im.height+30); cmp.paste(im,(x,y+22)); d.text((x+4,y+2),f'{lab} · {heads[c]}',font=FS,fill='#1A3A9C' if lab=='v0.2' else '#999')
cmp.save(PV+'/construction_comparison.png')
# ---- stress test v2
rows=[('R arm abduction (rhythm on)',[dict(R_abd=a,R_flex=0) for a in (0,40,80,120,150)],'up'),
      ('R elbow flex @abd30',[dict(R_abd=30,R_flex=a) for a in (0,50,100,130,155)],'up'),
      ('torso twist −1…+1 (arm R 30°)',[dict(twist=t,R_abd=30,R_flex=20) for t in (-1,-.5,0,.5,1)],'up'),
      ('torso bend 0 / .3 / .6 / .9 / 1.2',[dict(bend=b,R_abd=8,R_flex=10) for b in (0,.3,.6,.9,1.2)],'up'),
      ('squat 0 / .3 / .6 / .85 / 1.1',[dict(squat=s) for s in (0,.3,.6,.85,1.1)],'full'),
      ('weight shift / shrug / lean ±12',[dict(hip=4,root_x=8,torso=-3),dict(hip=-4,root_x=-8,torso=3),dict(shrug=12),dict(torso=-12),dict(torso=12)],'full')]
UP=(-40,10,680,560); stress={}
cells=[]
for lab,ps,vw in rows:
    for i,p in enumerate(ps):
        pp=A2.finalize(dict(p),0) if 'root_x' in p else p
        c,_=comps(R2,pp,UP if vw=='up' else VIEW); stress.setdefault(lab,[]).append(c)
        im=img(R2,pp,UP if vw=='up' else (-40,-10,680,900),250 if vw=='up' else 190)
        cells.append((im,lab if i==0 else ''))
cw=260; chh=max(c[0].height for c in cells)+30
st=Image.new('RGB',(5*cw,6*chh+50),BG); d=ImageDraw.Draw(st); d.rectangle([0,0,st.width,46],fill='#1A3A9C'); d.text((16,13),'v0.2 joint stress test — shoulders, elbows, twist, bend, squat, weight shift',font=FB,fill='white')
for i,(im,lab) in enumerate(cells):
    x,y=(i%5)*cw,(i//5)*chh+50; st.paste(im,(x+(cw-im.width)//2,y+22)); 
    if lab: d.text((x+6,y+3),lab,font=FB,fill='#1A3A9C')
st.save(PV+'/stress_test_v02.png')
# ---- ground contact over the reel
fr=reel2.build_frames(); err=[]; free=[]
for p in fr:
    L,ry=solve_legs(dict(DEFAULT,**p)); ay=[v['ankle'][1]+ry for v in L.values()]
    err.append(min(abs(a-827) for a in ay)); free.append(max(abs(a-827) for a in ay))
contact={'frames':len(fr),'max_support_foot_error_px':round(max(err),2),'max_second_foot_float_px':round(max(free),2),
         'frames_with_foot_float_gt_4px':int(sum(1 for x in free if x>4)),
         'max_root_drop_px':round(max(solve_legs(dict(DEFAULT,**p))[1] for p in fr),1)}
json.dump({'diag_components(1=clean single silhouette)':metrics,'stress_components':stress,'reel_ground_contact':contact},open('/home/claude/ucup2/metrics.json','w'),indent=1)
print(json.dumps(metrics,indent=0)); print(stress); print(contact)
