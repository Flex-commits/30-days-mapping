"""Day 07 · 10 minute map: how far sunlight travels in ten minutes, planets placed for 7 Nov 2026."""
from pathlib import Path
import math,os,datetime
R=Path(__file__).resolve().parents[1];os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
PAPER,INK,SEPIA,VERM,FAINT='#f4eddd','#2b2520','#7d6d5a','#b23a24','#d9cdb4'
F={k:FontProperties(fname=str(R/'fonts'/v)) for k,v in {'serif':'serif.ttf','italic':'serif-italic.ttf','sans':'sans.ttf'}.items()}
AU,C=149597870.7,299792.458;MIN=60*C/AU  # AU travelled by light per minute
# JPL approximate Keplerian elements (Standish, valid 1800–2050): a, da, e, de, L, dL, varpi, dvarpi (per Julian century)
EL={'Mercury':(0.38709927,0.00000037,0.20563593,0.00001906,252.25032350,149472.67411175,77.45779628,0.16047689),
'Venus':(0.72333566,0.00000390,0.00677672,-0.00004107,181.97909950,58517.81538729,131.60246718,0.00268329),
'Earth':(1.00000261,0.00000562,0.01671123,-0.00004392,100.46457166,35999.37244981,102.93768193,0.32327364),
'Mars':(1.52371034,0.00001847,0.09339410,0.00007882,-4.55343205,19140.30268499,-23.94362959,0.44441088)}
DATE=datetime.datetime(2026,11,7,tzinfo=datetime.timezone.utc);T=(2440587.5+DATE.timestamp()/86400-2451545)/36525
def body(a,da,e,de,L,dL,w,dw):
 a+=da*T;e+=de*T;L+=dL*T;w+=dw*T;M=math.radians((L-w)%360);E=M
 for _ in range(30):E-=(E-e*math.sin(E)-M)/(1-e*math.cos(E))
 r=a*(1-e*math.cos(E));nu=2*math.atan2(math.sqrt(1+e)*math.sin(E/2),math.sqrt(1-e)*math.cos(E/2));th=nu+math.radians(w)
 f=np.linspace(0,2*np.pi,721);ro=a*(1-e*e)/(1+e*np.cos(f));orb=(ro*np.cos(f+math.radians(w)),ro*np.sin(f+math.radians(w)))
 return r,th,orb
fig=plt.figure(figsize=(7.2,9),facecolor=PAPER);ax=fig.add_axes([0.075,0.115,0.85,0.68],facecolor=PAPER);ax.set_aspect('equal');ax.axis('off')
V=1.70;ax.set_xlim(-V,V);ax.set_ylim(-V,V)
t=np.linspace(0,2*np.pi,721)
for m in range(1,10):ax.plot(m*MIN*np.cos(t),m*MIN*np.sin(t),color=FAINT,lw=.45,ls=(0,(1,2.2)),zorder=1)
for m in [2,4,6,8]:
 ang=math.radians(-62);ax.text((m*MIN)*math.cos(ang),(m*MIN)*math.sin(ang),f'{m} min',fontproperties=F['sans'],fontsize=4.6,color=SEPIA,ha='center',va='center',rotation=28,zorder=6,bbox={'facecolor':PAPER,'edgecolor':'none','pad':.6})
R10=10*MIN;ax.plot(R10*np.cos(t),R10*np.sin(t),color=VERM,lw=1.5,zorder=4)
# curved lettering along the ten-minute ring (bottom arc, read left to right)
s='TEN MINUTES OF LIGHT';n=len(s);span=math.radians(40);mid=math.radians(-90)
for i,ch in enumerate(s):
 a=mid-span/2+span*i/(n-1);rr=R10+0.055
 ax.text(rr*math.cos(a),rr*math.sin(a),ch,fontproperties=F['serif'],fontsize=8.5,color=VERM,ha='center',va='center',rotation=math.degrees(a)+90,zorder=6)
for k in [0,1,2]:ax.add_patch(plt.Circle((0,0),.045+k*.022,color=VERM,alpha=[1,.25,.1][k],lw=0,zorder=7-k))
ax.text(0,-.11,'Sun',fontproperties=F['italic'],fontsize=9,color=INK,ha='center',va='top',zorder=8)
POS={'Mercury':(1,'left',.06,.0),'Venus':(1,'left',.06,0),'Earth':(1,'left',.07,0),'Mars':(1,'left',.07,0)}
for name,el in EL.items():
 r,th,(ox,oy)=body(*el);ax.plot(ox,oy,color=INK,lw=.55,alpha=.7,zorder=3)
 x,y=r*math.cos(th),r*math.sin(th);s=r*AU/C;inside=s<=600
 ax.add_patch(plt.Circle((x,y),.028 if name in('Earth','Mars') else .022,facecolor=INK if inside else PAPER,edgecolor=INK,lw=.8,zorder=9))
 # labels perpendicular-ish: placed outward along the radial direction, offset sideways
 ux,uy=math.cos(th),math.sin(th);px,py=-uy,ux;lx,ly=x+px*.07,y+py*.07
 ax.text(lx,ly+.03,name,fontproperties=F['italic'],fontsize=10.5,color=INK,ha='right' if px<0 else 'left',va='center',zorder=9)
 ax.text(lx,ly-.05,f'{int(s//60)} min {round(s%60):02d} s',fontproperties=F['sans'],fontsize=5.4,color=VERM if inside else SEPIA,ha='right' if px<0 else 'left',va='center',zorder=9,bbox={'facecolor':PAPER,'edgecolor':'none','pad':.8})
fig.text(.06,.955,'THOMAS HAGOS  /  30-DAY MAP CHALLENGE 2026',fontproperties=F['sans'],fontsize=5.6,color=SEPIA)
fig.text(.94,.955,'DAY 07  ·  10 MINUTE MAP',fontproperties=F['sans'],fontsize=5.6,color=SEPIA,ha='right')
fig.text(.5,.905,'Ten Minutes of Sunlight',fontproperties=F['serif'],fontsize=30,color=INK,ha='center')
fig.text(.5,.872,'Light leaving the Sun reaches Earth in about eight minutes.\nTen minutes on, it has passed us and is still short of Mars.',fontproperties=F['italic'],fontsize=9.5,color=SEPIA,ha='center',va='top',linespacing=1.45)
fig.text(.5,.085,'Filled: reached within ten minutes   ·   Open: not yet   ·   Dotted rings: one light-minute apart',fontproperties=F['sans'],fontsize=5.4,color=SEPIA,ha='center')
fig.text(.5,.052,'Planets placed for 7 November 2026, 00:00 UTC, from JPL approximate Keplerian elements; orbits drawn flat in the ecliptic.\nLight-minute = 17,987,547 km (c = 299,792.458 km/s). Times are Sun-to-planet, not Earth-to-planet.',fontproperties=F['sans'],fontsize=4.6,color=SEPIA,ha='center',va='top',linespacing=1.5)
(R/'outputs').mkdir(exist_ok=True);fig.savefig(R/'outputs/ten-minutes-of-sunlight.png',dpi=300,facecolor=PAPER);plt.close(fig)
from PIL import Image
im=Image.open(R/'outputs/ten-minutes-of-sunlight.png');w,h=im.size;cx,cy=w//2,int(h*.5);s=int(w*.62)
im.crop((cx-s//2,cy-s//2,cx+s//2,cy+s//2)).resize((600,600),Image.Resampling.LANCZOS).save(R/'outputs/07-thomas-hagos.png')
print('Rendered',im.size)
