"""Regression evidence from the rejected batch-4 local drafts."""
import json,unittest
from pathlib import Path
from build_peru_editorial import validate_page
ROOT=Path(__file__).resolve().parents[2]
class PeruReviewGate(unittest.TestCase):
 def test_actual_malformed_local_drafts_are_rejected(self):
  drafts=json.loads((ROOT/'planning/ai-os/peru-batch4-local-en.json').read_text())
  for name,page in drafts.items():
   with self.subTest(draft=name),self.assertRaises(ValueError):validate_page(page)
 def test_reviewed_bilingual_checkpoint_has_complete_sections(self):
  spec=json.loads((ROOT/'planning/ai-os/peru-batch4-editorial.json').read_text())
  for topic,langs in spec['pages'].items():
   for lang,page in langs.items():
    with self.subTest(topic=topic,language=lang):validate_page(page)
if __name__=='__main__':unittest.main()
