import sys, math, time
sys.path.insert(0,'/home/claude/ucup')
import ucup_rig as R, ucup_anim as A

FPS=30; DUR=20.0
P=A.pose_library()
BASE={k:R.DEFAULT[k] for k in R.DEFAULT}
def full(pose, ex=None):
    d=dict(BASE); 
    d.update(A.expr_full('neutral'))
    if ex: d.update(A.expr_full(ex))
    d.update(pose); return d
def K(t, ease, pose, ex=None, **ov):
    d=full(pose, ex); d.update(ov); return (t, ease, d)

rest=full({})
keys=[]
# --- idle: weight shift + glance
keys+= [K(0.0,'io',{}),
        K(1.2,'io',dict(root_x=6,torso=1.5,head=-1.5), gx=.8, gy=-.1),
        K(2.4,'io',dict(root_x=-3,torso=-1,head=1), gx=0)]
# --- wave
w=dict(P['wave'])
keys+= [K(2.7,'io',dict(R_abd=24,R_flex=26,torso=-1),'happy'),
        K(3.15,'back',w,'happy'),
        K(3.45,'io',dict(w,R_wrist=34),'happy'),K(3.7,'io',dict(w,R_wrist=-10),'happy'),
        K(3.95,'io',dict(w,R_wrist=34),'happy'),K(4.2,'io',dict(w,R_wrist=-10),'happy'),
        K(4.45,'io',dict(w,R_wrist=24),'happy'),
        K(4.9,'io',{},'neutral')]
# --- explain (talk)
e=dict(P['explain'])
keys+= [K(5.2,'back',e,'happy'),
        K(5.45,'io',dict(e,head=5),'happy',m_open=10),K(5.65,'io',dict(e,head=2),'happy',m_open=3),
        K(5.85,'io',dict(e,head=4,R_wrist=-18),'happy',m_open=11,m_w=26),K(6.05,'io',dict(e,head=1,R_wrist=-34),'happy',m_open=4),
        K(6.35,'back',dict(e,L_abd=40,L_flex=52,L_wrist=-26,L_hand='present',R_abd=e['R_abd']+6,head=4,torso=3),'happy',m_open=9,m_w=30),
        K(6.6,'io',dict(e,L_abd=40,L_flex=52,L_wrist=-26,L_hand='present',head=1,torso=3),'happy',m_open=3),
        K(6.85,'io',dict(e,L_abd=40,L_flex=52,L_wrist=-26,L_hand='present',head=3,torso=3),'happy',m_open=10),
        K(7.3,'io',{},'neutral')]
# --- point
p=dict(P['point'])
keys+= [K(7.75,'io',dict(R_abd=26,R_flex=75,R_hand='fist',R_wrist=0,torso=4,head=2),'focused',gx=0),
        K(8.2,'back',p,'focused',gx=1,gy=-.2),
        K(8.9,'io',dict(p,head=-6),'smirk',gx=1),
        K(9.4,'io',{},'neutral',gx=0)]
# --- think -> aha -> thumbs
t=dict(P['think']); tu=dict(P['thumbs_up'])
keys+= [K(9.9,'io',t,'curious'),
        K(10.7,'io',dict(t,head=-8,torso=2),'curious',gx=.9,gy=-.8),
        K(11.15,'back',dict(tu,torso=-3,head=-1,root_y=-4),'excited'),
        K(11.7,'io',tu,'happy'),
        K(12.3,'io',tu,'wink'),K(13.0,'io',tu,'wink'),
        K(13.4,'io',{},'neutral')]
# --- surprise recoil -> shrug
s_=dict(P['surprised_recoil']); sh=dict(P['shrug'])
keys+= [K(13.55,'back',s_,'surprised'),K(14.1,'io',s_,'surprised'),
        K(14.75,'io',sh,'embarrassed'),K(15.35,'io',sh,'embarrassed')]
# --- hop (anticipation, launch, apex, land squash, settle)
ch=dict(P['cheer'])
crouch=dict(R_abd=18,R_flex=40,L_abd=18,L_flex=40,torso=5,head=-3,root_y=27)
air=dict(ch,root_y=-52,R_knee=10,L_knee=-4,R_thigh=3,L_thigh=3)
keys+= [K(15.7,'io',{},'excited'),
        K(16.0,'in',crouch,'excited'),
        K(16.28,'out',air,'laugh'),
        K(16.5,'io',dict(air,root_y=-58),'laugh'),
        K(16.8,'in',dict(R_abd=20,R_flex=30,L_abd=20,L_flex=30,root_y=22,torso=3,head=2),'laugh'),
        K(17.05,'spring',dict(root_y=0,torso=0,head=0),'laugh'),
        K(17.9,'io',{},'happy'),
        K(19.0,'io',{},'neutral'),K(20.0,'io',{},'neutral')]
# explicit hand-state keys already inside poses; also set hand states for rest segments
SEGMENTS=[(0,2.5,'IDLE  breathing · weight shift · glance'),(2.5,5.0,'WAVE  anticipation · overshoot · wrist drag'),
 (5.0,7.5,'EXPLAIN  talk cycle · nods · two-hand gesture'),(7.5,9.5,'POINT  anticipation · eye leads · reach'),
 (9.5,13.5,'THINK → AHA → THUMBS UP → WINK'),(13.5,15.5,'RECOIL → SHRUG (embarrassed)'),
 (15.5,18.0,'HOP  crouch · stretch · squash · settle'),(18.0,20.0,'RETURN TO REST')]
BLINKS=[1.9,4.9,9.6,12.1,17.7,19.2]

def build_frames():
    tl=A.Timeline(keys)
    n=int(DUR*FPS)
    raw=[]
    for i in range(n):
        t=i/FPS
        raw.append(tl.pose(t))
    raw=A.secondary(raw,1/FPS)
    return [A.finalize(fr,i/FPS,BLINKS) for i,fr in enumerate(raw)]
