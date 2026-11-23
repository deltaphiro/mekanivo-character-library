import sys, os, subprocess, shutil
sys.path.insert(0,'/home/claude/ucup')
import reel, ucup_rig as R, cairosvg
from PIL import Image, ImageDraw, ImageFont
OUT='/mnt/user-data/outputs/ucup_v0.1'; os.makedirs(OUT+'/preview',exist_ok=True)
FR='/home/claude/ucup/frames'; shutil.rmtree(FR,ignore_errors=True); os.makedirs(FR)
VIEW=(-60,-100,720,1000)
def font(sz,bold=False):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if bold else ''),'/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf'%('Bold' if bold else 'Regular')]:
        if os.path.exists(p): return ImageFont.truetype(p,sz)
    return ImageFont.load_default()
frames=reel.build_frames()
def shadow(p):
    h=-p['root_y']; k=max(.55,1-abs(h)/160)
    return (f'<ellipse cx="{300+p["root_x"]:.1f}" cy="866" rx="{105*k:.1f}" ry="{11*k:.1f}" fill="#000" opacity="{.16*k:.2f}"/>'
            f'<rect x="-60" y="866" width="720" height="34" fill="#E9E3D6"/>')
def label(t):
    for a,b,l in reel.SEGMENTS:
        if a<=t<b: return l
    return ''
fnt,fb=font(22),font(17,True)
for i,p in enumerate(frames):
    s=R.svg_doc(p,ids=False,bg='#F4F1EA',view=VIEW,extra=shadow(p))
    png=f'{FR}/f{i:04d}.png'
    cairosvg.svg2png(bytestring=s.encode(),write_to=png,output_width=720)
    im=Image.open(png).convert('RGB'); d=ImageDraw.Draw(im)
    d.rectangle([0,0,720,44],fill='#1A3A9C'); d.text((16,10),'UCUP · motion test v0.1 (draft)',font=fb,fill='white')
    d.text((16,962),label(i/reel.FPS),font=fnt,fill='#1A3A9C'); d.text((600,966),f't={i/reel.FPS:4.1f}s',font=fb,fill='#555')
    im.save(png)
mp4=OUT+'/preview/ucup_motion_test.mp4'
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(reel.FPS),'-i',FR+'/f%04d.png','-c:v','libx264','-pix_fmt','yuv420p','-crf','17',mp4],check=True)
# contact sheet: 20 frames at chosen key moments
picks=[0.5,1.3,3.2,3.7,4.2,5.9,6.6,7.8,8.4,10.4,11.3,12.6,13.7,14.9,15.95,16.3,16.5,16.9,17.15,19.5]
ims=[Image.open(f'{FR}/f{int(t*reel.FPS):04d}.png').crop((60,60,690,960)).resize((252,360)) for t in picks]
sh=Image.new('RGB',(252*10,360*2+0),'#F4F1EA'); d=ImageDraw.Draw(sh)
for i,(im,t) in enumerate(zip(ims,picks)):
    x,y=(i%10)*252,(i//10)*360; sh.paste(im,(x,y)); d.text((x+8,y+6),f'{t:.2f}s',font=fb,fill='#1A3A9C')
sh.save(OUT+'/preview/motion_contact_sheet.png')
print('ok', os.path.getsize(mp4)/1e6,'MB')
