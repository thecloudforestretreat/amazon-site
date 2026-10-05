import hashlib,importlib.util,json,tempfile
from pathlib import Path
from unittest.mock import patch
import unittest
spec=importlib.util.spec_from_file_location('promote',Path(__file__).with_name('promote.py'))
promote=importlib.util.module_from_spec(spec);spec.loader.exec_module(promote)

class PromotionSafetyTests(unittest.TestCase):
    def package(self,root):
        run=root/'planning/ai-os/runs/cuyabeno/test';run.mkdir(parents=True)
        source=root/'src/data/ecuador-destinations.json';source.parent.mkdir(parents=True)
        source.write_text(json.dumps([{'slug':'cuyabeno','en':{},'es':{}}]))
        hashes={}
        for language in ['en','es']:
            p=run/f'{language}-reviewed.json'
            p.write_text(json.dumps({'language':language,'quick':'Summary','sections':[{'heading':'Heading','paragraphs':['Text','More text']} for _ in range(10)],'faqs':[['Question','Answer']]}))
            hashes[language]=hashlib.sha256(p.read_bytes()).hexdigest()
        (run/'editorial-review.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reviewed_sha256':hashes}))
        return run,source
    def test_changed_output_never_changes_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);run,source=self.package(root);before=source.read_bytes()
            (run/'es-reviewed.json').write_text('{}')
            with patch.object(promote,'ROOT',root),self.assertRaisesRegex(ValueError,'Reviewed output changed'): promote.promote(run)
            self.assertEqual(source.read_bytes(),before)
    def test_stale_source_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);run,source=self.package(root);source.write_text('[]')
            with patch.object(promote,'ROOT',root),self.assertRaisesRegex(ValueError,'Source changed'): promote.promote(run)
            self.assertEqual(source.read_text(),'[]')
    def test_both_languages_are_applied_together(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);run,source=self.package(root)
            with patch.object(promote,'ROOT',root): promote.promote(run)
            destination=json.loads(source.read_text())[0]
            self.assertEqual(destination['en']['quick'],'Summary')
            self.assertEqual(destination['es']['quick'],'Summary')
if __name__=='__main__':unittest.main()
