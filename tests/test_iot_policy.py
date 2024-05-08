import json
import unittest
import z3
from policytool import IoTPolicy

class TestIoTPolicy(unittest.TestCase):
  def load(self, policy_file):
    file = open(policy_file)
    self.policy = IoTPolicy(json.load(file))
    file.close()
  
  def test_build_connect(self):
    id = z3.String('id')
    self.load('tests/policies/aws-samples/unreg_connect.json')
    connect_cons = self.policy.build_connect(id)
    
    solver = z3.Solver()
    solver.add(connect_cons)
    
    self.assertEqual(solver.check(), z3.sat)
    self.assertEqual(solver.model()[id], 'client1')
    
  def test_build_publish(self):
    id = z3.String('id')
    topic = z3.String('topic')
    self.load('tests/policies/aws-samples/unreg_sub-pub-topic.json')
    connect_cons = self.policy.build_connect(id)
    publish_cons = self.policy.build_publish(topic, id)
    
    solver = z3.Solver()
    solver.add(connect_cons)
    solver.add(publish_cons)
    
    self.assertEqual(solver.check(), z3.sat)
    self.assertIn(solver.model()[id], ['clientId1', 'clientId2', 'clientId3'])
    self.assertEqual(solver.model()[topic], 'some_specific_topic')
    
  def test_build_sub_rec(self):
    id = z3.String('id')
    topic = z3.String('topic')
    self.load('tests/policies/aws-samples/unreg_sub-pub-topic.json')
    connect_cons = self.policy.build_connect(id)
    subscribe_cons = self.policy.build_subscribe(topic, id)
    receive_cons = self.policy.build_receive(topic, id)
    
    solver = z3.Solver()
    solver.add(connect_cons)
    solver.add(z3.And(subscribe_cons, receive_cons))
    
    self.assertEqual(solver.check(), z3.sat)
    self.assertIn(solver.model()[id], ['clientId1', 'clientId2', 'clientId3'])
    self.assertEqual(solver.model()[topic], 'some_specific_topic')
    
  def test_deny_pub(self):
    id = z3.String('id')
    topic = z3.String('topic')
    self.load('tests/policies/aws-samples/unreg_deny-pub.json')
    connect_cons = self.policy.build_connect(id)
    publish_cons = self.policy.build_publish(topic, id)
    
    solver = z3.Solver()
    solver.add(connect_cons)
    solver.add(publish_cons)
    
    self.assertEqual(solver.check(), z3.sat)
    self.assertIn(solver.model()[id], ['clientId1', 'clientId2', 'clientId3'])
    self.assertNotEqual(solver.model()[topic], 2)
    self.assertEqual(solver.model()[topic][0], 'a')
