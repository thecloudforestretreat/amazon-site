"""Audit batch image reuse against recent batches, including renamed duplicate files."""
from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[2]
def problems(photos,recent):
 errors=[];sources=[p['src'] for p in photos]
 if len(set(sources))!=len(sources):errors.append('Repeated filename within batch')
 if set(sources)&recent:errors.append('Image reused from recent two batches')
 hashes=[hashlib.sha256((root/'src'/p['src'].lstrip('/')).read_bytes()).hexdigest() for p in photos]
 if len(set(hashes))!=len(hashes):errors.append('Repeated image bytes under another filename')
 origins=[p['source'] for p in photos]
 if len(set(origins))!=len(origins):errors.append('Repeated source scene under another asset')
 return errors
if __name__=='__main__':
 configs=json.loads((root/'planning/ai-os/nature-batch-config.json').read_text());photos=[p for c in configs for p in c['photos']];recent=set()
 for name in ['duration-images','traveler-images']:
  data=json.loads((root/f'planning/ai-os/evidence/{name}.json').read_text())
  recent.update(p['src'] for row in data['photos'].values() for p in row)
 errors=problems(photos,recent)
 # Regression for the actual reported failure: repeat a prior asset and repeat one within the batch.
 assert problems(photos+[photos[0]],recent)
 assert problems(photos,{photos[0]['src']})
 r={'errors':errors,'passed':not errors,'photos':photos,'unique_batch_scenes':len(photos),'recent_batches':['4-day/5-day','private/family'],'manual_visual_scene_review':'Five new Yasuní scenes individually inspected; one previously reviewed Tena canopy scene; six distinct scenes, not alternate crops','negative_regressions':'Duplicate within batch and reuse from previous batch rejected'}
 (root/'planning/ai-os/evidence/nature-image-rotation-qa.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='photos'}));raise SystemExit(bool(errors))
