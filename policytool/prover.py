#  TODO: better name
import networkx as nx
from policytool.node import Node

# TODO:!!! On false should reply with the wrong path -- counterexample
class Prover:
  def __init__(self, graph: nx.DiGraph):
    self._graph = graph
    
  def reach(self, source: str, target: str):
    return nx.has_path(self._graph, source, target)
  
  # TODO: change name
  def weak_reach_only(self, source: str, targets: list[str]):
    paths = nx.single_source_shortest_path(self._graph, source)
    return set(paths).issubset([source] + targets)

  def reach_only(self, source: str, targets: list[str]):
    paths = nx.single_source_shortest_path(self._graph, source)
    return set(paths) == set([source] + targets)
  
  def only_reached_by(self, target: str, sources: list[str]):
    paths = nx.single_target_shortest_path(self._graph, target)
    return set(paths) == set([target] + sources)
  
  def isolated(self, sys1:list[str], sys2: list[str],
               outgoing_allowed_topics: list[str] = [],
               incoming_allowed_topics: list[str] = []):
    if not set(sys1).isdisjoint(sys2):
      return False
    
    graph_copy = self._graph.copy()
    for dev in sys1:
      graph_copy.add_edge('_A', dev)
      graph_copy.add_edge(dev, '_C')

    for dev in sys2:
      graph_copy.add_edge(dev, '_B')
      graph_copy.add_edge('_D', dev)
      
    for node in self._graph.nodes:
      if type(node) is Node:
        if (node.first in sys1 and node.second in sys2) or (node.first in sys2 and node.second in sys1):
          graph_copy.remove_node(node)

    return not (nx.has_path(graph_copy, '_A', '_B') or nx.has_path(graph_copy, '_D', '_C'))
    # generate copy of graph
    # make nodes a, b, c, d
    # while(path = shortest(a, b)) || while(reach(a, b)) -> path = shortest(a,b)
      # if path.length > 5 return false
      # if path[0] != a || path[4] != b return false
      # if path[1] \notin sys1 || path[3] \notin sys2 return false
      # add restriction of outgoin_topics to path[2] predicate
      # if sat return false
      
    # same thing other way round
    # return true at the end