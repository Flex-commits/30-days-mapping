"""Build the static archive and the animated main page."""
from pathlib import Path
import subprocess,sys,os,shutil
R=Path(__file__).resolve().parents[1]
subprocess.run([sys.executable,str(R/'scripts/build_static_page.py')],check=True)
shutil.copy2(R/'site/index.html',R/'site/static.html')
env=dict(os.environ,AKSUM_OUTPUT_DIR=str(R/'outputs/living-city'))
subprocess.run([sys.executable,str(R/'scripts/build_living_city.py')],env=env,check=True)
shutil.copy2(R/'outputs/living-city/aksum-living-city.html',R/'site/index.html')
shutil.copytree(R/'data/photos',R/'site/assets/photos',dirs_exist_ok=True)
print('Built animated main page and static archive.')
