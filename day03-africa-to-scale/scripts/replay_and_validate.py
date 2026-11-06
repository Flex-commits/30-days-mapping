"""Rebuild saved layouts from prepared inputs, recompute all public fit metrics."""
from pathlib import Path
import json,csv
from shapely.geometry import shape,mapping
from shapely.affinity import rotate,translate
from shapely.ops import unary_union
R=Path(__file__).resolve().parents[1];D=R/'data/processed/continents';fs=json.loads((D/'display-preplacement.geojson').read_text())['features'];G={f['properties']['id']:shape(f['geometry']) for f in fs};assert len(G)==len(fs)==7
results={}
for inputname,outname,reportname in [('placements.json','layout.geojson','validation.json'),('individual-placements.json','individual-layout.geojson','individual-validation.json')]:
 if not (R/inputname).exists():continue
 saved=json.loads((R/inputname).read_text());features=[];reports=[]
 for p in saved['panels']:
  n=p['panel'];host=G[p['host']];guests=[];ids=[];drifts=[]
  for v in p['placements']:
   g=translate(rotate(G[v['id']],v['rotation_degrees'],origin=(0,0)),xoff=v['translation_x_m'],yoff=v['translation_y_m']);assert g.is_valid;d=abs(g.area/G[v['id']].area-1);assert d<1e-12;drifts.append(d);guests.append(g);ids.append(v['id'])
  outside={k:g.difference(host).area/1e6 for k,g in zip(ids,guests)};overlap=sum(a.intersection(b).area/1e6 for i,a in enumerate(guests) for b in guests[i+1:]);total=sum(g.area for g in guests)/1e6
  report={'panel':n,'host':p['host'],'guests':ids,'status':'verified fit' if sum(outside.values())==0 and overlap==0 else 'partial overlay; full containment not found','guest_total_km2':total,'host_km2':host.area/1e6,'area_ratio_percent':total/(host.area/1e6)*100,'outside_km2':outside,'pairwise_overlap_km2':overlap,'relative_area_drift':max(drifts),'valid':True,'interpretation':'A saved partial overlay is not a certified fit; bounded search failure is not an impossibility proof.'};u=unary_union(guests);report.update({'outside_guest_union_km2':u.difference(host).area/1e6,'host_covered_unique_km2':u.intersection(host).area/1e6,'remaining_comparison_area_km2':host.difference(u).area/1e6});reports.append(report)
  features.append({'type':'Feature','properties':{'panel':n,'id':p['host'],'role':'host'},'geometry':mapping(host)})
  features.extend({'type':'Feature','properties':{'panel':n,'id':k,'role':'guest'},'geometry':mapping(g)} for k,g in zip(ids,guests))
 (D/outname).write_text(json.dumps({'type':'FeatureCollection','features':features},separators=(',',':')));(D/reportname).write_text(json.dumps(reports,indent=2));results[reportname]=reports
 with (R/'outputs'/reportname.replace('.json','.csv')).open('w') as f:
  fields=['panel','host','guests','status','guest_total_km2','host_km2','area_ratio_percent','outside_total_km2','pairwise_overlap_km2','relative_area_drift','host_covered_unique_km2','remaining_comparison_area_km2'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for x in reports:w.writerow({**{k:x[k] for k in fields if k not in ['guests','outside_total_km2']},'guests':'+'.join(x['guests']),'outside_total_km2':sum(x['outside_km2'].values())})
print(json.dumps({k:[{'guests':x['guests'],'status':x['status'],'outside_km2':sum(x['outside_km2'].values())} for x in v] for k,v in results.items()},indent=2))
