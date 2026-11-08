"""Freeze USGS's cached orthoimagery. Local pixel dates are not exposed by this MapServer."""
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from concurrent.futures import ThreadPoolExecutor
from pyproj import Transformer
from PIL import Image
import json,hashlib,time
R=Path(__file__).resolve().parents[1];RAW=R/'data/raw';C=json.loads((R/'config.json').read_text());T=Transformer.from_crs(4326,26918,always_xy=True);SERVICE='https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer'
frames=[]
for p in C['pairs']:
 xy=[T.transform(p[s]['lon'],p[s]['lat']) for s in ['nj','ny']];x=sum(z[0] for z in xy)/2;y=sum(z[1] for z in xy)/2;w=C['frame_width_m'];h=C['frame_height_m'];frames.append({'id':p['id'],'bounds':[x-w/2,y-h/2,x+w/2,y+h/2],'size':[1560,930]})
xy=[T.transform(p[s]['lon'],p[s]['lat']) for p in C['pairs'] for s in ['nj','ny']];x=(min(z[0] for z in xy)+max(z[0] for z in xy))/2;y=(min(z[1] for z in xy)+max(z[1] for z in xy))/2;frames.append({'id':'overview','bounds':[x-4900,y-10150,x+4900,y+10150],'size':[1200,2486]})
def download(url):
 for attempt in range(3):
  try:
   with urlopen(Request(url,headers={'User-Agent':'ThomasHagos-MUSA-map/1.0'}),timeout=60) as z:return z.read()
  except Exception:
   if attempt==2:raise
   time.sleep(1)
def fetch(f):
 params={'bbox':','.join(map(str,f['bounds'])),'bboxSR':26918,'imageSR':26918,'size':','.join(map(str,f['size'])),'format':'jpg','dpi':150,'transparent':'false','f':'json'};u=SERVICE+'/export?'+urlencode(params);meta_path=RAW/('usgs-'+f['id']+'-metadata.json');p=RAW/('usgs-'+f['id']+'.jpg')
 if not meta_path.exists():meta_path.write_bytes(download(u))
 m=json.loads(meta_path.read_text());assert 'error' not in m,m
 if not p.exists():p.write_bytes(download(m['href']))
 im=Image.open(p);assert im.format=='JPEG';ext=m['extent'];f.update({'actual_bounds':[ext[k] for k in ['xmin','ymin','xmax','ymax']],'actual_size':list(im.size),'request_url':u,'source_file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':'USGS Imagery Only / The National Map','acquisition_date_note':'Service metadata reports CONUS NAIP sources 2017–2021; exact local pixel dates unavailable. Service refresh June 2024 is not capture date.'});print(f['id'],p.stat().st_size,flush=True);return f
meta=RAW/'usgs-imagery-metadata.json'
if not meta.exists():meta.write_bytes(download(SERVICE+'?f=json'))
result=list(ThreadPoolExecutor(max_workers=4).map(fetch,frames));(R/'data/imagery-frames.json').write_text(json.dumps(result,indent=2))
