"""Regression: preserve local usage even when model field names fail validation."""
import io,json,runpy,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[2]
class WorkerFailure(unittest.TestCase):
 def test_metrics_survive_translated_keys(self):
  with tempfile.TemporaryDirectory() as temp:
   base=Path(temp);script=base/'scripts/ai_os/activity_draft.py';script.parent.mkdir(parents=True);shutil.copyfile(root/'scripts/ai_os/activity_draft.py',script);(base/'planning/ai-os/runs').mkdir(parents=True)
   malformed={lang:[{'titulo':'Ruta','puntos':['a','b','c']} for _ in range(6)] for lang in ['en','es']}
   response={'message':{'content':json.dumps(malformed)},'prompt_eval_count':7,'eval_count':99}
   def fake_open(request,timeout):
    payload=json.loads(request.data);self.assertEqual(payload['format']['required'],['en','es']);self.assertEqual(payload['format']['properties']['es']['items']['required'],['heading','points'])
    return io.BytesIO(json.dumps(response).encode())
   with patch('urllib.request.urlopen',side_effect=fake_open):
    with self.assertRaises(AssertionError):runpy.run_path(str(script),run_name='__main__')
   status=next((base/'planning/ai-os/runs').glob('*/*/status.json'));saved=json.loads(status.read_text());self.assertEqual(saved['prompt_eval_count'],7);self.assertEqual(saved['eval_count'],99);self.assertTrue((status.parent/'raw.json').exists());self.assertFalse((status.parent/'draft.json').exists())
if __name__=='__main__':unittest.main()
