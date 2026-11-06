"""Rebuild the saved map in a fresh directory from frozen archives, without searching."""
from pathlib import Path
import tempfile,shutil,subprocess,sys,json,hashlib
R=Path(__file__).resolve().parents[1];T=Path(tempfile.mkdtemp(prefix='africa-continent-clean-',dir='/private/tmp'));(T/'data/raw').mkdir(parents=True);(T/'outputs').mkdir();(T/'docs').mkdir()
for name in ['config.json','source-manifest.json','placements.json','individual-placements.json','requirements.txt']:shutil.copy2(R/name,T/name)
shutil.copytree(R/'scripts',T/'scripts');shutil.copytree(R/'docs/fonts',T/'docs/fonts')
for s in json.loads((R/'source-manifest.json').read_text())['sources']:shutil.copy2(R/'data/raw'/s['filename'],T/'data/raw'/s['filename'])
steps=[['download_frozen.py'],['prepare_continents.py'],['replay_and_validate.py'],['country_coverage.py'],['audit_geography.py'],['proxy_audit.py'],['reference_checks.py'],['render_continents.py'],['build_page.py']];logs=[]
for step in steps:
 p=subprocess.run([sys.executable,str(T/'scripts'/step[0]),*step[1:]],cwd=T,text=True,capture_output=True);logs.append(' '.join(step)+'\n'+p.stdout+p.stderr);assert p.returncode==0,'Clean rebuild failed: '+logs[-1]
files=['outputs/continent-areas.csv','outputs/asia-country-coverage.csv','outputs/validation.csv','outputs/individual-validation.csv','outputs/continent-pairings.png','outputs/africa-to-scale.png','data/processed/continents/comparison-projected.geojson','data/processed/continents/layout.geojson','data/processed/continents/individual-layout.geojson','outputs/03-thomas-hagos.png','outputs/asia-country-comparison.png','site/index.html','outputs/published-area-checks.csv','data/processed/continents/validation.json','data/processed/continents/individual-validation.json'];checks=[]
for name in files:
 a=hashlib.sha256((R/name).read_bytes()).hexdigest();b=hashlib.sha256((T/name).read_bytes()).hexdigest();checks.append({'file':name,'sha256':a,'identical':a==b})
report={'clean_directory':str(T),'frozen_input_checksums_verified':True,'search_repeated':False,'checks':checks,'all_identical':all(x['identical'] for x in checks)};(R/'docs/clean-rebuild.json').write_text(json.dumps(report,indent=2));(R/'docs/clean-rebuild.log').write_text('\n\n'.join(logs));assert report['all_identical'],'Rebuild differs; inspect report before handoff';print(json.dumps(report,indent=2))
