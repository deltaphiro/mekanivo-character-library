"""UCUP chest logo "m." rebuilt as clean vector from the reference (measured geometry, not a raster crop).
Unit box: m = 505 x 365, dot centre (489,288) r 76 -> overall 565 x 365.  y down."""
LW, LH = 565.0, 365.0
P = {'x1': 90.8, 'x2': 203.8, 'x3': 295, 'x4': 407.4, 'x5': 504, 'rc': 57, 'arch_y': 133.4, 'base': 365, 'tl_y': 31.2, 'tl_c1': (-3.3, 23.2), 'tl_c2': (45.3, 10.7), 'pk1': (132.0, 1.1), 'a1c1': (195.9, -0.7), 'a1c2': (226.7, 15.7), 'notch': (255, 42), 'a2c1': (274.2, 27.0), 'a2c2': (299.8, 6.5), 'pk2': (362.0, -1.3), 'r1': (440.7, -10.0), 'r2': (509.4, 45.2), 're': (504.0, 124.8), 'cut0': (504.0, 144.7), 'cutq': (498.2, 146.6), 'cut1': (502.4, 156.3), 'cut2': (408.0, 206.0), 'dot': (489, 288), 'dr': 76}

def m_path(p=P):
    a, b = p['arch_y'], p['base']; c0 = p['cut0'][1]
    return (f"M0 {b} L0 {p['tl_y']} C{p['tl_c1'][0]} {p['tl_c1'][1]} {p['tl_c2'][0]} {p['tl_c2'][1]} {p['pk1'][0]} {p['pk1'][1]} "
            f"C{p['a1c1'][0]} {p['a1c1'][1]} {p['a1c2'][0]} {p['a1c2'][1]} {p['notch'][0]} {p['notch'][1]} "
            f"C{p['a2c1'][0]} {p['a2c1'][1]} {p['a2c2'][0]} {p['a2c2'][1]} {p['pk2'][0]} {p['pk2'][1]} "
            f"C{p['r1'][0]} {p['r1'][1]} {p['r2'][0]} {p['r2'][1]} {p['re'][0]} {p['re'][1]} L504 {c0} C504 {c0 + 8} 500 {c0 + 12} 494 {c0 + 15} "
            f"L{p['cut2'][0]} {p['cut2'][1]} L{p['x4']} {a} A{p['rc'] - 0.5} {p['rc']} 0 0 0 {p['x3']} {a} L{p['x3']} {b} L{p['x2']} {b} L{p['x2']} {a} "
            f"A{p['rc']} {p['rc']} 0 0 0 {p['x1']} {a} L{p['x1']} {b} Z")

def logo_group(cx, cy, width, white='#FFFFFF', orange='#FA9112', gid=None, clip=None, p=P):
    """centred at (cx,cy); width = overall width incl. dot"""
    s = width / LW
    idattr = f' id="{gid}"' if gid else ''
    cl = f' clip-path="url(#{clip})"' if clip else ''
    return (f'<g{idattr}{cl}><g transform="translate({cx:.2f} {cy:.2f}) scale({s:.5f}) translate({-LW / 2:.1f} {-LH / 2:.1f})">'
            f'<path d="{m_path(p)}" fill="{white}"/><circle cx="{p["dot"][0]}" cy="{p["dot"][1]}" r="{p["dr"]}" fill="{orange}"/></g></g>')
