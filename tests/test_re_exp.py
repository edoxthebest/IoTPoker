import unittest
import z3
from policytool import ReExp
from policytool import Thing
from policytool import IoT

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
  
  def test_parse_qmark(self):
    res = 'test?'
    re_parsed = ReExp.parse(res)
    re_expected = z3.Concat(z3.Re('test'), ReExp.RE_QMARK)
    self.assertEqual(re_parsed, re_expected)
    
  def test_parse_star(self):
    res = 'topic/*/status'
    re_parsed = ReExp.parse(res, ['topic', 'status'])
    re_expected = z3.Concat(z3.Re('\u03b1'),
                            z3.Re('/'), 
                            ReExp.RE_STAR,
                            z3.Re('/'),
                            z3.Re('\u03b2'))
    self.assertEqual(re_parsed, re_expected)
      
  def test_parse_plus(self):
    res = '+/temp'
    re_parsed = ReExp.parse(res, ['temp'])
    re_expected = z3.Concat(z3.Re('+'), z3.Re('/'), z3.Re('\u03b1'))
    self.assertEqual(re_parsed, re_expected)
      
  def test_parse_hash(self):
    res = '#'
    re_parsed = ReExp.parse(res)
    re_expected = z3.Re('#')
    self.assertEqual(re_parsed, re_expected)

  def test_parse_client_id(self):
    res = 'Client/${iot:ClientId}'
    re_parsed = ReExp.parse(res, ['Client'], 'test')
    re_expected = z3.Concat(z3.Re('\u03b1'), z3.Re('/'), z3.Re('test'))
    self.assertEqual(re_parsed, re_expected)
    
  def test_tokens_contained(self):
    res = 'floor1/floor?'
    re_parsed = ReExp.parse(res)
    re_expected = z3.Concat(z3.Re('floor1'),
                            z3.Re('/'),
                            z3.Re('floor'),
                            ReExp.RE_QMARK)
    self.assertEqual(re_parsed, re_expected)
    
  def test_tokens_client(self):
    res = 'test/te${iot:ClientId}'
    re_parsed = ReExp.parse(res, [], 'st')
    re_expected = z3.Concat(z3.Re('test'), z3.Re('/'), z3.Re('te'), z3.Re('st'))
    self.assertEqual(re_parsed, re_expected)
   
  def test_token_sequence_qmarks(self): 
    res = 'test/something/????'
    re_parsed = ReExp.parse(res, ['something'])
    re_expected = z3.Concat(z3.Re('test'),
                            z3.Re('/'),
                            z3.Re('\u03b1'),
                            z3.Re('/'),
                            ReExp.RE_QMARK,
                            ReExp.RE_QMARK,
                            ReExp.RE_QMARK,
                            ReExp.RE_QMARK)
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
    res = '${iot:Connection.Thing.ThingName}'
    thing_file = 'tests/things/thing_presence_sensor_floor1.json'
    thing: Thing = Thing.from_file(thing_file, None)
    
    re_parsed = ReExp.parse(res, ['presenceSensor1'], 'test', thing.name, thing.attrs)
    re_expected = z3.Re('\u03b1')
    self.assertEqual(re_parsed, re_expected)
    
  def test_parse_thing_attrs(self):
    res = 'physicalAC/floor${iot:Connection.Thing.Attributes[floor]}/${iot:ClientId}/enable'
    thing_file = 'tests/things/thing_presence_sensor_floor1.json'
    thing: Thing = Thing.from_file(thing_file, None)
    
    re_parsed = ReExp.parse(res, ['physicalAC', 'floor1', 'enable'], 'testT', thing.name, thing.attrs)
    re_expected = z3.Concat(z3.Re('\u03b1'),
                            z3.Re('/'),
                            z3.Re('\u03b2'),
                            z3.Re('/'),
                            z3.Re('testT'),
                            z3.Re('/'),
                            z3.Re('\u03b3'))
    self.assertEqual(re_parsed, re_expected)
