import networkx as nx
import unittest
from policytool import Certificate, PolicyGraph, PolicyReader, Prover, Thing

class TestProver(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    graph_1_edges = [('a', 'b'), ('b', 'c'), ('d', 'a')]
    cls.graph_1 = nx.DiGraph()
    cls.graph_1.add_edges_from(graph_1_edges)
    
    case_study_dir = 'tests/policies/case-study/'
    elevator_pol = PolicyReader.read_policy_file(case_study_dir + 'elevator.json')
    lock1_pol = PolicyReader.read_policy_file(case_study_dir + 'floor1_door_lock.json')
    lamda_fire_alarm_pol = PolicyReader.read_policy_file(case_study_dir + 'lambda_fire_alarm.json')
    pSensor1_pol = PolicyReader.read_policy_file(case_study_dir + 'thing_presence_sensor.json')
    elevator = Certificate([elevator_pol], 'elevator')
    lock1 = Certificate([lock1_pol], 'lock1')
    lambda_fire_alarm = Certificate([lamda_fire_alarm_pol], 'lambda_fire_alarm')
    pSensor1 = Thing.from_file('tests/things/thing_presence_sensor_floor1.json', pSensor1_pol)
    policy_graph = PolicyGraph([elevator, lock1, lambda_fire_alarm, pSensor1])
    policy_graph.build_sym_graph()
    cls.graph_2 = policy_graph._graph

    # graph_2_edges = [('a', 'b'), ('b', 'c'), ('d', 'a')]
    # cls.graph_2 = nx.DiGraph().add_edges_from(graph_2_edges)
    
  def test_reach(self):
    prover = Prover(self.graph_1)
    self.assertTrue(prover.reach('a', 'b'))
    self.assertTrue(prover.reach('b', 'c'))
    self.assertTrue(prover.reach('d', 'a'))
    self.assertTrue(prover.reach('a', 'c'))
    self.assertFalse(prover.reach('a', 'd'))

  def test_reach_certs(self):
    prover = Prover(self.graph_2)
    self.assertTrue(prover.reach('lambda_fire_alarm', 'elevator'))
    self.assertTrue(prover.reach('lambda_fire_alarm', 'lock1'))
    self.assertFalse(prover.reach('elevator', 'lock1'))
    
  def test_weak_reach_only(self):
    prover = Prover(self.graph_1)
    self.assertTrue(prover.weak_reach_only('a', ['b', 'c']))
    self.assertTrue(prover.weak_reach_only('d', ['a', 'b', 'c']))
    self.assertFalse(prover.weak_reach_only('a', ['b']))
    self.assertFalse(prover.weak_reach_only('d', ['a', 'b']))
    self.assertTrue(prover.weak_reach_only('b', ['a', 'c']))

  def test_reach_only(self):
    prover = Prover(self.graph_1)
    self.assertTrue(prover.reach_only('a', ['b', 'c']))
    self.assertTrue(prover.reach_only('d', ['a', 'b', 'c']))
    self.assertFalse(prover.reach_only('a', ['b']))
    self.assertFalse(prover.reach_only('d', ['a', 'b']))
    self.assertFalse(prover.reach_only('b', ['a', 'c']))

  def test_only_reached_by(self):
    prover = Prover(self.graph_1)
    self.assertTrue(prover.only_reached_by('a', ['d']))
    self.assertTrue(prover.only_reached_by('b', ['a', 'd']))    
    self.assertTrue(prover.only_reached_by('c', ['a', 'b', 'd']))    
    self.assertTrue(prover.only_reached_by('d', []))
    self.assertFalse(prover.only_reached_by('b', ['a']))
    self.assertFalse(prover.only_reached_by('c', ['a', 'b']))

  def test_isolated_certs(self):
    prover = Prover(self.graph_2)
    
    self.assertTrue(prover.isolated(['lambda_fire_alarm'], ['elevator']))
    self.assertTrue(prover.isolated(['elevator'], ['lambda_fire_alarm']))
    self.assertTrue(prover.isolated(['lambda_fire_alarm'], ['lock1']))
    self.assertTrue(prover.isolated(['lock1'], ['lambda_fire_alarm']))
    self.assertFalse(prover.isolated(['presenceSensor1'], ['lambda_fire_alarm']))
    self.assertFalse(prover.isolated(['lambda_fire_alarm'], ['presenceSensor1']))