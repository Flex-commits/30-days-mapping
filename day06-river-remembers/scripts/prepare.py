"""Clip unchanged NHD source geometry; save projected display layers and archival crops."""
from pathlib import Path
import os,json
R=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(R/'.mplconfig'))
import geopandas as gpd
from shapely.geometry import box
from shapely import make_valid
import fitz
C=json.loads((R/'config.json').read_text());bounds=box(*C['bounds_wgs84']);report={}
for name in ['river-areas','lakes']:
 g=gpd.read_file(R/f'data/raw/{name}.geojson');assert g.crs.to_epsg()==4326
 assert g.PERMANENT_IDENTIFIER.is_unique
 invalid=int((~g.is_valid).sum());g.geometry=g.geometry.map(make_valid);g=gpd.clip(g,bounds,keep_geom_type=True)
 g=g[['PERMANENT_IDENTIFIER','GNIS_NAME','FTYPE','FCODE','FDATE','geometry']]
 g.to_file(R/f'data/processed/{name}.geojson',driver='GeoJSON')
 g.to_crs(C['projection']).to_file(R/'data/processed/reference.gpkg',layer=name,driver='GPKG')
 report[name]={'source_features':len(gpd.read_file(R/f'data/raw/{name}.geojson')),'display_features':len(g),'source_invalid_repaired_for_display':invalid}
states=gpd.read_file(R/'data/raw/ne-50m-states.geojson');states=states[states.adm0_a3=='USA'];states=states[['name','postal','geometry']];states.to_file(R/'data/processed/us-states.geojson',driver='GeoJSON')
p=fitz.open(R/'data/raw/mrc-1938-sheet05.pdf')[0]
for name,rect in C['archive_crops_pdf_points'].items():
 p.get_pixmap(matrix=fitz.Matrix(2.5,2.5),clip=fitz.Rect(rect),alpha=False).save(R/f'data/processed/archive-{name}.png')
(R/'docs/processing.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
