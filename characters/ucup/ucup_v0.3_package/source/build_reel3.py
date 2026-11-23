import os as _o
HERE=_o.path.dirname(_o.path.abspath(__file__))
import sys, os, subprocess, shutil, json
sys.path.insert(0,HERE)
import reel3, ucup_rig3 as R3, cairosvg
from ucup_rig3 import solve_legs, DEFAULT
from PIL import Image, ImageDraw, ImageFont
OUT=os.environ.get('UCUP_OUT', os.path.join(HERE,'..','rebuilt')); os.makedirs(OUT+'/preview',exist_ok=True)
FR=os.path.join(HERE,'frames'); shutil.rmtree(FR,ignore_errors=True); os.makedirs(FR)
VIEW=(-60,-100,720,1000)
def font(sz,b=False): return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),sz)
frames=reel3.build_frames()
def shadow(p):
    ry=solve_legs(dict(DEFAULT,**p))[1]; k=max(.6,1-abs(min(0,ry))/160)
    return (f'<ellipse cx="{300+p["root_x"]:.1f}" cy="866" rx="{108*k:.1f}" ry="{11*k:.1f}" fill="#000" opacity="{.16*k:.2f}"/>'
            f'<rect x="-60" y="866" width="720" height="34" fill="#E9E3D6"/>')
def label(t):
    for a,b,l in reel3.SEGMENTS:
        if a<=t<b: return l
    return ''
fnt,fb=font(21),font(17,True)
for i,p in enumerate(frames):
    s=R3.svg_doc(p,ids=False,bg='#F4F1EA',view=VIEW,extra=shadow(p))
    png=f'{FR}/f{i:04d}.png'; cairosvg.svg2png(bytestring=s.encode(),write_to=png,output_width=720)
    im=Image.open(png).convert('RGB'); d=ImageDraw.Draw(im)
    d.rectangle([0,0,720,44],fill='#1A3A9C'); d.text((16,10),'UCUP v0.3 · proportion & attachment revision · motion test (draft)',font=fb,fill='white')
    d.text((16,962),label(i/reel3.FPS),font=fnt,fill='#1A3A9C'); d.text((612,966),f't={i/reel3.FPS:4.1f}s',font=fb,fill='#555'); im.save(png)
mp4=OUT+'/preview/ucup_v03_motion_test.mp4'
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',FR+'/f%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','17',mp4],check=True)
picks=[0.6,1.3,2.5,4.4,5.0,6.5,8.0,9.0,10.8,12.0,13.8,15.0,16.6,18.5,19.8,21.0,22.2,23.5]
ims=[Image.open(f'{FR}/f{int(t*30):04d}.png').crop((40,60,700,960)).resize((264,360)) for t in picks]
sh=Image.new('RGB',(264*9,360*2),'#F4F1EA'); d=ImageDraw.Draw(sh)
for i,(im,t) in enumerate(zip(ims,picks)):
    x,y=(i%9)*264,(i//9)*360; sh.paste(im,(x,y)); d.text((x+8,y+6),f'{t:.1f}s',font=fb,fill='#1A3A9C')
sh.save(OUT+'/preview/v03_motion_contact_sheet.png'); print('ok')
