"""Checkpointed, local-only destination drafting adapter for AI-OS.
No automatic publication or modification of AI-OS configuration.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / 'planning/ai-os/runs'

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def validate(data, language, job):
    if not isinstance(data, dict) or data.get('language') != language:
        raise ValueError('Missing or incorrect language')
    sections = data.get('sections', [])
    if len(sections) != len(job['sections']):
        raise ValueError('Incomplete section coverage')
    for section in sections:
        if not isinstance(section.get('heading'), str) or len(section.get('paragraphs', [])) < 2:
            raise ValueError('Incomplete section')
        if any(not isinstance(p, str) or '<' in p or 'http' in p for p in section['paragraphs']):
            raise ValueError('Only plain text is accepted')
    faqs = data.get('faqs', [])
    if len(faqs) < 5 or any(len(faq) != 2 or not all(isinstance(x, str) for x in faq) for faq in faqs):
        raise ValueError('FAQ shape is invalid')
    words = len(re.findall(r'\S+', ' '.join([data.get('quick', '')] + [p for s in sections for p in s['paragraphs']] + [t for f in faqs for t in f])))
    if words < job['minimum_words'] or words > job['maximum_words']:
        raise ValueError(f'Word count {words} outside editorial band')
    return words

def _run(slug):
    if not re.fullmatch('[a-z][a-z-]*', slug):
        raise ValueError('Invalid slug')
    job = json.loads((ROOT / f'planning/ai-os/jobs/{slug}.json').read_text())
    evidence = json.loads((ROOT / f'planning/ai-os/evidence/{slug}.json').read_text())
    # This is an installed local model override for this pilot, not a global change.
    model = job['model']
    request_key = digest({'job':job, 'evidence':evidence, 'version':1})
    directory = STATE / slug / request_key[:12]
    directory.mkdir(parents=True, exist_ok=True)
    report = {'job':slug, 'request_hash':request_key, 'model':model, 'provider':'ollama', 'cloud_worker_tokens':0, 'status':'drafting', 'languages':{}}
    report_path = directory / 'status.json'
    report_path.write_text(json.dumps(report, indent=2))
    for language in job['languages']:
        output = directory / f'{language}.json'
        metrics = directory / f'{language}-usage.json'
        if output.exists() and metrics.exists():
            draft = json.loads(output.read_text())
            if json.loads(metrics.read_text()).get('output_sha256') != digest(draft):
                raise ValueError('Cached draft integrity mismatch; supervisor review required')
            report['languages'][language] = {**json.loads(metrics.read_text()), 'words':validate(draft, language, job), 'cache_hit':True}
            continue
        schema = {'language':language,'quick':'80-word summary','sections':[{'heading':'Language-appropriate heading','paragraphs':['Paragraph','Paragraph']}], 'faqs':[['Question','Answer']]}
        prompt = f'''Write an original practical Cuyabeno destination guide in {'English' if language == 'en' else 'idiomatic Spanish'}. Return a JSON object only. Shape: {json.dumps(schema)}.
Exactly ten sections, in this order: {json.dumps(job['sections'])}.
Each section must have two substantial paragraphs, 130-155 words TOTAL per section. Quick answer 80-100 words. Six FAQ answers, 35-55 words each. Target 1750-2050 words total, excluding JSON syntax. No HTML, links or markdown. Each section must contain distinct useful decisions, not repetition. Use English/Spanish headings appropriate to output language. Use accents correctly.
Evidence and boundaries: {json.dumps(evidence, ensure_ascii=False)}.
Do not invent statistics, flight schedules, transfer durations, medical requirements, prices, endorsements or first-hand experience. Do not rank safety or imply official safety clearance. For health say to review current official guidance and consult a travel-health professional; no treatment or vaccination recommendations. For swimming say availability depends on operator instructions and local conditions, never a general recommendation. Do not promise dolphin sightings. Treat 3/4/5-day comparisons as suggested planning trade-offs, not actual package offers. Differentiate arrival and departure days from full activity days. Describe boat boarding and muddy trails honestly, ask for individual accessibility information. Discuss host-led community visits and permission for photography without promoting rituals. Cost comparisons require inclusions, not prices. No superlatives or luxury promises. Avoid the unsupported assumption that Cuyabeno always costs less than Yasuni. Ask travelers to verify lodge and operator arrangements. End with six useful FAQs, not a separate sales section.'''
        payload = {'model':model, 'messages':[{'role':'user','content':prompt}], 'stream':False,'think':False,'format':'json','keep_alive':'10m','options':{'temperature':0.2,'num_ctx':8192,'num_predict':6500}}
        attempts_file = directory / f'{language}-attempts.json'
        attempts = json.loads(attempts_file.read_text()) if attempts_file.exists() else {'count':0}
        if attempts['count'] >= 2:
            raise ValueError('Two generation attempts exhausted; supervisor review required')
        attempts['count'] += 1
        attempts_file.write_text(json.dumps(attempts))
        started = time.monotonic()
        req = Request('http://127.0.0.1:11434/api/chat', data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        try:
            with urlopen(req, timeout=900) as response:
                result = json.load(response)
            draft = json.loads(result['message']['content'])
            output.write_text(json.dumps(draft,ensure_ascii=False,indent=2)+'\n')
            usage = {k:result.get(k) for k in ['prompt_eval_count','eval_count','total_duration','load_duration','done_reason']}
            usage.update({'seconds':round(time.monotonic()-started,2),'output_sha256':digest(draft),'cache_hit':False})
            metrics.write_text(json.dumps(usage,indent=2)+'\n')
            report['languages'][language] = {**usage,'words':validate(draft, language, job)}
            report_path.write_text(json.dumps(report,indent=2)+'\n')
            print(f'{language}: {report["languages"][language]["words"]} words; local usage saved',flush=True)
        except Exception as error:
            report['status']='needs_review'
            report['error']=str(error)
            report_path.write_text(json.dumps(report,indent=2)+'\n')
            raise
    report['status']='awaiting_editorial_review'
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    print(directory)

def run(slug):
    STATE.mkdir(parents=True, exist_ok=True)
    with (STATE / 'worker.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError('A local Amazon worker is already running')
        try:
            _run(slug)
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('slug')
    run(parser.parse_args().slug)
