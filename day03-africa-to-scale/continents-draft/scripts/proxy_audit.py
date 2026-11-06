from pathlib import Path
import json
from shapely.geometry import shape
from shapely.geometry.polygon import orient
from pyproj import Geod
R=Path(__file__).resolve().parents[1];D=R/'data/processed/continents';cfg=json.loads((R/'config.json').read_text());G=Geod(ellps='WGS84')
def ps(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return [g]
 return [p for x in getattr(g,'geoms',[]) for p in ps(x)]
def area(g):return sum(abs(G.geometry_area_perimeter(orient(p,1))[0]) for p in ps(g))/1e6
original={f['properties']['id']:shape(f['geometry']) for f in json.loads((D/'continent-assembled-source-holes.geojson').read_text())['features']};geographic={f['properties']['id']:shape(f['geometry']) for f in json.loads((D/'continent-geographic.geojson').read_text())['features']};rows=[]
for f in json.loads((D/'display-preplacement.geojson').read_text())['features']:
 k=f['properties']['id'];g=shape(f['geometry']);p=g.simplify(cfg['search_simplification_m'],preserve_topology=False).buffer(0);rows.append({'id':k,'search_proxy_tolerance_m':cfg['search_simplification_m'],'search_proxy_area_effect_percent':(p.area/g.area-1)*100,'display_simplification_m':0,'display_simplification_area_effect':0,'uniform_interior_ring_filling_area_change_km2':area(geographic[k])-area(original[k]),'note':'Proxy only accelerates search; all displayed polygons, areas and containment tests use full geometry.'})
(D/'proxy-and-ring-audit.json').write_text(json.dumps(rows,indent=2));print('Search proxy and uniform ring-filling effects measured for all seven continents.')
