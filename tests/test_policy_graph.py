import unittest
from policytool import PolicyReader
from policytool import Certificate
from policytool import PolicyGraph

class TestPolicyGraph(unittest.TestCase):
  def test_case_study_sym_graph(self):
    reader = PolicyReader()
    reader.read_policy_dir('tests/policies/case-study')
    
    certs = [Certificate([pol], name) for name, pol in reader._policies.items()]
    
    graph = PolicyGraph(certs)
    graph.build_sym_graph()
    # graph.draw_tree(['floor1_badge_reader'])