"""Day 08 · Utopia: Ebenezer Howard's Garden City, drawn to scale from the dimensions in his text."""
from pathlib import Path
import math,os
R=Path(__file__).resolve().parents[1];os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle,Wedge
import numpy as np
PAPER,INK,SEPIA,VERM,GREEN,FIELD='#f4eddd','#2b2520','#7d6d5a','#b23a24','#8a9a6a','#e8e2c8'
F={k:FontProperties(fname=str(R/'fonts'/v)) for k,v in {'serif':'serif.ttf','italic':'serif-italic.ttf','sans':'sans.ttf'}.items()}
AC=4046.8564
def r_ac(a):return math.sqrt(a*AC/math.pi)
# Radii (m) from Howard: 6,000-acre estate; 1,000-acre town, 1,240 yd centre to edge;
# 5½-acre central garden; 145-acre Central Park; Crystal Palace arcade; Grand Avenue 420 ft wide; factories at the rim.
TOWN=1240*.9144;FARM=r_ac(6000);GARD=r_ac(5.5);PARK=r_ac(5.5+145);GA_MID=TOWN*.62;GA_W=420*.3048
fig=plt.figure(figsize=(7.2,9),facecolor=PAPER);ax=fig.add_axes([.06,.12,.88,.704]);ax.set_aspect('equal');ax.axis('off');V=FARM*1.04;ax.set_xlim(-V,V);ax.set_ylim(-V,V)
ax.add_patch(Circle((0,0),FARM,facecolor=FIELD,edgecolor=INK,lw=.9))
rng=np.random.default_rng(7)
for a in np.linspace(0,2*np.pi,90,endpoint=False):  # field hatching in the agricultural belt
 r0=TOWN+90+rng.random()*80;r1=FARM-60-rng.random()*120;ax.plot([r0*math.cos(a),r1*math.cos(a)],[r0*math.sin(a),r1*math.sin(a)],color=GREEN,lw=.35,alpha=.5)
ax.add_patch(Circle((0,0),TOWN,facecolor=PAPER,edgecolor=INK,lw=1.1,zorder=3))
ax.add_patch(Circle((0,0),TOWN,fill=False,edgecolor=INK,lw=2.2,ls=(0,(6,3)),zorder=6))  # circular railway
ax.add_patch(Wedge((0,0),TOWN-8,0,360,width=95,facecolor='#d8ccb4',edgecolor='none',zorder=4))  # factories & warehouses
ax.add_patch(Wedge((0,0),GA_MID+GA_W/2,0,360,width=GA_W,facecolor=GREEN,alpha=.55,edgecolor='none',zorder=4))  # Grand Avenue
ax.add_patch(Wedge((0,0),PARK+40,0,360,width=28,facecolor='none',edgecolor=SEPIA,hatch='|||',lw=0,zorder=4))  # Crystal Palace
ax.add_patch(Circle((0,0),PARK,facecolor=GREEN,alpha=.7,edgecolor='none',zorder=4))
ax.add_patch(Circle((0,0),GARD+95,facecolor=PAPER,edgecolor=INK,lw=.6,zorder=5))  # civic ring
ax.add_patch(Circle((0,0),GARD,facecolor=GREEN,edgecolor=INK,lw=.5,zorder=6))
for k in range(6):  # six boulevards, 120 ft wide, dividing six wards
 a=math.radians(90+60*k);ax.plot([0,TOWN*math.cos(a)],[0,TOWN*math.sin(a)],color=INK,lw=1.1,zorder=7)
 m=math.radians(120+60*k);ax.text(TOWN*.82*math.cos(m),TOWN*.82*math.sin(m),'WARD',fontproperties=F['sans'],fontsize=5,color=SEPIA,ha='center',va='center',rotation=math.degrees(m)-90,zorder=8)
def lab(x,y,s,size=8,font='italic',color=INK,**kw):ax.text(x,y,s,fontproperties=F[font],fontsize=size,color=color,ha='center',va='center',zorder=9,bbox={'facecolor':PAPER,'edgecolor':'none','pad':1,'alpha':.85},**kw)
lab(0,0,'Garden',6.5);lab(0,-PARK*.62,'Central Park',8);lab(PARK*.95,PARK*.55,'Crystal Palace',6.5)
lab(0,GA_MID,'Grand Avenue',8);lab(-TOWN*.86,-TOWN*.62,'Factories · rail',6.5)
lab(0,-(TOWN+FARM)/2,'Agricultural belt  ·  5,000 acres',9,'serif')
lab(0,(TOWN+FARM)/2,'Farms, allotments, orchards, homes for the aged',7)
# scale bar: 1 km
x0=-FARM*.95;y0=-FARM*1.0;ax.plot([x0,x0+1000],[y0,y0],color=INK,lw=1.4);ax.text(x0+500,y0+90,'1 km',fontproperties=F['sans'],fontsize=6,color=SEPIA,ha='center')
fig.text(.06,.955,'THOMAS HAGOS  /  30-DAY MAP CHALLENGE 2026',fontproperties=F['sans'],fontsize=5.6,color=SEPIA)
fig.text(.94,.955,'DAY 08  ·  UTOPIA',fontproperties=F['sans'],fontsize=5.6,color=SEPIA,ha='right')
fig.text(.5,.905,'The Garden City',fontproperties=F['serif'],fontsize=32,color=INK,ha='center')
fig.text(.5,.872,'Ebenezer Howard’s town of tomorrow, drawn to scale from his 1898 text.\n30,000 people on 1,000 acres, held inside 5,000 acres of countryside.',fontproperties=F['italic'],fontsize=9.5,color=SEPIA,ha='center',va='top',linespacing=1.45)
fig.text(.5,.085,'Town: 1,240 yards from centre to edge  ·  six boulevards, six wards  ·  Grand Avenue 420 ft wide  ·  circular railway at the rim',fontproperties=F['sans'],fontsize=5.2,color=SEPIA,ha='center')
fig.text(.5,.06,'Source: Ebenezer Howard, To-morrow: A Peaceful Path to Real Reform (1898), reissued as Garden Cities of To-morrow (1902). Ring widths not given\nin the text (civic ring, factory belt, Grand Avenue position) are estimated. A diagram, as Howard warned, not a plan for any site.',fontproperties=F['sans'],fontsize=4.6,color=SEPIA,ha='center',va='top',linespacing=1.5)
fig.savefig(R/'outputs/the-garden-city.png',dpi=300,facecolor=PAPER);plt.close(fig)
from PIL import Image
im=Image.open(R/'outputs/the-garden-city.png');w,h=im.size;s=int(w*.8);cx,cy=w//2,int(h*.53)
im.crop((cx-s//2,cy-s//2,cx+s//2,cy+s//2)).resize((600,600),Image.Resampling.LANCZOS).save(R/'outputs/08-thomas-hagos.png');print('ok',im.size)
