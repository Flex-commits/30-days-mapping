"""Country-coastline continent assembly with an explicit source-derived Eurasian divider."""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import json,math,csv
import shapefile
from shapely.geometry import shape,mapping,Polygon,MultiPolygon
from shapely.validation import make_valid,explain_validity
from shapely import set_precision
from shapely.geometry.polygon import orient
from shapely.ops import unary_union,transform
from shapely.affinity import scale,translate
from pyproj import Geod,Transformer
R=Path(__file__).resolve().parents[1];D=R/'data/processed/continents';D.mkdir(parents=True,exist_ok=True)
C=json.loads((R/'config.json').read_text());G=Geod(ellps='WGS84')
def rows(name):
 z=ZipFile(R/'data/raw'/name);s=next(x[:-4] for x in z.namelist() if x.endswith('.shp'));r=shapefile.Reader(shp=BytesIO(z.read(s+'.shp')),shx=BytesIO(z.read(s+'.shx')),dbf=BytesIO(z.read(s+'.dbf')),encoding='utf8')
 return [(x.record.as_dict(),shape(x.shape.__geo_interface__)) for x in r.iterShapeRecords()]
def parts(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 if not hasattr(g,'geoms'):return []
 return [p for x in g.geoms for p in parts(x)]
def area(g):return sum(abs(G.geometry_area_perimeter(orient(p,1))[0]) for p in parts(g))
def ring(v):
 out=[]
 for a,b in zip(v,v[1:]):
  out.append(a);n=max(0,math.ceil(G.inv(*a,*b)[2]/10000)-1)
  if n:out.extend(G.npts(*a,*b,n))
 return out+[v[-1]]
def dense(g):return MultiPolygon([Polygon(ring(list(p.exterior.coords)),[ring(list(h.coords)) for h in p.interiors]) for p in parts(g)])
def fc(path,fs):path.write_text(json.dumps({'type':'FeatureCollection','features':fs},separators=(',',':')))
def feature(g,**p):return {'type':'Feature','properties':p,'geometry':mapping(g)}
# Follow the source Europe polygon eastward boundary, Arctic -> Caspian -> Caucasus/Black Sea.
regs=rows('regions.zip');eu=max(next(g for p,g in regs if p['FEATURECLA']=='Continent' and p['NAME']=='EUROPE').geoms,key=lambda g:g.area)
coords=list(eu.exterior.coords)[:-1]
def idx(x,y):return min(range(len(coords)),key=lambda i:(coords[i][0]-x)**2+(coords[i][1]-y)**2)
a=idx(66.31,68.976);b=idx(36.6276,45.1513)
route=coords[a:]+coords[:b+1] if b<a else coords[a:b+1]
# The eastern route must traverse the Ural divider, not western Europe's coastline.
assert min(x for x,y in route)>35 and len(route)<2000
route=[(66.31,89.9)]+route+[(29.15,41.25),(29.0,41.0),(28.0,40.8),(26.4,40.2),(26.1,39.8),(25.5,35.0),(25.5,-89.9)]
mask=Polygon([(-179.9,89.9)]+route+[(-179.9,-89.9),(-179.9,89.9)]);assert mask.is_valid
fc(D/'europe-asia-divider.geojson',[feature(mask,id='Europe_side_mask',note='Source physical-region eastern route, extended through water; not a legal boundary')])
assembled={k:[] for k in C['projection_centers']};audit=[];country_chunks=[];original=[];repairs=[]
trans={'RUS','KAZ','TUR','GEO','AZE'}
for p,g in rows('countries.zip'):
 key=p['ADM0_A3'];assert g.is_valid,(key,'invalid raw geometry: explicit repair required');original.append(feature(g,id=key,admin=p['ADMIN']))
 for i,q in enumerate(parts(g)):
  pt=q.representative_point();x,y=pt.x,pt.y;group=None;chunks=[]
  if key=='RUS' and x<0:
   chunks=[('ASI',q)]  # Russian Far East west of the antimeridian is Asian, not western Europe.
  elif key in trans:
   # Detached Arctic islands follow the extended longitude divider; the mainland is genuinely split.
   e=q.intersection(mask);s=q.difference(mask)
   chunks=[('EUR',MultiPolygon(parts(e))),('ASI',MultiPolygon(parts(s)))]
  else:
   if key=='ATA':group='ANT'
   elif key=='AUS':group='AUS' if 110<x<155 and -45<y<-9 else None
   elif key=='FRA':
    if -6<x<11 and 40<y<52:group='EUR'
    elif -55<x<-50 and 1<y<7:group='SAM'
    elif 40<x<60 and -25<y<0:group='AFR'
    elif -90<x<-50 and 10<y<55:group='NAM'
   elif key=='USA':group=None if -161<x<-154 and 18<y<23 else 'NAM'
   elif p['CONTINENT']=='North America':group='NAM'
   elif p['CONTINENT']=='South America':group='SAM'
   elif p['REGION_UN']=='Africa':group='AFR'
   elif p['REGION_UN']=='Asia':group='ASI'
   elif p['CONTINENT']=='Europe':group='EUR'
   chunks=[(group,q)] if group else []
  assigned=[]
  for k,qpart in chunks:
   if qpart.is_empty:continue
   assert qpart.is_valid,(key,i,k)
   assembled[k].append(qpart);assigned.append(k);country_chunks.append(feature(qpart,id=key,component=i,continent=k,admin=p['ADMIN']))
  audit.append({'id':key,'admin':p['ADMIN'],'source_component':i,'representative_lon':x,'representative_lat':y,'assigned':assigned,'status':'included' if assigned else 'outside selected continent definitions (e.g. other Oceania/remote overseas components)'})
fc(D/'original-country-geographic.geojson',original);fc(D/'country-continent-chunks.geojson',country_chunks)
(D/'component-membership.json').write_text(json.dumps(audit,indent=2))
ice=rows('ice-shelves.zip');assert all(g.is_valid for p,g in ice);assembled['ANT'].extend(g for p,g in ice)
fc(D/'original-ice-shelves-geographic.geojson',[feature(g,id=i) for i,(p,g) in enumerate(ice)])
geo=[];sourceholes=[];projected=[];areas=[];frames={}
for k,gs in assembled.items():
 g=unary_union(gs);assert g.is_valid;sourceholes.append(feature(g,id=k));g=unary_union([Polygon(p.exterior) for p in parts(g)]);assert g.is_valid;lon,lat=C['projection_centers'][k];target=area(g);proj=f'+proj=laea +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs';t=Transformer.from_crs(4326,proj,always_xy=True).transform
 pg=transform(t,dense(g))
 if not pg.is_valid:
  before=pg.area;reason=explain_validity(pg);pg=MultiPolygon(parts(make_valid(pg)));effect=abs(pg.area/before-1);assert effect<1e-7 and abs(pg.area-before)<2e6,(k,effect)
  repairs.append({'id':k,'absolute_area_change_m2':abs(pg.area-before),'stage':'projected before normalization','operation':'make_valid, polygon components only','reason':reason,'relative_area_effect':effect})
 f=math.sqrt(target/pg.area);assert abs(f-1)<1e-5,(k,f);pg=scale(pg,xfact=f,yfact=f,origin=(0,0));cx,cy=pg.centroid.x,pg.centroid.y;pg=translate(pg,xoff=-cx,yoff=-cy)
 if not pg.is_valid:
  before=pg.area;reason=explain_validity(pg);pg=unary_union(parts(make_valid(pg)));effect=abs(pg.area/before-1);assert effect<1e-10
  repairs.append({'id':k,'stage':'after centering','operation':'make_valid and dissolve polygon components','reason':reason,'relative_area_effect':effect})
 assert pg.is_valid
 before=pg.area;pg=set_precision(pg,0.01);effect=abs(pg.area/before-1);assert effect<1e-7
 repairs.append({'id':k,'stage':'comparison preparation','operation':'0.01 m precision grid to remove numerical seam slivers','relative_area_effect':effect,'absolute_area_change_m2':abs(pg.area-before)})
 correction=math.sqrt(target/pg.area);pg=scale(pg,xfact=correction,yfact=correction,origin=(0,0));f*=correction;assert pg.is_valid
 frames[k]={'projection':proj,'normalization':f,'center_x_m':cx*correction,'center_y_m':cy*correction}
 geo.append(feature(g,id=k));projected.append(feature(pg,id=k,coordinate_units='metres',projection=proj))
 areas.append({'id':k,'geodesic_km2':target/1e6,'projected_km2':pg.area/1e6,'linear_normalization':f,'source_components':len(parts(g)),'valid':True,'display_simplification_m':0,'display_area_effect':0})
(D/'geometry-repairs.json').write_text(json.dumps(repairs,indent=2))
fc(D/'continent-assembled-source-holes.geojson',sourceholes)
fc(D/'continent-geographic.geojson',geo);fc(D/'comparison-projected.geojson',projected);fc(D/'display-preplacement.geojson',projected);(D/'area-preparation.json').write_text(json.dumps(areas,indent=2));(D/'projection-frames.json').write_text(json.dumps(frames,indent=2))
# Asian country pieces share Asia's single projection and frame. No country is independently reprojected here.
f=frames['ASI'];t=Transformer.from_crs(4326,f['projection'],always_xy=True).transform;af=[]
for row in country_chunks:
 if row['properties']['continent']!='ASI':continue
 pg=transform(t,dense(shape(row['geometry'])));pg=scale(pg,xfact=f['normalization'],yfact=f['normalization'],origin=(0,0));pg=translate(pg,xoff=-f['center_x_m'],yoff=-f['center_y_m'])
 if not pg.is_valid:
  before=pg.area;reason=explain_validity(pg);pg=unary_union(parts(make_valid(pg)));effect=abs(pg.area/before-1);assert (effect<1e-6 and abs(pg.area-before)<1e6) or abs(pg.area-before)<1,(row['properties'],before,pg.area,effect)
  repairs.append({'id':row['properties']['id'],'absolute_area_change_m2':abs(pg.area-before),'stage':'Asia country projection','operation':'make_valid/dissolve polygon components','reason':reason,'relative_area_effect':effect})
 af.append(feature(pg,**row['properties']))
fc(D/'asia-country-projected.geojson',af)
(D/'geometry-repairs.json').write_text(json.dumps(repairs,indent=2))
with (R/'outputs/continent-areas.csv').open('w') as o:
 w=csv.DictWriter(o,fieldnames=list(areas[0]));w.writeheader();w.writerows(areas)
print(json.dumps(areas,indent=2))
