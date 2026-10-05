"""Owner-authorized hub drafting, cached locally; never edits pages or deploys."""
import json,hashlib,time,fcntl
from format_review_gate import flags
from pathlib import Path
from urllib.request import Request,urlopen
root=Path(__file__).resolve().parents[2]
with (root/'planning/ai-os/runs/worker.lock').open('a') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 for slug,topics in [('safety-planning','named provider and guide; exact itinerary and current advice; transport responsibilities; emergency communication and response; activity equipment and personal requirements; written cancellation and change terms'),('destination-comparison','preferred wildlife experience; mainland versus island program; activity pace and constraints; total itinerary and transfer time; complete cost and exclusions; combining two destinations')]:
  prompt=f"""Return JSON en/es arrays, six objects each with heading and points (three short booking questions). Topics: {topics}. Editorial Ecuador Amazon guide. Natural Spanish tú. Ask the actual provider to confirm arrangements. No intros; no facts, seasonal calendar, forecasts, available services, promises, health/safety/legal claims or guaranteed sightings. Do not prescribe medicines, vaccines, treatments or universal gear. Do not name airlines, routes, durations or baggage limits. Never assume boots, life jackets, dry bags, power, storage, pickup or connections are included. Ask what the provider confirms for the specific booking. Never use English words in Spanish. Avoid presumed facilities or adjustments. JSON only."""

  key=hashlib.sha256(prompt.encode()).hexdigest()[:12];run=root/f'planning/ai-os/runs/{slug}/{key}';run.mkdir(parents=True,exist_ok=True)
  if (run/'draft.json').exists():print(slug,'cache hit',flush=True);continue
  attempt=run/'attempt.json';n=json.loads(attempt.read_text())['count'] if attempt.exists() else 0
  if n>=2:raise ValueError('Attempt limit reached')
  attempt.write_text(json.dumps({'count':n+1}));start=time.monotonic()
  payload={'model':'qwen3.5:9b','messages':[{'role':'user','content':prompt}],'think':False,'stream':False,'format':{'type':'object','properties':{l:{'type':'array','minItems':6,'maxItems':6,'items':{'type':'object','properties':{'heading':{'type':'string'},'points':{'type':'array','minItems':3,'maxItems':3,'items':{'type':'string'}}},'required':['heading','points'],'additionalProperties':False}} for l in ['en','es']},'required':['en','es'],'additionalProperties':False},'options':{'temperature':.15,'num_ctx':8192,'num_predict':2400}}
  with urlopen(Request('http://127.0.0.1:11434/api/chat',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'}),timeout=600) as response:r=json.load(response)
  (run/'status.json').write_text(json.dumps({'job':slug,'model':'qwen3.5:9b','status':'response_received_pending_validation','seconds':round(time.monotonic()-start,2),'prompt_eval_count':r.get('prompt_eval_count'),'eval_count':r.get('eval_count'),'cloud_worker_tokens':0,'cache_hit':False},indent=2)+'\n')
  raw=json.loads(r['message']['content']);(run/'raw.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
  for lang in ['en','es']:
   cards=raw[lang]
   assert isinstance(cards,list) and len(cards)==6
   for c in cards:assert isinstance(c.get('heading'),str) and len(c.get('points',[]))==3
  (run/'draft.json').write_text(json.dumps(raw,ensure_ascii=False,indent=2)+'\n')
  (run/'status.json').write_text(json.dumps({'job':slug,'model':'qwen3.5:9b','status':'awaiting_editorial_review','review_flags':flags(raw),'seconds':round(time.monotonic()-start,2),'prompt_eval_count':r.get('prompt_eval_count'),'eval_count':r.get('eval_count'),'cloud_worker_tokens':0,'cache_hit':False},indent=2)+'\n');print(slug,'draft saved',flush=True)
