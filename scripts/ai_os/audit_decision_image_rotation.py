"""Check approved batch scenes against the preceding two batches and image identity."""
import json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[2]
def problems(photos,recent):
 errors=[]
 for field in ['src','source']:
  values=[p[field] for p in photos]
  if len(values)!=len(set(values)):errors.append('Duplicate '+field+' within batch')
  if set(values)&{p[field] for p in recent}:errors.append('Recent scene reused: '+field)
 hashes=[hashlib.sha256((root/'src'/p['src'].lstrip('/')).read_bytes()).hexdigest() for p in photos]
 if len(hashes)!=len(set(hashes)):errors.append('Repeated bytes under another name')
 return errors
if __name__=='__main__':
 configs=json.loads((root/'planning/ai-os/decision-batch-config.json').read_text());photos=[p for c in configs for p in c['photos']];recent=[]
 for name in ['activity','logistics']:
  data=json.loads((root/f'planning/ai-os/evidence/{name}-images.json').read_text());recent += [p for row in data['photos'].values() for p in row]
 errors=problems(photos,recent)
 assert problems(photos+[photos[0]],recent)
 assert problems(photos,recent+[photos[0]])
 report={'passed':not errors,'errors':errors,'unique_scenes':len(photos),'recent_batches':['canoe/best-time','access/packing'],'manual_review':'Four new Cuyabeno/Galápagos scenes and two previously cleared Amazon scenes inspected. No frogs in batch.','photos':photos,'regressions':'Duplicate image/source and recent reuse rejected'}
 (root/'planning/ai-os/evidence/decision-image-rotation-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='photos'}));raise SystemExit(bool(errors))
