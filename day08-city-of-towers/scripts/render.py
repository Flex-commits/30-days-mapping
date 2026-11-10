"""Day 08 · Utopia: the storeyed stelae of Aksum, drawn at true height, with a plan of the Northern Stelae Field.

Heights and weights: Great Stele (Stele 1) 33 m, ~520 t, fallen; Stele 2 ("Obelisk of Axum") 24.6 m, ~160 t;
Stele 3 (King Ezana's Stele) 20.6 m, ~160 t, standing. Storeys: Great Stele 13 (as published);
Stele 2 and Stele 3 counted from photographs on Wikimedia Commons (window rows above the false door).
Positions: OpenStreetMap (ODbL), data/stelae-osm.json. The stelae are drawn as stylised elevations,
not measured drawings: heights and storey counts are true, widths and detail are schematic.
"""
from pathlib import Path
import json,math,os
R=Path(__file__).resolve().parents[1];os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Rectangle,Polygon,Circle,FancyArrowPatch
import matplotlib.patheffects as pe
PAPER,INK,SEPIA,VERM,GREEN,FIELD,FAINT='#f4eddd','#2b2520','#7d6d5a','#b23a24','#7f8c5e','#ebe4c9','#cfc3a6'
STONE='#d9cdb3'
F={k:FontProperties(fname=str(R/'fonts'/v)) for k,v in {'serif':'serif.ttf','italic':'serif-italic.ttf','sans':'sans.ttf'}.items()}
STELAE=[  # key, name, height m, storeys, weight, base width m (schematic), x position in elevation, fate
 ('3','King Ezana’s Stele',20.6,9,'about 160 t',2.7,-13,'Still standing.'),
 ('1','The Great Stele',33.0,13,'about 520 t',3.8,0,'Fell and broke, probably\nas it was being raised.'),
 ('2','The Rome Stele',24.6,10,'about 160 t',2.7,13,'Taken to Rome in 1937.\nReturned 2005, raised again 2008.'),
]
fig=plt.figure(figsize=(7.2,9),facecolor=PAPER)
# ---------------- elevation: the three great stelae at true height
ax=fig.add_axes([.06,.335,.88,.475]);ax.axis('off');ax.set_xlim(-22,22);ax.set_ylim(-3.2,36.5);ax.set_aspect('equal')
ax.add_patch(Rectangle((-22,-3.2),44,3.2,facecolor=FIELD,edgecolor='none',zorder=0));ax.plot([-22,22],[0,0],color=INK,lw=.9,zorder=1)
for m in range(5,36,5):  # height guides
 ax.plot([-21.2,21.2],[m,m],color=FAINT,lw=.4,ls=(0,(1,3)),zorder=0)
 ax.text(-21.6,m,f'{m} m',fontproperties=F['sans'],fontsize=4.6,color=SEPIA,ha='right',va='center')
def stele(cx,h,n,w,ghost=False):
 top=w*.78;head=w*.62           # taper, and the rounded headpiece
 body=h-head;bl,br,tl,tr=cx-w/2,cx+w/2,cx-top/2,cx+top/2
 ls=(0,(3,2)) if ghost else '-';fc=PAPER if ghost else STONE;a=1
 ax.add_patch(Polygon([(bl,0),(br,0),(tr,body),(tl,body)],closed=True,facecolor=fc,edgecolor=INK,lw=.8,ls=ls,zorder=3))
 # headpiece: a half-disc on the top, as on the standing stelae
 th=[math.pi*k/40 for k in range(41)];ax.add_patch(Polygon([(cx+top/2*math.cos(t)*1.05,body+head*math.sin(t)) for t in th],closed=True,facecolor=fc,edgecolor=INK,lw=.8,ls=ls,zorder=3))
 door=min(3.4,body*.16)        # false door at the base
 ax.add_patch(Rectangle((cx-w*.18,0),w*.36,door,facecolor='none',edgecolor=INK,lw=.5,ls=ls,zorder=4))
 ax.add_patch(Circle((cx+w*.09,door*.5),w*.025,facecolor=INK,edgecolor='none',zorder=4))
 sh=(body-door-.4)/n           # storeys stacked above the door
 for i in range(n):
  y0=door+.2+i*sh;f=y0/body;hw=(w-(w-top)*f)/2
  ax.plot([cx-hw,cx+hw],[y0,y0],color=INK,lw=.5,ls=ls,zorder=4)                     # floor line
  for k in range(5):                                                                  # beam ends ("monkey heads")
   ax.add_patch(Circle((cx-hw*.8+k*hw*.4,y0+sh*.13),min(.11,sh*.07),facecolor=INK if not ghost else 'none',edgecolor=INK,lw=.3,zorder=4))
  for k in (-1,0,1):                                                                  # a row of false windows
   ax.add_patch(Rectangle((cx+k*hw*.55-hw*.17,y0+sh*.32),hw*.34,sh*.46,facecolor='none',edgecolor=INK,lw=.4,ls=ls,zorder=4))
  ax.text(cx+hw+.35,y0+sh*.5,str(i+1),fontproperties=F['sans'],fontsize=3.9,color=VERM,ha='left',va='center',zorder=5)
 return body+head
halo=[pe.withStroke(linewidth=2.6,foreground=PAPER)]
for key,name,h,n,wt,w,cx,fate in STELAE:
 top=stele(cx,h,n,w,ghost=(key=='1'))
 ax.text(cx,top+1.15,name,fontproperties=F['serif'],fontsize=10.5,color=INK,ha='center',va='bottom',zorder=6,path_effects=halo)
 ax.text(cx,top+.35,f'{h:g} m  ·  {n} storeys  ·  {wt}',fontproperties=F['sans'],fontsize=5,color=SEPIA,ha='center',va='bottom',zorder=6,path_effects=halo)
 ax.text(cx,-.7,f'Stele {key}',fontproperties=F['sans'],fontsize=5,color=INK,ha='center',va='center',zorder=6)
 ax.text(cx,-1.25,fate,va='top',linespacing=1.25,fontproperties=F['italic'],fontsize=5.3,color=VERM if key=='1' else SEPIA,ha='center',zorder=6)
# a person for scale
px=5.2;ax.add_patch(Circle((px,1.58),.13,facecolor=INK,edgecolor='none',zorder=6));ax.plot([px,px],[.75,1.45],color=INK,lw=.9,zorder=6)
ax.plot([px-.2,px,px+.2],[0,.75,0],color=INK,lw=.8,zorder=6);ax.plot([px-.3,px,px+.3],[1.0,1.3,1.0],color=INK,lw=.7,zorder=6)
ax.text(px+.5,1.0,'1.7 m',fontproperties=F['sans'],fontsize=4.4,color=SEPIA,va='center',zorder=6)
ax.text(-6.6,30.6,'The Great Stele is drawn dashed:\nit lies broken on the ground.',fontproperties=F['italic'],fontsize=5.6,color=SEPIA,ha='right',va='top',linespacing=1.35)
ax.text(19.2,30.6,'Red numbers count the storeys\ncarved on each face.',fontproperties=F['italic'],fontsize=5.6,color=VERM,ha='right',va='top',linespacing=1.35)
# ---------------- plan: where they stand, from OpenStreetMap
D=json.loads((R/'data/stelae-osm.json').read_text())['nodes']
lat0,lon0=14.1322,38.7193;ky=110_600;kx=111_320*math.cos(math.radians(lat0))
def xy(n):return (n['lon']-lon0)*kx,(n['lat']-lat0)*ky
pa=fig.add_axes([.06,.085,.40,.215]);pa.set_aspect('equal');pa.axis('off')
NAMED={'Stele 1':'1','Stele 2':'2','Main obelisk':'3'}
pts=[(xy(n),NAMED.get(n['name'])) for n in D];pts=[p for p in pts if math.hypot(*p[0])<75]
xs=[p[0][0] for p in pts];ys=[p[0][1] for p in pts];pa.set_xlim(min(xs)-14,max(xs)+14);pa.set_ylim(min(ys)-14,max(ys)+12)
pa.add_patch(Rectangle((min(xs)-14,min(ys)-14),max(xs)-min(xs)+28,max(ys)-min(ys)+26,facecolor=FIELD,edgecolor=FAINT,lw=.6,zorder=0))
for (x,y),k in pts:
 if k:pa.add_patch(Circle((x,y),3.4,facecolor=VERM if k!='1' else PAPER,edgecolor=VERM,lw=.9,zorder=3));pa.text(x,y,k,fontproperties=F['sans'],fontsize=5.4,color=PAPER if k!='1' else VERM,ha='center',va='center',zorder=4)
 else:pa.add_patch(Circle((x,y),1.3,facecolor=INK,edgecolor='none',zorder=2))
sx,sy=min(xs)-10,min(ys)-10
for i in range(2):pa.add_patch(Rectangle((sx+i*10,sy),10,1,facecolor=INK if i==0 else PAPER,edgecolor=INK,lw=.4,zorder=5))
pa.text(sx,sy+2.2,'0',fontproperties=F['sans'],fontsize=4.4,color=SEPIA,ha='center');pa.text(sx+20,sy+2.2,'20 m',fontproperties=F['sans'],fontsize=4.4,color=SEPIA,ha='center')
nx,ny=max(xs)+8,max(ys)-2;pa.annotate('',xy=(nx,ny+7),xytext=(nx,ny),arrowprops={'arrowstyle':'-|>','lw':.6,'color':INK});pa.text(nx,ny+8.5,'N',fontproperties=F['serif'],fontsize=7,color=INK,ha='center')
fig.text(.06,.307,'WHERE THEY STAND',fontproperties=F['sans'],fontsize=5.6,color=SEPIA)
fig.text(.06,.075,'Northern Stelae Field, Aksum, Tigray, Ethiopia · 14.13° N, 38.72° E\nRed: the three great stelae (1, hollow, is fallen). Black: other stelae. More lie to the north-east. Positions: © OpenStreetMap contributors.',fontproperties=F['sans'],fontsize=4.5,color=SEPIA,va='top',linespacing=1.5)
# ---------------- the argument
tx=.53
fig.text(tx,.307,'WHY THIS IS A UTOPIA',fontproperties=F['sans'],fontsize=5.6,color=SEPIA)
fig.text(tx,.288,'Each stele is one block of granite, carved to look\nlike a tall building: a door at the base, then\nfloor after floor of windows and beam ends.\n\nThe style is real. Aksum’s palaces were built\nof stone and timber with the same beams and\nrecessed walls. But no building known from\nAksum rose anywhere near 13 floors.\n\nThey were raised around the 4th century AD and\nare believed to mark royal tombs. They show\na city that existed only in stone: an ideal,\ncarved for the dead.',fontproperties=F['serif'],fontsize=7.6,color=INK,va='top',linespacing=1.42)
# ---------------- titles
fig.text(.06,.955,'THOMAS HAGOS  /  30-DAY MAP CHALLENGE 2026',fontproperties=F['sans'],fontsize=5.6,color=SEPIA)
fig.text(.94,.955,'DAY 08  ·  UTOPIA',fontproperties=F['sans'],fontsize=5.6,color=SEPIA,ha='right')
fig.text(.5,.905,'A City of Towers',fontproperties=F['serif'],fontsize=34,color=INK,ha='center')
fig.text(.5,.879,'The storeyed stelae of Aksum, Ethiopia, drawn at their true height.',fontproperties=F['italic'],fontsize=9.5,color=SEPIA,ha='center',va='top')
fig.text(.5,.856,'Aksum carved skyscrapers it never built.',fontproperties=F['italic'],fontsize=11,color=VERM,ha='center',va='top')
fig.text(.5,.032,'Sources: heights and weights as commonly published (Wikipedia, “Obelisk of Axum” and “King Ezana’s Stele”). The Great Stele’s 13 storeys as published;\nstoreys on Steles 2 and 3 counted from photographs on Wikimedia Commons. Elevations are schematic: heights and storey counts are true, widths and carving are simplified.',fontproperties=F['sans'],fontsize=4.2,color=SEPIA,ha='center',va='top',linespacing=1.55)
(R/'outputs').mkdir(exist_ok=True);fig.savefig(R/'outputs/city-of-towers.png',dpi=300,facecolor=PAPER);plt.close(fig)
from PIL import Image
im=Image.open(R/'outputs/city-of-towers.png');w,h=im.size
# Thumbnail: the three stelae, cropped square from the elevation.
s=int(h*.49);cx,cy=w//2,int(h*(1-(.335+.475/2)))
im.crop((cx-s//2,cy-s//2,cx+s//2,cy+s//2)).resize((600,600),Image.Resampling.LANCZOS).save(R/'outputs/08-thomas-hagos.png')
print('Rendered',im.size)
