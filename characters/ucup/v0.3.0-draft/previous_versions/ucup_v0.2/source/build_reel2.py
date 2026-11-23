import sys, os, subprocess, shutil, json
sys.path.insert(0,'/home/claude/ucup2')
import reel2, ucup_rig2 as R2, cairosvg
from ucup_rig2 import solve_legs, DEFAULT
from PIL import Image, ImageDraw, ImageFont
OUT='/mnt/user-data/outputs/ucup_v0.2'; os.makedirs(OUT+'/preview',exist_ok=True)
FR='/home/claude/ucup2/frames'; shutil.rmtree(FR,ignore_errors=True); os.makedirs(FR)
VIEW=(-60,-100,720,1000)
def font(sz,b=False): return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),sz)
frames=reel2.build_frames()
def shadow(p):
    ry=solve_legs(dict(DEFAULT,**p))[1]; k=max(.6,1-abs(min(0,ry))/160)
    return (f'<ellipse cx="{300+p["root_x"]:.1f}" cy="866" rx="{108*k:.1f}" ry="{11*k:.1f}" fill="#000" opacity="{.16*k:.2f}"/>'
            f'<rect x="-60" y="866" width="720" height="34" fill="#E9E3D6"/>')
def label(t):
    for a,b,l in reel2.SEGMENTS:
        if a<=t<b: return l
    return ''
fnt,fb=font(21),font(17,True)
for i,p in enumerate(frames):
    s=R2.svg_doc(p,ids=False,bg='#F4F1EA',view=VIEW,extra=shadow(p))
    png=f'{FR}/f{i:04d}.png'; cairosvg.svg2png(bytestring=s.encode(),write_to=png,output_width=720)
    im=Image.open(png).convert('RGB'); d=ImageDraw.Draw(im)
    d.rectangle([0,0,720,44],fill='#1A3A9C'); d.text((16,10),'UCUP v0.2 · structural revision · motion test (draft)',font=fb,fill='white')
    d.text((16,962),label(i/reel2.FPS),font=fnt,fill='#1A3A9C'); d.text((612,966),f't={i/reel2.FPS:4.1f}s',font=fb,fill='#555'); im.save(png)
mp4=OUT+'/preview/ucup_v02_motion_test.mp4'
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',FR+'/f%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','17',mp4],check=True)
picks=[0.6,1.3,2.5,4.1,4.9,6.5,8.0,9.0,10.8,12.0,13.8,15.0,15.9,16.6,17.8,19.5]
ims=[Image.open(f'{FR}/f{int(t*30):04d}.png').crop((40,60,700,960)).resize((264,360)) for t in picks]
sh=Image.new('RGB',(264*8,360*2),'#F4F1EA'); d=ImageDraw.Draw(sh)
for i,(im,t) in enumerate(zip(ims,picks)):
    x,y=(i%8)*264,(i//8)*360; sh.paste(im,(x,y)); d.text((x+8,y+6),f'{t:.1f}s',font=fb,fill='#1A3A9C')
sh.save(OUT+'/preview/v02_motion_contact_sheet.png'); print('ok')
