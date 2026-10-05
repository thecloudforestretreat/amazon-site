import unittest
from format_review_gate import flags
class ObservedFailures(unittest.TestCase):
 def test_invented_services_and_times_are_flagged(self):
  self.assertEqual(set(flags({'intro':'A flight to Tena takes 6 to 8 hours.'})),{'invented_transport','unsupported_timing'})
 def test_bilingual_harmful_advice(self):
  self.assertEqual(set(flags({'en':'back to civilization','es':'probar la temperatura del agua'})),{'colonial_framing','unsafe_river_advice'})
 def test_observed_nature_failures(self):
  self.assertEqual(set(flags({"en":"Wildlife can be found at any time", "es":"Cómo enforce el guía; los salidas"})),{"unsupported_wildlife_timing","literal_spanish_failure"})
 def test_spanish_voice_regression(self):
  self.assertEqual(flags({"es":"Confirme los detalles; soliciten información."}),["spanish_voice_mismatch"])
  self.assertEqual(flags({"es":"Confirma los detalles y pide información."}),[])
 def test_decision_draft_observed_failures(self):
  self.assertEqual(set(flags({"en":"minute-by-minute schedule", "es":"camadas guiadas"})),{"literal_spanish_failure","unrealistic_specificity"})
 def test_species_gender_regression(self):
  self.assertEqual(flags({'es':'¿Son ciertas las avistamientos?'}),['literal_spanish_failure'])
  self.assertEqual(flags({'es':'Los avistamientos no están garantizados.'}),[])
 def test_reviewed_question_is_not_flagged(self):
  self.assertEqual(flags({'intro':'Which transport segments are included in the written proposal?'}),[])
if __name__=='__main__':unittest.main()
