from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import json,math,shapefile
from shapely.geometry import shape,mapping,Polygon,MultiPolygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union,transform
from shapely.affinity import scale,translate
from pyproj import Geod,Transformer,CRS
R=Path(__file__).resolve().parents[1];D=R/'data/processed';D.mkdir(exist_ok=True,parents=True);G=Geod(ellps='WGS84')
def parts(g):return list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
def oriented(g):return MultiPolygon([orient(p,sign=1) for p in parts(g)])
def area(g):return abs(G.geometry_area_perimeter(oriented(g))[0])
def densify_ring(coords):
 out=[]
 for a,b in zip(coords,coords[1:]):
  out.append(a);dist=G.inv(a[0],a[1],b[0],b[1])[2];n=max(0,math.ceil(dist/10000)-1)
  if n:out.extend(G.npts(a[0],a[1],b[0],b[1],n))
 out.append(coords[-1]);return out
def dense(g):return MultiPolygon([Polygon(densify_ring(list(p.exterior.coords)),[densify_ring(list(h.coords)) for h in p.interiors]) for p in parts(g)])
def fc(name,features): (D/name).write_text(json.dumps({'type':'FeatureCollection','features':features},separators=(',',':')))
def main():
 cfg=json.loads((R/'config.json').read_text());z=ZipFile(R/'data/raw/countries.zip');stem=next(x[:-4] for x in z.namelist() if x.endswith('.shp'));assert z.read(stem+'.VERSION.txt').decode().strip()=='5.1.1'
 rd=shapefile.Reader(shp=BytesIO(z.read(stem+'.shp')),shx=BytesIO(z.read(stem+'.shx')),dbf=BytesIO(z.read(stem+'.dbf')),encoding='utf8');features={}
 for sr in rd.iterShapeRecords():
  p=sr.record.as_dict();features[p['ADM0_A3']]=(p,shape(sr.shape.__geo_interface__))
 africarows=[(k,p,g) for k,(p,g) in features.items() if p['REGION_UN']=='Africa'];af_geos=[g for k,p,g in africarows];fr=features['FRA'][1];frparts=[(i,p) for i,p in enumerate(parts(fr)) if 40<p.representative_point().x<60 and -25<p.representative_point().y<0];af_geos.extend(p for i,p in frparts)
 originals=[];membership=[]
 for k,p,g in africarows:
  assert g.is_valid,(k,'invalid source; explicit repair required');originals.append({'type':'Feature','geometry':mapping(g),'properties':{'role':'Africa member','id':k,'admin':p['ADMIN']}});membership.append({'id':k,'admin':p['ADMIN'],'components':'all','region_un':p['REGION_UN']})
 for i,p in frparts:originals.append({'type':'Feature','geometry':mapping(p),'properties':{'role':'Africa French component','id':'FRA','component_index':i}})
 africa=unary_union(af_geos);assert africa.is_valid;membership.extend([{'id':'FRA','component_index':i,'bounds':p.bounds,'name':'Mayotte' if p.centroid.x<50 else 'Reunion'} for i,p in frparts]);(D/'africa-membership.json').write_text(json.dumps(membership,indent=2))
 projected=[];report=[]
 def prep(key,label,g,lon,lat,crs=None):
  assert g.is_valid,key;target=area(g);crs=crs or CRS.from_proj4(f'+proj=laea +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs');t=Transformer.from_crs(4326,crs,always_xy=True).transform;pg=transform(t,dense(g));f=math.sqrt(target/pg.area);assert abs(f-1)<.00001,(key,f);pg=scale(pg,xfact=f,yfact=f,origin=(0,0));pg=translate(pg,xoff=-pg.centroid.x,yoff=-pg.centroid.y)
  assert pg.is_valid and abs(pg.area/target-1)<1e-10;projected.append({'type':'Feature','geometry':mapping(pg),'properties':{'id':key,'label':label}});report.append({'id':key,'label':label,'geodesic_area_km2':target/1e6,'planar_area_km2':pg.area/1e6,'normalization_linear_factor':f,'projection':crs.to_string(),'source_component_count':len(parts(g)),'source_valid':g.is_valid,'repairs':'none','simplification_tolerance_m':0,'display_area_effect':0});return pg
 africa_crs=CRS.from_dict(cfg['africa_projection']);prep('AFR','Africa',africa,20,5,africa_crs)
 selections={'CHN':('China',features['CHN'][1],104,35),'IND':('India',features['IND'][1],80,22),'DEU':('Germany',features['DEU'][1],10.5,51),'JPN':('Japan',features['JPN'][1],137,37)}
 us=features['USA'][1];incl=[];excluded=[]
 for i,p in enumerate(parts(us)):
  c=p.representative_point();(incl if -125<=c.x<=-66 and 24<=c.y<=50 else excluded).append((i,p))
 selections['USA48']=('Contiguous United States',MultiPolygon([p for i,p in incl]),-98,39)
 (D/'usa-component-audit.json').write_text(json.dumps({'included':[{'index':i,'bounds':p.bounds} for i,p in incl],'excluded':[{'index':i,'bounds':p.bounds} for i,p in excluded],'note':cfg['comparison_components']['USA48']},indent=2))
 for key,(label,g,lon,lat) in selections.items():
  originals.append({'type':'Feature','geometry':mapping(g),'properties':{'role':'comparison candidate','id':key,'label':label}});prep(key,label,g,lon,lat)
 fc('source-geographic.geojson',originals);fc('comparison-projected.geojson',projected);fc('display-preplacement.geojson',projected);(D/'area-preparation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
