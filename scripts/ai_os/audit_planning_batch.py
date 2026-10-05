"""Check scene rotation and the cross-link label error observed in review."""
import json,re
from pathlib import Path
from audit_decision_image_rotation import problems
root=Path(__file__).resolve().parents[2]
configs=json.loads((root/'planning/ai-os/planning-batch-config.json').read_text());photos=[p for c in configs for p in c['photos']]
recent=[]
for batch in ['decision','species']:
 d=json.loads((root/f'planning/ai-os/evidence/{batch}-images.json').read_text());recent.extend(p for row in d['photos'].values() for p in row)
errors=problems(photos,recent)
for cfg in configs:
 for lang in ['en','es']:
  base=('/es' if lang=='es' else '')+'/ecuador/'
  other=next(c for c in configs if c!=cfg)
  expected=('Read Ecuador FAQs' if cfg['job']=='trip-plan-guide' else 'Plan your Amazon trip') if lang=='en' else ('Lee las preguntas frecuentes' if cfg['job']=='trip-plan-guide' else 'Planifica tu viaje')
  text=(root/'dist'/base.lstrip('/')/cfg[lang]/'index.html').read_text()
  links=re.findall(r'<a\b[^>]*href="'+re.escape(base+other[lang]+'/')+r'"[^>]*>(.*?)</a>',text)
  if expected not in links:errors.append('Cross-link target/label mismatch '+cfg['job']+' '+lang)
report={'passed':not errors,'errors':errors,'unique_scenes':len(photos),'recent_batches':['decision','species'],'checks':['Six distinct images and sources; no scenes from preceding two batches','Bilingual cross-link labels match destination'],'photos':photos}
(root/'planning/ai-os/evidence/planning-batch-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='photos'}));raise SystemExit(bool(errors))
