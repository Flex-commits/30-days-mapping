"""Download exact frozen bytes; never silently replace a source snapshot."""
from pathlib import Path
import json,hashlib,urllib.request
R=Path(__file__).resolve().parents[1];raw=R/'data/raw';raw.mkdir(parents=True,exist_ok=True)
for s in json.loads((R/'source-manifest.json').read_text())['sources']:
 p=raw/s['filename']
 if p.exists():b=p.read_bytes()
 else:
  with urllib.request.urlopen(s['download_url'],timeout=90) as f:b=f.read()
 assert hashlib.sha256(b).hexdigest()==s['sha256'],'Source changed: stop and review version, do not update silently.'
 if not p.exists():p.write_bytes(b)
 print(s['filename'],'verified')
