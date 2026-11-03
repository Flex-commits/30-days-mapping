"""Independent endpoint and label sanity checks on the selected source geometry."""
import json, numpy as np, geopandas as gpd,shapely
from pathlib import Path
from shapely.geometry import Point
R=Path(__file__).resolve().parents[1];D=R/'data/processed';report=json.loads((D/'validation.json').read_text());r=gpd.read_file(D/'rivers.gpkg').to_crs(report['projection']);r=r.set_index('HYRIV_ID');gaps=[]
for id,row in r.iterrows():
 if row.NEXT_DOWN:
  a=np.array(row.geometry.coords)[-1,:2];b=np.array(r.loc[row.NEXT_DOWN].geometry.coords)[0,:2];gaps.append(float(np.linalg.norm(a-b)))
report['max_downstream_endpoint_gap_m']=max(gaps);report['endpoint_gaps_over_1m']=sum(v>1 for v in gaps)
assert max(gaps)<1,'Unexpected source topology gap; inspect before publication.'
source=gpd.read_file(R/'data/raw/rivers.zip');excluded=source[source.MAIN_RIV!=report['main_riv']];report['excluded_endorheic_reaches']=int((excluded.ENDORHEIC==1).sum());report['excluded_other_outlet_reaches']=int((excluded.ENDORHEIC==0).sum())
# Lake attributes identify the geographic targets independently of placed text.
lakes=gpd.read_file(D/'lakes.gpkg');report['lakes_in_context']=lakes['name'].tolist()
(D/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report[k] for k in ['max_downstream_endpoint_gap_m','endpoint_gaps_over_1m','excluded_endorheic_reaches','excluded_other_outlet_reaches']},indent=2))
