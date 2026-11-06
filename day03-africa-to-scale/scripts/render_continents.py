"""Africa, to Scale: area-preserving continent overlays and gallery composition."""
from pathlib import Path
import os,json
R=Path(__file__).resolve().parents[1];os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.path import Path as MP
from matplotlib.patches import PathPatch,Rectangle
from matplotlib.font_manager import FontProperties
from shapely.geometry import shape
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from PIL import Image
D=R/'data/processed/continents';O=R/'outputs';O.mkdir(exist_ok=True)
BG='#101e2b';FG='#f2eee2';MU='#a8b7c2';ACC='#ffbf69';RED='#fc826f';WATER='#293e4b'
COL={'SAM':'#ffbf69','AUS':'#e89275','ANT':'#8eb9c2','EUR':'#ffe7a3','NAM':'#ffbf69','AFR':'#ffe7a3'}
NAMES={'SAM':'South America','AUS':'Australia','ANT':'Antarctica','EUR':'Europe','NAM':'North America','AFR':'Africa','ASI':'Asia'}
PALETTE=['#b47759','#c69a5d','#7f9c99','#b2aa79','#8a8797','#a9b7b5','#9b725c','#818c6b']
S=FontProperties(fname=str(R/'docs/fonts/sans.ttf'));B=FontProperties(fname=str(R/'docs/fonts/bold.ttf'))
def polys(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for x in getattr(g,'geoms',[]) for p in polys(x)]
def draw(ax,g,fc,ec=BG,lw=.3,z=2,hatch=None):
 for p in polys(g):
  p=orient(p,1);v=[];c=[]
  for ring in [p.exterior,*p.interiors]:
   q=list(ring.coords);v.extend(q);c.extend([MP.MOVETO]+[MP.LINETO]*(len(q)-2)+[MP.CLOSEPOLY])
  ax.add_patch(PathPatch(MP(v,c),facecolor=fc,edgecolor=ec,lw=lw,zorder=z,hatch=hatch))
def text(fig,x,y,t,size=11,c=FG,b=False,**kw):fig.text(x,y,t,fontproperties=B if b else S,fontsize=size,color=c,**kw)
def countries(ax,labels=True,fontsize=7):
 fs=json.loads((D/'asia-country-projected.geojson').read_text())['features'];groups={}
 for f in fs:groups.setdefault(f['properties']['id'],[]).append(f)
 for j,(k,rows) in enumerate(sorted(groups.items())):draw(ax,unary_union([shape(f['geometry']) for f in rows]),PALETTE[j%len(PALETTE)],BG,.35,2)
 names={'RUS':'RUSSIA\n(ASIAN PART)','CHN':'CHINA','IND':'INDIA','KAZ':'KAZAKHSTAN','SAU':'SAUDI\nARABIA','IRN':'IRAN','MNG':'MONGOLIA','IDN':'INDONESIA','PAK':'PAKISTAN','JPN':'JAPAN','TUR':'TÜRKIYE\n(ASIAN PART)'}
 if labels:
  for k,label in names.items():
   g=unary_union([shape(f['geometry']) for f in groups[k]]);p=max(polys(g),key=lambda p:p.area).representative_point();ax.text(p.x,p.y,label,fontproperties=B,fontsize=fontsize,ha='center',va='center',color=BG,zorder=12,path_effects=[pe.withStroke(linewidth=1.5,foreground=FG)])
 return groups
def panel(ax,host,guests,asia=False,labels=True):
 draw(ax,host,WATER,MU if asia else FG,.8,1)
 if asia:countries(ax,labels,7)
 for k,g in guests:
  if asia:draw(ax,g,'none',FG,1.7,7)
  else:
   draw(ax,g,COL[k],BG,.35,3)
   if labels:
    p=max(polys(g),key=lambda p:p.area).representative_point();ax.text(p.x,p.y,NAMES[k].upper().replace(' ','\n'),fontproperties=B,fontsize=11,ha='center',va='center',color=BG,zorder=8)
 draw(ax,host,'none',MU if asia else FG,1.05,6)
 for k,g in guests:draw(ax,g.difference(host),'none',RED,.5,9,'////')
 if len(guests)>1:draw(ax,guests[0][1].intersection(guests[1][1]),'#cf6070',FG,.3,10,'xxxx')
 ax.axis('off')
def limits(ax,b,span,height):
 cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2;ax.set(xlim=(cx-span/2,cx+span/2),ylim=(cy-height/2,cy+height/2),aspect='equal')
def dataset(individual):
 fs=json.loads((D/('individual-layout.geojson' if individual else 'layout.geojson')).read_text())['features'];reports=json.loads((D/('individual-validation.json' if individual else 'validation.json')).read_text());items=[]
 for r in reports:
  rows=[f for f in fs if f['properties']['panel']==r['panel']];h=shape(next(f['geometry'] for f in rows if f['properties']['role']=='host'));gs=[(f['properties']['id'],shape(f['geometry'])) for f in rows if f['properties']['role']=='guest'];items.append((r,h,gs,unary_union([h,*[g for k,g in gs]]).bounds))
 return items

def composition(individual=True):
 items=dataset(individual);fig=plt.figure(figsize=(20,25 if individual else 19),facecolor=BG)
 text(fig,.045,.961,'THOMAS HAGOS  /  30-DAY MAP CHALLENGE 2026',11,ACC,True);text(fig,.955,.961,'DAY 03 · POLYGONS',11,ha='right')
 text(fig,.045,.914,'AFRICA, TO SCALE',40,b=True);text(fig,.045,.884,'Continent outlines compared at one consistent area scale.',17,MU)
 text(fig,.045,.855,'AFRICA  29.90 million km²',13,ACC,True)
 text(fig,.045,.835,'Cream outline: Africa   ·   Color: comparison shapes   ·   Diagonal hatch: beyond the host outline',10,MU)
 span=max(max(b[2]-b[0] for r,h,g,b in items)*1.04,max(b[3]-b[1] for r,h,g,b in items)*1.04/.72);height=span*.72
 for i,(r,h,gs,b) in enumerate(items):
  asia=r['host']=='ASI';x=.045+(i%2)*.49;y=(.630-(i//2)*.250) if individual else (.500-(i//2)*.380)
  title=' + '.join(NAMES[k] for k,g in gs)+(' over Asia' if asia else ' over Africa')
  text(fig,x,y+(.187 if individual else .312),f'{i+1:02d}  {title}',16,b=True)
  ax=fig.add_axes([x,y,.425,.17 if individual else .295]);panel(ax,h,gs,asia);limits(ax,b,span,height)
  text(fig,x,y-.008,f"{r['guest_total_km2']/1e6:.2f} million km²  /  {r['area_ratio_percent']:.1f}% of {NAMES[r['host']]}'s area",11,ACC,True)
  outside=r.get('outside_guest_union_km2',sum(r['outside_km2'].values()));fraction=100*sum(r['outside_km2'].values())/r['guest_total_km2']
  if len(gs)==1:text(fig,x,y-.028,f"{100-fraction:.1f}% of {NAMES[gs[0][0]]}'s area within the outline · {fraction:.1f}% beyond",10,MU)
  else:text(fig,x,y-.028,f"Beyond host: {outside/1e6:.2f} million km² · Shape overlap: {r['pairwise_overlap_km2']/1e6:.2f} million km²",10,MU)
 footer=.058 if individual else .063
 text(fig,.045,footer,'Continent shapes repositioned and rotated; areas preserved.',12,b=True)
 text(fig,.045,footer-.016,'Equal physical area scale across panels. Locally centered WGS84 Lambert azimuthal equal-area shapes; no display simplification.',9,MU)
 text(fig,.045,footer-.029,'Natural Earth 1:50m: countries v5.1.1; geographic regions v5.0.0; perennial Antarctic ice shelves v4.1.0. Made with Natural Earth.',8.5,MU)
 text(fig,.045,footer-.042,'Africa includes Madagascar and listed regional islands. Australia includes Tasmania, not all Oceania. Areas use the saved geographic definitions.',8.5,MU)
 name='africa-to-scale' if individual else 'continent-pairings';fig.savefig(O/f'{name}.png',dpi=300,facecolor=BG);plt.close(fig)
 im=Image.open(O/f'{name}.png');im.thumbnail((1700,1700));im.save(O/f'{name}-preview.png')
def asia_detail():
 r,h,gs,b=dataset(True)[-1];fig=plt.figure(figsize=(17,12),facecolor=BG)
 text(fig,.04,.95,'AFRICA, TO SCALE',28,b=True);text(fig,.04,.907,'The comparison, reversed: Africa over country-colored Asia',16,MU)
 ax=fig.add_axes([.025,.13,.65,.72]);panel(ax,h,gs,True);span=(b[2]-b[0])*1.03;limits(ax,b,span,(b[3]-b[1])*1.03)
 rows=json.loads((D/'asia-country-coverage.json').read_text());text(fig,.70,.84,'AREA BENEATH AFRICA’S OUTLINE',10,ACC,True);text(fig,.70,.814,'Country / Asian source portion     million km²',8,MU)
 for i,row in enumerate(rows):
  label=row['country'].replace('United Arab Emirates','U.A.E.').replace('Palestine','Palestine')
  if row['id'] in ['RUS','TUR','KAZ','GEO','AZE']:label+=' (Asian part)'
  text(fig,.70,.785-i*.018,label,8);text(fig,.96,.785-i*.018,f"{row['covered_km2']/1e6:.3f}",8,ha='right')
 text(fig,.04,.090,'Africa: 29.90 million km² · 67.9% of Asia’s calculated area',12,ACC,True)
 text(fig,.04,.064,'93.8% of the moved Africa outline lies within Asia; diagonal hatching marks the 6.2% beyond it.',10)
 text(fig,.04,.040,'Countries supply geographic context. Covered portions are not whole-country equivalents. Source-unit names follow Natural Earth.',9,MU)
 text(fig,.04,.021,'Thomas Hagos · Day 03 / Polygons · Natural Earth 1:50m · Local WGS84 equal-area representations; rigid placement, areas preserved.',8.5,MU)
 fig.savefig(O/'asia-country-comparison.png',dpi=240,facecolor=BG);plt.close(fig)
def thumbnail():
 # Dedicated square composition using the same saved South America overlay; no clipped or resized geometry.
 r,h,gs,b=dataset(True)[0];fig=plt.figure(figsize=(6,6),facecolor=BG)
 text(fig,.06,.94,'DAY 03 / POLYGONS',9,ACC,True);text(fig,.06,.865,'AFRICA,',26,b=True);text(fig,.06,.797,'TO SCALE',26,b=True)
 ax=fig.add_axes([.08,.18,.84,.59]);panel(ax,h,gs,False,False);span=max((b[2]-b[0])*1.02,(b[3]-b[1])*1.02);limits(ax,b,span,span)
 text(fig,.06,.145,'SOUTH AMERICA OVER AFRICA',8,MU)
 text(fig,.06,.105,'CONTINENTS AT ONE AREA SCALE',9,ACC,True);text(fig,.06,.063,'Thomas Hagos · 2026',8,MU)
 fig.savefig(O/'03-thomas-hagos.png',dpi=100,facecolor=BG);plt.close(fig);assert Image.open(O/'03-thomas-hagos.png').size==(600,600)
if __name__=='__main__':
 composition(True);composition(False);asia_detail();thumbnail();print('Rendered main map, pairing comparison, Asia detail and 600 × 600 thumbnail.')
