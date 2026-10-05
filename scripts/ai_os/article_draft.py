"""Owner-authorized hub drafting, cached locally; never edits pages or deploys."""
import json,hashlib,time,fcntl
from format_review_gate import flags
from pathlib import Path
from urllib.request import Request,urlopen
root=Path(__file__).resolve().parents[2]
with (root/'planning/ai-os/runs/worker.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 for slug,topics in [('lodge-choice-article','choose precise setting; compare room arrangements; assess guiding and wildlife interests; compare everyday comfort; evaluate community ownership claims; compare complete written proposals'),('stay-length-article','count arrival and departure periods; assess a three-day stay; assess a four-day stay; assess a five-day stay; match pace and priorities; fit onward travel')]:
  prompt=f"""Return JSON en/es arrays, six objects each with heading, intro (an original 110-140 word practical explanatory paragraph) and points (three short questions a traveller should ask the actual operator). Topics: {topics}. Editorial Ecuador Amazon guide. Natural Spanish tú. Address each question to the actual operator, not to the traveller. Do not ask travellers their preferences; ask what the operator confirms. Use neutral plural or tú consistently in Spanish. No factual assertions about specific operators; no facts, seasonal calendar, forecasts, available services, promises, health/safety/legal claims or guaranteed sightings. Do not prescribe medicines, vaccines, treatments or universal gear. Do not name airlines, routes, durations or baggage limits. Never assume boots, life jackets, dry bags, power, storage, pickup or connections are included. Ask what the provider confirms for the specific booking. Never use English words in Spanish. Avoid presumed facilities or adjustments. JSON only."""

  key=hashlib.sha256(prompt.encode()).hexdigest()[:12];run=root/f'planning/ai-os/runs/{slug}/{key}';run.mkdir(parents=True,exist_ok=True)
  if (run/'draft.json').exists():print(slug,'cache hit',flush=True);continue
  attempt=run/'attempt.json';n=json.loads(attempt.read_text())['count'] if attempt.exists() else 0
  if n>=2:raise ValueError('Attempt limit reached')
  attempt.write_text(json.dumps({'count':n+1}));start=time.monotonic()
  payload={'model':'qwen3.5:9b','messages':[{'role':'user','content':prompt}],'think':False,'stream':False,'format':{'type':'object','properties':{l:{'type':'array','minItems':6,'maxItems':6,'items':{'type':'object','properties':{'heading':{'type':'string'},'intro':{'type':'string'},'points':{'type':'array','minItems':3,'maxItems':3,'items':{'type':'string'}}},'required':['heading','intro','points'],'additionalProperties':False}} for l in ['en','es']},'required':['en','es'],'additionalProperties':False},'options':{'temperature':.15,'num_ctx':8192,'num_predict':6500}}
  with urlopen(Request('http://127.0.0.1:11434/api/chat',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'}),timeout=600) as response:r=json.load(response)
  (run/'status.json').write_text(json.dumps({'job':slug,'model':'qwen3.5:9b','status':'response_received_pending_validation','seconds':round(time.monotonic()-start,2),'prompt_eval_count':r.get('prompt_eval_count'),'eval_count':r.get('eval_count'),'cloud_worker_tokens':0,'cache_hit':False},indent=2)+'\n')
  raw=json.loads(r['message']['content']);(run/'raw.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
  for lang in ['en','es']:
   cards=raw[lang]
   assert isinstance(cards,list) and len(cards)==6
   for c in cards:assert isinstance(c.get('heading'),str) and len(c.get('points',[]))==3
  (run/'draft.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
  (run/'status.json').write_text(json.dumps({'job':slug,'model':'qwen3.5:9b','status':'awaiting_editorial_review','review_flags':flags(raw),'seconds':round(time.monotonic()-start,2),'prompt_eval_count':r.get('prompt_eval_count'),'eval_count':r.get('eval_count'),'cloud_worker_tokens':0,'cache_hit':False},indent=2)+'\n');print(slug,'draft saved',flush=True)
