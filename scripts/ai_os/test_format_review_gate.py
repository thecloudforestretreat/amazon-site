import unittest
from format_review_gate import flags
class ObservedFailures(unittest.TestCase):
 def test_invented_services_and_times_are_flagged(self):
  self.assertEqual(set(flags({'intro':'A flight to Tena takes 6 to 8 hours.'})),{'invented_transport','unsupported_timing'})
 def test_bilingual_harmful_advice(self):
  self.assertEqual(set(flags({'en':'back to civilization','es':'probar la temperatura del agua'})),{'colonial_framing','unsafe_river_advice'})
 def test_reviewed_question_is_not_flagged(self):
  self.assertEqual(flags({'intro':'Which transport segments are included in the written proposal?'}),[])
if __name__=='__main__':unittest.main()
