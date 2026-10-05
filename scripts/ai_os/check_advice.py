"""Fetch official advice at most daily; changed content awaits editorial review."""
from pathlib import Path
from datetime import datetime,timezone,timedelta
from urllib.request import Request,urlopen
from html.parser import HTMLParser
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[2]
class AdviceText(HTMLParser):
 def __init__(self):super().__init__();self.depth=0;self.parts=[];self.skip=0
 def handle_starttag(self,t,a):
  attrs=dict(a)
  if not self.depth and t=='div' and 'gem-c-govspeak' in attrs.get('class',''):self.depth=1
  elif self.depth:self.depth+=1 if t not in ['br','hr','img','input','meta','link'] else 0
  if self.depth and t in ['script','style']:self.skip+=1
 def handle_endtag(self,t):
  if t in ['script','style'] and self.skip:self.skip-=1
  if self.depth:self.depth-=1
 def handle_data(self,s):
  if self.depth and not self.skip:self.parts.append(s)
 def text(self):return re.sub(r'\s+',' ',' '.join(self.parts)).strip()
def extract(raw):
 p=AdviceText();p.feed(raw);text=p.text()
 if len(text)<200:raise ValueError('Official advice body missing or too short')
 return text

def main():
 path=ROOT/'planning/ai-os/advice-monitor.json';state=json.loads(path.read_text()) if path.exists() else {'sources':{},'published_review_date':'2026-10-05'}
 now=datetime.now(timezone.utc);results=[]
 for slug in ['regional-risks','safety-and-security']:
  old=state['sources'].get(slug,{})
  if old.get('last_successful_check') and now-datetime.fromisoformat(old['last_successful_check'])<timedelta(hours=24):results.append({'source':slug,'status':'not_due'});continue
  url='https://www.gov.uk/foreign-travel-advice/ecuador/'+slug
  try:
   with urlopen(Request(url,headers={'User-Agent':'AmazonStagingAdviceMonitor/1.0'}),timeout=30) as r:raw=r.read().decode()
   text=extract(raw);digest=hashlib.sha256(text.encode()).hexdigest();changed=bool(old.get('content_sha256') and old['content_sha256']!=digest)
   snapshot='planning/ai-os/evidence/advice-'+slug+'-'+digest[:12]+'.txt';(ROOT/snapshot).write_text(text+'\n')
   state['sources'][slug]={**old,'url':url,'last_successful_check':now.isoformat(),'content_sha256':digest,'snapshot':snapshot,'review_required':changed or old.get('review_required',False)}
   results.append({'source':slug,'status':'changed_review_required' if changed else 'baseline_saved' if not old else 'unchanged'})
  except Exception as e:
   state['sources'][slug]={**old,'url':url,'last_failed_check':now.isoformat(),'last_error':str(e)};results.append({'source':slug,'status':'fetch_failed'})
 state['check_interval_hours']=24;state['publication_policy']='Reviewed bilingual copy only; successful fetch does not change published review date';path.write_text(json.dumps(state,indent=2)+'\n');print(json.dumps(results));return int(any(x['status']=='fetch_failed' for x in results))
if __name__=='__main__':raise SystemExit(main())
