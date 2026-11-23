import os as _o
HERE=_o.path.dirname(_o.path.abspath(__file__))
import sys, math
sys.path.insert(0,HERE)
import ucup_rig3 as R3, ucup_anim as A, anim3 as A2
from anim3 import arm2, both, knee_screen
from ucup_rig3 import DEFAULT, solve_legs
FPS=30; DUR=24.0
def full(pose, ex='neutral'):
    d=dict(DEFAULT); d.update(A.expr_full(ex)); d.update(pose); return d
def K(t,ease,pose,ex='neutral',**ov):
    d=full(pose,ex); d.update(ov); return (t,ease,d)
hips=both({},(356,488),(244,488),'fist',0,'out')
reachside=dict(R_abd=94,R_flex=0,R_hand='open',torso=5,L_abd=16,L_flex=10)
armup=dict(arm2('R',(428,105),'point',0,'out'),torso=-3,head=-3)
tw1=dict(twist=.8,torso=5,head=-4,hip=2); tw1.update(arm2('R',(240,350),'point',0,'down',tw1)); tw1.update(L_abd=22,L_flex=14)
rec=dict(R_abd=34,R_flex=62,R_wrist=-18,R_hand='open',L_abd=34,L_flex=62,L_wrist=-18,L_hand='open',torso=-6,head=-4,shrug=5)
shr=dict(R_abd=38,R_flex=48,R_wrist=-25,R_hand='present',L_abd=38,L_flex=48,L_wrist=-25,L_hand='present',shrug=10,head=7)
crossed=both(dict(arm_top='R'),(280,424),(322,452),'fist',0,'down',0,'fist')
sq=dict(squat=.85,torso=3)
kR,ry=knee_screen(sq,'R'); kL,_=knee_screen(sq,'L')
squat=both(sq,(kR[0]-6,kR[1]-ry-24),(kL[0]+6,kL[1]-ry-24),'relaxed',0,'out')
pre=dict(squat=.18,torso=4,R_abd=16,R_flex=30,L_abd=16,L_flex=30)
keys=[K(0,'io',{}),
 K(1.2,'io',dict(hip=3.5,root_x=8,torso=-3,head=2),gx=.8),
 K(2.5,'io',dict(hip=-3.5,root_x=-8,torso=3,head=-2)),
 K(3.3,'io',{}),
 K(3.9,'back',hips,'smirk'),
 K(4.9,'out',reachside,'happy'),K(5.5,'io',dict(reachside,torso=7),'happy'),
 K(6.3,'back',armup,'excited'),K(7.0,'io',armup,'excited'),
 K(7.7,'io',{},'neutral'),
 K(8.1,'io',dict(torso=-3,twist=-.15,R_abd=20,R_flex=40),'focused'),
 K(8.7,'back',tw1,'focused',gx=1),K(9.5,'io',tw1,'smirk',gx=1),
 K(10.1,'io',{},'neutral',gx=0),
 K(10.6,'back',rec,'surprised'),K(11.2,'io',rec,'surprised'),
 K(11.9,'io',shr,'embarrassed'),K(12.7,'io',shr,'embarrassed'),
 K(13.3,'io',crossed,'smirk'),K(14.1,'io',crossed,'smirk'),
 K(14.7,'back',hips,'smirk'),
 K(15.4,'in',dict(pre),'excited'),
 K(16.1,'io',squat,'curious'),K(16.9,'io',squat,'curious'),
 K(17.6,'back',{},'happy'),
 K(18.1,'io',dict(arm2('R',(436,196),'wave',10,'out'),head=12,face_x=10,torso=-1),'happy',gx=1),
 K(18.6,'io',dict(arm2('R',(436,196),'wave',34,'out'),head=10,face_x=10,torso=-1),'happy',gx=1),
 K(19.0,'io',dict(arm2('R',(436,196),'wave',-10,'out'),head=12,face_x=10,torso=-1),'happy',gx=1),
 K(19.6,'io',dict(arm2('R',(530,316),'point',0,'down'),head=6,face_x=6,torso=-2),'focused',gx=1),
 K(20.4,'back',dict(arm2('L',(164,196),'wave',10,'out'),head=-12,face_x=-10,torso=1),'happy',gx=-1),
 K(20.9,'io',dict(arm2('L',(164,196),'wave',34,'out'),head=-10,face_x=-10,torso=1),'happy',gx=-1),
 K(21.4,'io',dict(arm2('L',(164,196),'wave',-10,'out'),head=-12,face_x=-10,torso=1),'happy',gx=-1),
 K(22.0,'io',dict(head=5),'happy'),K(22.4,'io',dict(head=-1),'neutral'),
 K(23.0,'io',{},'neutral'),K(24.0,'io',{},'neutral')]
SEGMENTS=[(0,3.5,'WEIGHT SHIFT  hip tilt · counter-lean · feet planted'),(3.5,5.2,'ARM BEND  hands on hips → reach side'),
 (5.2,7.6,'ARM EXTEND  raise & point up (shoulder lifts)'),(7.6,10.2,'TORSO TWIST  twist + cross-body point'),
 (10.2,12.9,'REACTION  recoil → embarrassed shrug'),(12.9,15.0,'ARMS CROSSED → HANDS ON HIPS (arm layering)'),
 (15.0,18.0,'SQUAT  knees out · hands on knees · stand up'),(18.0,22.0,'HEAD + ARM  tilt · face turn · wave / point'),(22.0,24.0,'SETTLE')]
BLINKS=[1.9,5.3,9.6,12.4,16.6,19.4,22.6]
def secondary2(frames,dt):
    frames=A.secondary(frames,dt)
    full_=[dict(DEFAULT,**f) for f in frames]
    ryv=[solve_legs(f)[1] for f in full_]
    lry=A.lag_filter(ryv,dt,6.0,.35)
    for s in 'RL':
        up=[-f[f'{s}_abd'] for f in full_]; lu=A.lag_filter(up,dt,5.5,.35)
        for i,fr in enumerate(frames): fr[f'{s}_flex']=full_[i][f'{s}_flex']+0.4*(lu[i]-up[i])
    for i,fr in enumerate(frames): fr['cap_dy']=fr.get('cap_dy',0)+0.45*(lry[i]-ryv[i])
    return frames
def build_frames():
    tl=A.Timeline(keys); n=int(DUR*FPS)
    raw=[tl.pose(i/FPS) for i in range(n)]
    raw=secondary2(raw,1/FPS)
    return [A.finalize(fr,i/FPS,BLINKS) for i,fr in enumerate(raw)]
