"""Render actual unsimplified layouts; expose protrusions and overlaps."""
from pathlib import Path
import os,json,sys
R=Path(__file__).resolve().parents[1];os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch,Rectangle
from matplotlib.path import Path as MP
from matplotlib.font_manager import FontProperties
from shapely.geometry import shape
from shapely.ops import unary_union
from PIL import Image
D=R/'data/processed/continents';BG='#101e2b';FG='#f2eee2';MU='#a8b7c2';RED='#fc826f';COL={'SAM':'#ffbf69','AUS':'#e89275','ANT':'#8eb9c2','EUR':'#ffe7a3','NAM':'#ffbf69','AFR':'#ffe7a3'};NAMES={'SAM':'South America','AUS':'Australia','ANT':'Antarctica','EUR':'Europe','NAM':'North America','AFR':'Africa','ASI':'Asia'}
font=R/'docs/fonts';S=FontProperties(fname=str(font/'sans.ttf'));B=FontProperties(fname=str(font/'bold.ttf'))
def polys(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for x in getattr(g,'geoms',[]) for p in polys(x)]
def draw(ax,g,fc,ec=BG,lw=.3,z=2,hatch=None):
 from shapely.geometry.polygon import orient
 for p in polys(g):
  p=orient(p,1);vs=[];cs=[]
  for ring in [p.exterior,*p.interiors]:
   c=list(ring.coords);vs.extend(c);cs.extend([MP.MOVETO]+[MP.LINETO]*(len(c)-2)+[MP.CLOSEPOLY])
  ax.add_patch(PathPatch(MP(vs,cs),facecolor=fc,edgecolor=ec,lw=lw,zorder=z,hatch=hatch))
def main():
 individual='--individual' in sys.argv;layoutname='individual-layout.geojson' if individual else 'layout.geojson';reportname='individual-validation.json' if individual else 'validation.json';prefix='continents-individual' if individual else 'continents-feasibility';fs=json.loads((D/layoutname).read_text())['features'];reports=json.loads((D/reportname).read_text());areas={x['id']:x['geodesic_km2'] for x in json.loads((D/'area-preparation.json').read_text())};fig=plt.figure(figsize=(20,30 if individual else 19),facecolor=BG)
 def tx(x,y,t,size=11,c=FG,b=False,**kw):fig.text(x,y,t,fontsize=size,fontproperties=B if b else S,color=c,**kw)
 tx(.045,.961,'DAY 03 / POLYGONS · GEOGRAPHIC FEASIBILITY DRAFT',11,'#ffbf69',True);tx(.955,.961,'THOMAS HAGOS',11,ha='right');tx(.045,.919,'AFRICA, TO SCALE',39,b=True);tx(.045,.890,('Six individual comparisons. Each continent once. One area scale.' if individual else 'Four continent comparisons. Real outlines. One area scale.'),18,MU)
 tx(.045,.862,('Verified fits are distinguished from partial overlays. Hatching exposes portions outside the host.' if individual else 'These are search results—not verified fits. Hatching exposes portions outside the host.'),12,RED)
 tx(.045,.845,'Diagonal hatch: outside the host outline. Crosshatch: overlap between comparison continents.',10,MU)
 # Identical map dimensions and coordinate spans give equal physical area scale in all four panels.
 bounds=[]
 for n in range(1,len(reports)+1):
  gs=[shape(f['geometry']) for f in fs if f['properties']['panel']==n];u=unary_union(gs);bounds.append(u.bounds)
 spanx=max(b[2]-b[0] for b in bounds)*1.06;spany=max(b[3]-b[1] for b in bounds)*1.06;span=max(spanx,spany/.72);height=span*.72
 for i,report in enumerate(reports):
  x=.045+(i%2)*.49;y=(.640-(i//2)*.265) if individual else (.510-(i//2)*.390);asia=report['host']=='ASI'
  tx(x,y+(.190 if individual else .312),f"0{i+1}  "+(' + '.join(NAMES[k] for k in report['guests'])+(' over Asia' if asia else ' over Africa')),16,b=True)
  ax=fig.add_axes([x,y,.425,.175 if individual else .295]);ax.set_facecolor(BG);host=next(shape(f['geometry']) for f in fs if f['properties']['panel']==i+1 and f['properties']['role']=='host');guests=[(f['properties']['id'],shape(f['geometry'])) for f in fs if f['properties']['panel']==i+1 and f['properties']['role']=='guest'];draw(ax,host,'#293e4b',FG,.8,1)
  if asia:
   countryfs=json.loads((D/'asia-country-projected.geojson').read_text())['features'];groups={}
   for f in countryfs:groups.setdefault(f['properties']['id'],[]).append(f)
   # Stable colors assigned to countries; same country components retain their color.
   palette=['#b47759','#c69a5d','#7f9c99','#b2aa79','#8a8797','#a9b7b5','#9b725c','#818c6b']
   for j,(key,features) in enumerate(sorted(groups.items())):
    g=unary_union([shape(f['geometry']) for f in features]);draw(ax,g,palette[j%len(palette)],BG,.35,2)
   af=guests[0][1];draw(ax,af,'none',FG,1.8,7)
   large={'RUS':'RUSSIA\n(ASIAN PART)','CHN':'CHINA','IND':'INDIA','KAZ':'KAZAKHSTAN','SAU':'SAUDI ARABIA','IRN':'IRAN','MNG':'MONGOLIA','IDN':'INDONESIA','PAK':'PAKISTAN','JPN':'JAPAN','TUR':'TÜRKIYE\n(ASIAN PART)'}
   for key,label in large.items():
    if key not in groups:continue
    g=unary_union([shape(f['geometry']) for f in groups[key]]);p=max(polys(g),key=lambda p:p.area).representative_point();ax.text(p.x,p.y,label,fontsize=6.5,fontproperties=B,ha='center',va='center',color=BG,zorder=8)
   p=max(polys(af),key=lambda p:p.area).representative_point();ax.annotate('AFRICA OUTLINE',(p.x,p.y),xytext=(0,-35),textcoords='offset points',fontsize=8,fontproperties=B,color=FG,ha='center',zorder=10,arrowprops={'arrowstyle':'-','color':FG})
  else:
   for key,g in guests:
    draw(ax,g,COL[key],BG,.45,3);p=max(polys(g),key=lambda p:p.area).representative_point();ax.text(p.x,p.y,NAMES[key].upper().replace(' ','\n'),fontsize=10,fontproperties=B,color=BG,ha='center',va='center',zorder=5)
  draw(ax,host,'none',FG,1.0,6)
  for key,g in guests:draw(ax,g.difference(host),'none',RED,.55,9,'////')
  if len(guests)>1:draw(ax,guests[0][1].intersection(guests[1][1]),'#cf6070',FG,.3,10,'xxxx')
  b=bounds[i];cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2;ax.set(xlim=(cx-span/2,cx+span/2),ylim=(cy-height/2,cy+height/2),aspect='equal');ax.axis('off')
  total=report['guest_total_km2']/1e6;outside=report.get('outside_guest_union_km2',sum(report['outside_km2'].values()))/1e6;overlap=report['pairwise_overlap_km2']/1e6
  tx(x,y-.002,f"{total:.2f} million km² · {report['area_ratio_percent']:.1f}% of {NAMES[report['host']]}'s area",11,'#ffbf69',True)
  tx(x,y-.021,f"Outside host: {outside:.2f} million km²"+(f"  |  Shape overlap: {overlap:.2f} million km²" if len(guests)>1 else ''),10,MU)
  tx(x,y-.040,'Full containment not found in this bounded search.' if report['status']!='verified fit' else 'Verified fit: zero outside area and zero overlap.',10,RED if report['status']!='verified fit' else FG)
 tx(.045,.045 if individual else .055,'Shapes repositioned and rotated; areas preserved. No shrinking, cutting or clipping.',12,b=True)
 tx(.045,.032 if individual else .040,'Same physical area scale in every panel. Locally centered WGS84 Lambert azimuthal equal-area representations; no display simplification.',10,MU)
 tx(.045,.021 if individual else .027,'Natural Earth 1:50m countries v5.1.1; physical regions v5.0.0 inform the Europe–Asia division. Africa includes Madagascar and listed regional islands.',9,MU)
 tx(.045,.009 if individual else .014,'Australia includes Tasmania, not all Oceania. Antarctica includes Natural Earth perennial ice shelves v4.1.0; excludes seasonal sea ice. Historic source extent, not a current ice-front survey.',9,MU)
 fig.savefig(R/'outputs'/f'{prefix}-draft.png',dpi=200,facecolor=BG);plt.close(fig)
 im=Image.open(R/'outputs'/f'{prefix}-draft.png');im.thumbnail((1700,1700));im.save(R/'outputs'/f'{prefix}-preview.png');print('Rendered actual displayed polygons, hatching outside portions.')
if __name__=='__main__':main()
