"""Census land, the NY–NJ state line and five bank-to-bank Hudson crossings for Two States. One Agency."""
from pathlib import Path
import json,hashlib
from pyproj import Transformer,Geod
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point,LineString,box
from shapely.ops import nearest_points
R=Path(__file__).resolve().parents[1];D=R/'data/processed';D.mkdir(parents=True,exist_ok=True);RAW=R/'data/raw';RAW.mkdir(parents=True,exist_ok=True)
T=Transformer.from_crs(4326,26918,always_xy=True);G=Geod(ellps='WGS84')
PA=json.loads((R/'data/port-authority.json').read_text());SRC=json.loads((R/'data/sources.json').read_text())
# Crossings: schematic shore-to-shore links between approximate portal/terminal areas.
rows=[]
for c in PA['crossings']:
 a=(c['nj']['lon'],c['nj']['lat']);b=(c['ny']['lon'],c['ny']['lat']);assert all(-74.05<v[0]<-73.92 and 40.69<v[1]<40.88 for v in [a,b]);assert c['opened']<=c['pa_since']
 rows.append({'id':c['id'],'name':c['name'],'mode':c['mode'],'opened':c['opened'],'port_authority_since':c['pa_since'],'nj_end':c['nj']['place'],'ny_end':c['ny']['place'],'shore_to_shore_miles':G.inv(*a,*b)[2]/1609.344,'line_meaning':'Schematic straight link between approximate shore-side portals/terminals; not a surveyed alignment.','source':c['source'],'geometry':LineString([a,b])})
pa=gpd.GeoDataFrame(rows,crs=4326);assert pa.id.is_unique and pa.geometry.is_valid.all();pa.to_file(D/'port-authority-crossings.geojson',driver='GeoJSON');pa.drop(columns='geometry').to_csv(D/'port-authority-crossings.csv',index=False);print(f'{len(pa)} Port Authority crossings written.')
# Geography: Census counties minus TIGER water, dissolved by state, plus the TIGER NY–NJ boundary.
# No legal Port District circle is inferred (see docs/research-notes.md).
frame=box(*PA['design']['bounds_wgs84']).buffer(.04,join_style=2)  # padded so the projected map edge is always filled
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
# Sourced facility anchors (airports, docks, WTC): kept as data for the page text; not drawn on the map.
features=[]
for v in PA['airports']+PA['ports']+[v for v in PA['landmarks'] if v['id'] in PA['design']['selected_landmarks']]:
 features.append({'id':v['id'],'name':v['name'],'kind':v.get('kind','landmark'),'source':v['source'],'coordinate_source':v['coordinate_source'],'status':v['status'],'geometry':Point(v['lon'],v['lat'])})
gpd.GeoDataFrame(features,crs=4326).to_file(D/'port-authority-facilities.geojson',driver='GeoJSON');print('Sourced facility anchors written.')
