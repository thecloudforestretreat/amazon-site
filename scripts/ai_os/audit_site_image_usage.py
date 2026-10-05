"""Expose cross-page scene reuse; enforce retired frog rotation and page uniqueness."""
import json,re,hashlib
from collections import defaultdict
from pathlib import Path
root=Path(__file__).resolve().parents[2]
def inspect(pages):
 usage=defaultdict(list);errors=[]
 for route,images in pages.items():
  if len(images)!=len(set(images)):errors.append('Duplicate image on '+route)
  for image in images:usage[image].append(route)
 for src,routes in usage.items():
  if 'frog-' in src and len(routes)>1:errors.append('Frog reused across more than one EN page: '+src)
 return dict(usage),errors
if __name__=='__main__':
 pages={}
 for p in (root/'dist/ecuador').rglob('index.html'):
  main=re.search(r'<main\b[^>]*>(.*?)</main>',p.read_text(),re.S)[1]
  pages['/'+str(p.parent.relative_to(root/'dist'))+'/']=re.findall(r'<img[^>]+src=[\"\x27]([^\"\x27]+)',main)
 usage,errors=inspect(pages)
 assert inspect({'a':['frog-test.jpg'],'b':['frog-test.jpg'],'c':['frog-test.jpg']})[1]
 assert inspect({'a':['scene.jpg','scene.jpg']})[1]
 report={'passed':not errors,'errors':errors,'scope':'EN Ecuador compiled main images; bilingual mirrors counted once','usage':[{'src':src,'count':len(routes),'routes':routes} for src,routes in sorted(usage.items(),key=lambda item:-len(item[1]))],'policy':'No duplicates within page; frog scene only on its destination EN page; flag counts for editorial image selection','regressions':'Duplicate within page and three-page frog reuse rejected'}
 (root/'planning/ai-os/evidence/site-image-usage.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':report['passed'],'errors':errors,'most_used':report['usage'][:5]}));raise SystemExit(bool(errors))
