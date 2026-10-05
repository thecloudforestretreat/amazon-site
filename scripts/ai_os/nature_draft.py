"""Owner-authorized hub drafting, cached locally; never edits pages or deploys."""
import json,hashlib,time,fcntl
from format_review_gate import flags
from pathlib import Path
from urllib.request import Request,urlopen
root=Path(__file__).resolve().parents[2]
lock=(root/'planning/ai-os/runs/worker.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
for slug,topics in [('birdwatching-format','Match guide experience to your birding level; confirm outing habitat and observation method; discuss pace and activity group; confirm equipment arrangements; choose actual observation time versus transfers; check ethical approach and complete proposal'),('wildlife-format','Define observation interests rather than a species checklist; compare actual location and habitat; clarify guiding and group; check activity effort and pacing; confirm respectful observation without baiting feeding or handling; compare written inclusions and realistic expectations')]:
 prompt=f'''Draft six bilingual Ecuador Amazon planning cards about {slug}. JSON only: en and es arrays, each exactly six objects with heading, intro (55-70 words), points (three concrete booking questions of 15-22 words). Topics in order: {topics}. Write simple English and idiomatic Spanish in tu voice. This is an editorial comparison guide, not an operating business or verified product. Use third-person provider questions, never our team, we provide, we arrange or promises. Do not name destinations, species, prices, schedules, seasons, exact distances, minimum durations, facilities or equipment as available. Do not prescribe early starts or claim a time of day is best. Ask what the actual provider can confirm. No guaranteed sightings, exclusivity, specialist availability, safety or health claims. Do not recommend playback, bait, feeding or handling wildlife. Do not invent legal rules or permissions. No communities or host visits in these cards. Focus on questions useful before booking, not generic yes/no rhetorical questions. Extra time and specialist guiding do not guarantee wildlife. Do not assume binoculars, platforms, private boats or alternative outings are supplied. Output six cards per language, no FAQ or HTML.'''
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
 (run/'status.json').write_text(json.dumps({'job':slug,'model':'qwen3.5:9b','status':'awaiting_editorial_review','review_flags':flags(raw),'seconds':round(time.monotonic()-start,2),'prompt_eval_count':r.get('prompt_eval_count'),'eval_count':r.get('eval_count'),'cloud_worker_tokens':0,'cache_hit':False},indent=2)+'\n');print(slug,'draft saved',flush=True)
