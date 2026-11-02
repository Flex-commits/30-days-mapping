from pathlib import Path
import json,urllib.request,urllib.parse,concurrent.futures
root=Path(__file__).resolve().parents[1]
p=root/'source-data/geocodes.json';cache=json.loads(p.read_text())
queries={'adult-drop-in-06':'100-32 Atlantic Avenue, Ozone Park, NY 11416','adult-drop-in-08':'92-32 Union Hall Street, Jamaica, NY 11433','youth-drop-in-06':'165-13 Jamaica Avenue, Jamaica, NY 11432','youth-drop-in-07':'1600 Central Avenue, Far Rockaway, NY 11691'}
def get(pair):
 key,address=pair;url='https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?'+urllib.parse.urlencode({'address':address,'benchmark':'Public_AR_Current','format':'json'})
 return key,{'query':address,'url':url,'response':json.load(urllib.request.urlopen(url,timeout=40))}
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 for key,r in pool.map(get,queries.items()):
  cache[key]=r;p.write_text(json.dumps(cache,indent=2))
  print(key,r['response']['result']['addressMatches'])
