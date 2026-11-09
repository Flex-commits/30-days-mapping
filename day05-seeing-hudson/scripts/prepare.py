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
# Port Authority crossings: schematic shore-to-shore links between approximate portal/terminal areas.
PA=json.loads((R/'data/port-authority.json').read_text());rows=[]
for c in PA['crossings']:
 a=(c['nj']['lon'],c['nj']['lat']);b=(c['ny']['lon'],c['ny']['lat']);assert all(-74.05<v[0]<-73.92 and 40.69<v[1]<40.88 for v in [a,b]);assert c['opened']<=c['pa_since']
 rows.append({'id':c['id'],'name':c['name'],'mode':c['mode'],'opened':c['opened'],'port_authority_since':c['pa_since'],'nj_end':c['nj']['place'],'ny_end':c['ny']['place'],'shore_to_shore_miles':G.inv(*a,*b)[2]/1609.344,'line_meaning':'Schematic straight link between approximate shore-side portals/terminals; not a surveyed alignment.','source':c['source'],'geometry':LineString([a,b])})
pa=gpd.GeoDataFrame(rows,crs=4326);assert pa.id.is_unique and pa.geometry.is_valid.all();pa.to_file(D/'port-authority-crossings.geojson',driver='GeoJSON');pa.drop(columns='geometry').to_csv(D/'port-authority-crossings.csv',index=False);print(f'{len(pa)} Port Authority crossings written.')
# Regional geography: Census shoreline-clipped counties dissolved by state, plus the TIGER NY–NJ boundary.
# No legal Port District circle is inferred (see docs/research-notes.md).
from shapely.geometry import box
from shapely.ops import nearest_points
import pandas as pd
SRC=json.loads((R/'data/port-authority-sources.json').read_text());RAW=R/'data/raw/port-authority';frame=box(*PA['design']['bounds_wgs84']).buffer(.04,join_style=2)  # padded so the projected map edge is always filled
def raw(name):
 rec=next(v for v in SRC['inputs'] if v['file'].endswith(name));f=RAW/name
 if not f.exists():__import__('urllib.request').request.urlretrieve(rec['url'],f)
 assert hashlib.sha256(f.read_bytes()).hexdigest()==rec['sha256'],name;return rec,f
crec,cf=raw('cb-2024-county-500k.zip');srec,sf=raw('tl-2024-state.zip')
cty=gpd.read_file('zip://'+str(cf.resolve()),bbox=tuple(frame.bounds));cty=cty[cty.STATEFP.isin(['34','36'])]
water=pd.concat([gpd.read_file('zip://'+str(raw(v['file'].split('/')[-1])[1].resolve()),bbox=tuple(frame.bounds)) for v in SRC['inputs'] if '/aw-' in v['file']]).to_crs(26918);water=water[water.area>=50000]
cty=cty.to_crs(26918);cty.geometry=cty.geometry.difference(water.union_all()).simplify(10);cty=cty.to_crs(4326)
land=cty.dissolve(by='STUSPS').reset_index()[['STUSPS','geometry']].rename(columns={'STUSPS':'state'});land=gpd.clip(land,frame,keep_geom_type=True);land['source']=crec['url']
land.to_file(D/'port-authority-land.geojson',driver='GeoJSON')
shore=land.copy();shore.geometry=land.geometry.boundary;shore=gpd.clip(shore,frame);shore=shore[~shore.is_empty];shore.to_file(D/'port-authority-shoreline.geojson',driver='GeoJSON')
st=gpd.read_file('zip://'+str(sf.resolve()),bbox=tuple(frame.bounds));ny=st[st.STUSPS=='NY'].geometry.iloc[0];nj=st[st.STUSPS=='NJ'].geometry.iloc[0]
line=gpd.GeoDataFrame({'name':['New York – New Jersey state line'],'source':[srec['url']]},geometry=[ny.boundary.intersection(nj.boundary)],crs=4326);line=gpd.clip(line,frame);line.to_file(D/'port-authority-state-line.geojson',driver='GeoJSON')
# Draw each crossing bank-to-bank: snap its NJ anchor to the NJ shore and its NY anchor to the NY shore.
U=land.to_crs(26918).set_index('state').geometry;mapped=[]
for c in PA['crossings']:
 ends=[]
 for side,state in [('nj','NJ'),('ny','NY')]:
  p_=Point(T.transform(c[side]['lon'],c[side]['lat']));q=nearest_points(U[state].boundary,p_)[0];ends.append((q,p_.distance(q)))
 mapped.append({'id':c['id'],'mode':c['mode'],'snap_m_nj':round(ends[0][1],1),'snap_m_ny':round(ends[1][1],1),'meaning':'Schematic bank-to-bank link; anchors snapped to the nearest Census 1:500k shoreline of each state.','geometry':LineString([ends[0][0],ends[1][0]])})
gpd.GeoDataFrame(mapped,crs=26918).to_crs(4326).to_file(D/'port-authority-crossings-mapped.geojson',driver='GeoJSON');print('Census land, shoreline, state line and bank-to-bank crossings written.',[(m['id'],m['snap_m_nj'],m['snap_m_ny']) for m in mapped])
features=[]
for v in PA['airports']+PA['ports']+[v for v in PA['landmarks'] if v['id'] in PA['design']['selected_landmarks']]:
 features.append({'id':v['id'],'name':v['name'],'kind':v.get('kind','landmark'),'source':v['source'],'coordinate_source':v['coordinate_source'],'status':v['status'],'geometry':Point(v['lon'],v['lat'])})
gpd.GeoDataFrame(features,crs=4326).to_file(D/'port-authority-facilities.geojson',driver='GeoJSON');print('Regional coast and sourced facility anchors written.')
