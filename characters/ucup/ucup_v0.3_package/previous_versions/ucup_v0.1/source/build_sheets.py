import sys, os, re, json, math
sys.path.insert(0,'/home/claude/ucup')
import ucup_rig as R, ucup_anim as A, cairosvg
from lxml import etree
from PIL import Image, ImageDraw, ImageFont
OUT='/mnt/user-data/outputs/ucup_v0.1'; PV=OUT+'/preview'; os.makedirs(PV,exist_ok=True); os.makedirs(OUT+'/source',exist_ok=True)
BG='#F4F1EA'
def font(sz,bold=False):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if bold else ''),sz)
F,FB,FS=font(20),font(18,True),font(15)
def png(svg,w):
    cairosvg.svg2png(bytestring=svg.encode(),write_to='/tmp/_c.png',output_width=w); return Image.open('/tmp/_c.png').convert('RGB').copy()
def grid(cells,cols,cw,ch,title=None,pad=0):
    rows=(len(cells)+cols-1)//cols; top=50 if title else 0
    sh=Image.new('RGB',(cols*cw,rows*ch+top),BG); d=ImageDraw.Draw(sh)
    if title: d.rectangle([0,0,cols*cw,top],fill='#1A3A9C'); d.text((16,13),title,font=FB,fill='white')
    for i,(im,lab,tag) in enumerate(cells):
        x,y=(i%cols)*cw,(i//cols)*ch+top
        sh.paste(im,(x+(cw-im.width)//2,y+4)); 
        d.text((x+10,y+ch-34),lab,font=FB,fill='#1A3A9C')
        if tag: d.text((x+10+d.textlength(lab,font=FB)+8,y+ch-32),tag,font=FS,fill='#D8213F' if tag=='NEW' else '#666')
    return sh
P=A.pose_library()
# ---------- 1 clean SVG (rest, with semantic ids)
svg=R.svg_doc({},ids=True,title='Ucup — rest pose (rigged, editable)')
svg=svg.replace('</title>','</title><desc>MEKANIVO character Ucup v0.1.0-draft. Procedural vector rig. Groups: ucup-root > ucup-torso > (neck, head, arm-R/L > forearm > hand) ; ucup-leg-R/L > shin > foot. R/L = screen side.</desc>',1)
open(OUT+'/source/ucup_rest.svg','w').write(svg)
png(R.svg_doc({},ids=False,bg=BG),900).save(PV+'/ucup_rest_clean.png')
# ---------- 2 expressions
cells=[]
for n,e in A.EXPR.items():
    p=A.expr_full(n); p['cap_on']=1
    im=png(R.svg_doc(p,ids=False,bg=BG,view=(196,18,208,250)),230)
    cells.append((im,n,e['tag']))
sh=grid(cells,6,240,320,'UCUP — expression library  (REF = from reference sheet · NEW = created beyond reference)')
# visemes strip
vc=[]
for k,v in A.VISEMES.items():
    p=A.expr_full('neutral'); p.update(v)
    vc.append((png(R.svg_doc(p,ids=False,bg=BG,view=(196,18,208,250)),230),'viseme '+k,'NEW'))
vs=grid(vc,6,240,320)
# cap-off variants
cc=[]
for n in ('neutral','happy','confused'):
    p=A.expr_full(n); p['cap_on']=0
    cc.append((png(R.svg_doc(p,ids=False,bg=BG,view=(196,18,208,250)),230),n+' · cap off','REF'))
cs=grid(cc,6,240,320)
full=Image.new('RGB',(sh.width,sh.height+vs.height+cs.height-2),BG)
full.paste(sh,(0,0)); full.paste(vs,(0,sh.height)); full.paste(cs,(0,sh.height+vs.height)); full.save(PV+'/expressions_sheet.png')
# ---------- 3 hands
hc=[]
for st in R.HAND_STATES:
    s=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-60 -30 120 150" width="240" height="300"><rect x="-60" y="-30" width="120" height="150" fill="{BG}"/>'
       f'<path d="M-27 -30 L27 -30 L26 -8 Q0 -3 -26 -8 Z" fill="{R.C["blue"]}"/><g transform="translate(0 -4)">{R.hand_svg(st)}</g></svg>')
    hc.append((png(s,240),st,'REF' if st in('relaxed','open','point','thumbs','fist','peace') else 'NEW'))
grid(hc,5,250,340,'UCUP — hand states (rebuilt vector, screen-right hand; left = mirrored)').save(PV+'/hands_sheet.png')
# ---------- 4 poses
pc=[(png(R.svg_doc(P[n],ids=False,bg=BG,view=(-40,-10,680,900)),290),n,'') for n in P]
grid(pc,6,300,420,'UCUP — pose library (all rendered from the same rig; no per-pose redraw)').save(PV+'/poses_sheet.png')
# ---------- 5 stress test
rows=[('R arm abduction 0 / 40 / 80 / 120 / 150',[dict(R_abd=a,R_flex=0) for a in (0,40,80,120,150)]),
      ('R elbow flex @abd30: 0 / 45 / 90 / 135 / 160',[dict(R_abd=30,R_flex=a) for a in (0,45,90,135,160)]),
      ('L arm mirror check abd/flex',[dict(L_abd=a,L_flex=b) for a,b in ((0,0),(60,0),(90,45),(120,100),(150,20))]),
      ('head −15 / −8 / 0 / +8 / +15 · face_x ±',[dict(head=-15,face_x=-9),dict(head=-8),dict(),dict(head=8),dict(head=15,face_x=9)]),
      ('torso −12 / −6 / 0 / +6 / +12 · shrug 12',[dict(torso=-12),dict(torso=-6),dict(),dict(torso=6),dict(torso=0,shrug=12)])]
cells=[]
for lab,ps in rows:
    for i,p in enumerate(ps):
        cells.append((png(R.svg_doc(p,ids=False,bg=BG,view=(-40,10,680,560)),250),lab if i==0 else '',''))
st=grid(cells,5,260,270,'UCUP — joint stress test (look for seams, popping, gaps at extremes)')
legs=[dict(R_thigh=a,L_thigh=a) for a in (-4,8,18,30)]+[dict(R_knee=a,L_knee=-a*.6) for a in (20,35)]+[dict(root_y=y) for y in (28,-30)]
lc=[(png(R.svg_doc(p,ids=False,bg=BG,view=(100,440,400,460)),170),'','') for p in legs]
ls=grid(lc,8,180,260); ls_t=Image.new('RGB',(st.width,ls.height+36),BG); ImageDraw.Draw(ls_t).text((10,6),'legs: thigh abd −4/8/18/30 · knee 20/35 · root_y squash +28 / stretch −30',font=FB,fill='#1A3A9C'); ls_t.paste(ls,(0,36))
big=Image.new('RGB',(st.width,st.height+ls_t.height),BG); big.paste(st,(0,0)); big.paste(ls_t,(0,st.height)); big.save(PV+'/stress_test.png')
# ---------- 6 rig overlay + hierarchy
sx,sy=R.SHOULDER_R
def vec(th): return (math.sin(math.radians(th)),math.cos(math.radians(th)))
ex=(sx+R.UPPER*vec(9)[0],sy+R.UPPER*vec(9)[1]); wr=(ex[0]+R.FORE*vec(3)[0],ex[1]+R.FORE*vec(3)[1])
pts=[('neck / head',R.NECK,'#D8213F'),('cap (lag)',R.CAP_PIV,'#F26D1D'),('waist / torso',R.WAIST,'#D8213F'),
     ('shoulder',(sx,sy),'#1A3A9C'),('elbow',ex,'#1A3A9C'),('wrist',wr,'#1A3A9C'),
     ('shoulder',(600-sx,sy),'#1A3A9C'),('elbow',(600-ex[0],ex[1]),'#1A3A9C'),('wrist',(600-wr[0],wr[1]),'#1A3A9C'),
     ('hip',R.HIP_R,'#2E8B57'),('knee',(352,675),'#2E8B57'),('ankle',(352,827),'#2E8B57'),
     ('hip',(600-R.HIP_R[0],R.HIP_R[1]),'#2E8B57'),('knee',(248,675),'#2E8B57'),('ankle',(248,827),'#2E8B57')]
ov=''.join(f'<circle cx="{x}" cy="{y}" r="7" fill="{c}" stroke="#fff" stroke-width="2"/>' for _,(x,y),c in pts)
bones=[(R.NECK,R.WAIST),((sx,sy),ex),(ex,wr),((600-sx,sy),(600-ex[0],ex[1])),((600-ex[0],ex[1]),(600-wr[0],wr[1])),
       (R.HIP_R,(352,675)),((352,675),(352,827)),((252,502),(248,675)),((248,675),(248,827))]
ov=''.join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#1A3A9C" stroke-width="3" stroke-dasharray="6 4" opacity=".8"/>' for a,b in bones)+ov
tree=['HIERARCHY (pivot · range)','root  [translate x,y · plant legs]',' ├ pelvis (static fill)',' ├ leg-R/L  hip · thigh −5…30°',
 ' │   └ shin knee · −10…40°',' │       └ foot ankle · squash-compensated',' └ torso  waist · ±12° · breath scale',
 '     ├ neck (static) + collar',"     ├ head  neck · ±15° · face_x ±12px",'     │   ├ cap  pivot @head · lag spring',
 '     │   └ face: brows · eyes · mouth · fx','     ├ arm-R/L  shoulder · −55…150° · shrug 0…12',
 '     │   └ forearm elbow · 0…155°','     │       └ hand wrist · ±90° · 9 states','','Rig type: hybrid vector cutout, FK',
 '+ 2-bone IK helper (authoring/pose only)','Left side = mirrored right geometry','Joints overlap (round caps) → no gaps','Face = parametric (blendable)',
 'Not rigged: true turn / profile / back']
tx=''.join(f'<text x="640" y="{70+i*30}" font-family="DejaVu Sans" font-size="{20 if i else 22}" font-weight="{700 if i==0 else 400}" fill="#1A3A9C">{t.replace("&","&amp;")}</text>' for i,t in enumerate(tree))
rs=R.svg_doc({},ids=False,bg=BG,view=(0,0,1180,900),extra='')
rs=rs.replace('</svg>',ov+tx+'</svg>')
png(rs,1180).save(PV+'/rig_sheet.png')
# ---------- 7 exploded parts (extracted from the live rig by id)
ns={'s':'http://www.w3.org/2000/svg'}
root=etree.fromstring(R.character_svg({},True).join(['<svg xmlns="http://www.w3.org/2000/svg">','</svg>']))
def part(i,keep_nested=False):
    els=root.xpath(f'//*[@id="ucup-{i}"]',namespaces=ns)
    if not els: return None
    import copy; e=copy.deepcopy(els[0])
    if not keep_nested:
        for c in list(e):
            if c.tag.endswith('g') and c.get('id'): e.remove(c)
    if 'transform' in e.attrib and e.tag.endswith('g'): del e.attrib['transform']
    return re.sub(r' xmlns="[^"]+"','',etree.tostring(e).decode())
plist=[('hair-back',227,76,1),('face-base',244,118,1),('hair-fringe',229,76,1),('ear-L',224,170,1),('cap',234,64,1),('cap-visor',346,116,1),
       ('neck',268,224,1),('torso-art',224,293,.9),('logo',268,372,1.4),('pelvis',214,480,.9),('arm-R',-60,-30,.9),('forearm-R',-45,-30,.9),
       ('leg-R',-60,-10,.55),('shin-R',-60,-10,.6),('foot-R',-60,-12,1.5)]
cells=[]
for name,ox,oy,sc in plist:
    body=part(name)
    if body is None: continue
    if name in('arm-R','forearm-R','leg-R','shin-R','foot-R'): tr=f'translate({-ox*sc+10} {-oy*sc+10}) scale({sc})'
    else: tr=f'translate({10-ox*sc} {10-oy*sc}) scale({sc})'
    s=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 230 300" width="230" height="300"><rect width="230" height="300" fill="#DCE3F2"/><g transform="{tr}">{body}</g></svg>'
    cells.append((png(s,230),name,''))
grid(cells,5,240,340,'UCUP — part layout (extracted from rig source by semantic id)').save(PV+'/parts_sheet.png')
# ---------- 8 reference comparison
ref=Image.open('/mnt/user-data/uploads/1795337616561_gambar_20261122142302.jpg').convert('RGB')
a=ref.crop((330,295,490,735)); b=ref.crop((40,35,320,735))
mine=png(R.svg_doc({},ids=False,bg='#fff',view=(120,15,360,880)),360)
cmp=Image.new('RGB',(1500,980),'#fff'); d=ImageDraw.Draw(cmp)
d.rectangle([0,0,1500,50],fill='#1A3A9C'); d.text((16,13),'Reference (left, 2 crops)  vs  Reconstruction (right) — identity check',font=FB,fill='white')
cmp.paste(b.resize((int(b.width*820/b.height),820)),(20,70)); cmp.paste(a.resize((int(a.width*820/a.height),820)),(330,70)); cmp.paste(mine.resize((int(mine.width*820/mine.height),820)),(640,70))
notes=['IDENTITY LOCKED (kept):','• backwards orange cap: arch, dotted band, button, panel, visor','• black bowl cut, jagged fringe, hair visible behind jaw','• coral skin, dot eyes, thin brows, "c" nose, line smile','• royal-blue crewneck, dark hem band, white m. logo','• beige straight pants, red sneakers with cream sole','• flat fills, no outlines, minimal crease lines','','INTERPRETED / DIFFERENT:','• Reference sheet is inconsistent: hero figure ≈5 heads,','  turnaround ≈4.2 heads. I used ≈4.5 (head x1.12) for acting.','• Hero pose has hands in pockets; rest pose here is neutral','  (pockets pose exists separately).','• Sleeve cuffs rebuilt w/o the blue wrist band seen on the','  hand sheet (turnaround shows none).','• Shoe laces simplified to 3 ticks per shoe.','• Hidden areas inferred: hair top (cap-off), neck, knee,','  shoe heel, sleeve inner, elbow overlap.','• Side/back views NOT rebuilt yet (front-only rig).']
for i,t in enumerate(notes): d.text((960,80+i*36),t,font=FB if t.endswith(':') else FS,fill='#1A3A9C' if t.endswith(':') else '#222')
cmp.save(PV+'/reference_comparison.png')
# ---------- 9 library json
def rnd(o): return {k:(round(v,2) if isinstance(v,float) else v) for k,v in o.items()}
lib={'expressions':{k:dict(tag=v['tag'],params=rnd(v['p'])) for k,v in A.EXPR.items()},'visemes':{k:rnd(v) for k,v in A.VISEMES.items()},
     'hand_states':R.HAND_STATES,'poses':{k:rnd(v) for k,v in P.items()},'defaults':rnd(R.DEFAULT)}
json.dump(lib,open(OUT+'/source/states_library.json','w'),indent=1)
print('sheets ok')
