"""Verify saved source bytes or attempt restoration. A mismatch requires the frozen Git snapshot."""
from pathlib import Path
from urllib.request import Request,urlopen
import json,hashlib
R=Path(__file__).resolve().parents[1];manifest=json.loads((R/'data/source-manifest.json').read_text())
for f in manifest['frozen_inputs']:
 p=R/f['file']
 if p.exists():raw=p.read_bytes()
 else:
  with urlopen(Request(f['url'],headers={'User-Agent':'ThomasHagos-MUSA-map/1.0'}),timeout=90) as x:raw=x.read()
  if f['file'].endswith('-metadata.json') and '/w/api.php' in f['url']:
   d=json.loads(raw);pages=d.get('query',{}).get('pages',{});raw=json.dumps(next(iter(pages.values())),indent=2).encode()
 digest=hashlib.sha256(raw).hexdigest()
 if digest!=f['sha256']:raise RuntimeError(f"Source changed: {f['file']}. Restore the tracked frozen input from Git; do not silently substitute refreshed data.")
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
print('All frozen inputs verified.')
