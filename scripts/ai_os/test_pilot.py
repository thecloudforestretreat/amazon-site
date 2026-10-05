import copy
import importlib.util
from pathlib import Path
import unittest
import fcntl,tempfile
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('pilot',Path(__file__).with_name('pilot.py'))
pilot=importlib.util.module_from_spec(spec);spec.loader.exec_module(pilot)

class DraftContractTests(unittest.TestCase):
    def setUp(self):
        self.job={'sections':['one'],'minimum_words':5,'maximum_words':60}
        self.data={'language':'en','quick':'A practical guide','sections':[{'heading':'Planning','paragraphs':['Ask about the transfer','Confirm the guide language']}],'faqs':[['Question','Answer'] for _ in range(5)]}
    def test_accepts_complete_plain_text(self):
        self.assertGreater(pilot.validate(self.data,'en',self.job),5)
    def test_rejects_wrong_language(self):
        with self.assertRaises(ValueError): pilot.validate(self.data,'es',self.job)
    def test_rejects_unapproved_embedded_markup(self):
        self.data['sections'][0]['paragraphs'][0]='<script>bad</script>'
        with self.assertRaises(ValueError): pilot.validate(self.data,'en',self.job)
    def test_rejects_missing_coverage(self):
        self.data['sections']=[]
        with self.assertRaises(ValueError): pilot.validate(self.data,'en',self.job)
    def test_rejects_truncated_faq(self):
        self.data['faqs']=[['Question']]
        with self.assertRaises(ValueError): pilot.validate(self.data,'en',self.job)
    def test_concurrent_worker_cannot_start(self):
        with tempfile.TemporaryDirectory() as temp:
            state=Path(temp)
            with (state/'worker.lock').open('a') as held:
                fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
                with patch.object(pilot,'STATE',state),patch.object(pilot,'_run') as worker:
                    with self.assertRaises(RuntimeError): pilot.run('cuyabeno')
                    worker.assert_not_called()

    def test_cache_key_changes_with_evidence(self):
        original={'fact':'flooded forest'}
        self.assertNotEqual(pilot.digest(original),pilot.digest({'fact':'different source'}))

if __name__=='__main__': unittest.main()
