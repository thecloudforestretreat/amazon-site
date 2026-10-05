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
 def test_blog_heading_regression(self):
  self.assertEqual(flags({'es':'Compare Dura del Viaje'}),['literal_spanish_failure'])
  self.assertEqual(flags({'es':'Compara la duración del viaje'}),[])
 def test_observed_three_day_night_error(self):
  self.assertEqual(flags({'en':'Does the price cover all three nights of accommodation?'}),['day_night_confusion'])
  self.assertEqual(flags({'es':'¿El precio cubre las tres noches de alojamiento?'}),['day_night_confusion'])
  self.assertEqual(flags({'en':'How many nights are included?'}),[])
 def test_unguided_observation_assumption(self):
  self.assertEqual(flags({'en':'quiet periods for observation without a guide present'}),['unguided_observation_assumption'])
  self.assertEqual(flags({'es':'observación sin guía presente'}),['unguided_observation_assumption'])
  self.assertEqual(flags({'en':'Follow the guide’s access instructions.'}),[])
 def test_sighting_guarantee_request(self):
  self.assertEqual(flags({'en':'Do you provide any guarantees regarding wildlife sightings?'}),['sighting_guarantee_request'])
  self.assertEqual(flags({'es':'¿Proporcionan alguna garantía sobre los avistamientos?'}),['sighting_guarantee_request'])
  self.assertEqual(flags({'en':'Sightings are not guaranteed.'}),[])
 def test_reviewed_question_is_not_flagged(self):
  self.assertEqual(flags({'intro':'Which transport segments are included in the written proposal?'}),[])
if __name__=='__main__':unittest.main()
