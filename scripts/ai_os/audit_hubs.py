"""Rendered-source gates for both Ecuador hubs; no model calls."""
import json,re,hashlib
from pathlib import Path
from html import unescape
from ai_os.website.html import extract_page_signals
root=Path(__file__).resolve().parents[2];reports={}
for pair,en,es in [('pair_003','ecuador','es/ecuador'),('pair_009','ecuador/amazon-lodges','es/ecuador/lodges-en-la-amazonia'),('pair_010','ecuador/amazon-tours-from-quito','es/ecuador/tours-a-la-amazonia-desde-quito'),('pair_011','ecuador/3-day-amazon-tour','es/ecuador/tour-de-3-dias-en-la-amazonia'),('pair_012','ecuador/4-day-amazon-tour','es/ecuador/tour-de-4-dias-en-la-amazonia'),('pair_013','ecuador/5-day-amazon-tour','es/ecuador/tour-de-5-dias-en-la-amazonia'),('pair_014','ecuador/private-amazon-tour','es/ecuador/tour-privado-a-la-amazonia'),('pair_015','ecuador/family-amazon-tour','es/ecuador/tour-familiar-a-la-amazonia'),('pair_016','ecuador/amazon-birdwatching-tour','es/ecuador/tour-de-avistamiento-de-aves-en-la-amazonia'),('pair_017','ecuador/amazon-wildlife-tour','es/ecuador/tour-de-fauna-en-la-amazonia'),('pair_018','ecuador/amazon-canoe-tour','es/ecuador/tour-en-canoa-por-la-amazonia'),('pair_019','ecuador/best-time-to-visit-the-ecuador-amazon','es/ecuador/mejor-epoca-para-visitar-la-amazonia-ecuatoriana'),('pair_020','ecuador/how-to-get-to-the-ecuador-amazon','es/ecuador/como-llegar-a-la-amazonia-ecuatoriana'),('pair_021','ecuador/what-to-pack-for-the-amazon','es/ecuador/que-llevar-a-la-amazonia')]:
 for lang,route in [('en',en),('es',es)]:
  raw=(root/'dist'/route/'index.html').read_text();main=re.search(r'<main\b[^>]*>(.*?)</main>',raw,re.S)[1];signals=extract_page_signals(raw,'https://experiencetheamazon.com');errors=[]
  if 'eta-hub-page' not in re.search(r'<body[^>]*>',raw)[0] or '/assets/css/clusters/ecuador-hubs.css?v=' not in raw:errors.append('Missing scoped hub CSS or body class')
  words=len(re.findall(r'\S+',unescape(re.sub('<[^>]+>',' ',main))))
  if not 1000<=words<=2400:errors.append('Editorial main-content range')
  if len(signals.h1)!=1 or signals.document_language!=lang:errors.append('Heading or language')
  if signals.canonical!='https://experiencetheamazon.com/'+route+'/':errors.append('Canonical')
  if dict(signals.hreflang).get('en')!='https://experiencetheamazon.com/'+en+'/' or dict(signals.hreflang).get('es')!='https://experiencetheamazon.com/'+es+'/':errors.append('Language pair')
  if 'noindex' not in signals.robots:errors.append('Staging indexing')
  if signals.missing_alt_count or signals.unlabelled_control_count:errors.append('Unlabelled media or control')
  photos=re.findall(r'<img[^>]+src="([^"]+)"',main)
  if len(photos)!=3 or len(set(photos))!=3:errors.append('Three distinct images')
  if 'Reserved for' in main or 'Espacio reservado' in main or 'eta-card__visual' in main:errors.append('Placeholder remains')
  faq=[[unescape(q),unescape(a)] for q,a in re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>',main,re.S)]
  schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',raw,re.S)[1]);sfaq=next(s for s in schema['@graph'] if s['@type']=='FAQPage')
  if len(faq)!=6 or faq!=[[q['name'],q['acceptedAnswer']['text']] for q in sfaq['mainEntity']]:errors.append('Visible/schema FAQs mismatch')
  for src in photos:
   if not (root/'dist'/src.lstrip('/')).exists():errors.append('Photo file missing')
  for href in re.findall(r'href="(#[^"]+)"',raw):
   if href!='#' and f'id="{href[1:]}"' not in raw:errors.append('Broken fragment '+href)
  reports[route]={'pair_id':pair,'language':lang,'main_words':words,'faq_count':len(faq),'photos':photos,'sha256':hashlib.sha256(raw.encode()).hexdigest(),'errors':errors,'passed':not errors}
(root/'planning/ai-os/qa-hubs.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n');print(json.dumps(reports,ensure_ascii=False,indent=2));raise SystemExit(0 if all(r['passed'] for r in reports.values()) else 1)
