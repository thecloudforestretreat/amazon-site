import unittest,json,tempfile
from pathlib import Path
from unittest.mock import patch
from datetime import datetime,timezone
import check_advice as m
class TestAdvice(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'planning/ai-os/evidence').mkdir(parents=True);self.p=self.root/'planning/ai-os/advice-monitor.json';self.body='<div class="gem-c-govspeak"><p>'+('Regional advice. '*25)+'</p></div>';self.rootpatch=patch.object(m,'ROOT',self.root);self.rootpatch.start()
 def tearDown(self):self.rootpatch.stop();self.tmp.cleanup()
 def response(self,raw):
  class R:
   def __enter__(self):return self
   def __exit__(self,*a):pass
   def read(self):return raw.encode()
  return R()
 def test_ignore_chrome(self):self.assertEqual(m.extract('<nav>noise</nav>'+self.body),m.extract('<nav>new noise</nav>'+self.body))
 def test_reject_missing_advice(self):
  with self.assertRaises(ValueError):m.extract('<div>not advice</div>')
 def test_failed_fetch_keeps_success(self):
  old={'sources':{'regional-risks':{'last_successful_check':'2026-01-01T00:00:00+00:00','content_sha256':'old'}}};self.p.write_text(json.dumps(old))
  with patch.object(m,'urlopen',side_effect=OSError('offline')):self.assertEqual(m.main(),1)
  self.assertEqual(json.loads(self.p.read_text())['sources']['regional-risks']['last_successful_check'],'2026-01-01T00:00:00+00:00')
 def test_change_requires_review(self):
  self.p.write_text(json.dumps({'sources':{'regional-risks':{'content_sha256':'old'}},'published_review_date':'2026-01-01'}))
  with patch.object(m,'urlopen',return_value=self.response(self.body)):self.assertEqual(m.main(),0)
  state=json.loads(self.p.read_text());self.assertTrue(state['sources']['regional-risks']['review_required']);self.assertEqual(state['published_review_date'],'2026-01-01')
 def test_daily_cache(self):
  now=datetime.now(timezone.utc).isoformat();self.p.write_text(json.dumps({'sources':{s:{'last_successful_check':now} for s in ['regional-risks','safety-and-security']}}))
  with patch.object(m,'urlopen') as f:m.main();f.assert_not_called()
if __name__=='__main__':unittest.main()
