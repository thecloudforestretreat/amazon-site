"""Render supervisor-reviewed bilingual Peru editorial checkpoints; never deploy."""
import json,html,sys
from pathlib import Path
R=Path(__file__).resolve().parents[2]
e=lambda x:html.escape(str(x),quote=True)
def validate_page(d):
 if len(d.get('sections',[]))!=9:raise ValueError('Nine reviewed sections required')
 for row in d['sections']:
  if not isinstance(row,list) or len(row)!=3 or not all(isinstance(v,str) and v.strip() for v in row):raise ValueError('Section must contain heading and two text paragraphs')
 for key in ['quick','cta']:
  if not isinstance(d.get(key),list) or len(d[key])!=2 or not all(isinstance(v,str) for v in d[key]):raise ValueError('Invalid '+key)
 if len(d.get('faqs',[]))!=4 or any(not isinstance(v,list) or len(v)!=2 or not all(isinstance(s,str) for s in v) for v in d['faqs']):raise ValueError('Four question/answer pairs required')
def render(checkpoint):
 spec=json.loads(Path(checkpoint).read_text())
 if spec.get('editorial_status')!='reviewed':raise ValueError('Supervisor-reviewed checkpoint required')
 for topic,langs in spec['pages'].items():
  for lang,d in langs.items():
   validate_page(d)
   es=lang=='es';base='/es/peru/' if es else '/peru/';r=base+d['slug']+'/';other='en' if es else 'es';pair=('/peru/' if es else '/es/peru/')+langs[other]['slug']+'/';url='https://experiencetheamazon.com'+r
   crumbs=[('Inicio' if es else 'Home','/es/' if es else '/'),('Amazonía peruana' if es else 'Peruvian Amazon',base),(d['h1'],r)]
   def photo(key,alt,hero=False):
    im=spec['images'][key];a='fetchpriority="high"' if hero else 'loading="lazy"'
    return f'<figure class="peru-photo"><img src="/assets/images/peru/{key}.jpg" width="{im["width"]}" height="{im["height"]}" alt="{e(alt)}" {a} decoding="async"><figcaption><a href="{im["source"]}">{e(im["label"])}</a> · <a href="{im["license_url"]}">{e(im["license"])}</a></figcaption></figure>'
   breadcrumb='<nav class="peru-breadcrumb eta-shell" aria-label="'+('Ruta de navegación' if es else 'Breadcrumb')+'">'+'<span aria-hidden="true">›</span>'.join(f'<span aria-current="page">{e(n)}</span>' if i==2 else f'<a href="{u}">{e(n)}</a>' for i,(n,u) in enumerate(crumbs))+'</nav>'
   nav='<nav class="peru-nav eta-shell" aria-label="'+('Guías de Perú' if es else 'Peru guides')+'">'+''.join(f'<a href="{u}">{e(n)}</a>' for u,n in d['links'] if u!=r)+'</nav>'
   contact='/es/contacto/' if es else '/contact/'
   body=breadcrumb+nav+'<section class="eta-article-hero"><div class="eta-shell peru-hero"><div><p class="eta-kicker">'+('AMAZONÍA PERUANA' if es else 'PERUVIAN AMAZON')+f'</p><h1>{e(d["h1"])}</h1><p class="eta-lede">{e(d["lede"])}</p><a class="eta-button eta-button--gold" href="{contact}">'+('Planifica este viaje' if es else 'Plan this journey')+'</a></div>'+photo(d['hero'][0],d['hero'][1],True)+'</div></section>'
   body+='<section class="eta-section--tight"><div class="eta-shell peru-answer"><p class="eta-kicker">'+('DE UN VISTAZO' if es else 'AT A GLANCE')+f'</p><h2>{e(d["quick"][0])}</h2><p>{e(d["quick"][1])}</p></div></section>'
   for i,(heading,*paras) in enumerate(d['sections']):
    text=f'<h2>{e(heading)}</h2>'+''.join(f'<p>{e(p)}</p>' for p in paras)
    if str(i) in d['features']:
     key,alt=d['features'][str(i)];body+='<section class="eta-section eta-section--mist"><div class="eta-shell peru-feature'+(' peru-feature--reverse' if i%2 else '')+'">'+photo(key,alt)+'<div>'+text+'</div></div></section>'
    else:body+='<section class="eta-section"><div class="eta-shell eta-reading">'+text+'</div></section>'
   body+='<section class="eta-section"><div class="eta-shell eta-reading peru-faq"><h2>'+('Preguntas frecuentes' if es else 'Planning questions')+'</h2>'+''.join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q,a in d['faqs'])+'</div></section>'
   body+=f'<section class="eta-section"><div class="eta-shell peru-cta"><h2>{e(d["cta"][0])}</h2><p>{e(d["cta"][1])}</p><a class="eta-button eta-button--gold" href="{contact}">'+('Comparte tus planes' if es else 'Share your plans')+'</a><p>'+' · '.join(f'<a href="{u}">{e(n)}</a>' for u,n in d['links'] if u!=r)+'</p></div></section>'
   body+='<section class="eta-section--tight"><div class="eta-shell eta-reading"><h2>'+('Fuentes y alcance' if es else 'Sources & scope')+f'</h2><p>{e(d["scope"])}</p><ul>'+''.join(f'<li><a href="{u}">{e(n)}</a></li>' for n,u in d['sources'])+'</ul></div></section>'
   graph=[{'@type':'WebPage','@id':url+'#page','url':url,'name':d['h1'],'description':d['description'],'inLanguage':lang,'dateModified':spec['review_date'],'publisher':{'@type':'Organization','name':'Experience The Amazon','url':'https://experiencetheamazon.com/'},'breadcrumb':{'@id':url+'#breadcrumb'},'primaryImageOfPage':{'@type':'ImageObject','url':'https://experiencetheamazon.com/assets/images/peru/'+d['hero'][0]+'.jpg'}},{'@type':'BreadcrumbList','@id':url+'#breadcrumb','itemListElement':[{'@type':'ListItem','position':i+1,'name':n,'item':'https://experiencetheamazon.com'+u} for i,(n,u) in enumerate(crumbs)]},{'@type':'FAQPage','@id':url+'#questions','inLanguage':lang,'mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in d['faqs']]}]
   head=f'<meta charset="utf-8"><title>{e(d["title"])}</title><meta name="description" content="{e(d["description"])}"><link rel="canonical" href="{url}">'
   for l,t in [('en',('/peru/'+langs['en']['slug']+'/')),('es',('/es/peru/'+langs['es']['slug']+'/')),('x-default',('/peru/'+langs['en']['slug']+'/'))]:head+=f'<link rel="alternate" hreflang="{l}" href="https://experiencetheamazon.com{t}">'
   head+='{{ETA_HEAD}}<link rel="stylesheet" href="/assets/css/clusters/editorial.css"><link rel="stylesheet" href="/assets/css/clusters/peru.css">'
   for prop,value in [('type','website'),('title',d['title']),('description',d['description']),('url',url),('image','https://experiencetheamazon.com/assets/images/peru/'+d['hero'][0]+'.jpg'),('locale','es_ES' if es else 'en_US')]:head+=f'<meta property="og:{prop}" content="{e(value)}">'
   head+='<meta name="twitter:card" content="summary_large_image"><script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False)+'</script>'
   p=R/'src/pages'/lang/'peru'/d['slug']/'index.html';p.parent.mkdir(parents=True,exist_ok=True)
   p.write_text(f'<!doctype html><html lang="{lang}" data-language-pair="{pair}" data-page-id="peru_{topic}_{lang}" data-pair-id="peru_{topic}_001" data-page-type="{d["type"]}" data-country="peru" data-topic-cluster="peru-amazon" data-funnel-stage="consideration"><head>'+head+'</head><body>{{ETA_HEADER}}<main id="main-content">'+body+'</main>{{ETA_FOOTER}}</body></html>')
if __name__=='__main__':render(sys.argv[1])
