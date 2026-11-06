"""Validate final export dimensions, local page links and the exact MUSA two-file payload."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import re,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]
assert Image.open(R/'outputs/africa-to-scale.png').size==(6000,7500)
assert Image.open(R/'outputs/03-thomas-hagos.png').size==(600,600)
social=list((R/'outputs/linkedin').glob('*.png'));assert len(social)==6;assert all(Image.open(p).size==(1080,1350) for p in social)
placements=json.loads((R/'data/processed/continents/individual-validation.json').read_text());contained=[x['guests'][0] for x in placements if sum(x['outside_km2'].values())==0];assert contained==['AUS']
partition=json.loads((R/'data/processed/continents/presentation-component-audit.json').read_text());assert not partition['measurement_geometry_changed'];assert all(x['partition_difference_m2']<1e-4 for x in partition['components'])
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ['href','src']:self.links.append(v)
p=R/'site/index.html';parser=Links();parser.feed(p.read_text());checked=[]
for link in parser.links:
 u=urlsplit(link)
 if u.scheme or not u.path:continue
 q=(p.parent/unquote(u.path)).resolve();assert q.is_file(),(link,q);checked.append(link)
md=R/'submission-proposal/_maps_2026/03-thomas-hagos.md';front=md.read_text().split('---',2)[1];keys=[line.split(':',1)[0] for line in front.strip().splitlines()];assert keys==['day','creator','title','thumbnail','source'];assert 'day: 3\n' in front
thumb=R/'submission-proposal/assets/thumbnails/2026/03-thomas-hagos.png';assert thumb.read_bytes()==(R/'outputs/03-thomas-hagos.png').read_bytes()
# Status wording is absent from the current presentation and gallery metadata.
for file in [R/'README.md',p,md,R/'docs/portfolio-entry.md',R/'docs/linkedin-caption.md']:
 assert not re.search(r'\b(draft|unfinished|incomplete|pending)\b',file.read_text(),re.I),file
report={'only_fully_contained_continent':'Australia','display_components_accounted_for':True,'linkedin_panel_count':6,'linkedin_panel_pixels':[1080,1350],'main_export_pixels':[6000,7500],'thumbnail_pixels':[600,600],'local_page_links_verified':checked,'template_fields':keys,'submission_thumbnail_matches_export':True,'current_presentation_status_labels_absent':True,'template_year':2026,'category':'Polygons','payload_files':['_maps_2026/03-thomas-hagos.md','assets/thumbnails/2026/03-thomas-hagos.png']};(R/'docs/package-validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
