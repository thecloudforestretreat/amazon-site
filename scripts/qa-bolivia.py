"""Audit compiled Bolivia pages; staging protection is intentional, not an SEO failure."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json,re
class Page(HTMLParser):
 def __init__(self):super().__init__();self.main=False;self.text=[];self.links=[];self.ids=set();self.css=[];self.images=[];self.h1=0;self.h2=0;self.lang=None
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='html':self.lang=a.get('lang')
  if a.get('id'):self.ids.add(a['id'])
  if t=='main':self.main=True
  if t=='link' and a.get('rel')=='stylesheet':self.css.append(a['href'])
  if self.main:
   if t=='a':self.links.append(a.get('href',''))
   if t=='h1':self.h1+=1
   if t=='h2':self.h2+=1
   if t=='img':self.images.append(a)
 def handle_endtag(self,t):
  if t=='main':self.main=False
 def handle_data(self,d):
  if self.main:self.text.append(d)
root=Path('dist');pages={};htmls={};errors=[]
for f in root.rglob('index.html'):
 r='/'+str(f.relative_to(root)).replace('index.html','');s=f.read_text();p=Page();p.feed(s);pages[r]=p;htmls[r]=s
rows=[];titles=[];descs=[]
for r,p in sorted(pages.items()):
 if not r.startswith(('/bolivia/','/es/bolivia/')):continue
 s=htmls[r];issues=[];title=re.search('<title>(.*?)</title>',s)[1];desc=re.search('<meta name="description" content="([^"]+)"',s)[1];titles.append(title);descs.append(desc)
 incoming=[k for k,v in pages.items() if k!=r and r in v.links];outgoing=set()
 for h in p.links:
  u=urlsplit(h)
  if u.netloc and u.netloc!='experiencetheamazon.com' or u.scheme and u.scheme not in ('https','http'):continue
  t=u.path or r
  if not t.startswith('/'):continue
  if t not in pages:issues.append('Broken route '+h)
  elif u.fragment and u.fragment not in pages[t].ids:issues.append('Broken anchor '+h)
  elif t!=r:outgoing.add(t)
 css=['/assets/css/core.css','/assets/css/clusters/editorial.css','/assets/css/clusters/bolivia.css']
 if [urlsplit(c).path for c in p.css if c.startswith('/assets/')]!=css:issues.append('Unexpected CSS stack')
 if p.h1!=1:issues.append('H1 count')
 if any(token in s for token in ['Boliviavian','boliviaana','Guías de Perú']):issues.append('Unreviewed geographic copy artifact')
 visible_faq=re.findall(r'<summary>(.*?)</summary><p>(.*?)</p>',s)
 from html import unescape
 if not re.search(r'<p>[^<]*<a href="/(?:es/)?bolivia/',s):issues.append('Missing contextual paragraph link')
 if len(title)>65 or len(desc)>170:issues.append('Metadata needs snippet review')
 if not incoming or len(outgoing)<3:issues.append('Insufficient contextual links')
 if any(not i.get('alt') or not i.get('width') or not i.get('height') for i in p.images):issues.append('Image metadata')
 sources=[i['src'] for i in p.images]
 if len(sources)!=len(set(sources)):issues.append('Duplicate page images')
 for i in sources:
  if not (root/i.lstrip('/')).exists():issues.append('Missing asset '+i)
 canonical=re.search('rel="canonical" href="([^"]+)"',s)[1]
 if canonical!='https://experiencetheamazon.com'+r:issues.append('Canonical mismatch')
 pair=re.search('data-language-pair="([^"]+)"',s)[1]
 if pair not in htmls or 'data-language-pair="'+r+'"' not in htmls[pair]:issues.append('Nonreciprocal language pair')
 schemas=[json.loads(x) for x in re.findall('<script type="application/ld\\+json">(.*?)</script>',s)]
 types={n['@type'] for v in schemas for n in v.get('@graph',[])}
 faq_nodes=[n for v in schemas for n in v.get('@graph',[]) if n.get('@type')=='FAQPage']
 schema_faq=[(n['name'],n['acceptedAnswer']['text']) for v in faq_nodes for n in v['mainEntity']]
 if [(unescape(q),unescape(a)) for q,a in visible_faq]!=schema_faq:issues.append('FAQ schema differs from visible answers')
 if not {'WebPage','BreadcrumbList'}.issubset(types):issues.append('Schema missing')
 words=len(' '.join(p.text).split())
 if words<800 or p.h2<8:issues.append('Content coverage requires editorial review')
 rows.append({'route':r,'main_words':words,'h2_sections':p.h2,'main_content_inlinks':incoming,'main_content_outlinks':sorted(outgoing),'css':p.css,'unique_images':len(sources),'schema_types':sorted(types),'issues':issues})
 errors.extend({'route':r,'issue':i} for i in issues)
if len(titles)!=len(set(titles)) or len(descs)!=len(set(descs)):errors.append({'issue':'Duplicate metadata'})
report={'pages_audited':len(rows),'errors':errors,'pages':rows,'limits':['Content counts do not prove editorial quality','Staging intentionally blocked from indexing; production eligibility requires country release','No live rankings, AI citations or field Core Web Vitals assessed']}
Path('planning/ai-os/bolivia-quality-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'pages':len(rows),'errors':errors,'word_range':[min(x['main_words'] for x in rows),max(x['main_words'] for x in rows)],'inlink_range':[min(len(x['main_content_inlinks']) for x in rows),max(len(x['main_content_inlinks']) for x in rows)]}));raise SystemExit(bool(errors))
