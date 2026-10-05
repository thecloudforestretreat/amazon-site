"""Atomically merge an exact reviewed pair into generated destination data."""
import hashlib,json,os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
def sha(data): return hashlib.sha256(data).hexdigest()
def promote(run):
    run=run.resolve()
    if not run.is_relative_to((ROOT/'planning/ai-os/runs').resolve()):
        raise ValueError('Review package outside the authorized workspace')
    approval=json.loads((run/'editorial-review.json').read_text())
    path=ROOT/'src/data/ecuador-destinations.json'
    if sha(path.read_bytes()) != approval['source_sha256']:
        raise ValueError('Source changed since review; refusing stale promotion')
    reviewed={}
    for language in ['en','es']:
        raw=(run/f'{language}-reviewed.json').read_bytes()
        if sha(raw)!=approval['reviewed_sha256'][language]:
            raise ValueError('Reviewed output changed; review must be repeated')
        content=json.loads(raw)
        if content['language']!=language or len(content['sections'])!=10:
            raise ValueError('Incomplete reviewed pair')
        reviewed[language]=content
    data=json.loads(path.read_text())
    d=next(x for x in data if x['slug']=='cuyabeno')
    for language,content in reviewed.items():
        for field in ['quick','sections','faqs']:
            d[language][field]=content[field]
    d['reviewedAt']='2026-10-05'
    d['imageSource']='https://unsplash.com/photos/green-trees-on-lake-during-daytime-_9UQKWOY0No'
    d['sources']=[
        {'title':'Ecuador Ministry of Tourism: Cuyabeno (2024)','url':'https://ecuador.travel/cuyabeno-eden-de-diversidad-natural/'},
        {'title':'Ecuador Ministry of Tourism: visiting Cuyabeno (2024)','url':'https://ecuador.travel/opciones-turisticas-en-cuyabeno/'}
    ]
    d['en']['lede']='Explore Cuyabeno’s seasonally flooded forest, lagoons and wildlife by canoe. Compare access, guides and lodge conditions before choosing a trip.'
    d['es']['lede']='Explora los bosques inundables, las lagunas y la fauna de Cuyabeno en canoa. Compara el acceso, la guianza y las condiciones de cada lodge antes de elegir.'
    d['en']['fit']='Canoe exploration and wildlife observation'
    d['es']['fit']='Exploración en canoa y observación de fauna'
    d['en']['title']='Cuyabeno Travel Guide | Wildlife, Lodges and Trip Planning'
    d['es']['title']='Guía de Cuyabeno | Fauna, Lodges y Planificación'
    replacement=json.dumps(data,ensure_ascii=False,indent=2)+'\n'
    temporary=path.with_suffix('.json.reviewed')
    temporary.write_text(replacement)
    os.replace(temporary,path)
    print('Promoted the reviewed English/Spanish pair atomically; no deployment performed')

if __name__=='__main__':
    promote(Path(sys.argv[1]))
