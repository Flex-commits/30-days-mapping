"""Verify frozen source bytes; restore missing inputs only when their checksums agree."""
from pathlib import Path
from urllib.request import Request,urlopen
import hashlib,json
R=Path(__file__).resolve().parents[1];M=json.loads((R/'data/source-manifest.json').read_text())
for f in M['frozen_inputs']:
 p=R/f['file']
 if p.exists():b=p.read_bytes()
 else:
  with urlopen(Request(f['url'],headers={'User-Agent':'ThomasHagos-MUSA/1.0'}),timeout=90) as r:b=r.read()
  if f.get('normalization')=='json-dumps':b=json.dumps(json.loads(b)).encode()
 if hashlib.sha256(b).hexdigest()!=f['sha256']:raise RuntimeError(f"Source changed: {f['file']}. Restore the frozen tracked input from Git; do not substitute changed data silently.")
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
print('Verified all frozen inputs.')
