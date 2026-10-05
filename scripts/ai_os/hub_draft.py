"""Owner-authorized hub drafting, cached locally; never edits pages or deploys."""
import json,hashlib,time,fcntl
from pathlib import Path
from urllib.request import Request,urlopen
root=Path(__file__).resolve().parents[2]
lock=(root/'planning/ai-os/runs/worker.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
for slug,topics in [('ecuador-hub','Pick your route; count full days; pace for a mixed group; respect hosts; check changing conditions; prepare a focused inquiry'),('lodge-hub','Location before room photos; compare two written quotes; align guide and group; family and mobility questions; daily activity rhythm; booking changes and contingency')]:
 prompt=f'''Write useful bilingual planning cards for an Ecuador Amazon {slug}. JSON only, keys en,es; each exactly six objects with heading, intro (35-45 words), points (three 12-18-word bullets). Topics in order: {topics}. Use inviting, simple English and idiomatic Spanish with tu voice. Sources already reviewed: Cuyabeno is a reserve with river/canoe trips; Yasuni/Napo properties need exact location checks, not every lodge is inside the national park; Tena/Misahualli road-access Napo bases, final transfers vary; Puyo is Pastaza city/gateway with road connection toward Banos and botanical/hosted visits. Host visits require invitation. These cards are editorial comparison advice, not verified products. No specific lodge brands, prices, schedules, exact distances, seasonal predictions, medical guidance, rules, permits, species promises, superlatives or assumed facilities. Do not claim guides or longer trips guarantee wildlife. Give concrete booking decision questions. Never assume communities welcome visitors, describe ceremonies, recommend gifts, discuss medicinal uses, or promise safety. No exoticizing metaphors. Do not prescribe a minimum trip duration or claim a particular time of day is best for wildlife. Avoid repeating generic disclaimers. Output only 6 cards per language, no FAQ, no HTML.'''
 key=hashlib.sha256(prompt.encode()).hexdigest()[:12];run=root/f'planning/ai-os/runs/{slug}/{key}';run.mkdir(parents=True,exist_ok=True)
 if (run/'draft.json').exists():print(slug,'cache hit',flush=True);continue
 attempt=run/'attempt.json';n=json.loads(attempt.read_text())['count'] if attempt.exists() else 0
 if n>=2:raise ValueError('Attempt limit reached')
 attempt.write_text(json.dumps({'count':n+1}));start=time.monotonic()
 payload={'model':'qwen3.5:9b','messages':[{'role':'user','content':prompt}],'think':False,'stream':False,'format':'json','options':{'temperature':.15,'num_ctx':8192,'num_predict':5500}}
 with urlopen(Request('http://127.0.0.1:11434/api/chat',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'}),timeout=600) as response:r=json.load(response)
 raw=json.loads(r['message']['content']);(run/'raw.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
 for lang in ['en','es']:
  cards=raw[lang]
  assert isinstance(cards,list) and len(cards)==6
  for c in cards:assert isinstance(c.get('heading'),str) and isinstance(c.get('intro'),str) and len(c.get('points',[]))==3
 (run/'draft.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
 (run/'status.json').write_text(json.dumps({'job':slug,'model':'qwen3.5:9b','status':'awaiting_editorial_review','seconds':round(time.monotonic()-start,2),'prompt_eval_count':r.get('prompt_eval_count'),'eval_count':r.get('eval_count'),'cloud_worker_tokens':0,'cache_hit':False},indent=2)+'\n');print(slug,'draft saved',flush=True)
