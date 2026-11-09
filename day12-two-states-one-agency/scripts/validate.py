"""Check sources, geometry, layout, page links and a deterministic re-render for Two States. One Agency."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import json,hashlib,csv,subprocess,sys
from PIL import Image
import geopandas as gpd
from shapely.geometry import Point,box
from pyproj import Geod,Transformer
R=Path(__file__).resolve().parents[1];PA=json.loads((R/'data/port-authority.json').read_text());SRC=json.loads((R/'data/sources.json').read_text());checks={}
G=Geod(ellps='WGS84');T=Transformer.from_crs(4326,26918,always_xy=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Every committed or downloaded input matches its recorded hash (Census zips are fetched by prepare.py when absent).
present=[v for v in SRC['inputs'] if (R/v['file']).exists()];assert all(sha(R/v['file'])==v['sha256'] for v in present)
assert all((R/v['file']).exists() for v in SRC['inputs'] if v['file'].startswith('fonts/') or v['file'].endswith('.csv'));checks['input_hashes_match_sources']=True
# Facts and facilities are sourced; uncertain ridership stays off; no false Port District circle.
assert PA['design']['district_circle'] is False and PA['path_ridership']['display'] is False and PA['path_ridership']['status']=='uncertain'
for group in ['crossings','airports','ports','landmarks','beyond_frame']:
 for v in PA[group]:assert v['source'].startswith('https://') and v['status']=='confirmed',v.get('id',v.get('name'))
for v in PA['facts']+PA['portfolio']['items']:assert v['source'].startswith('https://') and v['status']=='confirmed'
assert len(PA['crossings'])==5 and len(PA['airports'])==3 and len(PA['ports'])==2;checks['every_fact_and_feature_sourced']=True
b=box(*PA['design']['bounds_wgs84']);f=box(*PA['design']['focus_wgs84']);pa=gpd.read_file(R/'data/processed/port-authority-crossings.geojson');assert len(pa)==5 and pa.id.is_unique
for c in PA['crossings']:
 assert c['opened']<=c['pa_since'] and c['nj']['lon']<c['ny']['lon'],c['id']
 for side in ['nj','ny']:assert f.covers(Point(c[side]['lon'],c[side]['lat'])),c['id']
 row=pa[pa.id==c['id']].iloc[0];assert list(row.geometry.coords)==[(c['nj']['lon'],c['nj']['lat']),(c['ny']['lon'],c['ny']['lat'])]
air={v['ident']:v for v in csv.DictReader(open(R/'data/raw/airport-codes.csv'))}
for v in PA['airports']:lat,lon=map(float,air[v['id']]['coordinates'].split(','));assert (v['lat'],v['lon'])==(lat,lon)
fac=gpd.read_file(R/'data/processed/port-authority-facilities.geojson');assert len(fac)==6 and fac.within(b).all();checks['crossing_anchors_in_frame_and_airport_coordinates_match']=True
sl=gpd.read_file(R/'data/processed/port-authority-state-line.geojson');assert len(sl)==1 and sl.to_crs(26918).length.iloc[0]>1000 and sl.source.str.startswith('https://www2.census.gov/').all()
land=gpd.read_file(R/'data/processed/port-authority-land.geojson');assert set(land.state)=={'NJ','NY'} and land.is_valid.all()
mp=gpd.read_file(R/'data/processed/port-authority-crossings-mapped.geojson');assert set(mp.id)=={c['id'] for c in PA['crossings']} and (mp[['snap_m_nj','snap_m_ny']]<600).all().all()
L=land.to_crs(26918).set_index('state');mp=mp.to_crs(26918)
for _,r in mp.iterrows():a_,b_=[Point(c) for c in r.geometry.coords];assert L.geometry.loc['NJ'].distance(a_)<1 and L.geometry.loc['NY'].distance(b_)<1,r.id
checks['census_land_state_line_and_bank_to_bank_crossings']=True
xx,yy=T.transform(-74.0,40.70);inv=Transformer.from_crs(26918,4326,always_xy=True);p0=inv.transform(xx,yy);p1=inv.transform(xx+1609.344,yy);assert abs(G.inv(*p0,*p1)[2]/1609.344-1)<.001;checks['one_mile_scale_ground_check']=True
assert Image.open(R/'outputs/two-states-one-agency.png').size==(3500,3000) and Image.open(R/'outputs/two-states-one-agency-phone.png').size==(1600,2000) and Image.open(R/'outputs/12-thomas-hagos.png').size==(600,600);checks['export_sizes']=True
layout=json.loads((R/'docs/layout.json').read_text());assert len(layout)==2 and all(not v['overlapping_text'] and v['all_text_inside_canvas'] for v in layout);checks['label_boxes_without_overlap_or_clipping']=True
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.images=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a' and 'href' in a:self.links.append(a['href'])
  if tag=='img':assert a.get('alt');self.images.append(a['src'])
  if tag=='source':self.images.append(a['srcset'])
p=Parser();p.feed((R/'site/index.html').read_text())
for s in p.links+p.images:
 if not urlparse(s).scheme and not s.startswith('#') and not s.startswith('../'):assert (R/'site'/unquote(s)).exists(),s
checks['static_page_local_links_and_image_alt_text']=True
outs=['two-states-one-agency.png','two-states-one-agency-phone.png','12-thomas-hagos.png'];before={n:sha(R/'outputs'/n) for n in outs}
subprocess.run([sys.executable,str(R/'scripts/render.py')],check=True,stdout=subprocess.DEVNULL);assert {n:sha(R/'outputs'/n) for n in outs}==before;checks['repeat_render_byte_identical']=True
report={'passed':all(checks.values()),'checks':checks,'outputs':before,'limitations':'Crossings are schematic bank-to-bank links between approximate anchors; no surveyed alignment or legal jurisdiction boundary is drawn.'};(R/'docs/validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
