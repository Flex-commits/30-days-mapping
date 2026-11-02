"""Join each service to its nearest MTA subway/SIR station by haversine distance.
Distances are straight-line proximity, not routes. Inputs are saved snapshots.
"""
import json, math, statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'dist/data/locations.json').read_text())
raw=json.loads((ROOT/'source-data/mta-stations.json').read_text())
stations=[{'id':s['gtfs_stop_id'],'name':s['stop_name'],'routes':s['daytime_routes'],'system':'SIR' if s['division']=='SIR' else 'Subway','lat':float(s['gtfs_latitude']),'lon':float(s['gtfs_longitude'])} for s in raw]
def haversine(a,b):
 la1,lo1,la2,lo2=map(math.radians,[a['lat'],a['lon'],b['lat'],b['lon']]);h=math.sin((la2-la1)/2)**2+math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
 return 6371008.8*2*math.atan2(math.sqrt(h),math.sqrt(1-h))
features=[]
for r in rows:
 station=min(stations,key=lambda s:haversine(r,s));d=haversine(r,station)
 r['nearest_station']=station;r['rail_distance_m']=round(d,1);r['rail_distance_miles']=round(d/1609.344,6)
 r['rail_method']='Nearest MTA subway or Staten Island Railway station centroid by haversine distance. Straight line; not a walking route. Bus stops, entrances, ferry connections and service changes are not modeled.'
 features.append({'type':'Feature','geometry':{'type':'LineString','coordinates':[[station['lon'],station['lat']],[r['lon'],r['lat']]]},'properties':{'id':r['id'],'service':r['name'],'type':r['type'],'station':station['name'],'routes':station['routes'],'system':station['system'],'distance_m':round(d,1),'distance_miles':round(d/1609.344,6),'method':r['rail_method']}})
(ROOT/'dist/data/locations.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
(ROOT/'dist/data/locations.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[r['lon'],r['lat']]},'properties':r} for r in rows]},ensure_ascii=False))
(ROOT/'dist/data/rail-links.geojson').write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,indent=2)+'\n')
(ROOT/'dist/data/stations.json').write_text(json.dumps(stations,ensure_ascii=False,separators=(',',':')))
print('Stations:',len(stations),'Links:',len(features),'Within 500m:',sum(r['rail_distance_m']<=500 for r in rows),'Median:',round(statistics.median(r['rail_distance_m'] for r in rows)))
