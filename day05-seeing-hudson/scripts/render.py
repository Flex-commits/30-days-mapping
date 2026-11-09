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
print('Rendered poster, three paired-site sheets and square thumbnail.')
