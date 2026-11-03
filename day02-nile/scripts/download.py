"""Download authoritative inputs; raw files stay out of Git."""
from pathlib import Path
from urllib.request import urlretrieve
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1];RAW=ROOT/'data/raw';RAW.mkdir(parents=True,exist_ok=True)
URLS={
'rivers.zip':'https://ihp-wins.unesco.org/dataset/26832148-4635-485a-ba78-73c05c8c423c/resource/0566b163-a1ad-426d-8ac0-431a1c41a532/download/hydrorivers-the-nile-basin.zip',
'basins02.zip':'https://ihp-wins.unesco.org/dataset/17efa45f-07d6-433d-9af8-312608a73c2e/resource/30413ce8-4b43-45de-b7ff-48b72880302e/download/hybas_lake_af_lev02_v1c.zip',
'countries.zip':'https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_0_countries.zip',
'lakes.zip':'https://naturalearth.s3.amazonaws.com/10m_physical/ne_10m_lakes.zip',
}
def get(item):
 name,url=item;p=RAW/name
 if not p.exists():
  tmp=p.with_suffix('.part');urlretrieve(url,tmp);tmp.rename(p)
 return {'file':name,'url':url,'downloaded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
if __name__=='__main__':
 records=list(ThreadPoolExecutor(max_workers=4).map(get,URLS.items()))
 original=ROOT/'data/downloads.json'
 if original.exists():
  expected={r['file']:r['sha256'] for r in json.loads(original.read_text())}
  for r in records:
   if r['sha256']!=expected[r['file']]:raise RuntimeError(f"Source snapshot changed: {r['file']}. Review before updating the original manifest.")
  (ROOT/'data/downloads-current.json').write_text(json.dumps(records,indent=2))
 else:original.write_text(json.dumps(records,indent=2))
 print('\n'.join(f"{r['file']}: {r['bytes']:,} bytes" for r in records))
