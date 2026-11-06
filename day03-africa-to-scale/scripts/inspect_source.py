from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import shapefile,json
from shapely.geometry import shape
R=Path(__file__).resolve().parents[1];z=ZipFile(R/'data/raw/countries.zip');print('VERSION',z.read(next(n for n in z.namelist() if n.endswith('VERSION.txt'))))
stem=next(n[:-4] for n in z.namelist() if n.endswith('.shp'));reader=shapefile.Reader(shp=BytesIO(z.read(stem+'.shp')),shx=BytesIO(z.read(stem+'.shx')),dbf=BytesIO(z.read(stem+'.dbf')),encoding='utf8')
for r in reader.iterShapeRecords():
 p=r.record.as_dict()
 if p['CONTINENT']=='Africa' or p['ADM0_A3'] in ['USA','CHN','IND','FRA','ESP','PRT']:
  g=shape(r.shape.__geo_interface__);print(p['ADM0_A3'],p['ADMIN'],p['CONTINENT'],'parts',len(g.geoms) if hasattr(g,'geoms') else 1,'bounds',g.bounds,'valid',g.is_valid)
  if p['ADM0_A3']=='FRA':print('FRA parts',[(i,x.bounds) for i,x in enumerate(g.geoms)])
