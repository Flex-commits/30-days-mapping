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
def countries(ax,labels=True,fontsize=7,label_mask=None,compact=False):
 fs=json.loads((D/'asia-country-projected.geojson').read_text())['features'];groups={}
 for f in fs:groups.setdefault(f['properties']['id'],[]).append(f)
 for j,(k,rows) in enumerate(sorted(groups.items())):draw(ax,unary_union([shape(f['geometry']) for f in rows]),PALETTE[j%len(PALETTE)],BG,.35,2)
 names={'RUS':'RUSSIA\n(ASIAN PART)','CHN':'CHINA','IND':'INDIA','KAZ':'KAZAKHSTAN','SAU':'SAUDI\nARABIA','IRN':'IRAN','MNG':'MONGOLIA','IDN':'INDONESIA','PAK':'PAKISTAN','JPN':'JAPAN','TUR':'TÜRKIYE\n(ASIAN PART)'}
 if labels:
  for k,label in names.items():
   if compact and k in ['SAU','TUR','IDN']:continue
   g=unary_union([shape(f['geometry']) for f in groups[k]]);p=max(polys(g),key=lambda p:p.area).representative_point()
   if label_mask is not None and not label_mask.covers(p):continue
   ax.text(p.x+(300000 if k=='RUS' else 0),p.y-(130000 if k=='RUS' else 0),label,fontproperties=B,fontsize=fontsize,ha='center',va='center',color=BG,zorder=12,path_effects=[pe.withStroke(linewidth=1.5,foreground=FG)])
 return groups
def panel(ax,host,guests,asia=False,labels=True,outline=2.3,analysis_host=None,compact=False):
 draw(ax,host,WATER,MU if asia else FG,.8,1)
 if asia:countries(ax,labels,6.5,label_mask=host,compact=compact)
 for k,g in guests:
  if asia:draw(ax,g,'none',FG,1.7,7)
  else:
   draw(ax,g,COL[k],'none' if k=='ANT' else BG,.35,3)
   if labels:
    p=max(polys(g),key=lambda p:p.area).representative_point();ax.text(p.x,p.y,NAMES[k].upper().replace(' ','\n'),fontproperties=B,fontsize=11,ha='center',va='center',color=BG,zorder=8)
 draw(ax,host,'none',MU if asia else FG,1.05,6)
 for k,g in guests:draw(ax,g.difference(host if analysis_host is None else analysis_host),'none',RED,.5,9,'////')
 if len(guests)>1:draw(ax,guests[0][1].intersection(guests[1][1]),'#cf6070',FG,.3,10,'xxxx')
 africa=guests[0][1] if asia else host
 draw(ax,africa,'none',BG,outline+2,13);draw(ax,africa,'none',FG,outline,14)
 ax.axis('off')
def limits(ax,b,span,height):
 cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2;ax.set(xlim=(cx-span/2,cx+span/2),ylim=(cy-height/2,cy+height/2),aspect='equal')
def dataset(individual):
 fs=json.loads((D/('individual-layout.geojson' if individual else 'layout.geojson')).read_text())['features'];reports=json.loads((D/('individual-validation.json' if individual else 'validation.json')).read_text());items=[]
 for r in reports:
  rows=[f for f in fs if f['properties']['panel']==r['panel']];h=shape(next(f['geometry'] for f in rows if f['properties']['role']=='host'));gs=[(f['properties']['id'],shape(f['geometry'])) for f in rows if f['properties']['role']=='guest'];items.append((r,h,gs,unary_union([h,*[g for k,g in gs]]).bounds))
 return items

def main_parts(g):
 cfg=json.loads((R/'config.json').read_text())['presentation'];ps=polys(g);largest=max(ps,key=lambda p:p.area);main=[p for p in ps if p.area/g.area>=cfg['large_component_area_share'] or p.distance(largest)<=cfg['near_mainland_distance_m']];remote=[p for p in ps if not any(p is q for q in main)]
 return unary_union(main),unary_union(remote)
def view_item(item):
 r,h,gs,b=item;hm,hr=main_parts(h);gm=[];removed=[]
 for k,g in gs:
  m,rem=main_parts(g);gm.append((k,m));removed.append((k,rem))
 return hm,gm,unary_union([hm,*[g for k,g in gm]]).bounds,hr,removed

def island_context(fig,rect,item,main_bounds,size=6.5):
 r,h,gs,b=item;ax=fig.add_axes(rect);panel(ax,h,gs,r['host']=='ASI',False,outline=.65)
 w=b[2]-b[0];v=b[3]-b[1];limits(ax,b,w*1.08,v*1.08)
 ax.add_patch(Rectangle((0,0),1,1,transform=ax.transAxes,fill=False,edgecolor=MU,lw=.6,clip_on=False,zorder=20))
 x0,y0,x1,y1=main_bounds;ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,fill=False,edgecolor=ACC,lw=.65,linestyle='--',zorder=20))
 ax.set_title('ISLAND CONTEXT',fontsize=size,fontproperties=B,color=MU,pad=4)
 ax.text(.5,-.10,'Full extent · smaller scale',transform=ax.transAxes,fontproperties=S,fontsize=size-1,color=MU,ha='center')
 return ax

def composition(individual=True):
 items=dataset(individual);views=[view_item(i) for i in items];fig=plt.figure(figsize=(20,25 if individual else 19),facecolor=BG)
 text(fig,.045,.961,'THOMAS HAGOS  /  30-DAY MAP CHALLENGE 2026',11,ACC,True);text(fig,.955,.961,'DAY 03 · POLYGONS',11,ha='right')
 text(fig,.045,.914,'AFRICA, TO SCALE',40,b=True);text(fig,.045,.884,'Continent areas, compared. Africa is the reference.',17,MU)
 text(fig,.045,.855,'AFRICA  29.90 million km²',13,ACC,True)
 text(fig,.045,.835,'Cream: Africa · Hatch: beyond the host · Insets retain the full extent, including remote islands',10,MU)
 map_height=.155 if individual else .275;aspect=.34*20/(map_height*(25 if individual else 19));span=max(max(b[2]-b[0] for h,g,b,hr,rem in views)*1.06,max(b[3]-b[1] for h,g,b,hr,rem in views)*1.06*aspect);height=span/aspect
 for i,(item,v) in enumerate(zip(items,views)):
  r,h,gs,b=item;hm,gm,mb,hr,rem=v;asia=r['host']=='ASI';x=.045+(i%2)*.49;top=(.817-(i//2)*.250) if individual else (.817-(i//2)*.380)
  title=' + '.join(NAMES[k] for k,g in gs)
  text(fig,x,top,f'{i+1:02d}  {title.upper()}'+(' OVER ASIA' if asia else ''),16,b=True)
  text(fig,x,top-.030,f"{r['area_ratio_percent']:.1f}% of {NAMES[r['host']]}'s area",22,ACC,True)
  ax=fig.add_axes([x,top-(.195 if individual else .315),.34,map_height]);limits(ax,mb,span,height);panel(ax,hm,gm,asia,analysis_host=h,compact=True)
  # Original, complete geometry appears in the context inset; no components are dropped from totals.
  island_context(fig,[x+.355,top-.175,.075,.095],item,(ax.get_xlim()[0],ax.get_ylim()[0],ax.get_xlim()[1],ax.get_ylim()[1]))
  text(fig,x,top-(.209 if individual else .330),f"{r['guest_total_km2']/1e6:.2f} million km² · complete geometry, including islands",10,MU)
  fraction=100*sum(r['outside_km2'].values())/r['guest_total_km2']
  if len(gs)==1:
   note='Fully contained in the saved placement.' if sum(r['outside_km2'].values())==0 else f"Area-preserving overlay · {fraction:.1f}% beyond {NAMES[r['host']]}'s outline"
  else:note=f"Area-preserving overlays · {r['pairwise_overlap_km2']/1e6:.2f} million km² guest overlap"
  text(fig,x,top-(.227 if individual else .349),note,9.5,MU)
 footer=.041 if individual else .058
 text(fig,.045,footer,'Shapes repositioned and rotated; areas preserved. All measurements use the full original placements.',11,b=True)
 text(fig,.045,footer-.013,'Main views share one physical area scale; island context insets are smaller-scale overviews. Dashed boxes mark the main views.',9,MU)
 text(fig,.045,footer-.026,'Natural Earth 1:50m · WGS84 local equal-area representations · Africa includes Madagascar; Australia includes Tasmania, not all Oceania.',8.5,MU)
 name='africa-to-scale' if individual else 'continent-pairings';fig.savefig(O/f'{name}.png',dpi=300,facecolor=BG);plt.close(fig)
 im=Image.open(O/f'{name}.png');im.thumbnail((1700,1700));im.save(O/f'{name}-preview.png')

def social_panels():
 out=O/'linkedin';out.mkdir(exist_ok=True)
 for item in dataset(True):
  r,h,gs,b=item;hm,gm,mb,hr,rem=view_item(item);asia=r['host']=='ASI';key=gs[0][0];fig=plt.figure(figsize=(7.2,9),facecolor=BG)
  text(fig,.055,.950,'AFRICA, TO SCALE',15,b=True);text(fig,.945,.950,f"{r['panel']:02d} / 06",10,ACC,True,ha='right')
  text(fig,.055,.883,NAMES[key]+(' over Asia' if asia else ''),23,b=True)
  text(fig,.055,.807,f"{r['area_ratio_percent']:.1f}%",44,ACC,True);text(fig,.055,.758,f"of {NAMES[r['host']]}'s area",18)
  text(fig,.055,.724,f"{r['guest_total_km2']/1e6:.2f} million km² · all represented components",10,MU)
  ax=fig.add_axes([.055,.285,.89,.415]);aspect=.89*7.2/(.415*9);span=max((mb[2]-mb[0])*1.05,(mb[3]-mb[1])*1.05*aspect);limits(ax,mb,span,span/aspect);panel(ax,hm,gm,asia,True,outline=2.7,analysis_host=h,compact=True)
  island_context(fig,[.765,.145,.18,.115],item,(ax.get_xlim()[0],ax.get_ylim()[0],ax.get_xlim()[1],ax.get_ylim()[1]),size=7)
  fraction=100*sum(r['outside_km2'].values())/r['guest_total_km2']
  text(fig,.055,.240,'Fully contained' if fraction==0 else 'Area-preserving overlay',12,b=True)
  text(fig,.055,.210,f"{fraction:.1f}% of {NAMES[key]}'s area extends",10,MU);text(fig,.055,.187,f"beyond {NAMES[r['host']]}'s outline in this placement.",10,MU)
  text(fig,.055,.145,'Cream = Africa · Hatch = beyond host',9,MU)
  text(fig,.055,.105,'Shapes moved and rotated; areas preserved.',10)
  text(fig,.055,.072,'Inset: smaller scale · View scale varies across slides.',8,MU)
  text(fig,.055,.020,'WGS84 locally centered equal-area shapes',7.5,MU)
  text(fig,.055,.040,'Thomas Hagos · Day 03 / Polygons · Natural Earth 1:50m',8,MU)
  filename=f"{r['panel']:02d}-"+('africa-over-asia' if asia else NAMES[key].lower().replace(' ','-'));fig.savefig(out/f'{filename}.png',dpi=150,facecolor=BG);plt.close(fig)
  assert Image.open(out/f'{filename}.png').size==(1080,1350)

def display_audit():
 records=[]
 for item in dataset(True):
  r,h,gs,b=item;hm,gm,mb,hr,rem=view_item(item)
  for key,g,m,remote in [(r['host'],h,hm,hr),*[(k,g,main,rr) for (k,g),(kk,main),(rk,rr) in zip(gs,gm,rem)]]:
   reconstructed=unary_union([m,remote]);difference=g.symmetric_difference(reconstructed).area;assert difference<1e-4;assert m.intersection(remote).area==0
   records.append({'panel':r['panel'],'id':key,'main_component_count':len(polys(m)),'remote_component_count':len(polys(remote)),'main_km2':m.area/1e6,'remote_km2':remote.area/1e6,'full_km2':g.area/1e6,'partition_difference_m2':difference})
 (D/'presentation-component-audit.json').write_text(json.dumps({'policy':json.loads((R/'config.json').read_text())['presentation'],'components':records,'measurement_geometry_changed':False,'insets_use_full_placement':True},indent=2))

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
 # Dedicated main-view square; all original components remain in the linked full-map context.
 r,h,gs,b=dataset(True)[0];hm,gm,mb,hr,rem=view_item((r,h,gs,b));fig=plt.figure(figsize=(6,6),facecolor=BG)
 text(fig,.06,.94,'DAY 03 / POLYGONS',9,ACC,True);text(fig,.06,.865,'AFRICA,',26,b=True);text(fig,.06,.797,'TO SCALE',26,b=True)
 ax=fig.add_axes([.08,.18,.84,.59]);panel(ax,hm,gm,False,False,analysis_host=h);span=max((mb[2]-mb[0])*1.02,(mb[3]-mb[1])*1.02);limits(ax,mb,span,span)
 text(fig,.06,.175,'MAIN VIEW · ISLAND CONTEXT IN FULL MAP',6.5,MU)
 text(fig,.06,.145,'SOUTH AMERICA OVER AFRICA',8,MU)
 text(fig,.06,.105,'CONTINENTS AT ONE AREA SCALE',9,ACC,True);text(fig,.06,.063,'Thomas Hagos · 2026',8,MU)
 fig.savefig(O/'03-thomas-hagos.png',dpi=100,facecolor=BG);plt.close(fig);assert Image.open(O/'03-thomas-hagos.png').size==(600,600)
if __name__=='__main__':
 composition(True);composition(False);asia_detail();thumbnail();social_panels();display_audit();print('Rendered enlarged main views, full-extent island insets and six LinkedIn panels.')
