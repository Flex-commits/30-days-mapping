"""Create auditable site-pair geometry; distances connect anchors, not viewing rays."""
from pathlib import Path
import json,csv,hashlib
from pyproj import Transformer,Geod
import geopandas as gpd
from shapely.geometry import Point,LineString
R=Path(__file__).resolve().parents[1];C=json.loads((R/'config.json').read_text());D=R/'data/processed';D.mkdir(parents=True,exist_ok=True);credits={x['id']:x for x in json.loads((R/'data/photo-credits.json').read_text())};T=Transformer.from_crs(4326,26918,always_xy=True);G=Geod(ellps='WGS84');sites=[];pairs=[]
for p in C['pairs']:
 coords=[]
 for side in ['nj','ny']:
  s=p[side];c=credits[s['photo']];assert c['license'] in ['CC BY-SA 4.0','CC BY-SA 3.0'];assert c['creator'] and c['license_url'] and c['page_url'];assert -74.1<s['lon']<-73.9 and 40.68<s['lat']<40.89
  coords.append((s['lon'],s['lat']));sites.append({'id':p['id']+'-'+side,'pair':p['id'],'state':side.upper(),'name':s['name'],'longitude':s['lon'],'latitude':s['lat'],'coordinate_basis':s['coordinate_basis'],'official_source':s['source'],'photo_source':c['page_url'],'photo_author':c['creator'],'photo_date':c['capture_date'],'photo_license':c['license'],'geometry':Point(s['lon'],s['lat'])})
 az,_,dist=G.inv(*coords[0],*coords[1]);pairs.append({'id':p['id'],'title':p['title'],'distance_miles':dist/1609.344,'distance_definition':'WGS84 geodesic distance between approximate site anchors. Not river width, a route or verified sightline.','geometry':LineString(coords)})
points=gpd.GeoDataFrame(sites,crs=4326);lines=gpd.GeoDataFrame(pairs,crs=4326);points.to_file(D/'viewpoints.geojson',driver='GeoJSON');lines.to_file(D/'site-pairs.geojson',driver='GeoJSON');points.drop(columns='geometry').to_csv(D/'viewpoints.csv',index=False);lines.drop(columns='geometry').to_csv(D/'site-pairs.csv',index=False)
assert points.id.is_unique and len(points)==6 and len(lines)==3;assert points.geometry.is_valid.all() and lines.geometry.is_valid.all()
summary={'site_count':len(points),'pair_count':len(lines),'site_selection':'Purposive visual contrasts across three Lower Hudson sections; not a representative sample or comprehensive access inventory.','source_snapshot_date':C['source_snapshot_date'],'imagery_years':C['imagery_years'],'distance_method':'WGS84 geodesic / 1609.344 meters per mile','pair_lines':C['pair_line_meaning'],'photo_policy':'Historical dated photographs; different seasons, weather, fields of view and camera elevations. Not controlled comparisons of current views.','limits':['No terrain/building/vegetation visibility model.','Pair connections do not certify that observers can see each other or the opposite mapped point.','Coordinates from photo metadata are approximate, not surveyed; Fort Lee uses an official park entrance anchor, not a camera position.','Photographs and aerial imagery are not contemporary with one another.','Public-site documentation does not certify current access, closures or universal accessibility.']}
(D/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
