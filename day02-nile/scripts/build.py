"""Select the Nile by basin code and directed river connectivity; never fabricate links."""
from pathlib import Path
from collections import defaultdict,Counter
import json
import shapely
import geopandas as gpd
from shapely.geometry import Point,box
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw';OUT=ROOT/'data/processed';OUT.mkdir(exist_ok=True)
CONFIG=json.loads((ROOT/'config.json').read_text());CRS=CONFIG['projection']
r=gpd.read_file(RAW/'rivers.zip');b=gpd.read_file(RAW/'basins02.zip');b=b[b.PFAF_ID==CONFIG['basin_pfaf_id']].copy();assert len(b)==1
# UNESCO's Nile subset preserves the original IDs; use the dominant connected outlet.
root=int(r.groupby('MAIN_RIV').size().idxmax());network=r[r.MAIN_RIV==root].copy();assert root==CONFIG['main_riv']
nexts=dict(zip(network.HYRIV_ID.astype(int),network.NEXT_DOWN.astype(int)));reverse=defaultdict(list)
for a,z in nexts.items():reverse[z].append(a)
def path(seed):
 out=[];seen=set()
 while seed:
  assert seed not in seen and seed in nexts,'Cycle or missing downstream reach'
  seen.add(seed);out.append(seed);seed=nexts[seed]
 return out
def before_join(a,z):
 pa,pz=path(a),set(path(z));return pa[next(i for i,v in enumerate(pa) if v in pz)-1]
white=before_join(10445476,10442890);blue=before_join(10442890,10445476);atbara=before_join(10383506,10445476)
def upstream(seed):
 seen=set();todo=[seed]
 while todo:
  v=todo.pop()
  if v not in seen:seen.add(v);todo.extend(reverse[v])
 return seen
groups={k:upstream(v) for k,v in [('White Nile system',white),('Blue Nile system',blue),('Atbara system',atbara)]}
network['system']='Main Nile / other connected tributaries'
for k,ids in groups.items():network.loc[network.HYRIV_ID.isin(ids),'system']=k
# Check every edge points to a retained reach or the single sea outlet; validate drainage terminates.
assert len(set(nexts.values())-set(nexts)-{0})==0
state={0}
for seed in nexts:
 trail=[];local=set();v=seed
 while v not in state:
  assert v not in local;local.add(v);trail.append(v);v=nexts[v]
 state.update(trail)
assert len(state)==len(network)+1
basin=b.geometry.union_all();shapely.prepare(basin);inside=shapely.intersects(basin,network.geometry.array)
assert inside.all(), 'Selected reach lies outside Nile basin'
for name,x,y in [('Khartoum',32.53,15.60),('Lake Victoria',33,-1),('Lake Tana',37.3,12),('Juba',31.6,4.85)]:assert basin.covers(Point(x,y)),name
context=gpd.read_file(RAW/'countries.zip',bbox=(20,-6,43,34));context=context[['ADMIN','NAME','geometry']];context=gpd.clip(context,box(20,-6,43,34))
lakes=gpd.read_file(RAW/'lakes.zip',bbox=(20,-6,43,34));lakes=lakes[lakes.intersects(basin)].copy();lakes=lakes[['name','geometry']]
# Native WGS84 geometry remains unchanged in this local cache. No raw hydrography is redistributed in Git.
for name,d in [('rivers',network),('basin',b),('countries',context),('lakes',lakes)]:
 p=OUT/(name+'.gpkg')
 if p.exists():p.unlink()
 d.to_file(p,driver='GPKG')
network[['HYRIV_ID','NEXT_DOWN','ORD_STRA','system']].to_csv(OUT/'reach-classification.csv',index=False)
terminal=network[network.NEXT_DOWN==0].iloc[0]
report={'basin_pfaffstetter_level2':17,'basin_hybas_id':int(b.iloc[0].HYBAS_ID),'basin_area_source_km2':float(b.iloc[0].SUB_AREA),'main_riv':root,'connected_reaches':len(network),'subset_reaches':len(r),'excluded_other_network_reaches':len(r)-len(network),'single_outlet_reaches':int((network.NEXT_DOWN==0).sum()),'all_downstream_ids_retained':True,'all_paths_terminate_without_cycles':True,'all_reaches_intersect_nile_boundary':bool(inside.all()),'system_counts':network.system.value_counts().to_dict(),'strahler_counts':{str(k):v for k,v in Counter(network.ORD_STRA).items()},'seed_reaches_before_confluences':{'White Nile system':white,'Blue Nile system':blue,'Atbara system':atbara},'projection':CRS,'delta_limitation':'Single-flow-direction network retains one sea outlet; not a full delta distributary or irrigation-channel inventory. No channels have been added.','lake_limitation':'Natural Earth lake polygons are generalized independently of HydroRIVERS. River centerlines crossing lakes are modeled routing, not surveyed open-water channels.'}
(OUT/'validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
