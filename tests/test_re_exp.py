import unittest
import z3
from policytool import ReExp
from policytool import Thing

#TODO: add test descrp

class TestReExp(unittest.TestCase):
  def test_re_expr(self):
    id = z3.String('id')
    
    solver = z3.Solver()
    solver.add(z3.InRe(id, ReExp.RE_EMPTY))
    self.assertEqual(solver.check(), z3.unsat)
    
    solver = z3.Solver()
    solver.add(z3.InRe(id, ReExp.RE_QMARK))
    solver.add(z3.InRe(id, z3.Re('?')))
    self.assertEqual(solver.check(), z3.unsat)

    solver = z3.Solver()
    solver.add(z3.InRe(id, ReExp.RE_PLUS))
    solver.add(z3.InRe(id, z3.Re('/')))
    self.assertEqual(solver.check(), z3.unsat)
    
  
  def test_parse_qmark(self):
    arn = 'arn:aws:iot:us-east-1:123456789012:client/test?'
    re_parsed = ReExp.parse(arn, None)
    re_expected = z3.Concat(z3.Re('test'), ReExp.RE_QMARK)
    self.assertEqual(re_parsed, re_expected)
    
  def test_parse_star(self):
    arn = 'arn:aws:iot:us-east-1:123456789012:topic/topic/*/status'
    re_parsed = ReExp.parse(arn, None)
    re_expected = z3.Concat(z3.Re('topic/'), 
                            ReExp.RE_STAR,
                            z3.Re('/status'))
    self.assertEqual(re_parsed, re_expected)
      
  def test_parse_plus(self):
    arn = 'arn:aws:iot:us-east-1:123456789012:topicfilter/+/temp'
    re_parsed = ReExp.parse(arn, None)
    re_expected = z3.Concat(ReExp.RE_PLUS, z3.Re('/temp'))
    self.assertEqual(re_parsed, re_expected)
      
  def test_parse_hash(self):
    arn = 'arn:aws:iot:us-east-1:123456789012:topicfilter/#'
    re_parsed = ReExp.parse(arn, None)
    re_expected = ReExp.RE_HASH
    self.assertEqual(re_parsed, re_expected)

  def test_parse_client_id(self):
    arn = 'arn:aws:iot:us-east-1:123456789012:client/Client/${iot:ClientId}'
    re_parsed = ReExp.parse(arn, 'test')
    re_expected = z3.Concat(z3.Re('Client/'), z3.Re('test'))
    self.assertEqual(re_parsed, re_expected)
    
  def test_parse_thing(self):
    res = ('client/${iot:Connection.Thing.ThingName}/'
           'floor${iot:Connection.Thing.Attributes[floor]}/'
           'some_other_attr/${iot:Connection.Thing.Attributes[other]}'
          )
    test_thing = Thing('testT', None, None, {'floor':'1', 'other':'test_value'}, None)
    parsed_res = ReExp.parse_thing(res, test_thing.name, test_thing.attrs)
    self.assertEqual(parsed_res, 'client/testT/floor1/some_other_attr/test_value')

  def test_parse_thing_name(self):
    arn = 'arn:aws:iot:us-east-1:123456789012:client/${iot:Connection.Thing.ThingName}'
    thing_file = 'tests/things/thing_presence_sensor_floor1.json'
    thing: Thing = Thing.from_file(thing_file, None)
    
    re_parsed = ReExp.parse(arn, 'test', thing.name, thing.attrs)
    re_expected = z3.Re('presenceSensor1')
    self.assertEqual(re_parsed, re_expected)
    
  def test_parse_thing_attrs(self):
    arn = 'topic/physicalAC/floor${iot:Connection.Thing.Attributes[floor]}/${iot:ClientId}/enable'
    thing_file = 'tests/things/thing_presence_sensor_floor1.json'
    thing: Thing = Thing.from_file(thing_file, None)
    
    re_parsed = ReExp.parse(arn, 'testT', thing.name, thing.attrs)
    re_expected = z3.Concat(z3.Re('physicalAC/floor1/'), z3.Re('testT'), z3.Re('/enable'))
    self.assertEqual(re_parsed, re_expected)

  # TODO: Does not handle possible mqtt wildcards in the client id
