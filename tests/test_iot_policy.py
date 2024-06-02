import json
import unittest
import z3
from policytool import PolicyReader, Thing

class TestIoTPolicy(unittest.TestCase):
  def setUp(self):
    self._id = z3.String('id')
    self.topic = z3.String('topic')
        
  def init(self, policy_file, test_con, test_pub, test_sub_rec,
           thing_name = None, thing_attr = None):
    policy = PolicyReader.read_policy_file(policy_file)
    connect_cons = policy.build_connect(self._id, thing_name, thing_attr)
    publish_cons = policy.build_publish(self.topic, self._id, thing_name, thing_attr)
    subscribe_cons = policy.build_subscribe(self.topic, self._id, thing_name, thing_attr)
    receive_cons = policy.build_receive(self.topic, self._id, thing_name, thing_attr)
    
    solver = z3.Solver()
    if test_con: solver.add(connect_cons)
    if test_pub: solver.add(publish_cons)
    if test_sub_rec: solver.add(z3.And(subscribe_cons, receive_cons))

    return solver
  
  def init_thing(self, test_con, test_pub, test_sub_rec):
    thing_file = 'tests/things/thing_presence_sensor_floor1.json'
    self.thing: Thing = Thing.from_file(thing_file, None)
    return self.init('tests/policies/case-study/thing_presence_sensor.json', 
                      test_con, test_pub, test_sub_rec,
                      self.thing.name, self.thing.attrs)
  
  def test_build_connect(self):
    solver = self.init('tests/policies/aws-samples/unreg_connect.json', True, False, False)
    
    self.assertEqual(solver.check(), z3.sat)
    self.assertEqual(solver.model()[self._id], 'client1')
    
  def test_build_publish(self):
    solver = self.init('tests/policies/aws-samples/unreg_sub-pub-topic.json', True, True, False)
        
    self.assertEqual(solver.check(), z3.sat)
    self.assertIn(solver.model()[self._id], ['clientId1', 'clientId2', 'clientId3'])
    self.assertEqual(solver.model()[self.topic], 'some_specific_topic')
    
  def test_build_sub_rec(self):
    solver = self.init('tests/policies/aws-samples/unreg_sub-pub-topic.json', True, False, True)
        
    self.assertEqual(solver.check(), z3.sat)
    self.assertIn(solver.model()[self._id], ['clientId1', 'clientId2', 'clientId3'])
    self.assertEqual(solver.model()[self.topic], 'some_specific_topic')
    
  def test_deny_pub(self):
    solver = self.init('tests/policies/aws-samples/unreg_deny-pub.json', True, True, False)
      
    self.assertEqual(solver.check(), z3.sat)
    self.assertIn(solver.model()[self._id], ['a', 'b', 'c'])
    self.assertEqual(solver.model()[self.topic], 'c')
    
  def test_deny_sub_rec(self):
    solver = self.init('tests/policies/aws-samples/unreg_deny-sub.json', False, False, True)
    re_star = z3.Star(z3.AllChar(z3.ReSort(z3.StringSort())))
    solver.add(z3.InRe(self.topic, z3.Concat(re_star, z3.Re('admin'))))
    
    self.assertEqual(solver.check(), z3.sat)
    self.assertEqual(solver.model()[self.topic], 'admin')
    
    solver.add(z3.InRe(self.topic, z3.Re('restricted/admin')))
    self.assertEqual(solver.check(), z3.unsat)

  def test_multi_statement(self):
    solver = self.init('tests/policies/aws-samples/unreg_multi-stmt.json', True, True, True)
    solver.add(z3.InRe(self._id, z3.Re('client1')))
    solver.add(z3.InRe(self.topic, z3.Re('testTopic')))
    
    self.assertEqual(solver.check(), z3.sat)
    self.assertEqual(solver.model()[self._id], 'client1')
    self.assertEqual(solver.model()[self.topic], 'testTopic')

  def test_build_connect_thing(self):
    solver = self.init_thing(True, False, False)

    self.assertEqual(solver.check(), z3.sat)
    self.assertEqual(solver.model()[self._id], self.thing.name)

  def test_build_publish_thing(self):
    solver = self.init_thing(True, True, False)
    floor = self.thing.attrs['floor']
    
    self.assertEqual(solver.check(), z3.sat)
    self.assertEqual(solver.model()[self._id], self.thing.name)
    self.assertEqual(solver.model()[self.topic], 
      f'physicalAC/floor{floor}/detectedMovement/light{floor}')
    
  def test_build_sub_rec_thing(self):
    solver = self.init_thing(True, False, True)
    floor = self.thing.attrs['floor']
    
    self.assertEqual(solver.check(), z3.sat)
    self.assertEqual(solver.model()[self._id], self.thing.name)
    self.assertEqual(solver.model()[self.topic], 
      f'physicalAC/floor{floor}/{self.thing.name}/enable')


#TODO: check later
  def test_valid_client(self):
    pass
  
  def test_no_client(self):
    pass
  
  def test_policy_union(self):
    pass
