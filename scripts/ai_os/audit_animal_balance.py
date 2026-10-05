"""Guard the reviewed broad-fauna guide against insect-dominated photography."""
import json
from pathlib import Path

def problems(photos):
 groups=[p.get('animalGroup') for p in photos]
 errors=[]
 if any(g not in {'mammal','bird','reptile','amphibian','fish','invertebrate'} for g in groups):errors.append('Reviewed animal group missing')
 if len({g for g in groups if g and g!='invertebrate'})<3:errors.append('Broad fauna guide needs three vertebrate groups represented')
 if groups.count('invertebrate')>1:errors.append('Invertebrates dominate feature photography')
 return errors

if __name__=='__main__':
 root=Path(__file__).resolve().parents[2]
 cfg=next(c for c in json.loads((root/'planning/ai-os/species-batch-config.json').read_text()) if c['job']=='animals-guide')
 errors=problems(cfg['photos'])
 report={'passed':not errors,'errors':errors,'groups':[p.get('animalGroup') for p in cfg['photos']],'scope':'Broad animals guide editorial balance only; labels manually verified, not automatic species identification'}
 (root/'planning/ai-os/evidence/animal-balance-qa.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report));raise SystemExit(bool(errors))
