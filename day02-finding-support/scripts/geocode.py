from pathlib import Path
import json,urllib.request,urllib.parse,concurrent.futures
ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'source-data/directory.json').read_text())['records']
cachepath=ROOT/'source-data/geocodes.json'
cache=json.loads(cachepath.read_text()) if cachepath.exists() else {}
def fetch(r):
 if r['id'] in cache:return r['id'],cache[r['id']]
 city={'Manhattan':'New York','Bronx':'Bronx','Brooklyn':'Brooklyn','Queens':'Queens','Staten Island':'Staten Island'}[r['borough']]
 address=r['address'].split(', Floor')[0]+', '+city+', NY'
 url='https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?'+urllib.parse.urlencode({'address':address,'benchmark':'Public_AR_Current','format':'json'})
 try:
  response=json.load(urllib.request.urlopen(url,timeout=40))
  return r['id'],{'query':address,'url':url,'response':response}
 except Exception as e:return r['id'],{'query':address,'error':str(e)}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for key,value in pool.map(fetch,rows):
  cache[key]=value;cachepath.write_text(json.dumps(cache,indent=2))
for r in rows:
 c=cache[r['id']];m=c.get('response',{}).get('result',{}).get('addressMatches',[])
 print(r['id'],r['name'],json.dumps(m[0] if m else {'error':'No match'}))
