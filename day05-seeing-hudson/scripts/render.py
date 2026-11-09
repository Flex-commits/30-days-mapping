"""Render a reproducible Hudson visual essay using real georeferenced imagery and dated photographs."""
from pathlib import Path
import json,os,textwrap
R=Path(__file__).resolve().parents[1];os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Circle
from matplotlib.font_manager import FontProperties
from matplotlib import patheffects as pe
from PIL import Image,ImageOps
import numpy as np
from pyproj import Transformer
C=json.loads((R/'config.json').read_text());frames={x['id']:x for x in json.loads((R/'data/imagery-frames.json').read_text())};credits={x['id']:x for x in json.loads((R/'data/photo-credits.json').read_text())};OUT=R/'outputs';OUT.mkdir(exist_ok=True);T=Transformer.from_crs(4326,26918,always_xy=True)
BG='#101e2b';FG='#f2eee2';MUT='#a8b7c2';GOLD='#edb969';RULE='#49606b';sans=FontProperties(fname=str(R/'docs/fonts/sans.ttf'));bold=FontProperties(fname=str(R/'docs/fonts/bold.ttf'))
def ft(fig,x,y,s,size=10,col=FG,font=sans,**kw):return fig.text(x,y,s,color=col,fontproperties=font,fontsize=size,**kw)
def rule(fig,y,x0=.055,x1=.945):fig.add_artist(plt.Line2D([x0,x1],[y,y],transform=fig.transFigure,color=RULE,lw=.6))
def aerial(ax,key,alpha=.68):
 f=frames[key];im=np.asarray(Image.open(R/'data/raw'/f['source_file']).convert('RGB'));rgb=im/255.;rgba=np.dstack([rgb,np.where(np.max(im,axis=2)<3,0.,alpha)]);x0,y0,x1,y1=f['actual_bounds'];ax.set_facecolor(BG);ax.imshow(rgba,extent=[x0,x1,y0,y1],origin='upper',zorder=0);ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
 for spine in ax.spines.values():spine.set_color(RULE);spine.set_linewidth(.45)
 return f['actual_bounds']
def marker(ax,p,side,label=True):
 x,y=T.transform(p[side]['lon'],p[side]['lat']);ax.scatter([x],[y],s=37,color=p['color'] if side=='nj' else FG,edgecolor=BG,linewidth=1,zorder=8)
 if label:
  dx=-110 if side=='nj' else 110;ax.text(x+dx,y+90,p['id']+(' W' if side=='nj' else ' E'),ha='right' if side=='nj' else 'left',fontproperties=bold,fontsize=7,color=FG,zorder=9,path_effects=[pe.withStroke(linewidth=2,foreground=BG)])
 return x,y
def pairline(ax,p):
 a=marker(ax,p,'nj');b=marker(ax,p,'ny');ax.plot([a[0],b[0]],[a[1],b[1]],color=p['color'],ls=(0,(3,3)),lw=.95,zorder=7)
def scalebar(ax,bounds,miles=.5,fx=.055,fy=.065):
 x0,y0,x1,y1=bounds;x=x0+(x1-x0)*fx;y=y0+(y1-y0)*fy;length=miles*1609.344;ax.plot([x,x+length],[y,y],color=FG,lw=1.5,zorder=9);ax.text(x,y+(y1-y0)*.035,f'{miles:g} mile'+('s' if miles!=1 else ''),fontproperties=sans,fontsize=7,color=FG,zorder=9,path_effects=[pe.withStroke(linewidth=2,foreground=BG)])
def photo(fig,rect,key):
 ax=fig.add_axes(rect);w,h=int(rect[2]*1800),int(rect[3]*2160);im=Image.open(R/'data/raw/photos'/(key+'.jpg')).convert('RGB');im=ImageOps.fit(im,(w,h),centering=(.5,.45));ax.imshow(im);ax.axis('off');return ax
if '--port-authority-only' not in __import__('sys').argv:
 fig=plt.figure(figsize=(15,18),facecolor=BG)
 # Subtle architectural corner rules continue the existing map series.
 for x,d in [(.04,1),(.96,-1)]:
  fig.add_artist(plt.Line2D([x,x,x+.018*d],[.94,.976,.976],transform=fig.transFigure,color=GOLD,lw=.8))
 ft(fig,.057,.951,'THOMAS HAGOS  /  30-DAY MAP CHALLENGE 2026',9,GOLD,bold);ft(fig,.944,.951,'DAY 05 · SENSES: SIGHT',9,FG,ha='right')
 ft(fig,.055,.893,'SEEING THE HUDSON',43,FG,bold);ft(fig,.058,.853,C['subtitle'],21,MUT)
 ft(fig,.058,.82,'Six public places. Three pairings. A river seen from both sides.',12,FG);rule(fig,.797)
 ft(fig,.058,.777,'THE LOWER HUDSON',9,GOLD,bold);ft(fig,.52,.777,'NEW JERSEY / WEST SHORE',9,GOLD,bold);ft(fig,.739,.777,'NEW YORK / EAST SHORE',9,FG,bold)
 # Map overview and three paired photographic rows.
 a=fig.add_axes([.055,.224,.405,.535]);bounds=aerial(a,'overview',.72)
 for p in C['pairs']:
  pairline(a,p);f=frames[p['id']];x0,y0,x1,y1=f['actual_bounds'];a.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,facecolor='none',edgecolor=p['color'],lw=.8,zorder=5))
  # The frame number sits in its west margin; labels refer to sites, not camera orientations.
  a.text(x0+130,y1-300,p['id'],fontproperties=bold,fontsize=14,color=p['color'],zorder=10,path_effects=[pe.withStroke(linewidth=2,foreground=BG)])
 for name,lon,lat,rotation in [('NEW JERSEY',-74.047,40.788,0),('MANHATTAN',-73.966,40.800,63),('HUDSON RIVER',-73.984,40.806,65),('JERSEY CITY',-74.048,40.719,0)]:
  x,y=T.transform(lon,lat);a.text(x,y,name,fontproperties=bold,fontsize=8,color=FG,ha='center',rotation=rotation,zorder=10,path_effects=[pe.withStroke(linewidth=2.8,foreground=BG)])
 a.text(.94,.96,'N ↑',transform=a.transAxes,ha='right',fontproperties=bold,color=FG,fontsize=9,zorder=12);scalebar(a,bounds,1,.60,.035)
 for i,p in enumerate(C['pairs']):
  top=.742-i*.183
  ft(fig,.52,top,p['id']+'  /  '+p['title'],14,p['color'],bold)
  for j,side in enumerate(['nj','ny']):
   x=.52+j*.219;s=p[side];key=s['photo'];rec=credits[key];ft(fig,x,top-.023,s['short'],9,FG,bold);photo(fig,[x,top-.122,.204,.088],key)
   date=rec['capture_date'][:10];ft(fig,x,top-.138,rec['creator']+' · '+date,6.8,MUT)
   for n,line in enumerate(textwrap.wrap(s['view'],35)):ft(fig,x,top-.153-n*.011,line,7.5,FG)
  if i<2:rule(fig,top-.169,.52,.943)
 # Compact interpretive key, followed by a clear method statement.
 ft(fig,.058,.198,'●  WEST-SHORE SITE',8,GOLD,bold);ft(fig,.245,.198,'●  EAST-SHORE SITE',8,FG,bold)
 ft(fig,.058,.177,'Dashed lines pair places for comparison; they are not verified sightlines.',8,MUT)
 ft(fig,.52,.198,'A DIFFERENT FRAME ON THE SAME WATER',9,GOLD,bold)
 ft(fig,.52,.177,'Position, foreground and light shape the photographs.',9,FG)
 ft(fig,.52,.158,'Different dates and weather: no controlled east–west comparison.',7.5,MUT)
 rule(fig,.135)
 ft(fig,.058,.114,'AERIAL MAP + DATED PHOTOGRAPHS',8,GOLD,bold)
 ft(fig,.058,.094,'USGS orthoimagery mosaic · CONUS source range 2017–2021; local pixel dates unresolved. Not a current-condition survey.',7.5,MUT)
 ft(fig,.058,.075,'Photos: Dtabb73 · Kidfly182 · Famartin · G. Scott Segler · Jllm06 · Jmccabe371. CC BY-SA 4.0 / 3.0; cropped details. Full credits in project.',7.1,MUT)
 ft(fig,.058,.056,'Approximate site anchors. Fort Lee uses the park’s published entrance coordinate. EPSG:26918 · Scale in miles · North up.',7.2,MUT)
 ft(fig,.058,.037,'A visual essay—not a viewshed model, an access inventory or proof that paired observers can see each other.',7.3,MUT)
 ft(fig,.058,.016,'flex-commits.github.io/30-days-mapping/seeing-the-hudson/',7,MUT)
 ft(fig,.944,.016,'#30DayMapChallenge / #teamMUSA',8,GOLD,ha='right')
 fig.savefig(OUT/'seeing-the-hudson.png',dpi=300,facecolor=BG);fig.savefig(OUT/'seeing-the-hudson-preview.png',dpi=100,facecolor=BG);plt.close(fig)
 # Three paired-site sheets retain readable geography and photos for small screens.
 for p in C['pairs']:
  fig=plt.figure(figsize=(8,10),facecolor=BG);ft(fig,.06,.95,'05 / SIGHT · THOMAS HAGOS',10,GOLD,bold);ft(fig,.06,.89,'SEEING THE HUDSON',23,FG,bold);ft(fig,.06,.85,p['id']+' / '+p['title'],14,p['color'],bold)
  ax=fig.add_axes([.06,.47,.88,.33]);b=aerial(ax,p['id'],.87);pairline(ax,p);scalebar(ax,b,.5);ax.text(.96,.93,'N ↑',transform=ax.transAxes,color=FG,ha='right',fontproperties=bold,fontsize=9)
  for j,side in enumerate(['nj','ny']):
   x=.06+j*.46;rec=credits[p[side]['photo']];ft(fig,x,.43,side.upper()+' / '+p[side]['short'],8.5,FG,bold);photo(fig,[x,.235,.42,.17],p[side]['photo']);ft(fig,x,.214,rec['creator']+' · '+rec['capture_date'][:10],6.5,MUT)
  for k,line in enumerate(textwrap.wrap(p['story'],77)):ft(fig,.06,.169-k*.024,line,9,FG)
  ft(fig,.06,.081,'Dashed line = editorial pairing, not a verified sightline.',7,MUT);ft(fig,.06,.057,'USGS orthoimagery · Local capture dates unresolved · Composition CC BY-SA 4.0',6.6,MUT);ft(fig,.06,.035,'Dated views; different conditions. Sources and full credits accompany the project.',6.5,MUT)
  fig.savefig(OUT/('pair-'+p['id']+'.png'),dpi=160,facecolor=BG);plt.close(fig)
 # Dedicated gallery square, not a center-crop of the tall poster.
 fig=plt.figure(figsize=(6,6),facecolor=BG);ft(fig,.065,.93,'05 / SIGHT',10,GOLD,bold);ft(fig,.065,.79,'SEEING\nTHE HUDSON',26,FG,bold,linespacing=1.05);ft(fig,.065,.72,'Two shores. One river. Different views.',9,MUT)
 a=fig.add_axes([.065,.22,.87,.42]);b=aerial(a,'02',.8);pairline(a,C['pairs'][1]);ft(fig,.065,.155,'NEW JERSEY ↔ NEW YORK',11,GOLD,bold);ft(fig,.065,.10,'Six public places · Three photographic pairings',8,FG);ft(fig,.065,.055,'Thomas Hagos · USDA / USGS imagery · Full credits in project',6.5,MUT);fig.savefig(OUT/'05-thomas-hagos.png',dpi=100,facecolor=BG);plt.close(fig)
# Section 04: The Stitch. All geometry and facts build on the existing chapter.
from matplotlib.textpath import TextPath
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch,Ellipse
import geopandas as gpd
serif=FontProperties(fname=str(R/'docs/fonts/serif.ttf'));italic=FontProperties(fname=str(R/'docs/fonts/italic.ttf'))
PA=json.loads((R/'data/port-authority.json').read_text());TEAL='#86afb2';CORAL='#de8c68'

def text_on_curve(ax,text,curve,fontsize=12,color=TEAL,font=italic,tracking=1.2):
 """Place glyphs at true display-space arc lengths; rotate each to the local tangent.

 `curve` is an Nx2 sequence in the map's projected units. Tracking is in points.
 No geometry, font size or aspect ratio is changed by this helper.
 """
 ax.figure.canvas.draw();xy=ax.transData.transform(np.asarray(curve));seg=np.linalg.norm(np.diff(xy,axis=0),axis=1);arc=np.r_[0,np.cumsum(seg)];pt=ax.figure.dpi/72
 widths=[]
 for ch in text:
  w=TextPath((0,0),ch if ch!=' ' else 'n',size=fontsize,prop=font).get_extents().width
  widths.append((w if ch!=' ' else w*.6)*pt+tracking*pt)
 assert sum(widths)<arc[-1], 'Water label does not fit its saved curve.'
 cursor=(arc[-1]-sum(widths))/2;artists=[]
 for ch,w in zip(text,widths):
  d=cursor+w/2;k=min(max(np.searchsorted(arc,d)-1,0),len(seg)-1);f=(d-arc[k])/max(seg[k],1e-9);pos=xy[k]*(1-f)+xy[k+1]*f;rot=np.degrees(np.arctan2(*(xy[k+1]-xy[k])[::-1]));data=ax.transData.inverted().transform(pos)
  if ch!=' ':artists.append(ax.text(*data,ch,rotation=rot,rotation_mode='anchor',ha='center',va='center',fontproperties=font,fontsize=fontsize,color=color,zorder=6))
  cursor+=w
 return artists

def eye(ax,x,y,size=260):
 """Small drawn eye, centered on an existing approximate viewing-place anchor."""
 verts=[(x-size,y),(x,y+size*.8),(x+size,y),(x,y-size*.8),(x-size,y)];path=MPath(verts,[MPath.MOVETO,MPath.CURVE3,MPath.CURVE3,MPath.CURVE3,MPath.CURVE3]);ax.add_patch(PathPatch(path,fc=BG,ec=FG,lw=.7,zorder=12));ax.add_patch(Circle((x,y),size*.21,fc=FG,ec='none',zorder=13))

WATER='#0a1520';LAND='#182a39';SHORE='#2c4351'
SHEETS={'landscape':{'year':13,'name':8.2,'eye':210,'lw':2.4},'phone':{'year':17,'name':10.5,'eye':260,'lw':2.8}}
# Label anchors (lon, lat) chosen by eye on the rendered sheet; leaders point to the mapped feature.
LABELS=[('gwb','George Washington Bridge','1931',(-73.905,40.872),'left'),('lincoln','Lincoln Tunnel','1937',(-73.935,40.752),'left'),
 ('holland','Holland Tunnel · agency 1930','1927',(-73.925,40.722),'left'),('path','PATH tubes · agency 1962','1908–09',(-74.090,40.744),'right'),
 ('wtc','World Trade Center','1973',(-73.935,40.690),'left'),('KLGA','LaGuardia · leased','1947',(-73.862,40.822),'left'),
 ('KJFK','Idlewild / JFK · leased','1947',(-73.885,40.578),'left'),('KEWR','Newark Airport · leased','1948',(-74.243,40.712),'left'),
 ('docks','Port Newark–Elizabeth · terminal','1962',(-74.243,40.628),'left')]
PHONE={'path':((-74.075,40.770),'right'),'KEWR':((-74.243,40.724),'left')}
def mapped_crossings():return gpd.read_file(R/'data/processed/port-authority-crossings-mapped.geojson').to_crs(26918).set_index('id')
def draw_pa_map(ax,sheet='landscape'):
 """The Hudson as a seam: one shared land colour for both states, a thin state line, gold agency works stitched across it."""
 k=SHEETS[sheet];bounds=PA['design']['bounds_wgs84'];x0,y0=T.transform(bounds[0],bounds[1]);x1,y1=T.transform(bounds[2],bounds[3])
 ax.set_facecolor(WATER);ax.set_xlim(x0,x1);ax.set_ylim(y0,y1);ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
 for sp in ax.spines.values():sp.set_visible(False)
 land=gpd.read_file(R/'data/processed/port-authority-land.geojson').to_crs(26918);land.plot(ax=ax,color=LAND,edgecolor=SHORE,linewidth=.3,zorder=1)
 gpd.read_file(R/'data/processed/port-authority-state-line.geojson').to_crs(26918).plot(ax=ax,color=FG,linewidth=.75,linestyle=(0,(5,3)),alpha=.75,zorder=4)
 cx=mapped_crossings();mode={'bridge':'-','tunnel':(0,(3.2,1.6)),'rail':(0,(1,1.4))}
 for ident,row in cx.iterrows():
  xs,ys=row.geometry.xy;ax.plot(xs,ys,color=WATER,lw=k['lw']+2.6,solid_capstyle='round',zorder=7);ax.plot(xs,ys,color=GOLD,lw=k['lw'],ls=mode[row['mode']],solid_capstyle='round',zorder=8);ax.scatter(xs,ys,s=k['lw']*5,color=GOLD,zorder=9)
 pts={}
 for v in PA['airports']:
  x,y=T.transform(v['lon'],v['lat']);pts[v['id']]=[(x,y)];ax.scatter([x],[y],marker='^',s=k['lw']*22,fc=GOLD,ec=WATER,lw=.8,zorder=10)
 docks=[T.transform(v['lon'],v['lat']) for v in PA['ports']];pts['docks']=docks
 for x,y in docks:ax.scatter([x],[y],marker='s',s=k['lw']*12,fc=GOLD,ec=WATER,lw=.8,zorder=10)
 w=next(v for v in PA['landmarks'] if v['id']=='wtc');pts['wtc']=[T.transform(w['lon'],w['lat'])];ax.scatter(*zip(*pts['wtc']),marker='*',s=k['lw']*30,color=GOLD,ec=WATER,lw=.6,zorder=10)
 mid=lambda g:g.interpolate(.5,normalized=True).coords[0]
 for ident in ['gwb','lincoln','holland']:pts[ident]=[cx.loc[ident].geometry.coords[-1]]
 pts['path']=[cx.loc['path-uptown'].geometry.coords[0],cx.loc['path-downtown'].geometry.coords[0]]
 for p in C['pairs']:
  for sd in ['nj','ny']:eye(ax,*T.transform(p[sd]['lon'],p[sd]['lat']),size=k['eye'])
 labels=[]
 for ident,name,year,ll,ha in LABELS:
  if sheet=='phone' and ident in PHONE:ll,ha=PHONE[ident]
  lx,ly=T.transform(*ll)
  for ax_,ay_ in pts[ident]:ax.plot([ax_,lx],[ay_,ly],color=GOLD,alpha=.45,lw=.45,zorder=6)
  halo=[pe.withStroke(linewidth=3,foreground=WATER)]
  labels.append(ax.annotate(year,(lx,ly),xytext=(0,1.5),textcoords='offset points',ha=ha,va='bottom',fontproperties=serif,fontsize=k['year'],color=GOLD,zorder=11,path_effects=halo))
  labels.append(ax.annotate(name,(lx,ly),xytext=(0,-1.5),textcoords='offset points',ha=ha,va='top',fontproperties=sans,fontsize=k['name'],color=FG,zorder=11,path_effects=halo))
 for txt,lon,lat in [('N E W   J E R S E Y',-74.185,40.862),('N E W   Y O R K',-73.800,40.872)]:
  labels.append(ax.text(*T.transform(lon,lat),txt,ha='center',fontproperties=bold,fontsize=k['name']+.8,color=MUT,alpha=.85,zorder=5))
 ax.figure.canvas.draw()
 river=[T.transform(lon,lat) for lon,lat in [(-74.012,40.773),(-73.997,40.797),(-73.983,40.820),(-73.969,40.842)]]
 water=text_on_curve(ax,'HUDSON RIVER' if sheet=='landscape' else 'HUDSON',river,fontsize=k['name']+1.6,tracking=1.2)
 for q in water:q.set_path_effects([pe.withStroke(linewidth=2.6,foreground=WATER)]);q.set_zorder(6)
 kill=[T.transform(lon,lat) for lon,lat in [(-74.150,40.6505),(-74.120,40.6515),(-74.090,40.6525)]]
 line_lab=text_on_curve(ax,'STATE LINE',kill,fontsize=k['name']-1.6,color=FG,font=sans,tracking=1.6)
 for q in line_lab:q.set_path_effects([pe.withStroke(linewidth=2.2,foreground=WATER)]);q.set_alpha(.8);q.set_zorder(6)
 labels.append(ax.text(*T.transform(-74.040,40.600),'New York Harbor',fontproperties=italic,fontsize=k['name']+1,color=TEAL,ha='center',zorder=6))
 sx,sy=T.transform(-73.985,40.552);length=5*1609.344;ax.plot([sx,sx+length],[sy,sy],color=MUT,lw=.9,zorder=6)
 for xx,t,ha in [(sx,'0','left'),(sx+length,'5 miles','right')]:ax.text(xx,sy+500,t,ha=ha,fontproperties=sans,fontsize=k['name']-1.5,color=MUT,zorder=6)
 ax.text(.975,.975,'N ↑',transform=ax.transAxes,ha='right',va='top',fontsize=k['name'],fontproperties=bold,color=MUT)
 return labels,water

def record_layout(fig,labels,edition):
 """Record named-label and figure-text bounds for reproducible collision checks."""
 fig.canvas.draw();renderer=fig.canvas.get_renderer();inv=fig.transFigure.inverted();records=[]
 for q in list(fig.texts)+labels:
  if not q.get_text().strip():continue
  b=q.get_window_extent(renderer).transformed(inv);records.append({'text':q.get_text(),'bounds':[b.x0,b.y0,b.x1,b.y1]})
 overlaps=[]
 for i,a in enumerate(records):
  x0,y0,x1,y1=a['bounds']
  for b in records[i+1:]:
   u0,v0,u1,v1=b['bounds']
   if min(x1,u1)>max(x0,u0)+.0001 and min(y1,v1)>max(y0,v0)+.0001:overlaps.append([a['text'],b['text']])
 return {'edition':edition,'labels':records,'overlapping_text':overlaps,'all_text_inside_canvas':all(0<=v['bounds'][0]<v['bounds'][2]<=1 and 0<=v['bounds'][1]<v['bounds'][3]<=1 for v in records)}

# Landscape sheet: the argument on the left, the seam in the middle, a single thread of years below.
THREAD=[(1908,'H&M tubes open\n(later PATH)',GOLD),(1921,'Port Compact\nsigned',GOLD),(1927,'Holland\nTunnel',GOLD),(1931,'George Washington\nBridge',GOLD),(1937,'Lincoln\nTunnel',GOLD),
 (1947.5,'Airports\nleased',GOLD),(1956,'Ideal X sails\n(private ship)',FG),(1962,'PATH · Elizabeth\nterminal',GOLD),(1973,'World Trade\nCenter',GOLD)]
YEARTXT={1947.5:'1947–48'}
fig=plt.figure(figsize=(14,12),facecolor=BG)
for x,d in [(.04,1),(.96,-1)]:fig.add_artist(plt.Line2D([x,x,x+.018*d],[.945,.976,.976],transform=fig.transFigure,color=GOLD,lw=.8))
ft(fig,.055,.953,'THOMAS HAGOS  /  30-DAY MAP CHALLENGE 2026',8.5,GOLD,bold);ft(fig,.945,.953,'DAY 05 · SENSES: SIGHT',8.5,FG,ha='right')
ft(fig,.055,.902,'SEEING THE HUDSON',27,FG,bold);ft(fig,.055,.872,'04  /  EMPIRE ON THE HUDSON',9,MUT,bold)
ft(fig,.052,.745,'1921',76,GOLD,serif)
ft(fig,.055,.655,'Two states.\nOne agency.',30,FG,serif,linespacing=1.12)
ft(fig,.055,.488,'A river is a border. In 1921\nNew York and New Jersey agreed\nto manage their shared port\nas one. The bridges, tunnels,\ntrains, airports and docks that\nfollowed helped make two\nshores one metropolis.',10.2,FG,sans,linespacing=1.62)
y=.368
for lab,ls,col in [('Built or run by the agency','-',GOLD),('Road tunnel',(0,(3.2,1.6)),GOLD),('PATH rail tubes',(0,(1,1.4)),GOLD),('NY–NJ state line',(0,(5,3)),FG)]:
 fig.add_artist(plt.Line2D([.055,.09],[y,y],transform=fig.transFigure,color=col,lw=2 if col==GOLD else .9,ls=ls));ft(fig,.102,y-.004,lab,8.6,MUT);y-=.024
ft(fig,.055,y-.006,'▲ airport   ■ docks   ★ WTC',8.6,GOLD);y-=.03
ft(fig,.055,y-.004,'Eyes: the six viewing places',8.6,MUT);ft(fig,.055,y-.022,'from pairs 01–03.',8.6,MUT)
a=fig.add_axes([.30,.215,.655,.65]);labels,water=draw_pa_map(a,'landscape')
# The thread: one century of years, stitched.
t0,t1,xa,xb,ty=1904,1977,.07,.93,.135;X=lambda yr:xa+(yr-t0)/(t1-t0)*(xb-xa)
fig.add_artist(plt.Line2D([xa,xb],[ty,ty],transform=fig.transFigure,color=MUT,lw=.6,alpha=.7))
for n,(yr,txt,col) in enumerate(THREAD):
 x=X(yr);big=yr==1921;fig.add_artist(plt.Line2D([x,x],[ty-.007,ty+.007],transform=fig.transFigure,color=col,lw=2.6 if big else 1.6))
 ft(fig,x,ty+.013,YEARTXT.get(yr,str(int(yr))),20 if big else 14,col,serif,ha='center')
 ft(fig,x,ty-.024-(n%2)*.034,txt,7.4,MUT,sans,ha='center',va='top',linespacing=1.35)
rule(fig,.048)
ft(fig,.055,.031,'Selected works, not a full inventory. Crossings are schematic bank-to-bank links; facility and viewing-place anchors are approximate. Sources and research notes in the project.',7,MUT)
ft(fig,.055,.016,'Land: U.S. Census 2024 counties (1:500k) minus TIGER/Line water · State line: TIGER/Line 2024 · EPSG:26918 · North up',7,MUT);ft(fig,.945,.016,'#30DayMapChallenge / #teamMUSA',7.5,GOLD,ha='right')
layout=[record_layout(fig,labels,'landscape')];fig.savefig(OUT/'port-authority.png',dpi=250,facecolor=BG);plt.close(fig)
# Phone edition: the map dominates; the page text carries the chronology.
f=plt.figure(figsize=(8,10),facecolor=BG);ft(f,.06,.962,'SEEING THE HUDSON',20,FG,bold);ft(f,.06,.936,'04  /  EMPIRE ON THE HUDSON',8,MUT,bold)
ft(f,.06,.842,'1921',54,GOLD,serif);ft(f,.40,.877,'Two states.',24,FG,serif);ft(f,.40,.842,'One agency.',24,FG,serif)
m=f.add_axes([.02,.115,.96,.70]);mobile_labels,_=draw_pa_map(m,'phone')
ft(f,.06,.085,'Gold: works built or run by the Port Authority. Dashed cream: NY–NJ state line.',8,MUT);ft(f,.06,.064,'Eyes: six viewing places. Crossings schematic; anchors approximate.',8,MUT)
ft(f,.06,.030,'Census 2024 land and water · EPSG:26918 · Thomas Hagos',7,MUT)
layout.append(record_layout(f,mobile_labels,'phone'));f.savefig(OUT/'port-authority-web.png',dpi=200,facecolor=BG);plt.close(f);(R/'docs/port-authority-layout.json').write_text(json.dumps(layout,indent=2))
print('Rendered Port Authority chapter.')
