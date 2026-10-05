"""Deterministic pilot checks, reusing AI-OS's installed HTML signal parser."""
from dataclasses import asdict
from html import unescape
from pathlib import Path
import hashlib,json,re,sys
from ai_os.website.html import extract_page_signals

ROOT=Path(__file__).resolve().parents[2]
def audit():
    data=json.loads((ROOT/'src/data/ecuador-destinations.json').read_text())
    destination=next(d for d in data if d['slug']=='cuyabeno')
    expected={'en':'https://experiencetheamazon.com/ecuador/cuyabeno/','es':'https://experiencetheamazon.com/es/ecuador/cuyabeno/'}
    report={'pair_id':'pair_005','errors':[],'pages':{},'engine':'ai_os.website.html.extract_page_signals'}
    for lang in ['en','es']:
        route=('/es' if lang=='es' else '')+'/ecuador/cuyabeno/'
        path=ROOT/'dist'/route.strip('/')/'index.html'
        html=path.read_text()
        signals=extract_page_signals(html,'https://experiencetheamazon.com')
        errors=[]
        if signals.document_language != lang: errors.append('Language mismatch')
        if len(signals.h1)!=1: errors.append('Exactly one H1 required')
        if not signals.title or not signals.meta_description: errors.append('Missing search metadata')
        if signals.canonical != expected[lang]: errors.append('Canonical mismatch')
        for code,url in {**expected,'x-default':expected['en']}.items():
            if dict(signals.hreflang).get(code)!=url: errors.append('Reciprocal hreflang mismatch')
        if 'noindex' not in (signals.robots or ''): errors.append('Staging must be noindex')
        if 'data-pair-id="pair_005"' not in html or 'data-destination="cuyabeno"' not in html: errors.append('Missing analytics context')
        main=re.search(r'<main\b[^>]*>(.*?)</main>',html,re.S).group(1)
        reading_content=re.sub(r'<aside\b[^>]*>.*?</aside>','',main,flags=re.S)
        visible=unescape(re.sub(r'<[^>]+>',' ',reading_content))
        words=len(re.findall(r'\S+',visible))
        if words<1000 or words>2400: errors.append('Main content outside editorial range')
        schemas=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',html,re.S)]
        faq=next(x for schema in schemas for x in schema.get('@graph',[]) if x['@type']=='FAQPage')
        schema_faqs=[[x['name'],x['acceptedAnswer']['text']] for x in faq['mainEntity']]
        visible_faqs=[[unescape(re.sub('<[^>]+>','',x)).strip(),unescape(re.sub('<[^>]+>','',y)).strip()] for x,y in re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>',main,re.S)]
        if schema_faqs != visible_faqs or schema_faqs != destination[lang]['faqs']: errors.append('Visible and schema FAQs differ')
        if len(destination[lang].get('sections',[]))!=10: errors.append('Incomplete section coverage')
        if destination.get('imageSource') not in html: errors.append('Missing image source credit')
        if not (ROOT/'dist'/destination['image'].lstrip('/')).is_file(): errors.append('Missing image asset')
        if signals.missing_alt_count or signals.unlabelled_control_count: errors.append('Unlabelled image or control')
        for href in re.findall(r'href="(#[^"]+)"',html):
            if f'id="{href[1:]}"' not in html: errors.append('Broken page fragment '+href)
        report['errors'] += [lang+': '+e for e in errors]
        report['pages'][lang]={'route':route,'main_words':words,'word_count_scope':'Main content excluding guide navigation','html_sha256':hashlib.sha256(html.encode()).hexdigest(),'signals':asdict(signals)}
    if (ROOT/'dist/robots.txt').read_text().strip()!='User-agent: *\nDisallow: /': report['errors'].append('Staging robots file mismatch')
    report['passed']=not report['errors']
    out=ROOT/'planning/ai-os/qa.json'
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'passed':report['passed'],'errors':report['errors'],'words':{l:p['main_words'] for l,p in report['pages'].items()}},indent=2))
    return report
if __name__=='__main__':
    sys.exit(0 if audit()['passed'] else 1)
