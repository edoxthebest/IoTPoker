import logging
import unittest
import z3
from policytool import PolicyReader, Thing

logging.getLogger('IoT:Poker').setLevel(logging.DEBUG)

class TestIoTPolicy(unittest.TestCase):
  def setUp(self):
    self._id = z3.String('id')
    self.topic = z3.String('topic')
        
  def init(self, policy_file, test_con = False, test_pub = False, test_sub_rec = False,
           thing_name = None, thing_attr = None):
    policy = PolicyReader.read_policy_file(policy_file)
    connect_cons = policy.build_connect(self._id, [], thing_name, thing_attr)
    publish_cons = policy.build_publish(self.topic, self._id, [], thing_name, thing_attr)
    subscribe_cons = policy.build_subscribe(self.topic, self._id, [], thing_name, thing_attr)
    receive_cons = policy.build_receive(self.topic, self._id, [], thing_name, thing_attr)
    
    solver = z3.Solver()
    if test_con: solver.add(connect_cons)
    if test_pub: solver.add(publish_cons)
    if test_sub_rec: solver.add(z3.And(subscribe_cons, receive_cons))

    return solver
  
  def init_thing(self, test_con, test_pub, test_sub_rec):
    thing_file = 'tests/things/thing_presence_sensor_floor1.json'
    policy_file = 'tests/policies/case-study/thing_presence_sensor.json'
    self.thing: Thing = Thing.from_file(thing_file, None)
    return self.init(policy_file, test_con, test_pub, test_sub_rec,
                      self.thing.name, self.thing.attrs)
    
  def test_parse_iot_resource(self):
    policy_aws = PolicyReader.read_policy_file('tests/policies/aws-samples/unreg_cid-var.json')
    policy_issues = PolicyReader.read_policy_file('tests/policies/wildcard_issues/pub_on_2_sub_on_1.json')
    policy_flaw_2 = PolicyReader.read_policy_file('tests/policies/policy_benchmark/FLAW1/FLAW1-Error-2.json')
    policy_flaw_4 = PolicyReader.read_policy_file('tests/policies/policy_benchmark/FLAW1/FLAW1-Error-4.json')
    policy_flaw_14 = PolicyReader.read_policy_file('tests/policies/policy_benchmark/FLAW1/FLAW1-Error-14.json')

    
    self.assertCountEqual(policy_aws.connect.allow, {'clientId1', 'clientId3', 'clientId2'})
    self.assertCountEqual(policy_aws.publish.allow, {'sensor/device/${iot:ClientId}'})
    self.assertCountEqual(policy_aws.subscribe.allow, {'command/device/${iot:ClientId}'})
    self.assertCountEqual(policy_aws.receive.allow, {'command/device/${iot:ClientId}'})
    
    self.assertCountEqual(policy_issues.connect.allow, {'*'})
    self.assertCountEqual(policy_issues.publish.allow, {'${iot:ClientId}/${iot:ClientId}'})
    self.assertCountEqual(policy_issues.subscribe.allow, {'*'})
    self.assertCountEqual(policy_issues.subscribe.deny, {'A/B/C', '#', 'A/#', '+/#', '?/?/#', 'AAAAA/B?A/CC*/DDD?/EE${iot:ClientId}/??/FFF/GG'})
    self.assertCountEqual(policy_issues.receive.allow, {'*'})

    self.assertCountEqual(policy_flaw_2.connect.allow, {'*'})
    self.assertCountEqual(policy_flaw_2.publish.allow, {'*'})
    self.assertCountEqual(policy_flaw_2.subscribe.allow, {'*'})
    self.assertCountEqual(policy_flaw_2.receive.allow, {'*'})
    
    self.assertCountEqual(policy_flaw_4.connect.allow, {'*'})
    self.assertCountEqual(policy_flaw_4.publish.allow, {'$aws/things/*/shadow/*'})
    self.assertCountEqual(policy_flaw_4.subscribe.allow, {'$aws/things/*/shadow/*'})
    self.assertCountEqual(policy_flaw_4.receive.allow, {'$aws/things/*/shadow/*'})
    
    self.assertCountEqual(policy_flaw_14.connect.allow, {'*'})
    self.assertCountEqual(policy_flaw_14.publish.allow, {'iotbutton/G030MD0000000001', 'iotbutton/G030MD0000000002', 'inetbutton/all', 'inetbutton/all'})
    self.assertCountEqual(policy_flaw_14.subscribe.allow, {'$aws/things/*/shadow/update/accepted', 'iotbutton/G030MD0000000001', 'iotbutton/G030MD0000000002', 'inetbutton/all'})
    self.assertCountEqual(policy_flaw_14.receive.allow, {'$aws/things/*/shadow/update/accepted', 'iotbutton/G030MD0000000001', 'iotbutton/G030MD0000000002', 'inetbutton/all'})
    
  def test_parse_string_literals(self):
    policy_aws = PolicyReader.read_policy_file('tests/policies/aws-samples/unreg_cid-var.json')
    policy_issues = PolicyReader.read_policy_file('tests/policies/wildcard_issues/pub_on_2_sub_on_1.json')
    policy_flaw_2 = PolicyReader.read_policy_file('tests/policies/policy_benchmark/FLAW1/FLAW1-Error-2.json')
    policy_flaw_4 = PolicyReader.read_policy_file('tests/policies/policy_benchmark/FLAW1/FLAW1-Error-4.json')

    self.assertCountEqual(policy_aws.strings, {'sensor', 'command', 'device'})
    self.assertCountEqual(policy_issues.strings, {'AAAAA', 'FFF', 'GG'})
    self.assertCountEqual(policy_flaw_2.strings, {})
    self.assertCountEqual(policy_flaw_4.strings, {'$aws', 'things', 'shadow'})
    
    self.assertCountEqual(policy_issues.danger_strings, {'B', 'A','CC', 'DDD', 'EE'})
    
    self.assertCountEqual(policy_aws.strings, policy_aws.safe_strings)
    self.assertCountEqual(policy_issues.safe_strings, {'FFF'})
    self.assertCountEqual(policy_flaw_2.strings, policy_flaw_2.safe_strings)
    self.assertCountEqual(policy_flaw_4.strings, policy_flaw_4.safe_strings)
  
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
