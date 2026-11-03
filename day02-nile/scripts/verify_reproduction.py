from pathlib import Path
import subprocess,hashlib,json,sys
R=Path(__file__).resolve().parents[1];exe=sys.executable;im=R/'outputs/nile-connected.png';before=hashlib.sha256(im.read_bytes()).hexdigest()
for s in ['build.py','check_geometry.py','render.py','thumbnail.py','package_site.py']:
 subprocess.run([exe,str(R/'scripts'/s)],check=True,stdout=subprocess.DEVNULL)
after=hashlib.sha256(im.read_bytes()).hexdigest();assert before==after,'Reproduced pixels differ'
from PIL import Image
assert Image.open(im).size==(3600,4800);assert Image.open(R/'outputs/02-thomas-hagos.png').size==(600,600)
report={'full_pipeline_rebuilt_from_cached_raw':True,'png_sha256':after,'byte_identical_render':True,'poster_pixels':[3600,4800],'thumbnail_pixels':[600,600]};(R/'data/processed/reproduction.json').write_text(json.dumps(report,indent=2));print(report)
