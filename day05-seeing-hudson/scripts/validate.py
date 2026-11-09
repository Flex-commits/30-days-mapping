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
PA=json.loads((R/'data/port-authority.json').read_text());ov=next(f for f in frames if f['id']=='overview');x0,y0,x1,y1=ov['actual_bounds'];pa=gpd.read_file(R/'data/processed/port-authority-crossings.geojson');assert len(pa)==len(PA['crossings']) and pa.id.is_unique
for c in PA['crossings']:
 assert c['opened']<=c['pa_since'] and c['source'].startswith('https://')
 for s in ['nj','ny']:x,y=T.transform(c[s]['lon'],c[s]['lat']);assert x0<=x<=x1 and y0<=y<=y1,c['id']
 assert c['nj']['lon']<c['ny']['lon'],c['id']
assert set(PA['pair_links'])=={p['id'] for p in C['pairs']} and PA['portfolio']['source'].startswith('https://');assert Image.open(R/'outputs/port-authority.png').size==(3500,3000);checks['port_authority_crossings_in_overview_and_sourced']=True
# Extended chapter evidence: sources, coordinates and protected exports.
import csv
from shapely.geometry import Point,box
assert PA['design']['district_circle'] is False
for group in ['crossings','airports','ports','landmarks','beyond_frame']:
 for v in PA[group]:assert v['source'].startswith('https://') and v['status']=='confirmed',v['id'] if 'id' in v else v['name']
for v in PA['facts']+PA['portfolio']['items']:assert v['source'].startswith('https://') and v['status']=='confirmed'
assert PA['path_ridership']['display'] is False and PA['path_ridership']['status']=='uncertain'
assert len(PA['crossings'])==5 and len(PA['airports'])==3 and len(PA['ports'])==2
b=box(*PA['design']['bounds_wgs84']);fac=gpd.read_file(R/'data/processed/port-authority-facilities.geojson');assert len(fac)==6 and fac.id.is_unique and fac.is_valid.all() and fac.within(b).all() and fac.source.str.startswith('https://').all() and fac.coordinate_source.str.len().min()>10
for v in PA['crossings']:
 for side in ['nj','ny']:assert b.covers(Point(v[side]['lon'],v[side]['lat']))
 # Existing prepared crossing geometry must still match the recorded endpoint anchors.
 row=pa[pa.id==v['id']].iloc[0];assert list(row.geometry.coords)==[(v['nj']['lon'],v['nj']['lat']),(v['ny']['lon'],v['ny']['lat'])]
air={v['ident']:v for v in csv.DictReader(open(R/'data/raw/port-authority/airport-codes.csv'))}
for v in PA['airports']:
 lat,lon=map(float,air[v['id']]['coordinates'].split(','));assert (v['lat'],v['lon'])==(lat,lon) and -74.3<lon<-73.6 and 40.5<lat<40.95
assert points.within(b).all()
for name in ['land','shoreline']:
 coast=gpd.read_file(R/f'data/processed/port-authority-{name}.geojson');assert coast.is_valid.all() and coast.source.str.startswith('https://').all()
xx,yy=T.transform(-74.234,40.566);inv=Transformer.from_crs(26918,4326,always_xy=True);a=inv.transform(xx,yy);b_=inv.transform(xx+8046.72,yy);assert abs(G.inv(*a,*b_)[2]/8046.72-1)<.001
checks['port_authority_five_mile_scale_ground_check']=True
sl=gpd.read_file(R/'data/processed/port-authority-state-line.geojson');assert len(sl)==1 and sl.to_crs(26918).length.iloc[0]>1000 and sl.source.str.startswith('https://www2.census.gov/').all()
land=gpd.read_file(R/'data/processed/port-authority-land.geojson');assert set(land.state)=={'NJ','NY'} and land.is_valid.all()
mp=gpd.read_file(R/'data/processed/port-authority-crossings-mapped.geojson');assert set(mp.id)=={c['id'] for c in PA['crossings']} and (mp[['snap_m_nj','snap_m_ny']]<600).all().all()
L=land.to_crs(26918).set_index('state');mp=mp.to_crs(26918)
for _,r in mp.iterrows():a_,b_=[Point(c) for c in r.geometry.coords];assert L.geometry.loc['NJ'].distance(a_)<1 and L.geometry.loc['NY'].distance(b_)<1,r.id
checks['port_authority_census_land_state_line_and_bank_to_bank_crossings']=True
assert Image.open(R/'outputs/port-authority-web.png').size==(1600,2000)
layout=json.loads((R/'docs/port-authority-layout.json').read_text());assert len(layout)==2 and all(not v['overlapping_text'] and v['all_text_inside_canvas'] for v in layout)
checks.update({'port_authority_every_mapped_feature_and_fact_sourced':True,'port_authority_airport_coordinate_order_and_all_anchors_in_extent':True,'port_authority_label_boxes_without_overlap_or_clipping':True,'port_authority_uncertain_ridership_omitted_and_no_false_legal_circle':True})
protected=json.loads((R/'docs/protected-exports.json').read_text());assert all(hashlib.sha256((R/'outputs'/name).read_bytes()).hexdigest()==h for name,h in protected.items());checks['all_six_protected_exports_match_6191e71']=True
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
poster=R/'outputs/seeing-the-hudson.png';before=hashlib.sha256(poster.read_bytes()).hexdigest();subprocess.run([sys.executable,str(R/'scripts/render.py')],check=True,stdout=subprocess.DEVNULL);assert hashlib.sha256(poster.read_bytes()).hexdigest()==before;assert all(hashlib.sha256((R/'outputs'/name).read_bytes()).hexdigest()==h for name,h in protected.items());checks['repeat_render_byte_identical']=True
report={'passed':all(checks.values()),'checks':checks,'frozen_inputs':len(manifest['frozen_inputs']),'poster_sha256':before,'viewpoint_count':6,'pair_count':3,'poster_pixels':[4500,5400],'thumbnail_pixels':[600,600],'browser_visual_QA':'Pending publication approval; static landscape and portrait editions visually inspected in three composition passes. Page is staged locally, not pushed.','limitations':'No modeled visibility, current-condition claim or certified access/coordinate accuracy.'};(R/'docs/validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
