from pathlib import Path
import json
from shapely.geometry import shape
from shapely.geometry.polygon import orient
from pyproj import Geod
R=Path(__file__).resolve().parents[1];D=R/'data/processed/continents';G=Geod(ellps='WGS84')
def ps(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for x in getattr(g,'geoms',[]) for p in ps(x)]
f=json.loads((D/'original-country-geographic.geojson').read_text())['features'];ids=[x['properties']['id'] for x in f];assert len(ids)==len(set(ids));assert all(shape(x['geometry']).is_valid for x in f)
cs=json.loads((D/'continent-geographic.geojson').read_text())['features'];overlaps=[]
for i,a in enumerate(cs):
 for b in cs[i+1:]:
  g=shape(a['geometry']).intersection(shape(b['geometry']));ar=sum(abs(G.geometry_area_perimeter(orient(p,1))[0]) for p in ps(g))/1e6
  overlaps.append({'a':a['properties']['id'],'b':b['properties']['id'],'overlap_km2':ar})
a=json.loads((D/'area-preparation.json').read_text());errors=[abs(x['projected_km2']/x['geodesic_km2']-1) for x in a];assert max(errors)<1e-12
# Country pieces should cover the Asia comparison surface, with only numerical preparation-edge differences.
from shapely.ops import unary_union
ac=json.loads((D/'asia-country-projected.geojson').read_text())['features'];u=unary_union([shape(x['geometry']) for x in ac]);asia=next(shape(x['geometry']) for x in json.loads((D/'comparison-projected.geojson').read_text())['features'] if x['properties']['id']=='ASI');coverage_difference=u.symmetric_difference(asia).area/1e6
report={'unique_source_ids':len(ids),'all_raw_country_geometries_valid':True,'geographic_continent_intersections':overlaps,'max_geodesic_to_prepared_relative_area_error':max(errors),'asia_country_to_continent_symmetric_difference_km2':coverage_difference,'display_simplification_m':0,'repair_log':'geometry-repairs.json','claims':'See each layout validation: zero outside area is required for a verified fit; unresolved overlays are not certified.'}
(D/'geography-audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
