"""Translate only the reviewed English source; preserve raw model drafts."""
import hashlib,json,time,fcntl,sys
from pathlib import Path
from urllib.request import Request,urlopen
root=Path(__file__).resolve().parents[2]
run=next((root/'planning/ai-os/runs/cuyabeno').glob('*'))
worker_lock=(run.parent.parent/'worker.lock').open('a')
fcntl.flock(worker_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
review_path=run/'editorial-review.json'
if review_path.exists():
    review=json.loads(review_path.read_text())
    for language in ['en','es']:
        content=(run/f'{language}-reviewed.json').read_bytes()
        if hashlib.sha256(content).hexdigest()!=review['reviewed_sha256'][language]:
            raise ValueError('Reviewed content changed; do not overwrite it with a new translation')
    print('Reviewed pair is locked; no translation generation required')
    sys.exit(0)
source=json.loads((run/'en-reviewed.json').read_text())
key=hashlib.sha256(json.dumps(source,sort_keys=True).encode()).hexdigest()
out=run/'es-reviewed.json'
if out.exists() and (run/'translation-usage.json').exists() and json.loads((run/'translation-usage.json').read_text()).get('source_hash') == key:
    print('Translation cache hit')
else:
    prompt='Translate this reviewed English guide into clear, natural Spanish for travelers in Ecuador. Use tú consistently in the instructions. Use caminatas, senderos fangosos, acceso, guianza, equipaje and traslados, never caminatos, barrocos, portal or empaquetado. Avoid literal calques. Write as a professional Spanish travel editor. Preserve all facts, caveats, questions, paragraph counts, and section order. Do not add facts, transport claims, medical claims, guarantees or stronger conclusions. Keep the JSON shape, change language to es, translate quick, headings, paragraphs and FAQs. No HTML or links. Return JSON only. Source: '+json.dumps(source,ensure_ascii=False)
    payload={'model':'qwen3.5:27b','messages':[{'role':'user','content':prompt}],'stream':False,'think':False,'format':'json','options':{'temperature':0,'num_ctx':12288,'num_predict':8000}}
    started=time.monotonic()
    with urlopen(Request('http://127.0.0.1:11434/api/chat',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'}),timeout=900) as response:
        result=json.load(response)
    content=json.loads(result['message']['content'])
    assert content['language']=='es' and len(content['sections'])==10 and len(content['faqs'])==6
    out.write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    usage={k:result.get(k) for k in ['prompt_eval_count','eval_count','total_duration','done_reason']}
    usage.update({'model':'qwen3.5:27b','seconds':round(time.monotonic()-started,2),'source_hash':key})
    (run/'translation-usage.json').write_text(json.dumps(usage,indent=2)+'\n')
    print('Reviewed-source translation saved')
