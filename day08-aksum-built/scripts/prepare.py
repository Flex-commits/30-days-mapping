"""Verify the frozen geography, or regenerate terrain from its original georeferenced tile.

python scripts/prepare.py [--terrain /path/to/dem.tif]
The source crop is tracked, so rendering does not require a 40 MB download.
"""
from pathlib import Path
import argparse,json,hashlib
import numpy as np
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config.json').read_text());p=argparse.ArgumentParser();p.add_argument('--terrain');args=p.parse_args()
if args.terrain:
 import rasterio
 from rasterio.windows import Window
 v=C['terrain_window']
 with rasterio.open(args.terrain) as src:
  assert src.crs.to_epsg()==4326 and src.tags()['AREA_OR_POINT']=='Point'
  z=src.read(1,window=Window(v['column'],v['row'],v['width'],v['height'])).astype('float32');lon,lat=src.xy(v['row'],v['column']);step=src.res[0]
  assert step==abs(src.transform.e)
  np.savez_compressed(R/'data/terrain.npz',z=z,lat_top=lat,lon_left=lon,step=step)
  metadata={'source_url':C['terrain_url'],'source_sha256':hashlib.sha256(Path(args.terrain).read_bytes()).hexdigest(),'source_crs':str(src.crs),'source_shape':list(src.shape),'source_transform':list(src.transform),'source_tags':src.tags(),'window':v,'first_pixel_center':[lon,lat],'step':step,'crop_shape':list(z.shape),'crop_value_sha256':hashlib.sha256(z.tobytes()).hexdigest(),'surface_note':'Modern digital surface model, not reconstructed ancient bare earth.'}
  (R/'data/terrain-provenance.json').write_text(json.dumps(metadata,indent=2))
t=np.load(R/'data/terrain.npz');z=t['z'];assert z.shape==(80,109) and np.isfinite(z).all() and z.min()>1500 and z.max()<3000
s=json.loads((R/'data/sites.json').read_text());assert len({v['osm'] for v in s['sites']+s['other_stelae']})==len(s['sites'])+len(s['other_stelae'])
print('Verified saved terrain grid and unique landmark identifiers.')
# Independent provenance for each saved point, using frozen official OSM API XML.
import xml.etree.ElementTree as ET
nodes={n.attrib['id']:n for n in ET.parse(R/'data/osm-nodes.xml').getroot().findall('node')};provenance=[]
for v in s['sites']+s['other_stelae']:
 kind,ident=v['osm'].split('/')
 if kind=='node':
  n=nodes[ident];lat=float(n.attrib['lat']);lon=float(n.attrib['lon']);version=n.attrib['version'];basis='OSM node'
 else:
  root=ET.parse(R/f'data/osm-way-{ident}.xml').getroot();way=root.find('way');nn={n.attrib['id']:n for n in root.findall('node')};refs=[nn[n.attrib['ref']] for n in way.findall('nd')];lat=float(np.mean([float(n.attrib['lat']) for n in refs]));lon=float(np.mean([float(n.attrib['lon']) for n in refs]));version=way.attrib['version'];basis='Mean vertices of OSM way (not surveyed centroid)'
 assert abs(lat-v['lat'])<.000001 and abs(lon-v['lon'])<.000001,v['osm']
 provenance.append({'osm':v['osm'],'source':'https://www.openstreetmap.org/'+v['osm'],'version':version,'source_lat':lat,'source_lon':lon,'saved_lat':v['lat'],'saved_lon':v['lon'],'coordinate_basis':basis})
(R/'data/site-provenance.json').write_text(json.dumps(provenance,indent=2));print('Verified all site positions against frozen OSM node/way records.')
