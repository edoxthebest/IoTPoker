import unittest
import z3
from policytool import Certificate, IoTPolicy, TopicWitness, PolicyReader
from policyuniverse.policy import Policy

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
    self.assertRegex(solver.model()[topic_sub].__str__(), r'fire/floor./smokeLevels')

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
  
  def test_get_topic_witness_multi_level_wildcard(self):
    pol = PolicyReader.read_policy_file(self.pol_dir + 'can_sub_with_#_or_+.json')
    cert1 = Certificate([pol], 'cert_1')
    cert2 = Certificate([pol], 'cert_2')
    witness = cert1.get_topic_witness(cert2)
  
    self.assertIsNotNone(witness)
    self.assertIn(witness.id1, ['A', 'B', 'C'])
    self.assertIn(witness.id2, ['A', 'B', 'C'])
    self.assertEqual(witness.topic, 'A')
    self.assertIn(witness.topic_filter, ['#', '+'])

  def test_get_topic_witness_single_level_wildcard(self):
    pol = PolicyReader.read_policy_file(self.pol_dir + 'can_sub_with_+.json')
    cert1 = Certificate([pol], 'cert_1')
    cert2 = Certificate([pol], 'cert_2')
    witness = cert1.get_topic_witness(cert2)
  
    self.assertIsNotNone(witness)
    self.assertIn(witness.id1, ['A', 'B', 'C'])
    self.assertIn(witness.id2, ['A', 'B', 'C'])
    self.assertEqual(witness.topic, 'A/B/C')
    self.assertRegex(witness.topic_filter, r'[A+]/[B+]/[C+]')
    
def make_test_policy(con, pub, sub, rec):
  base_arn = 'arn:aws:iot:us-east-1:123456789012:'
  stmts = []
  
  if type(con) is tuple:
    stmts.append(dict(
      Effect='Deny',
      Action='iot:Connect',
      Resource=base_arn + 'client/' + con[1]
    ))
    con = con[0]
  stmts.append(dict(
    Effect='Allow',
    Action='iot:Connect',
    Resource=base_arn + 'client/' + con
  ))
  
  if type(pub) is tuple:
    stmts.append(dict(
      Effect='Deny',
      Action='iot:Publish',
      Resource=base_arn + 'topic/' + pub[1]
    ))
    pub = pub[0]
  stmts.append(dict(
    Effect='Allow',
    Action='iot:Publish',
    Resource=base_arn + 'topic/' + pub
  ))
  
  if type(sub) is tuple:
    stmts.append(dict(
      Effect='Deny',
      Action='iot:Subscribe',
      Resource=base_arn + 'topicfilter/' + sub[1]
    ))
    sub = sub[0]
  stmts.append(dict(
    Effect='Allow',
    Action='iot:Subscribe',
    Resource=base_arn + 'topicfilter/' + sub
  ))
  
  if type(rec) is tuple:
    stmts.append(dict(
      Effect='Deny',
      Action='iot:Receive',
      Resource=base_arn + 'topic/' + rec[1]
    ))
    rec = rec[0]
  stmts.append(dict(
    Effect='Allow',
    Action='iot:Receive',
    Resource=base_arn + 'topic/' + rec
  ))
    
  return IoTPolicy(dict(
    Version='2012-10-17',
    Statement=stmts
  ))
    

class TestGetTopicWitness(unittest.TestCase):
  def test_no_connection_loop(self):
    pol = make_test_policy('*', 'C', 'D', 'D')
    cert1 = Certificate([pol], 'cert_1')
    cert2 = Certificate([pol], 'cert_2')
    self.assertIsNone(cert1.get_topic_witness(cert2))
    
  def test_subscribe_with_multi_wild(self):
    pol = make_test_policy('A', 'C', '#', '*')
    cert1 = Certificate([pol], 'cert_1')
    cert2 = Certificate([pol], 'cert_2')
    witness = cert1.get_topic_witness(cert2)
    
    self.assertIsNotNone(witness)
    self.assertEqual(witness.id1, 'A')
    self.assertEqual(witness.id2, 'A')
    self.assertEqual(witness.topic, 'C')
    self.assertEqual(witness.topic_filter, '#')
    
  def test_no_sub_with_multi_wild(self):
    pol = make_test_policy('A', 'C', ('#', '#'), '*')
    cert1 = Certificate([pol], 'cert_1')
    cert2 = Certificate([pol], 'cert_2')
    self.assertIsNone(cert1.get_topic_witness(cert2))

  def test_topic_from_client_ids(self):
    pol1 = make_test_policy('A', '${iot:ClientId}/B', '*', '*')
    pol2 = make_test_policy('B', '*', '+/${iot:ClientId}', 'A/*')
    cert1 = Certificate([pol1], 'cert_1')
    cert2 = Certificate([pol2], 'cert_2')
    witness = cert1.get_topic_witness(cert2)
    
    self.assertIsNotNone(witness)
    self.assertEqual(witness.id1, 'A')
    self.assertEqual(witness.id2, 'B')
    self.assertEqual(witness.topic, 'A/B')
    self.assertEqual(witness.topic_filter, '+/B')

  def test_case_study_reader1_light1(self):
    pol1 = PolicyReader.read_policy_file('tests/policies/case-study/floor1_badge_reader.json')
    pol2 = PolicyReader.read_policy_file('tests/policies/case-study/light.json')
    cert1 = Certificate([pol1], 'cert_1')
    cert2 = Certificate([pol2], 'cert_2')
    self.assertIsNone(cert1.get_topic_witness(cert2))
    
if __name__ == '__main__':
    pol1 = PolicyReader.read_policy_file('tests/policies/case-study/floor1_badge_reader.json')
    pol2 = PolicyReader.read_policy_file('tests/policies/case-study/light.json')
    cert1 = Certificate([pol1], 'cert_1')
    cert2 = Certificate([pol2], 'cert_2')
    print(cert1.get_topic_witness(cert2))
