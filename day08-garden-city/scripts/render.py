"""Day 08 · Utopia: Ebenezer Howard's 'Group of Slumless Smokeless Cities' (1898, Diagram No. 7), redrawn to scale.

Printed figures (Diagram No. 7): total 66,000 acres, population 250,000; Central City 12,000 acres, pop. 58,000;
six garden cities of 9,000 acres, pop. 32,000 each. Each town proper: 1,000 acres (Howard, ch. 1).
Ring distances not printed as numbers are measured against the diagram's own 2-mile scale bar.
"""
from pathlib import Path
import math,os
R=Path(__file__).resolve().parents[1];os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle
import matplotlib.patheffects as pe
import numpy as np
PAPER,INK,SEPIA,VERM,GREEN,FIELD,FAINT='#f4eddd','#2b2520','#7d6d5a','#b23a24','#7f8c5e','#ebe4c9','#cfc3a6'
F={k:FontProperties(fname=str(R/'fonts'/v)) for k,v in {'serif':'serif.ttf','italic':'serif-italic.ttf','sans':'sans.ttf'}.items()}
ACRE=4046.8564;MILE=1609.344
def r_acres(a):return math.sqrt(a*ACRE/math.pi)/MILE   # radius in miles of a circle of `a` acres
OUTER=r_acres(66000)      # 5.73 mi — whole group
CENTRAL_MUNI=r_acres(12000)  # 2.44 mi — Central City municipal boundary
TOWN=r_acres(1000)        # 0.71 mi — each garden city's built town
CENTRAL_TOWN=1.14         # measured from the diagram (its pink built area)
RING=4.20                 # garden-city centres / inter-municipal canal, measured
RAIL=3.18                 # inter-municipal railway, measured
CITIES=[('Garden City',120),('Gladstone',60),('Justitia',0),('Rurisville',-60),('Philadelphia',-120),('Concord',180)]
fig=plt.figure(figsize=(7.2,9),facecolor=PAPER)
ax=fig.add_axes([.06,.128,.88,.69]);ax.set_aspect('equal');ax.axis('off');V=6.15;ax.set_xlim(-V,V);ax.set_ylim(-V,V)
t=np.linspace(0,2*np.pi,721)
def ring(r,cx=0,cy=0,**kw):ax.plot(cx+r*np.cos(t),cy+r*np.sin(t),**kw)
def P(r,deg):a=math.radians(deg);return r*math.cos(a),r*math.sin(a)
# countryside
ax.add_patch(Circle((0,0),OUTER,facecolor=FIELD,edgecolor='none',zorder=0))
rng=np.random.default_rng(11)
for _ in range(260):  # sparse field strokes, like an engraver's tint
 r=math.sqrt(rng.random())*OUTER*.98;a=rng.random()*2*np.pi;x,y=r*math.cos(a),r*math.sin(a);d=rng.random()*np.pi;L=.18+rng.random()*.2
 ax.plot([x-L*math.cos(d)/2,x+L*math.cos(d)/2],[y-L*math.sin(d)/2,y+L*math.sin(d)/2],color=GREEN,lw=.3,alpha=.35,zorder=1)
ring(OUTER,color=INK,lw=1.2,zorder=8)
# municipal boundaries: Central City circle + six radial lines between garden-city sectors
ring(CENTRAL_MUNI,color=SEPIA,lw=.6,ls=(0,(4,3)),zorder=2)
for k in range(6):
 a=30+60*k;ax.plot(*zip(P(CENTRAL_MUNI,a),P(OUTER,a)),color=SEPIA,lw=.6,ls=(0,(4,3)),zorder=2)
# inter-municipal railway ring and radial main lines (ink with paper ties = railway symbol)
def rail(xs,ys,lw=2.0,z=4):
 ax.plot(xs,ys,color=INK,lw=lw,zorder=z,solid_capstyle='butt');ax.plot(xs,ys,color=PAPER,lw=lw*.45,ls=(0,(2.2,2.2)),zorder=z+.1,solid_capstyle='butt')
rail(RAIL*np.cos(t),RAIL*np.sin(t))
for _,a in CITIES:
 x0,y0=P(CENTRAL_TOWN,a);x1,y1=P(OUTER,a);rail([x0,x1],[y0,y1],1.6)
# canals: inter-municipal ring through the towns + Grand Canal east–west to the sea (double line)
def canal(xs,ys,z=3):
 ax.plot(xs,ys,color=SEPIA,lw=3.4,zorder=z,solid_capstyle='butt');ax.plot(xs,ys,color=FIELD,lw=1.9,zorder=z+.1,solid_capstyle='butt')
canal(RING*np.cos(t),RING*np.sin(t))
canal([-OUTER,OUTER],[-.17,-.17])
def town(cx,cy,r,col,lw=1.1):
 ax.add_patch(Circle((cx,cy),r*1.12,facecolor=FIELD,edgecolor='none',zorder=5))         # allotment margin
 ax.add_patch(Circle((cx,cy),r,facecolor=PAPER,edgecolor=col,lw=lw,zorder=6))
 ring(r*.62,cx,cy,color=GREEN,lw=1.6*r/TOWN,alpha=.75,zorder=6.2)                        # Grand Avenue
 ax.add_patch(Circle((cx,cy),r*math.sqrt(.15),facecolor=GREEN,alpha=.55,edgecolor='none',zorder=6.3))  # central park
 for k in range(6):a=math.radians(90+60*k);ax.plot([cx,cx+r*math.cos(a)],[cy,cy+r*math.sin(a)],color=col,lw=.45,zorder=6.4)
 ring(r*.96,cx,cy,color=col,lw=.5,zorder=6.5)
town(0,0,CENTRAL_TOWN,INK,1.3)
halo=[pe.withStroke(linewidth=3,foreground=FIELD)]
for name,a in CITIES:
 cx,cy=P(RING,a);phl=name=='Philadelphia';col=VERM if phl else INK
 town(cx,cy,TOWN,col,1.8 if phl else 1.1)
 if abs(math.sin(math.radians(a)))<.1: lx,ly=cx,cy+TOWN+.62           # east/west towns: label above
 else: lx,ly=P(RING+TOWN+.55,a)
 ax.text(lx,ly+.12,name,fontproperties=F['serif'],fontsize=13 if phl else 11,color=col,ha='center',va='center',zorder=9,path_effects=halo)
 ax.text(lx,ly-.2,'32,000',fontproperties=F['sans'],fontsize=5.6,color=col if phl else SEPIA,ha='center',va='center',zorder=9,path_effects=halo)
ax.text(0,-CENTRAL_TOWN-.3,'Central City',fontproperties=F['serif'],fontsize=12,color=INK,ha='center',va='center',zorder=9,path_effects=halo)
ax.text(0,-CENTRAL_TOWN-.6,'58,000',fontproperties=F['sans'],fontsize=5.6,color=SEPIA,ha='center',va='center',zorder=9,path_effects=halo)
# Howard's countryside, labelled where he put things (positions from the diagram)
for s,x,y in [('New forest',0,1.95),('Large farms',2.25,1.2),('Epileptic farms',0,2.62),('Insane asylum',.25,-2.0),('Home for inebriates',-1.7,-1.15),
 ('Homes for waifs',-2.15,1.82),('Brickfields',-4.15,2.75),('Cemetery',4.55,2.5),('Agricultural college',2.95,-2.55),('College for the blind',3.45,-3.55),
 ('Industrial homes',-4.25,-2.7),('Convalescent homes',-.62,5.25),('Stone quarries',.95,5.05),('New forests',3.35,-1.5)]:
 ax.text(x,y,s,fontproperties=F['italic'],fontsize=6.4,color=SEPIA,ha='center',va='center',zorder=7,path_effects=halo)
for s,x,y,rot in [('INTER-MUNICIPAL RAILWAY',-2.62,-1.95,37),('INTER-MUNICIPAL CANAL',0,3.95,0),('GRAND CANAL',-2.05,-.42,0),('TO THE SEA →',5.3,-.45,0)]:
 ax.text(x,y,s,fontproperties=F['sans'],fontsize=4.6,color=INK,ha='center',va='center',rotation=rot,zorder=9,path_effects=halo)
# scale bar in Howard's miles
sx,sy=-5.9,-5.95
for i in range(2):ax.add_patch(plt.Rectangle((sx+i,sy),1,.07,facecolor=INK if i==0 else PAPER,edgecolor=INK,lw=.5,zorder=9))
for v,s in [(0,'0'),(1,'1'),(2,'2 miles')]:ax.text(sx+v,sy+.2,s,fontproperties=F['sans'],fontsize=5,color=SEPIA,ha='center' if v<2 else 'left',zorder=9)
# legend (right corner)
lx,ly=3.6,-5.55
rail([lx,lx+.5],[ly+.42,ly+.42],1.6);ax.text(lx+.62,ly+.42,'Railways',fontproperties=F['sans'],fontsize=5,color=SEPIA,va='center')
canal([lx,lx+.5],[ly+.1,ly+.1],9);ax.text(lx+.62,ly+.1,'Canals',fontproperties=F['sans'],fontsize=5,color=SEPIA,va='center')
ax.plot([lx,lx+.5],[ly-.22,ly-.22],color=SEPIA,lw=.6,ls=(0,(4,3)));ax.text(lx+.62,ly-.22,'Municipal boundaries',fontproperties=F['sans'],fontsize=5,color=SEPIA,va='center')
# titles
fig.text(.06,.955,'THOMAS HAGOS  /  30-DAY MAP CHALLENGE 2026',fontproperties=F['sans'],fontsize=5.6,color=SEPIA)
fig.text(.94,.955,'DAY 08  ·  UTOPIA',fontproperties=F['sans'],fontsize=5.6,color=SEPIA,ha='right')
fig.text(.5,.915,'The Social City',fontproperties=F['serif'],fontsize=32,color=INK,ha='center')
fig.text(.5,.888,'Ebenezer Howard’s group of “slumless, smokeless cities,” 1898, redrawn to scale.\n250,000 people in seven towns, joined by rail and canal, with farms and forests between them.',fontproperties=F['italic'],fontsize=9,color=SEPIA,ha='center',va='top',linespacing=1.45)
fig.text(.5,.846,'One of the towns is named Philadelphia.',fontproperties=F['italic'],fontsize=9.5,color=VERM,ha='center',va='top')
fig.text(.5,.1,'Each garden city: 9,000 acres, a town of 1,000 acres at its heart  ·  Central City: 12,000 acres  ·  whole group: 66,000 acres',fontproperties=F['sans'],fontsize=5.2,color=SEPIA,ha='center')
fig.text(.5,.078,'Source: Ebenezer Howard, To-morrow: A Peaceful Path to Real Reform (London, 1898), Diagram No. 7, “Group of Slumless Smokeless Cities”;\ndropped from the 1902 edition, Garden Cities of To-morrow. Areas and populations as printed. Ring distances measured against the diagram’s own\nscale bar. Each town is drawn with the plan of Howard’s Diagram No. 2. Countryside labels are Howard’s, in his words and roughly where he put them.',fontproperties=F['sans'],fontsize=4.5,color=SEPIA,ha='center',va='top',linespacing=1.55)
(R/'outputs').mkdir(exist_ok=True);fig.savefig(R/'outputs/the-social-city.png',dpi=300,facecolor=PAPER);plt.close(fig)
from PIL import Image
im=Image.open(R/'outputs/the-social-city.png');w,h=im.size
# Thumbnail: the six towns and centre, cropped square from the map.
s=int(w*.82);cx,cy=w//2,int(h*(1-(.128+.69/2)))
im.crop((cx-s//2,cy-s//2,cx+s//2,cy+s//2)).resize((600,600),Image.Resampling.LANCZOS).save(R/'outputs/08-thomas-hagos.png')
print('Rendered',im.size)
