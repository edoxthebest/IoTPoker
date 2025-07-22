import unittest
import cvc5.pythonic as cvc5
from policytool import PolicyReader, Certificate

class TestCvc5(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    weird_policy_seq = [40, 66]#[193, 7]#[193, 2, 150, 69, 98, 202, 173, 25, 212, 143, 41, 108, 99, 185, 108, 141, 10, 163, 7] #[162, 6] #[193, 5] #[ 193, 199, 14, 85, 112, 187, 189, 15, 79, 39, 5]
    policy_dir = 'tests/policies/policy_benchmark'
    cls.certs = []
    
    for flaw_no in weird_policy_seq:
      path = f'{policy_dir}/FLAW1/FLAW1-Error-{flaw_no}.json'
      cls.certs.append(Certificate([PolicyReader.read_policy_file(path)], flaw_no))
  
  def test_cvc5_halting(self):
    cert_0 = self.certs[0]
    for cert in self.certs:
      if cert == cert_0:
        continue
      
      print(f'Checking certificates:\t {cert_0.name}  ->  {cert.name}')
      witness, invokes = cert_0.get_topic_witness(cert)
      print(witness)
      
  # def test_slow_hard_solver(self):
    