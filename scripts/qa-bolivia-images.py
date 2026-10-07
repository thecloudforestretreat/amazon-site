"""Audit owner photo promotion against the compiled bilingual country, without browser claims."""
import json,hashlib,re
from pathlib import Path
from html.parser import HTMLParser
class Images(HTMLParser):
 def __init__(self):super().__init__();self.main=False;self.images=[]
 def handle_starttag(self,t,a):
  if t=='main':self.main=True
  if t=='img' and self.main:self.images.append(dict(a))
 def handle_endtag(self,t):
  if t=='main':self.main=False
P=Path('planning/ai-os');s=json.loads((P/'bolivia-images-reviewed.json').read_text());errors=[];rows=[]
for topic,v in s['pages'].items():
 for lang,d in v.items():
  route=('/es/bolivia/' if lang=='es' else '/bolivia/')+(d['slug']+'/' if d['slug'] else '')
  html=(Path('dist')/route.strip('/')/'index.html').read_text();parser=Images();parser.feed(html)
  keys=[d['hero'][0]]+[im[0] for im in d['features'].values()];expected=[s['images'][k] for k in keys];hashes=[]
  if len(parser.images)!=3:errors.append(route+' incorrect image count')
  for actual,want in zip(parser.images,expected):
   for field in ['src','width','height']:
    if str(actual.get(field))!=str(want[field]):errors.append(route+' image '+field+' mismatch')
   f=Path('dist')/want['src'].lstrip('/');digest=hashlib.sha256(f.read_bytes()).hexdigest();hashes.append(digest)
   if digest!=want['web_sha256']:errors.append(route+' promoted file hash mismatch')
  if len(set(hashes))!=3:errors.append(route+' duplicate image bytes')
  if {'amazon-thatched-cabin-forest-path','amazon-thatched-cabins-walkway'}.issubset(keys):errors.append(route+' same cabin scene twice')
  hero=expected[0]['src']
  if 'https://experiencetheamazon.com'+hero not in html:errors.append(route+' social/schema hero missing')
  if '<figcaption>' in html:errors.append(route+' old photo credit caption retained')
  if any(x in html for x in ['photograph was made at Chalalán','photograph here documents one Yacuma','La fotografía del ave se tomó','Tuichi photographs on this page']):errors.append(route+' stale photo geography claim')
  rows.append({'route':route,'assets':[x['src'] for x in expected],'hub_click_depth':0 if not d['slug'] else 1,'matched_language_selection':True})
assert s['pages'].keys()==json.loads((P/'bolivia-batch6-reviewed.json').read_text())['pages'].keys()
report={'pages_checked':len(rows),'errors':errors,'pages':rows,'limits':['Hash checks detect byte duplicates; scene uniqueness also requires human review','Static dimensions and metadata checks are not rendered desktop/mobile QA','No live inquiry submission or inbox delivery performed in this run']};(P/'bolivia-image-qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pages':len(rows),'errors':errors}));raise SystemExit(bool(errors))
