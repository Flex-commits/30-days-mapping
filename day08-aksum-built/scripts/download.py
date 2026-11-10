"""Verify/restore small frozen inputs; optionally retrieve the original terrain tile."""
from pathlib import Path
import json,hashlib,urllib.request,argparse
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--terrain',action='store_true');a=p.parse_args();M=json.loads((R/'data/source-manifest.json').read_text())
for f in M['frozen_inputs']:
 out=R/f['file']
 if not out.exists():
  with urllib.request.urlopen(f['snapshot_url'],timeout=60) as r:b=r.read()
 else:b=out.read_bytes()
 if hashlib.sha256(b).hexdigest()!=f['sha256']:raise RuntimeError('Frozen input changed: '+f['file']+'. Restore the tracked source snapshot from this commit.')
 if not out.exists():out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(b)
if a.terrain:
 C=json.loads((R/'config.json').read_text());P=json.loads((R/'data/terrain-provenance.json').read_text());out=R/'data/raw/dem.tif';out.parent.mkdir(parents=True,exist_ok=True)
 if not out.exists():
  with urllib.request.urlopen(C['terrain_url'],timeout=120) as r:out.write_bytes(r.read())
 assert hashlib.sha256(out.read_bytes()).hexdigest()==P['source_sha256'],'Terrain tile changed; do not silently replace the saved source.'
 print(out)
print('Verified all frozen inputs.')
