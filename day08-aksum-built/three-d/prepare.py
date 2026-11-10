from pathlib import Path
import json,xml.etree.ElementTree as ET,hashlib
import numpy as np
from pyproj import Transformer
R=Path(__file__).resolve().parents[1];O=R/'three-d';T=np.load(R/'data/terrain.npz');Z=T['z'];top=float(T['lat_top']);left=float(T['lon_left']);step=float(T['step']);tr=Transformer.from_crs(4326,32637,always_xy=True);ox,oy=tr.transform(38.719,14.13)
def xy(la,lo):
 x,y=tr.transform(lo,la);return [round(x-ox,2),round(oy-y,2)]
terrain=[]
for i,row in enumerate(Z):
 for j,z in enumerate(row):
  x,y=xy(top-i*step,left+j*step);terrain.append([x,round(float(z)-2150,2),y])
x=ET.parse(O/'aksum-current-osm.xml').getroot();nodes={n.attrib['id']:(float(n.attrib['lat']),float(n.attrib['lon'])) for n in x.findall('node')};roads=[]
for w in x.findall('way'):
 tags={t.attrib['k']:t.attrib['v'] for t in w.findall('tag')}
 if 'highway' not in tags or tags['highway'] in ['construction','proposed']:continue
 pts=[xy(*nodes[n.attrib['ref']]) for n in w.findall('nd') if n.attrib['ref'] in nodes]
 if len(pts)>1:roads.append({'osm_way':w.attrib['id'],'kind':tags['highway'],'name':tags.get('name',''),'points':pts})
sites=[]
for s in json.loads((R/'data/sites.json').read_text())['sites']:
 x,y=xy(s['lat'],s['lon']);sites.append(dict(s,x=x,z=y))
data={'terrain':terrain,'rows':Z.shape[0],'cols':Z.shape[1],'roads':roads,'sites':sites,'projection':'EPSG:32637; metres; altitude offset 2150m; no vertical exaggeration','terrain_source':'Copernicus modern DSM','modern_roads_source':'OpenStreetMap API map extract, downloaded 2026-11-10','modern_roads_sha256':hashlib.sha256(Path(O/'aksum-current-osm.xml').read_bytes()).hexdigest()}
(O/'scene-data.json').write_text(json.dumps(data,separators=(',',':')));print(len(terrain),'terrain vertices;',len(roads),'current road ways;',len(sites),'landmarks')
