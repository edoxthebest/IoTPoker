import unittest
import z3
from policytool import ReExp

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

  # Does not handle possible mqtt wildcards in the client id
