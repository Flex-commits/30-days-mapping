"""Check independent provenance, geometry, layout assets and deterministic export."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import json,hashlib,re,subprocess,sys
from PIL import Image
import geopandas as gpd
from pyproj import Geod,Transformer
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config.json').read_text());manifest=json.loads((R/'data/source-manifest.json').read_text());photos=json.loads((R/'data/photo-credits.json').read_text());frames=json.loads((R/'data/imagery-frames.json').read_text());checks={}
checks['frozen_input_hashes']=all(hashlib.sha256((R/x['file']).read_bytes()).hexdigest()==x['sha256'] for x in manifest['frozen_inputs']);assert checks['frozen_input_hashes']
points=gpd.read_file(R/'data/processed/viewpoints.geojson');pairs=gpd.read_file(R/'data/processed/site-pairs.geojson');assert len(points)==6 and points.id.is_unique and len(pairs)==3 and pairs.id.is_unique and points.geometry.is_valid.all() and pairs.geometry.is_valid.all();checks['six_unique_sites_three_pairs']=True
G=Geod(ellps='WGS84');T=Transformer.from_crs(4326,26918,always_xy=True)
for p in C['pairs']:
 a,b=[(p[s]['lon'],p[s]['lat']) for s in ['nj','ny']];dist=G.inv(*a,*b)[2]/1609.344;reported=float(pairs[pairs.id==p['id']].distance_miles.iloc[0]);assert abs(dist-reported)<1e-9
 for side in ['nj','ny']:
  r=next(x for x in photos if x['id']==p['id']+'-'+side);assert r['license'] in ['CC BY-SA 4.0','CC BY-SA 3.0'];assert r['creator'] and r['license_url'] and r['page_url'];assert re.fullmatch(r'\d{4}-\d{2}-\d{2}',r['capture_date'][:10])
  if r.get('camera_latitude'):
   assert abs(float(r['camera_latitude'])-p[side]['lat'])<1e-7 and abs(float(r['camera_longitude'])-p[side]['lon'])<1e-7
  else:assert p['id']=='03' and side=='nj' and p[side]['coordinate_basis'].startswith('Park operator')
  frame=next(f for f in frames if f['id']==p['id']);x,y=T.transform(*[p[side][k] for k in ['lon','lat']]);x0,y0,x1,y1=frame['actual_bounds'];assert x0<=x<=x1 and y0<=y<=y1
checks.update({'geodesic_miles_independently_checked':True,'photo_dates_rights_and_coordinate_bases_checked':True,'sites_within_corresponding_aerial_frames':True})
for f in frames:
 image=R/'data/raw'/f['source_file'];assert list(Image.open(image).size)==f['actual_size'];assert hashlib.sha256(image.read_bytes()).hexdigest()==f['sha256'];assert all(__import__('math').isfinite(x) for x in f['actual_bounds']);assert 'bboxSR=26918' in f['request_url'] and 'imageSR=26918' in f['request_url']
checks['imagery_bounds_pixels_hashes_and_CRS']=True
assert Image.open(R/'outputs/seeing-the-hudson.png').size==(4500,5400);assert Image.open(R/'outputs/05-thomas-hagos.png').size==(600,600);checks['export_sizes']=True
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'href' in a:self.links.append(a['href'])
  if tag=='img':assert a.get('alt');self.images.append(a['src'])
p=Parser();p.feed((R/'site/index.html').read_text())
for s in p.links+p.images:
 if not urlparse(s).scheme and not s.startswith('#'):assert (R/'site'/unquote(s)).exists(),s
assert len(p.images)>=10;checks['static_page_local_links_and_image_alt_text']=True
poster=R/'outputs/seeing-the-hudson.png';before=hashlib.sha256(poster.read_bytes()).hexdigest();subprocess.run([sys.executable,str(R/'scripts/render.py')],check=True,stdout=subprocess.DEVNULL);assert hashlib.sha256(poster.read_bytes()).hexdigest()==before;checks['repeat_render_byte_identical']=True
report={'passed':all(checks.values()),'checks':checks,'frozen_inputs':len(manifest['frozen_inputs']),'poster_sha256':before,'viewpoint_count':6,'pair_count':3,'poster_pixels':[4500,5400],'thumbnail_pixels':[600,600],'browser_visual_QA':'Pending; static poster inspected separately.','limitations':'No modeled visibility, current-condition claim or certified access/coordinate accuracy.'};(R/'docs/validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
