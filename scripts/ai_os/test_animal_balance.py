import unittest
from audit_animal_balance import problems
class BalanceTests(unittest.TestCase):
 def photos(self,*groups):return [{'animalGroup':g} for g in groups]
 def test_balanced(self):self.assertFalse(problems(self.photos('mammal','bird','reptile')))
 def test_previous_insect_dominance(self):self.assertTrue(problems(self.photos('mammal','invertebrate','invertebrate')))
 def test_three_mammals_insufficient(self):self.assertTrue(problems(self.photos('mammal','mammal','mammal')))
 def test_unknown_requires_review(self):self.assertTrue(problems(self.photos('mammal','bird',None)))
if __name__=='__main__':unittest.main()
