from pathlib import Path
import json,csv
from shapely.geometry import shape
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];D=R/'data/processed/continents';fs=json.loads((D/'layout.geojson').read_text())['features'];af=next(shape(f['geometry']) for f in fs if f['properties']['panel']==4 and f['properties']['role']=='guest');countries=json.loads((D/'asia-country-projected.geojson').read_text())['features'];groups={}
for f in countries:groups.setdefault(f['properties']['id'],[]).append(f)
rows=[]
for key,fs in groups.items():
 g=unary_union([shape(f['geometry']) for f in fs]);assert g.is_valid;covered=g.intersection(af).area/1e6
 if covered>0:rows.append({'id':key,'country':fs[0]['properties']['admin'],'covered_km2':covered,'asian_country_piece_km2':g.area/1e6,'covered_percent':min(100.0,covered/(g.area/1e6)*100),'not_covered_km2':g.difference(af).area/1e6,'coverage_class':'entire Asian source piece' if g.difference(af).area==0 else 'partial Asian source piece'})
rows.sort(key=lambda x:-x['covered_km2']);(D/'asia-country-coverage.json').write_text(json.dumps(rows,indent=2))
with (R/'outputs/asia-country-coverage.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('Asian country portions calculated:',len(rows))

allcountries=unary_union([shape(f['geometry']) for f in countries]);(D/'asia-coverage-summary.json').write_text(json.dumps({'covered_source_units':len(rows),'country_portion_total_km2':sum(x['covered_km2'] for x in rows),'africa_area_outside_country_attribution_km2':af.difference(allcountries).area/1e6,'note':'Outside-country remainder includes outside-Asia protrusion, unassigned water and numerical geometry preparation edges. No whole-country equivalence claimed.'},indent=2))
