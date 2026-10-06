"""Audit current editorial article batch against saved recent image evidence."""
import json,re,sys
batch=sys.argv[1] if len(sys.argv)>1 else "experience"
assert batch in ["experience","gateway"]
recent_names=["article","blog"] if batch=="experience" else ["experience","article"]
from pathlib import Path
from audit_decision_image_rotation import problems
r=Path(__file__).resolve().parents[2];b=r/'planning/ai-os';configs=json.loads((b/f'{batch}-batch-config.json').read_text());photos=[p for c in configs for p in c['photos']];recent=[]
for name in recent_names:
 d=json.loads((b/f'evidence/{name}-images.json').read_text());recent.extend(p for row in d['photos'].values() for p in row)
errors=problems(photos,recent)
for c in configs:
 for lang in ['en','es']:
  base=('/es' if lang=='es' else '')+'/ecuador/';t=(r/'dist'/base.lstrip('/')/c[lang]/'index.html').read_text()
  if ('Explora el diario amazónico' if lang=='es' else 'Explore the Amazon journal') not in re.findall(r'<a[^>]+href="'+base+r'blog/"[^>]*>(.*?)</a>',t):errors.append('Journal link mismatch')
  graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',t,re.S)[1])['@graph']
  if not any(x['@type']=='Article' for x in graph):errors.append('Article schema missing')
report=dict(passed=not errors,errors=errors,unique_scenes=len(photos),recent_batches=recent_names,photos=photos)
(b/f'evidence/{batch}-batch-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='photos'}));raise SystemExit(bool(errors))
