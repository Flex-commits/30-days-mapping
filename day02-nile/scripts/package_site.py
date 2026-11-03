"""Copy the documented page and rendered outputs to the repository's Pages directory."""
from pathlib import Path
import shutil
R=Path(__file__).resolve().parents[1];target=R.parent/'docs/nile'
if target.exists():shutil.rmtree(target)
shutil.copytree(R/'docs',target,dirs_exist_ok=True)
for name in ['nile-connected.png','02-thomas-hagos.png']:shutil.copy2(R/'outputs'/name,target/name)
for src,name in [(R/'data/sources.json','sources.json'),(R/'data/processed/validation.json','validation.json')]:shutil.copy2(src,target/name)
print(target)
