"""Bounded rigid-placement search. A failed search is not a proof of impossibility."""
from pathlib import Path
import json,math,time
import numpy as np
from shapely.geometry import shape,mapping
from shapely.affinity import rotate,translate
R=Path(__file__).resolve().parents[1];D=R/'data/processed/continents';C=json.loads((R/'config.json').read_text());rng=np.random.default_rng(C['seed'])
fs=json.loads((D/'display-preplacement.geojson').read_text())['features'];G={x['properties']['id']:shape(x['geometry']) for x in fs};P={k:g.simplify(C['search_simplification_m'],preserve_topology=False).buffer(0) for k,g in G.items()}
def move(g,p):return translate(rotate(g,p[0],origin=(0,0)),xoff=p[1],yoff=p[2])
def feature(g,**p):return {'type':'Feature','properties':p,'geometry':mapping(g)}
reports=[];layout=[];saved=[]
for panel,test in enumerate(C['panels'],1):
 start=time.monotonic();host=test['host'];ids=test['guests'];h=P[host];states=[];placed=[];xmin,ymin,xmax,ymax=h.bounds
 for key in ids:
  best=(float('inf'),None,None)
  for trial in range(C['pair_initial_trials_per_guest']):
   p=[float(rng.integers(-12,12)*15),float(rng.uniform(xmin*.65,xmax*.65)),float(rng.uniform(ymin*.65,ymax*.65))];g=move(P[key],p)
   if not g.is_valid:continue
   cost=g.difference(h).area+sum(g.intersection(o).area*2 for o in placed)
   if cost<best[0] and move(G[key],p).is_valid:best=(cost,p,g)
  states.append(best[1]);placed.append(best[2])
 # Coordinate refinement, all transformations remain rigid. No shape scaling or clipping.
 for sweep in range(C['pair_refinement_sweeps']):
  radius=700000/(1+sweep);delta=30/(1+sweep)
  for j,key in enumerate(ids):
   def score(g):return g.difference(h).area+sum(g.intersection(o).area*2 for n,o in enumerate(placed) if n!=j)
   best=score(placed[j])
   for trial in range(C['pair_refinement_trials_per_guest_per_sweep']):
    base=states[j];p=[base[0]+rng.uniform(-delta,delta),base[1]+rng.normal(0,radius),base[2]+rng.normal(0,radius)];g=move(P[key],p)
    if not g.is_valid:continue
    cost=score(g)
    if cost<best and move(G[key],p).is_valid:best=cost;states[j]=[float(v) for v in p];placed[j]=g
 full=[move(G[k],p) for k,p in zip(ids,states)];out=[g.difference(G[host]).area/1e6 for g in full];overlap=sum(a.intersection(b).area/1e6 for i,a in enumerate(full) for b in full[i+1:]);total=sum(g.area for g in full)/1e6
 valid=all(g.is_valid for g in full);drift=max(abs(g.area/G[k].area-1) for k,g in zip(ids,full));status='verified fit' if sum(out)==0 and overlap==0 else 'partial overlay; full containment not found'
 report={'panel':panel,'host':host,'guests':ids,'status':status,'guest_total_km2':total,'host_km2':G[host].area/1e6,'area_ratio_percent':total/(G[host].area/1e6)*100,'outside_km2':dict(zip(ids,out)),'pairwise_overlap_km2':overlap,'relative_area_drift':drift,'valid':valid,'runtime_seconds':round(time.monotonic()-start,1),'interpretation':'No containment claim unless outside and overlap are exactly zero. Bounded search failure is not an impossibility proof.'}
 reports.append(report);saved.append({'panel':panel,'host':host,'placements':[{'id':k,'rotation_degrees':p[0],'translation_x_m':p[1],'translation_y_m':p[2]} for k,p in zip(ids,states)]});layout.append(feature(G[host],panel=panel,id=host,role='host'))
 layout.extend(feature(g,panel=panel,id=k,role='guest') for k,g in zip(ids,full))
 print(json.dumps(report),flush=True)
(D/'layout.geojson').write_text(json.dumps({'type':'FeatureCollection','features':layout},separators=(',',':')));(D/'validation.json').write_text(json.dumps(reports,indent=2));(R/'placements.json').write_text(json.dumps({'seed':C['seed'],'panels':saved},indent=2))
