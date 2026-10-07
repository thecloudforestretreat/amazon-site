"""Audit crawlable links, main-content inlinks and click depth in compiled pages."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
from collections import deque
import json,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else 'dist-ecuador')
class Page(HTMLParser):
 def __init__(self):super().__init__();self.main=False;self.links=set();self.content=set();self.indexable=True
 def handle_starttag(self,t,a):
  a=dict(a)
  if t=='main':self.main=True
  if t=='meta' and a.get('name')=='robots' and 'noindex' in a.get('content',''):self.indexable=False
  if t=='a':
   u=urlsplit(a.get('href',''))
   if u.netloc and u.netloc not in ['experiencetheamazon.com','www.experiencetheamazon.com']:return
   if not u.path.startswith('/') or '/assets/' in u.path:return
   p=unquote(u.path);p=p if p.endswith('/') else p+'/'
   self.links.add(p)
   if self.main:self.content.add(p)
 def handle_endtag(self,t):
  if t=='main':self.main=False
pages={}
for f in root.rglob('index.html'):
 p=Page();p.feed(f.read_text());pages['/'+str(f.relative_to(root)).replace('index.html','')]=p
incoming={r:set() for r in pages};context={r:set() for r in pages};broken=[]
for r,p in pages.items():
 for target in p.links:
  if target in pages:
   if r!=target:incoming[target].add(r)
  else:broken.append({'source':r,'target':target})
 for target in p.content:
  if target in pages and target!=r:context[target].add(r)
depth={'/':0,'/es/':0};q=deque(depth)
while q:
 r=q.popleft()
 for t in pages[r].links:
  if t in pages and t not in depth:depth[t]=depth[r]+1;q.append(t)
rows=[{'route':r,'incoming_pages':len(incoming[r]),'main_content_incoming_pages':len(context[r]),'main_content_outgoing_pages':len(p.content-{r}),'click_depth':depth.get(r)} for r,p in sorted(pages.items()) if p.indexable and (r.startswith('/ecuador/') or r.startswith('/es/ecuador/'))]
print(json.dumps({'artifact':str(root),'pages_audited':len(rows),'broken_routes':broken,'orphans':[r for r in rows if not r['incoming_pages']],'without_main_content_inlinks':[r for r in rows if not r['main_content_incoming_pages']],'max_click_depth':max((r['click_depth'] or 0 for r in rows),default=0),'pages':rows},indent=2))
