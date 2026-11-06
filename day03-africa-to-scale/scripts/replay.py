"""Reproduce the saved rigid layout without repeating the placement search."""
from pathlib import Path
import json
from shapely.geometry import shape,mapping
from shapely.affinity import rotate,translate
R=Path(__file__).resolve().parents[1];D=R/'data/processed'
f=json.loads((D/'display-preplacement.geojson').read_text())['features'];g={x['properties']['id']:shape(x['geometry']) for x in f};p=json.loads((R/'placements.json').read_text())['placements'];out=[{'type':'Feature','properties':{'id':'AFR'},'geometry':mapping(g['AFR'])}]
for x in p:
 a=translate(rotate(g[x['id']],x['rotation_degrees'],origin=(0,0)),xoff=x['translation_x_m'],yoff=x['translation_y_m']);assert a.is_valid and a.difference(g['AFR']).area==0;assert abs(a.area/g[x['id']].area-1)<1e-12
 for b in out[1:]:assert a.intersection(shape(b['geometry'])).area==0
 out.append({'type':'Feature','properties':{'id':x['id']},'geometry':mapping(a)})
(D/'layout.geojson').write_text(json.dumps({'type':'FeatureCollection','features':out},separators=(',',':')))
print('Saved placement replay: valid geometry, zero overlap/protrusion, area preserved.')
