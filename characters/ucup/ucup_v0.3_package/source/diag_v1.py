import os as _o
HERE=_o.path.dirname(_o.path.abspath(__file__))
import sys; sys.path.insert(0,HERE)
import ucup_rig as R, ucup_anim as A, cairosvg
from PIL import Image, ImageDraw, ImageFont
arm=A.arm; e=A.expr
D={}
D['01 hands on hips']=dict(**arm('R',(336,508),'fist',wrist=-40,bend='out'),**{k:v for k,v in arm('L',(336,508),'fist',wrist=-40,bend='out').items()})
D['02 arms crossed']=dict(**arm('R',(232,408),'open',bend='down'),**arm('L',(368,414),'open',bend='down'))
D['03 one arm up']=arm('R',(440,100),'point',bend='out')
D['04 both arms up']=dict(**arm('R',(440,150),'open',bend='out'),**arm('L',(160,150),'open',bend='out'))
D['05 hand on head']=arm('R',(360,176),'open',wrist=-20,bend='out')
D['06 reach forward']=dict(R_abd=25,R_flex=0,R_hand='open')
D['07 reach far side']=dict(R_abd=88,R_flex=0,R_hand='open',torso=4)
D['08 bend forward']=dict(torso=12,head=8)
D['09 squat']=dict(root_y=70)
D['10 twist + arm']=dict(torso=8,head=-6,**arm('R',(220,320),'point',bend='down'),L_abd=40,L_flex=20)
if __name__=='__main__':
    ims=[]
    for n,p in D.items():
        cairosvg.svg2png(bytestring=R.svg_doc(p,ids=False,bg='#F4F1EA',view=(-40,-10,680,900)).encode(),write_to='/tmp/d.png',output_width=300)
        ims.append((n,Image.open('/tmp/d.png').convert('RGB').copy()))
    sh=Image.new('RGB',(300*5,452*2),'#F4F1EA'); d=ImageDraw.Draw(sh); f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16)
    for i,(n,im) in enumerate(ims):
        x,y=(i%5)*300,(i//5)*452; sh.paste(im,(x,y)); d.text((x+8,y+6),n,font=f,fill='#1A3A9C')
    sh.save(os.path.join(HERE,'before_diag.png'))
