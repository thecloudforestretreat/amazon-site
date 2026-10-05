import json,unittest
from pathlib import Path
from draft_schema import normalize_draft
class DraftShapeTests(unittest.TestCase):
    def setUp(self):
        self.raw=json.loads(next(Path('planning/ai-os/runs/misahualli').glob('*/draft.json')).read_text())
    def test_object_faq_and_alternate_context_are_normalized_without_mutating_raw(self):
        normalized=normalize_draft(self.raw)
        self.assertEqual(normalized['en']['faqs'][0],[self.raw['en']['faqs'][0]['question'],self.raw['en']['faqs'][0]['answer']])
        self.assertEqual(normalized['es']['sections'][0]['paragraphs'][0],self.raw['es']['sections'][0]['intro'])
        self.assertNotIn('paragraphs',self.raw['en']['sections'][0])
    def test_missing_context_is_rejected(self):
        self.raw['es']['sections'][0].pop('practical_context')
        with self.assertRaises(ValueError):normalize_draft(self.raw)
    def test_empty_faq_is_rejected(self):
        self.raw['en']['faqs'][0]['answer']=''
        with self.assertRaises(ValueError):normalize_draft(self.raw)
if __name__=='__main__':unittest.main()
