from pathlib import Path
import urllib.request,json,hashlib,datetime
R=Path(__file__).resolve().parents[1];D=R/'data/raw';D.mkdir(exist_ok=True,parents=True)
urls={'countries.zip':'https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_0_countries.zip','natural-earth-source.html':'https://www.naturalearthdata.com/downloads/50m-cultural-vectors/50m-admin-0-countries-2/','natural-earth-terms.html':'https://www.naturalearthdata.com/about/terms-of-use/'}
manifest={}
for name,url in urls.items():
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'MUSA Africa to Scale geographic study'}),timeout=60) as f:b=f.read();final=f.url;modified=f.headers.get('Last-Modified')
 (D/name).write_bytes(b);manifest[name]={'url':url,'final_url':final,'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'http_last_modified':modified,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
(R/'data/downloads.json').write_text(json.dumps(manifest,indent=2));print('Natural Earth snapshot downloaded')
