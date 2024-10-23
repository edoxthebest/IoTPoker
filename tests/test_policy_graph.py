import unittest
from policytool import PolicyReader
from policytool import Certificate
from policytool import PolicyGraph

class TestPolicyGraph(unittest.TestCase):
  def test_case_study_sym_graph(self):
    return
    reader = PolicyReader()
    reader.read_policy_dir('tests/policies/case-study')
    
    certs = [Certificate([pol], name) for name, pol in reader._policies.items()]
    
    graph = PolicyGraph(certs)
    graph.build_sym_graph()
    
  def test_same_policy_opti(self):
    pol_light = PolicyReader.read_policy_file('tests/policies/case-study/light.json')
    pol_badge = PolicyReader.read_policy_file('tests/policies/case-study/floor1_badge_reader.json')
    cert_light1 = Certificate([pol_light], 'light_1')
    cert_light2 = Certificate([pol_light], 'light_2')
    cert_lambda = Certificate([pol_badge], 'lambda')
    
    graph = PolicyGraph([cert_light1, cert_light2, cert_lambda])
    graph.build_sym_graph()
    
    self.assertEqual(graph.hard_solver_invokes, 1)
