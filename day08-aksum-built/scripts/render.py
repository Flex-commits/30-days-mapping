"""Day 08 Utopia: an imagined Aksum skyline on sourced modern terrain.

Tower heights are artistic scenario choices, not historical reconstructions or
site-specific structural capacities. Source dimensions inspire the height module.
"""
from pathlib import Path
import json,math,os
R=Path(__file__).resolve().parents[1];os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Polygon,Rectangle
import matplotlib.patheffects as pe
import numpy as np
PAPER,INK,SEPIA,VERM,GREEN,FIELD,FAINT='#f4eddd','#2b2520','#7d6d5a','#b23a24','#7f8c5e','#ebe4c9','#cfc3a6'
FRONT,SIDE,TOP,WATER,HOUSE='#e9bca6','#c98f78','#f5dfd1','#c9d2c6','#ebe3d2'
F={k:FontProperties(fname=str(R/'fonts'/v)) for k,v in {'serif':'serif.ttf','italic':'serif-italic.ttf','sans':'sans.ttf'}.items()}
CFIG=json.loads((R/'config.json').read_text());STOREY=CFIG['storey_metres'];PODIUM=CFIG['podium_metres'];LIMIT=CFIG['maximum_chosen_storeys'];BUILDINGS=[]
from pyproj import Transformer
UTM=Transformer.from_crs(4326,32637,always_xy=True)
def height(n):return PODIUM+n*STOREY
# ------------------------------------------------------------------ data
T=np.load(R/'data/terrain.npz');Z=T['z'];LAT_TOP=float(T['lat_top']);LON_L=float(T['lon_left']);STEP=float(T['step'])
S=json.loads((R/'data/sites.json').read_text());SITE={s['name']:s for s in S['sites']}
LAT0=LAT_TOP-(Z.shape[0]-1)*STEP;LONC=38.7175;KY=110_600;KX=111_320*math.cos(math.radians(14.13))
C,VE,ZB=CFIG['north_foreshortening'],CFIG['vertical_exaggeration'],2090      # depth foreshortening, vertical exaggeration (ground and buildings alike), datum
def zat(lat,lon):          # bilinear terrain height
 r=(LAT_TOP-lat)/STEP;c=(lon-LON_L)/STEP;r0,c0=int(r),int(c);assert 0<=r<Z.shape[0]-1 and 0<=c<Z.shape[1]-1, (lat,lon);fr,fc=r-r0,c-c0
 return float(Z[r0,c0]*(1-fr)*(1-fc)+Z[r0+1,c0]*fr*(1-fc)+Z[r0,c0+1]*(1-fr)*fc+Z[r0+1,c0+1]*fr*fc)
def scr(lat,lon,z=None):
 z=zat(lat,lon) if z is None else z
 x,y=UTM.transform(lon,lat);return x-ORIGIN[0],(y-ORIGIN[1])*C+(z-ZB)*VE
ORIGIN=UTM.transform(LONC,LAT0)
def row_of(lat):return int((LAT_TOP-lat)/STEP)+1   # first terrain row drawn in front of this latitude
fig=plt.figure(figsize=(7.2,9),facecolor=PAPER)
ax=fig.add_axes([.02,.425,.96,.415]);ax.axis('off')
# ------------------------------------------------------------------ terrain, back to front
lons=np.linspace(LON_L,LON_L+(Z.shape[1]-1)*STEP,420);cols=(lons-LON_L)/STEP
XX,YY=UTM.transform(lons,np.full_like(lons,14.13));X=XX-ORIGIN[0];YBOT=-300
for i in range(Z.shape[0]):
 lat=LAT_TOP-i*STEP;z=np.interp(cols,np.arange(Z.shape[1]),Z[i])
 _,yn=UTM.transform(lons,np.full_like(lons,lat));y=(yn-ORIGIN[1])*C+(z-ZB)*VE;zo=10+i
 ax.fill_between(X,y,YBOT,color=PAPER,lw=0,zorder=zo)
 if i%2==0 or i==Z.shape[0]-1:ax.plot(X,y,color=INK if i%10==0 else SEPIA,lw=.4 if i%10==0 else .3,zorder=zo+.01)
# ------------------------------------------------------------------ buildings
def box(lat,lon,n,w,d,col=VERM,front=FRONT,side=SIDE,top=TOP,lw=.45,setback=True,zbump=.5):
 BUILDINGS.append({'lat':float(lat),'lon':float(lon),'storeys':int(n),'height_metres':height(n),'width_metres':float(w),'depth_metres':float(d),'kind':'imagined home' if col==SEPIA else 'imagined landmark tower','basis':'illustrative scenario, not surveyed/reconstructed building geometry'});X0,Y0=scr(lat,lon);zo=10+row_of(lat)+zbump;dx,dy=d*.38,d*C
 tiers=[(PODIUM,w*1.18,d*1.1)]
 if setback and n>=6:a=math.ceil(n*.62);b=math.ceil((n-a)*.6);tiers+=[(a*STOREY,w,d),(b*STOREY,w*.8,d*.8),((n-a-b)*STOREY,w*.6,d*.6)]
 else:tiers+=[(n*STOREY,w,d)]
 y=Y0;floors=[]
 for k,(h,ww,dd) in enumerate(tiers):
  if h<=0:continue
  H=h*VE;x0,x1=X0-ww/2,X0+ww/2;ddx,ddy=dd*.38,dd*C
  ax.add_patch(Polygon([(x1,y),(x1+ddx,y+ddy),(x1+ddx,y+ddy+H),(x1,y+H)],closed=True,facecolor=side,edgecolor=col,lw=lw,zorder=zo))
  ax.add_patch(Rectangle((x0,y),ww,H,facecolor=front,edgecolor=col,lw=lw,zorder=zo+.01))
  ax.add_patch(Polygon([(x0,y+H),(x1,y+H),(x1+ddx,y+H+ddy),(x0+ddx,y+H+ddy)],closed=True,facecolor=top,edgecolor=col,lw=lw,zorder=zo+.02))
  if k>0:
   m=int(round(h/STOREY))
   for j in range(1,m):ax.plot([x0,x1],[y+j*STOREY*VE]*2,color=col,lw=.22,zorder=zo+.03)
   if ww>12:
    for j in range(m):ax.plot([X0-ww*.18,X0+ww*.18],[y+(j+.55)*STOREY*VE]*2,color=col,lw=.5,alpha=.55,zorder=zo+.03)  # window band
  y+=H
 return X0,y+d*C   # top-of-building point (screen)
labels=[]
def tower(lat,lon,n,w,d,label=None,**kw):
 xt,yt=box(lat,lon,n,w,d,**kw)
 if label:labels.append((xt,yt)+label)
# Houses: three chosen storeys, at reproducibly imagined positions.
rng=np.random.default_rng(CFIG['house_seed']);core=[(14.1305,38.7195),(14.1265,38.7090),(14.1270,38.7240)]
houses=[]
while len(houses)<85:
 la=14.1235+rng.random()*.014;lo=38.7035+rng.random()*.028
 if min(math.hypot((la-a)*KY,(lo-b)*KX) for a,b in core)>420:continue
 g=abs(zat(la+.0003,lo)-zat(la-.0003,lo))+abs(zat(la,lo+.0003)-zat(la,lo-.0003))
 if g>9:continue
 if any(math.hypot((la-a)*KY,(lo-b)*KX)<55 for a,b in houses):continue
 houses.append((la,lo))
TOWERS=[(14.13180,38.71893),(14.13195,38.71919),(14.13213,38.71928),(SITE['Dungur / Palace of Queen of Sheba']['lat'],SITE['Dungur / Palace of Queen of Sheba']['lon'])]
for la,lo in houses:
 if min(math.hypot((la-a)*KY,(lo-b)*KX) for a,b in [(s['lat'],s['lon']) for s in S['sites']])<75:continue
 box(la,lo,3,16+rng.random()*10,14,col=SEPIA,front=HOUSE,side='#cdbfa5',top='#efe6d4',lw=.25,setback=False,zbump=.4)
# Mai Shum reservoir (real)
ms=SITE['Baths of Queen Sheba'];zw=zat(ms['lat'],ms['lon'])-2
ring=[scr(ms['lat']+38*math.sin(t)/KY,ms['lon']+60*math.cos(t)/KX,zw) for t in np.linspace(0,2*math.pi,60)]
ax.add_patch(Polygon(ring,closed=True,facecolor=WATER,edgecolor=SEPIA,lw=.5,zorder=10+row_of(ms['lat']-38/KY)+.6))
# Other stelae become small towers (5–7 storeys)
for k,s in enumerate(S['other_stelae']+[SITE[n] for n in ('Stele 4','Stele 6','Stele 7')]):
 box(s['lat'],s['lon'],5+k%3,9,8,setback=False,lw=.3)
# The named towers
def at(n):return SITE[n]['lat'],SITE[n]['lon']
tower(*at('Stele 1'),13,22,16)
tower(*at('Stele 2'),10,18,14,zbump=.45)
tower(*at('Main obelisk'),9,18,14,('Northern Stelae Field',f'three imagined towers at the stelae:\n13, 10 and 9 storeys  ·  {height(13):.0f}, {height(10):.0f} and {height(9):.0f} m',.50,.93,'center'),zbump=.4)
tower(*at('Dungur / Palace of Queen of Sheba'),19,55,52,('Dungur palace',f'19 storeys  ·  {height(19):.0f} m',.13,.80,'center'))
tower(*at("Enda Nebura'ed Palace Ruins"),8,46,40,('Enda Nebura’ed',f'8 storeys  ·  {height(8):.0f} m',.97,.50,'right'))
tower(*at('Church of Our Lady Mary of Zion'),12,34,30,('Church of Mary of Zion',f'12 storeys  ·  {height(12):.0f} m',.30,.62,'center'))
tower(*at('tomb of king bazen'),6,20,18,('Tomb of King Bazen',f'6 storeys  ·  {height(6):.0f} m',.90,.33,'center'))
tower(*at('Ezana Inscription'),7,18,16,('Ezana’s inscription',f'gate, 7 storeys  ·  {height(7):.0f} m',.62,.80,'center'))
kl,ko=at('Tombs of Kings Kaleb and Gebremeskel')
tower(kl,ko-28/KX,11,20,18,('Tombs of Kaleb and Gebre Meskel',f'twin towers, 11 storeys  ·  {height(11):.0f} m',.86,.93,'center'))
box(kl,ko+28/KX,11,20,18)
halo=[pe.withStroke(linewidth=3.6,foreground=PAPER)]
ax.set_xlim(X[0],X[-1]);YL=(-110,1660);ax.set_ylim(*YL);ax.set_aspect('equal')
for xt,yt,name,line,fx,fy,ha in labels:
 xl=X[0]+fx*(X[-1]-X[0]);yl=YL[0]+fy*(YL[1]-YL[0])
 ax.plot([xt,xl],[yt+6,yl-40],color=VERM,lw=.45,zorder=300)
 ax.text(xl,yl,line,fontproperties=F['sans'],fontsize=4.8,color=VERM,ha=ha,va='bottom',linespacing=1.35,zorder=301,path_effects=halo)
 ax.text(xl,yl+(100 if '\n' in line else 46),name,fontproperties=F['serif'],fontsize=8.4,color=INK,ha=ha,va='bottom',zorder=301,path_effects=halo)
xm,ym=scr(ms['lat']-40/KY,ms['lon']+70/KX);ax.text(xm+40,ym-10,'Mai Shum · schematic',fontproperties=F['italic'],fontsize=6,color=SEPIA,ha='left',va='top',zorder=301,path_effects=halo)
# frame: scale bar and view note
sx=X[0]+120;sy=-75
for i in range(2):ax.add_patch(Rectangle((sx+i*250,sy),250,14,facecolor=INK if i==0 else PAPER,edgecolor=INK,lw=.4,zorder=400))
ax.text(sx,sy+30,'0',fontproperties=F['sans'],fontsize=4.6,color=SEPIA,ha='center',zorder=400);ax.text(sx+500,sy+30,'500 m',fontproperties=F['sans'],fontsize=4.6,color=SEPIA,ha='center',zorder=400)
ax.text(X[-1]-100,sy+6,f'LOOKING NORTH  ·  VERTICAL EXAGGERATION {VE:g}×  ·  IMAGINED BUILDINGS',fontproperties=F['sans'],fontsize=4.6,color=SEPIA,ha='right',va='center',zorder=400)
# ------------------------------------------------------------------ Yeha panel (true scale)
fig.text(.06,.392,'THE INSPIRATION  ·  YEHA, ABOUT 800 BC',fontproperties=F['sans'],fontsize=5.6,color=SEPIA)
ya=fig.add_axes([.06,.16,.40,.22]);ya.set_xlim(-6,132);ya.set_ylim(-9,98);ya.set_aspect('equal');ya.axis('off')
ya.plot([-6,132],[0,0],color=INK,lw=.8)
for m in (20,40,60,80):ya.plot([-6,132],[m,m],color=FAINT,lw=.35,ls=(0,(1,3)),zorder=0);ya.text(-6.5,m,f'{m} m',fontproperties=F['sans'],fontsize=4.2,color=SEPIA,ha='right',va='center')
# Great Temple: stands today to 14 m
ya.add_patch(Rectangle((2,0),18.5,14,facecolor='#d9cdb3',edgecolor=INK,lw=.7));ya.text(11.25,17,'Great Temple',fontproperties=F['serif'],fontsize=6.5,color=INK,ha='center')
ya.text(11.25,-4.2,'14 m, still standing',fontproperties=F['italic'],fontsize=5,color=SEPIA,ha='center')
# Palace: surviving podium, eight-storey reconstruction and a 19-storey illustration.
px,pw=38,47.5
ya.add_patch(Rectangle((px,6),pw,LIMIT*STOREY,facecolor='none',edgecolor=VERM,lw=.7,ls=(0,(3,2))))
for j in range(1,LIMIT):ya.plot([px,px+pw],[6+j*STOREY]*2,color=VERM,lw=.2,alpha=.5)
yy=6
for k,(m,ww) in enumerate([(5,pw),(3,pw*.78)]):
 ya.add_patch(Rectangle((px+(pw-ww)/2,yy),ww,m*STOREY,facecolor=FRONT,edgecolor=VERM,lw=.6));yy+=m*STOREY
ya.add_patch(Rectangle((px-2,0),pw+4,6,facecolor='#d9cdb3',edgecolor=INK,lw=.7))
ya.text(px+pw/2,-4.2,'Grat Be’al Gebri palace',fontproperties=F['italic'],fontsize=5,color=SEPIA,ha='center')
ya.text(px+pw+3,3,'podium survives',fontproperties=F['sans'],fontsize=4.2,color=INK,va='center')
ya.text(px+pw+2,6+4*STOREY,'8 storeys:\nthe excavators’\nreconstruction',fontproperties=F['sans'],fontsize=4.2,color=VERM,va='center',linespacing=1.2)
ya.text(px+pw+2,height(LIMIT)-2,f'19-storey illustration:\n{height(LIMIT):.0f} m with this module',fontproperties=F['sans'],fontsize=4.2,color=VERM,va='top',linespacing=1.2)
ya.add_patch(Rectangle((124,0),3.8,33,facecolor='#d9cdb3',edgecolor=INK,lw=.6));ya.text(126,-4.2,'Aksum stele',fontproperties=F['italic'],fontsize=5,color=SEPIA,ha='center');ya.text(126,35,'33 m',fontproperties=F['sans'],fontsize=4.2,color=INK,ha='center')
fig.text(.06,.152,'Heights to scale. Yeha research is not an Aksum capacity assessment.',fontproperties=F['italic'],fontsize=5.6,color=SEPIA)
# ------------------------------------------------------------------ reading the scenario
lx=.53
fig.text(lx,.392,'READ THE CITY',fontproperties=F['sans'],fontsize=6,color=SEPIA)
items=[('Ground','Modern Copernicus surface elevations,\nnot a reconstruction of the ancient landscape.'),
 ('Places','Landmark anchors from OpenStreetMap.\nThey are approximate, not excavation plans.'),
 ('Towers','All imagined. Storey counts and footprints\nare design choices, not historical evidence.'),
 ('Homes','Illustrative three-storey houses.\nTheir locations are generated with a fixed seed.'),
 ('Heights','6 m podium + 4.32 m per storey.\n19 chosen storeys gives 88.08 m.'),
 ('Scope','The Yeha study concerns wall sections.\nIt does not certify these Aksum towers.')]
y=.367
for h,t in items:
 fig.text(lx,y,h,fontproperties=F['serif'],fontsize=8,color=INK,va='top');fig.text(lx+.085,y-.001,t,fontproperties=F['sans'],fontsize=5.4,color=INK,va='top',linespacing=1.4);y-=.033
# Short production sequence; the view is a contemporary design scenario.
fig.text(.06,.137,'DOCUMENTED GEOGRAPHY → AN IMAGINED SKYLINE',fontproperties=F['sans'],fontsize=6,color=SEPIA)
for x,head,body in [(.06,'01 / Terrain','30 m surface grid'),(.29,'02 / Landmarks','Documented site anchors'),(.53,'03 / Massing','Chosen storeys and footprints'),(.77,'04 / A new view','Oblique, looking north')]:
 fig.text(x,.113,head,fontproperties=F['serif'],fontsize=8,color=INK);fig.text(x,.096,body,fontproperties=F['sans'],fontsize=5.1,color=SEPIA)
# Titles and small Africa locator give geography before the imagined skyline.
fig.text(.06,.962,'THOMAS HAGOS  /  30-DAY MAP CHALLENGE 2026',fontproperties=F['sans'],fontsize=5.6,color=SEPIA)
fig.text(.94,.962,'DAY 08  ·  UTOPIA',fontproperties=F['sans'],fontsize=5.6,color=SEPIA,ha='right')
fig.text(.5,.912,'Aksum, Built',fontproperties=F['serif'],fontsize=34,color=INK,ha='center')
fig.text(.5,.888,'An imagined skyline for Ethiopia’s ancient capital.',fontproperties=F['italic'],fontsize=10,color=SEPIA,ha='center',va='top')
fig.text(.5,.866,'Documented landmarks. Imagined towers and homes.',fontproperties=F['italic'],fontsize=9,color=VERM,ha='center',va='top')
loc=fig.add_axes([.045,.858,.105,.085]);loc.axis('off');loc.set_aspect('equal')
for f in json.loads((R/'data/locator-countries.geojson').read_text())['features']:
 if f['properties'].get('CONTINENT')!='Africa':continue
 geom=f['geometry'];polys=[geom['coordinates']] if geom['type']=='Polygon' else geom['coordinates']
 for v in polys:loc.add_patch(Polygon(v[0],closed=True,fc=VERM if f['properties'].get('ADMIN')=='Ethiopia' else '#ded3bb',ec=PAPER,lw=.2))
loc.plot(38.7193,14.132,'o',color=INK,ms=1.5);loc.set_xlim(-19,53);loc.set_ylim(-36,39);fig.text(.047,.851,'AKSUM / ETHIOPIA',fontproperties=F['sans'],fontsize=4.2,color=SEPIA)
fig.text(.5,.074,'A study-inspired scenario, not an archaeological reconstruction or structural safety assessment.',fontproperties=F['italic'],fontsize=6.2,color=VERM,ha='center')
fig.text(.5,.052,'Inspiration: Drieschner et al. (2023), 8-storey Yeha reconstruction; Drieschner & Schnelle (2026), Yeha wall analysis, as reported by BTU.\nSites: © OpenStreetMap contributors, ODbL. Locator: Natural Earth, public domain. Font: IM FELL English, SIL OFL 1.1. Sources and licenses in the project.',fontproperties=F['sans'],fontsize=4.3,color=SEPIA,ha='center',va='top',linespacing=1.5)
fig.text(.5,.023,'Produced using Copernicus WorldDEM-30 © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018\nprovided under COPERNICUS by the European Union and ESA; all rights reserved.',fontproperties=F['sans'],fontsize=3.8,color=SEPIA,ha='center',va='top',linespacing=1.3)
(R/'outputs').mkdir(exist_ok=True);fig.savefig(R/'outputs/aksum-built.png',dpi=300,facecolor=PAPER);plt.close(fig)
from PIL import Image
im=Image.open(R/'outputs/aksum-built.png');w,h=im.size
# A separate square composition preserves the main view at gallery size.
top=im.crop((0,int(h*.035),w,int(h*.59))).convert('RGB');sq=Image.new('RGB',(w,w),PAPER);sq.paste(top,(0,(w-top.size[1])//2));sq.resize((600,600),Image.Resampling.LANCZOS).save(R/'outputs/08-thomas-hagos.png')
# A large landscape detail makes the skyline easy to inspect online.
im.crop((0,int(h*.15),w,int(h*.60))).save(R/'outputs/aksum-skyline-detail.png')
(R/'data/scenario-buildings.json').write_text(json.dumps({'note':CFIG['scenario_note'],'buildings':BUILDINGS},indent=2))
print('Rendered',im.size,'scenario buildings',len(BUILDINGS))
