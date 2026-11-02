"""Normalize public directory records and reproduce address points from cached geocodes."""
import json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'source-data/directory.json').read_text());cache=json.loads((ROOT/'source-data/geocodes.json').read_text())
rows=[]
phones={'intake-02':'929-281-2330','intake-03':'718-483-7700','intake-05':'718-503-6400','youth-drop-in-01':'212-206-0574','youth-drop-in-02':'646-690-8986','youth-drop-in-03':'212-695-2220','youth-drop-in-04':'646-230-1037','youth-drop-in-05':'718-685-3850','youth-drop-in-06':'718-526-2400','youth-drop-in-07':'646-518-1202','youth-drop-in-08':'718-876-4752'}
for n,r in enumerate(source['records'],1):
 hit=cache[r['id']]['response']['result']['addressMatches'][0]
 assert hit['addressComponents']['state']=='NY'
 lon,lat=hit['coordinates']['x'],hit['coordinates']['y']
 assert -74.3<lon<-73.65 and 40.45<lat<40.95
 kind='adult' if r['id'].startswith('adult') else 'intake' if r['id'].startswith('intake') else 'youth'
 hours=r['hours'].split('; call to confirm')[0].replace(' (NYC311 listing)','').replace(' (official listing)','')
 record={'id':r['id'],'number':str(n).zfill(2),'name':r['name'],'type':kind,'category':r['category'],'borough':r['borough'],'address':r['address'],'audience':r['audience'],'hours':hours,'listed24h':kind!='youth' or hours=='24/7','phone':phones.get(r['id']),'phone_ext':'2080' if r['id']=='youth-drop-in-06' else None,'lat':lat,'lon':lon,'source':r['source_url'],'additional_source':r.get('supporting_source_url'),'checked':'2026-11-02','coordinate_source':cache[r['id']]['url'],'coordinate_method':'U.S. Census address interpolation; approximate street location, not an entrance survey','matched_address':hit['matchedAddress']}
 if r['longitude'] is not None:
  dx=(lon-r['longitude'])*111320*math.cos(math.radians(lat));dy=(lat-r['latitude'])*111320
  record['difference_from_opendata_m']=round(math.hypot(dx,dy))
 rows.append(record)
(ROOT/'dist/data/locations.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
(ROOT/'dist/data/locations.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','geometry':{'type':'Point','coordinates':[r['lon'],r['lat']]},'properties':r} for r in rows]},ensure_ascii=False))
# Reduce high-resolution shoreline vertices while keeping approximately 5m precision.
def simplify(points,tol=.00005):
 if len(points)<4:return points
 a,b=points[0],points[-1];dx=b[0]-a[0];dy=b[1]-a[1];den=dx*dx+dy*dy
 best,index=0,0
 for i,p in enumerate(points[1:-1],1):
  t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/den)) if den else 0
  dist=(p[0]-a[0]-t*dx)**2+(p[1]-a[1]-t*dy)**2
  if dist>best:best,index=dist,i
 if best>tol*tol:return simplify(points[:index+1],tol)[:-1]+simplify(points[index:],tol)
 return [a,b]
geo=json.loads((ROOT/'source-data/boroughs.geojson').read_text())
for f in geo['features']:
 for polygon in f['geometry']['coordinates']:
  for i,ring in enumerate(polygon):
   reduced=simplify(ring)
   if len(reduced)>=4:polygon[i]=[[round(x,6),round(y,6)] for x,y,*_ in reduced]
(ROOT/'dist/data/boroughs.geojson').write_text(json.dumps(geo,separators=(',',':')))
print('21 address-matched locations; 5 boroughs. Largest existing-coordinate difference:',max(r.get('difference_from_opendata_m',0) for r in rows),'m')
