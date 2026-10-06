"""Deterministic release checks; browser/accessibility/performance reviews remain separate."""
import json,re,sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
root=Path(sys.argv[1] if len(sys.argv)>1 else 'dist')
class Page(HTMLParser):
 def __init__(self):
  super().__init__();self.ids=[];self.links=[];self.assets=[];self.h1=0;self.main=0;self.images=[];self.controls=[];self.labels=[];self.alternates=[];self.canonical=[];self.lang='';self.schema=[];self.in_schema=False
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.append(a['id'])
  if t=='html':self.lang=a.get('lang','')
  if t=='main':self.main+=1
  if t=='h1':self.h1+=1
  if t=='a':self.links.append(a.get('href',''))
  if t=='img':self.images.append(a);self.assets.append(a.get('src',''))
  if t=='script' and a.get('src'):self.assets.append(a['src'])
  if t=='link' and a.get('rel')=='stylesheet':self.assets.append(a.get('href',''))
  if t=='link' and a.get('rel')=='alternate':self.alternates.append(a)
  if t=='link' and a.get('rel')=='canonical':self.canonical.append(a.get('href'))
  if t in ['input','textarea','select'] and a.get('type') not in ['hidden','checkbox']:self.controls.append(a)
  if t=='label' and a.get('for'):self.labels.append(a['for'])
  if t=='script' and a.get('type')=='application/ld+json':self.in_schema=True
 def handle_endtag(self,t):
  if t=='script':self.in_schema=False
 def handle_data(self,d):
  if self.in_schema:self.schema.append(d)
files=list(root.rglob('*.html'));pages={}
for f in files:
 route='/'+str(f.relative_to(root)).replace('index.html','');p=Page();p.feed(f.read_text());pages[route]=p
errors=[];checked=[]
for route,p in pages.items():
 if not(route.startswith('/ecuador/') or route.startswith('/es/ecuador/') or route in ['/','/es/','/contact/','/es/contacto/','/about/','/es/nuestra-propuesta/','/privacy-policy/','/es/politica-de-privacidad/','/terms/','/es/terminos/']):continue
 checked.append(route)
 def fail(reason):errors.append({'route':route,'reason':reason})
 if p.h1!=1:fail(f'{p.h1} H1 headings')
 if p.main!=1:fail(f'{p.main} main landmarks')
 if len(p.ids)!=len(set(p.ids)):fail('duplicate IDs')
 if p.lang!=('es' if route.startswith('/es/') else 'en'):fail('wrong document language')
 if len(p.canonical)!=1:fail('canonical missing or duplicated')
 for a in p.alternates:
  target=urlsplit(a.get('href','')).path
  if target not in pages:fail('missing language counterpart '+target)
 for image in p.images:
  if 'alt' not in image:fail('image lacks alt attribute')
 for c in p.controls:
  if c.get('name')=='website':continue # wrapped, visually hidden honeypot label
  if not(c.get('id') in p.labels or c.get('aria-label') or c.get('aria-labelledby')):fail('unlabelled control '+c.get('name',''))
 for asset in p.assets:
  if asset.startswith('/') and not(root/urlsplit(asset).path.lstrip('/')).is_file():fail('missing asset '+asset)
 for href in p.links:
  if not href or href=='#':continue # runtime WhatsApp/mailto bindings
  u=urlsplit(href)
  if u.netloc:continue
  if u.path and not u.path.startswith('/'):continue
  target=u.path or route
  if target not in pages:fail('broken route '+target);continue
  if u.fragment and unquote(u.fragment) not in pages[target].ids:fail('broken anchor '+href)
 for schema in p.schema:
  try:json.loads(schema)
  except ValueError:fail('invalid JSON-LD')
report={'scope':'Ecuador and launch support pages','pages_checked':len(checked),'checks':['headings','main landmarks','unique IDs','language counterparts','image alt presence','form labels','asset availability','routes and anchors','JSON-LD syntax'],'errors':errors,'passed':not errors,'limitations':['No automated WCAG conformance certification','Contrast, keyboard interaction and responsive visuals require browser review','Navigation timing is a lab observation, not field Core Web Vitals']}
Path('planning/ai-os/ecuador-release-static-qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(bool(errors))
