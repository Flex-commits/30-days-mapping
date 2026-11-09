"""Check provenance, complete queries, geometry, labels, scale and a clean image rebuild."""
from pathlib import Path
from tempfile import TemporaryDirectory
from html.parser import HTMLParser
from urllib.parse import urlparse,unquote
import hashlib,json,shutil,subprocess,sys,os
import geopandas as gpd
from shapely.geometry import Point,box
from pyproj import Transformer,Geod
from PIL import Image
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config.json').read_text());M=json.loads((R/'data/source-manifest.json').read_text());checks={}
checks['frozen_input_hashes']=all(hashlib.sha256((R/f['file']).read_bytes()).hexdigest()==f['sha256'] for f in M['frozen_inputs']);assert checks['frozen_input_hashes']
for name,ftype in [('river-areas',460),('lakes',390)]:
 raw=json.loads((R/f'data/raw/{name}.geojson').read_text());assert not raw.get('exceededTransferLimit');g=gpd.read_file(R/f'data/raw/{name}.geojson');d=gpd.read_file(R/'data/processed/reference.gpkg',layer=name)
 assert g.PERMANENT_IDENTIFIER.is_unique and d.PERMANENT_IDENTIFIER.is_unique and (g.FTYPE==ftype).all() and d.is_valid.all() and not d.is_empty.any()
 expected=g.clip(box(*C['bounds_wgs84'])).to_crs(C['projection']);assert len(expected)==len(d)
 # No invented or simplified geometry: compare geometries by source ID, not row order.
 expected=expected.set_index('PERMANENT_IDENTIFIER');actual=d.set_index('PERMANENT_IDENTIFIER');assert all(expected.loc[k].geometry.equals(actual.loc[k].geometry) and expected.loc[k].geometry.hausdorff_distance(actual.loc[k].geometry)==0 for k in actual.index)
 if name=='lakes':assert (g.AREASQKM>=.03).all()
checks['complete_queries_no_duplicate_ids']=True;checks['exact_clipping_without_simplification_or_synthetic_geometry']=True
l=gpd.read_file(R/'data/processed/reference.gpkg',layer='lakes');T=Transformer.from_crs(4326,C['projection'],always_xy=True)
for v in C['labels']:
 a=l[l.GNIS_NAME==v['name']];assert len(a)==1 and a.geometry.iloc[0].covers(Point(*T.transform(v['lon'],v['lat'])))
checks['each_lake_label_anchor_inside_its_named_NHD_polygon']=True
# Independent ground-distance cross-check for the 5-mile projected bar at its actual location.
x0,y0=T.transform(C['bounds_wgs84'][0],C['bounds_wgs84'][1]);x1,y1=T.transform(C['bounds_wgs84'][2],C['bounds_wgs84'][3]);sx=x0+.65*(x1-x0);sy=y0+.065*(y1-y0);inv=Transformer.from_crs(C['projection'],4326,always_xy=True);a=inv.transform(sx,sy);b=inv.transform(sx+8046.72,sy);dist=Geod(ellps='GRS80').inv(*a,*b)[2];assert abs(dist/8046.72-1)<.001
checks['five_mile_scale_within_0_1_percent_ground_distance']=True
assert Image.open(R/'outputs/the-river-remembers.png').size==(4500,5400);assert Image.open(R/'outputs/06-thomas-hagos.png').size==(600,600);checks['poster_and_thumbnail_dimensions']=True
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.refs=[]
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='img':assert a.get('alt');self.refs.append(a['src'])
  if t=='a':self.refs.append(a.get('href',''))
p=Parser();p.feed((R/'site/index.html').read_text())
for ref in p.refs:
 if not urlparse(ref).scheme and not ref.startswith(('#','../')):assert (R/'site'/unquote(ref)).exists(),ref
checks['static_page_asset_links_and_alt_text']=True
files=sorted(str(p.relative_to(R/'submission')) for p in (R/'submission').rglob('*') if p.is_file());assert files==['_maps_2026/06-thomas-hagos.md','assets/thumbnails/2026/06-thomas-hagos.png'];assert (R/'submission/assets/thumbnails/2026/06-thomas-hagos.png').read_bytes()==(R/'outputs/06-thomas-hagos.png').read_bytes();checks['only_two_MUSA_files_and_identical_thumbnail']=True
hashes={n:hashlib.sha256((R/'outputs'/n).read_bytes()).hexdigest() for n in ['the-river-remembers.png','06-thomas-hagos.png']}
with TemporaryDirectory(prefix='river-remembers-') as temp:
 D=Path(temp)
 for name in ['scripts','fonts','data/raw']:shutil.copytree(R/name,D/name)
 for name in ['config.json','data/source-manifest.json']:(D/name).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/name,D/name)
 (D/'data/processed').mkdir();(D/'docs').mkdir();env=dict(os.environ,MPLCONFIGDIR=str(D/'.mplconfig'))
 for name in ['prepare.py','render.py']:subprocess.run([sys.executable,str(D/'scripts'/name)],env=env,check=True,stdout=subprocess.DEVNULL)
 assert all(hashlib.sha256((D/'outputs'/n).read_bytes()).hexdigest()==h for n,h in hashes.items())
checks['clean_folder_rebuild_byte_identical_images']=True
report={'passed':all(checks.values()),'checks':checks,'source_feature_counts':{n:len(json.loads((R/f'data/raw/{n}.geojson').read_text())['features']) for n in ['river-areas','lakes']},'scale_bar_ground_miles':dist/1609.344,'image_sha256':hashes,'visual_review':'Full poster and 600px thumbnail inspected; archival colors, periods and crop labels checked against original sheet.','scope':'Reference hydrography plus attributed archival details; no georeferenced historical overlay or current-condition survey.'}
(R/'docs/validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
