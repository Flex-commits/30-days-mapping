from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import json,hashlib,subprocess,sys
import numpy as np
from PIL import Image
from pyproj import Transformer,Geod
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config.json').read_text());M=json.loads((R/'data/source-manifest.json').read_text());checks={}
assert all(hashlib.sha256((R/v['file']).read_bytes()).hexdigest()==v['sha256'] for v in M['frozen_inputs']);checks['all_frozen_inputs_match']=True
T=np.load(R/'data/terrain.npz');z=T['z'];P=json.loads((R/'data/terrain-provenance.json').read_text());assert list(z.shape)==P['crop_shape'] and hashlib.sha256(z.tobytes()).hexdigest()==P['crop_value_sha256'];assert [float(T['lon_left']),float(T['lat_top'])]==P['first_pixel_center'];checks['terrain_matches_original_source_grid_and_values']=True
prov=json.loads((R/'data/site-provenance.json').read_text());assert len(prov)==27 and len({v['osm'] for v in prov})==27;assert all(abs(v['source_lat']-v['saved_lat'])<1e-6 and abs(v['source_lon']-v['saved_lon'])<1e-6 and v['version'] for v in prov);checks['all_site_anchors_match_OSM_source_records']=True
B=json.loads((R/'data/scenario-buildings.json').read_text())['buildings'];top=float(T['lat_top']);left=float(T['lon_left']);step=float(T['step']);bottom=top-(z.shape[0]-1)*step;right=left+(z.shape[1]-1)*step
for v in B:
 assert bottom<v['lat']<top and left<v['lon']<right
 assert 3<=v['storeys']<=C['maximum_chosen_storeys'] and abs(v['height_metres']-(C['podium_metres']+v['storeys']*C['storey_metres']))<1e-9
 assert v['kind'].startswith('imagined')
assert abs(max(v['height_metres'] for v in B)-88.08)<1e-9;checks['every_scenario_building_in_extent_and_height_arithmetic_checked']=True
# Independent UTM east-west scale check.
f=Transformer.from_crs(4326,32637,always_xy=True);inv=Transformer.from_crs(32637,4326,always_xy=True);x,y=f.transform(38.715,14.13);a=inv.transform(x,y);b=inv.transform(x+500,y);assert abs(Geod(ellps='WGS84').inv(*a,*b)[2]/500-1)<.001;checks['east_west_500_m_scale_ground_check']=True
for n,size in [('aksum-built.png',(2160,2700)),('08-thomas-hagos.png',(600,600))]:assert Image.open(R/'outputs'/n).size==size
checks['poster_and_thumbnail_dimensions']=True
class PHTML(HTMLParser):
 def __init__(self):super().__init__();self.refs=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='img':assert a.get('alt');self.refs.append(a['src'])
  if t=='a':self.refs.append(a.get('href',''))
p=PHTML();p.feed((R/'site/index.html').read_text())
for v in p.refs:
 if not urlparse(v).scheme and not v.startswith(('../','#')):assert (R/'site'/v).exists(),v
checks['static_page_links_and_image_alt_text']=True
before={v:hashlib.sha256((R/'outputs'/v).read_bytes()).hexdigest() for v in ['aksum-built.png','08-thomas-hagos.png','aksum-skyline-detail.png']};subprocess.run([sys.executable,str(R/'scripts/render.py')],check=True,stdout=subprocess.DEVNULL);assert all(hashlib.sha256((R/'outputs'/v).read_bytes()).hexdigest()==h for v,h in before.items());checks['repeat_render_images_byte_identical']=True
report={'passed':True,'checks':checks,'building_count':len(B),'landmark_towers':sum(v['kind']=='imagined landmark tower' for v in B),'imagined_houses':sum(v['kind']=='imagined home' for v in B),'image_sha256':before,'visual_QA':'Poster and thumbnail inspected; skyline detail provided for larger view.','scope':'Speculative illustration, not archaeological reconstruction or site-capacity assessment.'};(R/'docs/validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
