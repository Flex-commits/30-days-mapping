"""Bounded, deterministic rigid placement feasibility search, not optimal packing."""
from pathlib import Path
import json,math,time
import numpy as np
from shapely.geometry import shape,mapping,Point
from shapely.affinity import rotate,translate
from shapely.prepared import prep
R=Path(__file__).resolve().parents[1];D=R/'data/processed'
def main():
 cfg=json.loads((R/'config.json').read_text());fs=json.loads((D/'display-preplacement.geojson').read_text())['features'];geos={f['properties']['id']:shape(f['geometry']) for f in fs};af=geos['AFR'];host=max(af.geoms,key=lambda g:g.area) if hasattr(af,'geoms') else af;safe=host.buffer(-cfg['placement_clearance_m']);prepared=prep(safe);grid=cfg['placement_grid_m'];xmin,ymin,xmax,ymax=safe.bounds
 xs=np.arange(math.ceil(xmin/grid)*grid,xmax,grid);ys=np.arange(math.ceil(ymin/grid)*grid,ymax,grid);points=[(float(x),float(y)) for x in xs for y in ys if safe.contains(Point(x,y))]
 angles=[0]+[a*s for a in range(15,181,15) for s in [1,-1] if not(a==180 and s==-1)];cache={};logs=[]
 targets={'CHN':(-600000,1300000),'USA48':(-600000,1200000),'IND':(1100000,-1500000),'DEU':(-1900000,200000),'JPN':(500000,0)}
 def candidates(key,occupied,limit=1):
  pref=targets[key];ordered=sorted(points,key=lambda p:((p[0]-pref[0])**2+(p[1]-pref[1])**2));hits=[];attempts=0
  for angle in angles:
   token=(key,angle)
   if token not in cache:cache[token]=(rotate(geos[key].simplify(10000,preserve_topology=True),angle,origin=(0,0)),rotate(geos[key],angle,origin=(0,0)))
   proxy,actual=cache[token]
   for x,y in ordered:
    attempts+=1
    if attempts>cfg['max_attempts_per_country']:break
    p=translate(proxy,xoff=x,yoff=y)
    if not prepared.contains(p):continue
    if any(p.intersects(g.buffer(15000)) for g in occupied):continue
    full=translate(actual,xoff=x,yoff=y)
    if not prepared.contains(full) or any(full.intersects(g.buffer(15000)) for g in occupied):continue
    hits.append((full,{'id':key,'rotation_degrees':angle,'translation_x_m':x,'translation_y_m':y,'attempts_at_hit':attempts}))
    if len(hits)>=limit:return hits,attempts
   if attempts>cfg['max_attempts_per_country']:break
  return hits,attempts
 tests=[['CHN','USA48','IND'],*cfg['candidate_sets']];chosen=None
 for items in tests:
  print('Testing',items,flush=True);first,n=candidates(items[0],[],limit=6);best=[]
  for shape0,placement0 in first:
   packed=[shape0];placements=[placement0]
   for key in items[1:]:
    fits,tried=candidates(key,packed)
    if not fits:break
    packed.append(fits[0][0]);placements.append(fits[0][1])
   if len(packed)>len(best):best=placements
   if len(packed)==len(items):chosen=(packed,placements);break
  logs.append({'candidate_set':items,'largest_search_attempts':n,'largest_shape_feasible_start_count':len(first),'best_prefix_placed':[x['id'] for x in best],'complete':chosen is not None,'interpretation':'A failed bounded search is not a proof of geometric impossibility.'})
  if chosen:break
 if chosen is None:
  items=['USA48','IND'];first,_=candidates(items[0],[],1);packed=[first[0][0]];placements=[first[0][1]]
  fits,_=candidates('IND',packed)
  if fits:packed.append(fits[0][0]);placements.append(fits[0][1])
  chosen=(packed,placements)
 packed,placements=chosen
 areas=[g.area for g in packed];outside=[g.difference(af).area for g in packed];overlap=[{'a':placements[i]['id'],'b':placements[j]['id'],'overlap_m2':packed[i].intersection(packed[j]).area} for i in range(len(packed)) for j in range(i+1,len(packed))]
 assert max(outside)==0 and all(x['overlap_m2']==0 for x in overlap)
 errors=[abs(g.area/geos[p['id']].area-1) for g,p in zip(packed,placements)];assert max(errors)<1e-12
 (R/'placements.json').write_text(json.dumps({'placements':placements,'search_log':logs,'seed':cfg['random_seed'],'search_is_deterministic':True},indent=2));(D/'layout.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','geometry':mapping(af),'properties':{'id':'AFR'}}]+[{'type':'Feature','geometry':mapping(g),'properties':{'id':p['id']}} for g,p in zip(packed,placements)]},separators=(',',':')))
 summary={'selected':[p['id'] for p in placements],'africa_km2':af.area/1e6,'comparison_km2':sum(areas)/1e6,'share_percent':sum(areas)/af.area*100,'remaining_comparison_area_km2':(af.area-sum(areas))/1e6,'outside_m2':outside,'pairwise_overlap':overlap,'max_relative_area_change_through_placement':max(errors),'display_geometries_valid':all(g.is_valid for g in packed),'source_and_display_simplification_m':0,'clearance_target_m':15000,'interpretation':'Area-preserving partial packing, not an exact fill. Residual is unoccupied comparison area, not empty African land.'};(D/'draft-validation.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
