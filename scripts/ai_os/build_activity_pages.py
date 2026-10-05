"""Build reviewed duration guides only; no model calls, no deploy."""
from pathlib import Path
import json,html,re,hashlib
root=Path(__file__).resolve().parents[2]; esc=html.escape
data={d['slug']:d for d in json.loads((root/'src/data/ecuador-destinations.json').read_text())}
def hero(d):
 return dict(src=d['image'],width=d['imageWidth'],height=d['imageHeight'],altEn=d['imageAltEn'],altEs=d['imageAltEs'],credit=d['imageCredit'].removeprefix('Photo: '),source=d['imageSource'],license=d.get('imageLicenseLabel','CC BY 2.0' if d.get('imageLicense') else ''),licenseUrl=d.get('imageLicense',''))
configs=json.loads((root/'planning/ai-os/activity-batch-config.json').read_text())
copy=json.loads((root/'planning/ai-os/activity-batch-content.json').read_text())
for cfg in configs:
 job=cfg['job'];runs=list((root/f'planning/ai-os/runs/{job}').glob('*/draft.json'));assert len(runs)==1,runs
 draft=json.loads((runs[0].parent/'reviewed.json').read_text())
 for lang in ['en','es']:
  c=copy[job][lang];route=('/es' if lang=='es' else '')+'/ecuador/'+cfg[lang]+'/';en='/ecuador/'+cfg['en']+'/';es='/es/ecuador/'+cfg['es']+'/';contact='/es/contacto/' if lang=='es' else '/contact/';hub='/es/ecuador/' if lang=='es' else '/ecuador/';faqid='preguntas' if lang=='es' else 'faqs'
  def photo(p,hero=False):
   credit=('Foto: ' if lang=='es' else 'Photo: ')+f'<a href="{esc(p["source"])}">{esc(p["credit"])}</a>'
   if p.get('licenseUrl'):credit+=f' · <a href="{p["licenseUrl"]}">{p["license"]}</a>'
   credit+=' · '+('Adaptada' if lang=='es' else 'Edited')
   attrs='fetchpriority="high"' if hero else 'loading="lazy"'
   return f'<figure class="{"eta-country-art eta-country-art--licensed" if hero else "eta-hub-photo"}"><img src="{p["src"]}" width="{p["width"]}" height="{p["height"]}" alt="{esc(p["altEs" if lang=="es" else "altEn"])}" decoding="async" {attrs}><figcaption class="eta-photo-credit">{credit}</figcaption></figure>'
  schema={'@context':'https://schema.org','@graph':[{'@type':'WebPage','name':c['title'],'url':'https://experiencetheamazon.com'+route,'inLanguage':lang},{'@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in c['faqs']]}]}
  s=f'<!doctype html><html lang="{lang}" data-language-pair="{es if lang=="en" else en}" data-page-id="ecuador_{cfg["en"].replace("-","_")}" data-pair-id="{cfg["pair"]}" data-page-type="{cfg["pageType"]}" data-country="ecuador" data-topic-cluster="ecuador-trip-planning" data-funnel-stage="consideration"><head><meta charset="utf-8"><title>{esc(c["title"])}</title><meta name="description" content="{esc(c["lede"])}"><meta name="robots" content="index,follow"><link rel="canonical" href="https://experiencetheamazon.com{route}">'
  for l,r in [('en',en),('es',es),('x-default',en)]:s+=f'<link rel="alternate" hreflang="{l}" href="https://experiencetheamazon.com{r}">'
  s+='{{ETA_HEAD}}'+''.join(f'<link rel="stylesheet" href="/assets/css/clusters/{x}.css">' for x in ['ecuador-hubs','country','planning','trust'])+'<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False)+'</script></head><body class="eta-planning-page eta-hub-page">{{ETA_HEADER}}{{ETA_ECUADOR_NAV}}<main id="main-content">'
  s+=f'<div class="eta-shell eta-breadcrumbs"><a href="{hub}">Ecuador</a><span>›</span><span>{esc(c["title"].split(" | ")[0])}</span></div><section class="eta-country-hero"><div class="eta-shell eta-country-hero__grid"><div><p class="eta-kicker">{"Guía de viaje" if lang=="es" else "Ecuador trip guide"}</p><h1>{esc(c["h1"])}</h1><p class="eta-lede">{esc(c["lede"])}</p><div class="eta-actions"><a class="eta-button eta-button--gold" href="{contact}">{"Planifica tu viaje" if lang=="es" else "Plan this journey"}</a><a class="eta-button eta-button--outline" href="#compare">{"Compara las rutas" if lang=="es" else "Explore your options"}</a></div></div>{photo(cfg["photos"][0],True)}</div></section>'
  s+='<section class="eta-section--tight"><div class="eta-shell"><div class="eta-facts">'+''.join(f'<div class="eta-fact"><strong>{esc(a)}</strong><span>{esc(b)}</span></div>' for a,b in c['facts'])+'</div></div></section>'
  s+=f'<section class="eta-section" id="compare"><div class="eta-shell"><div class="eta-answer"><span class="eta-answer__label">{"Respuesta breve" if lang=="es" else "Quick answer"}</span><h2>{esc(c["intro"])}</h2><p>{esc(c["quick"])}</p></div><div class="eta-decision-grid" style="margin-top:32px">'
  for h,p,slug in c['cards']:s+=f'<article class="eta-decision-card"><h3>{esc(h)}</h3><p>{esc(p)}</p><a href="{hub+slug}/">{"Explora la guía" if lang=="es" else "Read the regional guide"} →</a></article>'
  s+='</div></div></section>'
  s+=f'<section class="eta-section eta-section--mist" id="practical-guide"><div class="eta-shell"><div class="eta-section-heading"><div><p class="eta-kicker">{"Decisiones prácticas" if lang=="es" else "Practical decisions"}</p><h2>{esc(c["guide"])}</h2></div><p>{esc(c["guidelede"])}</p></div><div class="eta-hub-guide">'
  for i,card in enumerate(draft[lang]):
   item=f'<article class="eta-hub-guide-card"><span class="eta-hub-number">{i+1:02}</span><h3>{esc(card["heading"])}</h3><p>{esc(card["intro"])}</p><ul>'+''.join(f'<li>{esc(p)}</li>' for p in card['points'])+'</ul></article>'
   if i in [0,3]:s+=f'<div class="eta-hub-guide-feature'+(' eta-hub-guide-feature--reverse' if i==3 else '')+'">'+photo(cfg['photos'][1 if i==0 else 2])+item+'</div>'
   else:s+=item
  s+='</div></div></section><section class="eta-section"><div class="eta-shell eta-decision-grid">'+''.join(f'<article class="eta-decision-card"><h2>{esc(c[h])}</h2><p>{esc(c[p])}</p></article>' for h,p in [('extra','extrap'),('extra2','extra2p')])+'</div></section>'
  s+=f'<section class="eta-section eta-section--mist" id="{faqid}"><div class="eta-shell eta-reading"><p class="eta-kicker">{"Preguntas frecuentes" if lang=="es" else "Your questions"}</p><h2>{"Antes de elegir" if lang=="es" else "Before you choose"}</h2><div class="eta-stack">'+''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q,a in c['faqs'])+'</div></div></section>'
  other=configs[1 if job=='canoe-format' else 0];otherroute=hub+other[lang]+'/'
  s+=f'<section class="eta-section"><div class="eta-shell eta-trust-strip"><p class="eta-kicker">{"El siguiente paso" if lang=="es" else "Your next step"}</p><h2>{"Cuéntanos cómo quieres viajar" if lang=="es" else "Tell us what your journey needs"}</h2><p>{"Comparte fechas, grupo, punto de partida, intereses y planes posteriores para preparar una consulta clara." if lang=="es" else "Share your dates, group, starting point, interests and onward plans to prepare a focused inquiry."}</p><div class="eta-actions"><a class="eta-button eta-button--gold" href="{contact}">{"Consulta tu viaje" if lang=="es" else "Ask about your journey"}</a><a class="eta-button eta-button--outline" href="{otherroute}">{"Explora la otra guía" if lang=="es" else ("Explore the travel-date guide" if job=="canoe-format" else "Explore the canoe guide")}</a></div></div></section>'
  old=(root/f'src/pages/{lang}/ecuador/'/Path('amazon-lodges/index.html' if lang=='en' else 'lodges-en-la-amazonia/index.html')).read_text()
  sources=old[old.index('<section class="eta-section--tight"><div class="eta-shell eta-reading"><h2>'):old.index('</main>')]
  if job=='season-planning':
   sources=(f'<section class="eta-section--tight"><div class="eta-shell eta-reading"><h2>'+('Climate sources' if lang=='en' else 'Fuentes climáticas')+'</h2><p><a href="https://unfccc.int/resource/docs/natc/ecunc1.pdf">Ecuador: First National Communication to the UNFCCC</a> · <a href="https://www.inamhi.gob.ec/catalogo-de-productos/">INAMHI</a></p><p>'+('Historical climate context, not a forecast; provider and route conditions require current confirmation.' if lang=='en' else 'Contexto climático histórico, no un pronóstico; confirma las condiciones actuales de proveedor y ruta.')+'</p></div></section>')
  s+=sources+'</main>{{ETA_FOOTER}}</body></html>\n'
  dest=root/f'src/pages/{lang}/ecuador/{cfg[lang]}/index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(s)
  (runs[0].parent/f'reviewed-{lang}.json').write_text(json.dumps(draft[lang],ensure_ascii=False,indent=2)+'\n')
(root/'planning/ai-os/evidence/activity-images.json').write_text(json.dumps({'date':'2026-10-05','photos':{c['job']:c['photos'] for c in configs}},ensure_ascii=False,indent=2)+'\n')
