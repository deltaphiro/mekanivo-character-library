import numpy as np, cairosvg
from PIL import Image
def probe_local(mod, pose, y_line=146.0):
    """hair visible ABOVE the hat's lower edge line, in head-local frame (head tilt is rigid, so only cap offsets can change this)"""
    p=dict(pose); p['head']=0; p['face_x']=0
    cairosvg.svg2png(bytestring=mod.svg_doc(p,ids=False,view=(150,0,300,300)).encode(),write_to='/tmp/hp.png',output_width=600)
    im=np.array(Image.open('/tmp/hp.png').convert('RGBA')).astype(int)
    r,g,b,a=im[:,:,0],im[:,:,1],im[:,:,2],im[:,:,3]
    hair=(a>150)&(r<70)&(g<35)&(b<35)&(r>g+8)
    return int(hair[:int(y_line*2),:].sum())
