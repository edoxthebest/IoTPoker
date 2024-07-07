import unittest
import z3
from policytool import Certificate, IoTPolicy, TopicWitness, PolicyReader

class TestCertificate(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    policy_dir = 'tests/policies/aws-samples'
    cls.policies = PolicyReader.read_policy_dir(policy_dir)
    cls.policy = IoTPolicy.union(cls.policies)
    cls.pol_dir = 'tests/policies/wildcard_issues/'
      
  def test_certificate(self):
    cert = Certificate(self.policies)
    
    self.assertEqual(cert.name, self.policy.client)
    self.assertEqual(cert.policy, self.policy)

    
  def test_named_certificate(self):
    cert = Certificate(self.policies, 'TestCert')
    
    self.assertEqual(cert.name, 'TestCert')
    self.assertEqual(cert.policy, self.policy)

  def test_get_access(self):
    policy_file = 'tests/policies/case-study/lambda_fire_alarm.json'
    policy = PolicyReader.read_policy_file(policy_file)
    cert = Certificate([policy], 'TestCert')
    
    id = z3.String('id')
    topic_pub = z3.String('topic_pub')
    topic_sub = z3.String('topic_sub')

    solver = z3.Solver()
    solver.add(cert.get_connect(id))
    solver.add(cert.get_publish(topic_pub, id))
    solver.add(z3.And(cert.get_subscribe(topic_sub, id),
                      cert.get_receive(topic_sub, id)))
    
    self.assertEqual(solver.check(), z3.sat)
    self.assertEqual(solver.model()[id], 'lambdaFireAlarm')
    self.assertEqual(solver.model()[topic_pub], 'fire/detected')
    self.assertEqual(solver.model()[topic_sub], 'fire/floorA/smokeLevels')

  def test_get_topic_witness_early_no_solution(self):
    pol = PolicyReader.read_policy_file(self.pol_dir + 'easy_no_solution.json')
    cert1 = Certificate([pol], 'cert_1')
    cert2 = Certificate([pol], 'cert_2')
    
    self.assertIsNone(cert1.get_topic_witness(cert2))

  
  def test_get_topic_witness_no_wildcards(self):
    pol = PolicyReader.read_policy_file(self.pol_dir + 'easy_solution.json')
    cert1 = Certificate([pol], 'cert_1')
    cert2 = Certificate([pol], 'cert_2')
    witness = cert1.get_topic_witness(cert2)
    
    self.assertIsNotNone(witness)
    self.assertIn(witness.id1, ['clientId1', 'clientId2', 'clientId3'])
    self.assertIn(witness.id2, ['clientId1', 'clientId2', 'clientId3'])
    self.assertEqual(witness.topic, witness.topic_filter)
    self.assertEqual(witness.topic, 'some_specific_topic')
  
  def test_get_topic_witness_multi_level_sub(self):
    pass
  
  # def test_get_topic_witne