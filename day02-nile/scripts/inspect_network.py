import geopandas as g
from pathlib import Path
from shapely.geometry import Point
p=Path(__file__).resolve().parents[1]/'data/raw';r=g.read_file(p/'rivers.zip');r=r[r.MAIN_RIV==10047863].copy();rp=r.to_crs(3857)
for name,x,y in [('White',32.48,15.5),('Blue',32.6,15.6),('Atbara',34.01,17.65),('Tana',37.3,11.6),('Victoria',33.2,.4),('delta',31,30.9)]:
 d=rp[r.ORD_STRA>=5];pt=g.GeoSeries([Point(x,y)],crs=4326).to_crs(3857).iloc[0];q=d.distance(pt).nsmallest(3);print(name,r.loc[q.index,['HYRIV_ID','NEXT_DOWN','ORD_STRA','ORD_CLAS','UPLAND_SKM']],q.values)
print('outlets',r[r.NEXT_DOWN==0][['HYRIV_ID','UPLAND_SKM','ORD_STRA']]);print('n',len(r),'orders',r.ORD_STRA.value_counts().to_dict())
