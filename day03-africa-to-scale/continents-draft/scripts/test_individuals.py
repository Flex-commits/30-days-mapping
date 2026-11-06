"""Fallback: bounded complete-continent tests; no arbitrary scaling or component omission."""
from pathlib import Path
import json,time
import numpy as np
from shapely.geometry import shape,mapping
from shapely.affinity import rotate,translate
from shapely.prepared import prep
R=Path(__file__).resolve().parents[1];D=R/'data/processed/continents';C=json.loads((R/'config.json').read_text());fs=json.loads((D/'display-preplacement.geojson').read_text())['features'];G={f['properties']['id']:shape(f['geometry']) for f in fs};rng=np.random.default_rng(C['seed']+1);host=G['AFR'];safe=prep(host.buffer(-C['individual_clearance_m']));proxyhost=host.simplify(18000,preserve_topology=False).buffer(0);layout=[];saved=[];reports=[]
for n,key in enumerate(['SAM','AUS','ANT','EUR','NAM'],1):
 best=(float('inf'),None,None);pgeo=G[key].simplify(18000,preserve_topology=False).buffer(0);found=False;start=time.monotonic()
 for trial in range(C['individual_max_trials']):
  if trial<5000 or best[1] is None:angle=float(rng.integers(-18,18)*10);x=float(rng.uniform(-2300000,2300000));y=float(rng.uniform(-2300000,2600000))
  else:
   radius=600000/(1+(trial-5000)/2000);b=best[1];angle=b[0]+float(rng.uniform(-12,12));x=b[1]+float(rng.normal(0,radius));y=b[2]+float(rng.normal(0,radius))
  g=translate(rotate(pgeo,angle,origin=(0,0)),xoff=x,yoff=y)
  if not g.is_valid:continue
  cost=g.difference(proxyhost).area
  if cost<=best[0]:
   full=translate(rotate(G[key],angle,origin=(0,0)),xoff=x,yoff=y)
   if not full.is_valid:continue
   best=(cost,[angle,x,y],full)
   if safe.contains(full):found=True;break
 g=best[2];out=g.difference(host).area/1e6;assert g.is_valid;drift=abs(g.area/G[key].area-1);assert drift<1e-12
 layout.extend([{'type':'Feature','properties':{'panel':n,'id':'AFR','role':'host'},'geometry':mapping(host)},{'type':'Feature','properties':{'panel':n,'id':key,'role':'guest'},'geometry':mapping(g)}]);saved.append({'panel':n,'host':'AFR','placements':[{'id':key,'rotation_degrees':best[1][0],'translation_x_m':best[1][1],'translation_y_m':best[1][2]}]})
 report={'panel':n,'host':'AFR','guests':[key],'status':'verified fit' if out==0 else 'partial overlay; full containment not found','guest_total_km2':g.area/1e6,'host_km2':host.area/1e6,'area_ratio_percent':g.area/host.area*100,'outside_km2':{key:out},'pairwise_overlap_km2':0,'relative_area_drift':drift,'valid':True,'trials':trial+1,'runtime_seconds':round(time.monotonic()-start,1)};reports.append(report);print(json.dumps(report),flush=True)
# Asia exception: retain the previous best saved overlay, with its truthful outside-area measure.
old=json.loads((D/'layout.geojson').read_text())['features'];oldreport=json.loads((D/'validation.json').read_text())[-1];oldreport['panel']=6;reports.append(oldreport)
for f in old:
 if f['properties']['panel']==4:f['properties']['panel']=6;layout.append(f)
p=json.loads((R/'placements.json').read_text())['panels'][-1];p['panel']=6;saved.append(p)
(D/'individual-layout.geojson').write_text(json.dumps({'type':'FeatureCollection','features':layout},separators=(',',':')));(D/'individual-validation.json').write_text(json.dumps(reports,indent=2));(R/'individual-placements.json').write_text(json.dumps({'seed':C['seed']+1,'panels':saved},indent=2))
