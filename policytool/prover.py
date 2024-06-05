#  TODO: better name
import networkx as nx
import time
from policytool.node import Node

class Prover:
  def __init__(self, graph: nx.DiGraph):
    self._graph = graph
  
  @staticmethod
  def print_time(start):
    print('-- {:.4f}s -- '.format(time.time() - start), end='')
    
  @staticmethod
  def print_path(path):
      for node in path:
        print (f'\t\t {node}')
    
  def reach(self, source: str, target: str, log_level=None):
    start_time = time.time()
    try:
      path = nx.shortest_path(self._graph, source, target)
    except:
      if log_level == 'info':
        self.print_time(start_time)
        print(f'No path found from {source} to {target}.')
      return False
    
    if log_level == 'info':
      self.print_time(start_time)
      print('Found the path:')
      # for node in path:
      #   print (f'\t\t {node}')
      self.print_path(path)
      print(f'{" " *13} from {source} to {target}.')
    return True, path
  
  # TODO: change name
  def weak_reach_only(self, source: str, targets: list[str]):
    paths = nx.single_source_shortest_path(self._graph, source)
    return set(paths).issubset([source] + targets)

  def reach_only(self, source: str, targets: list[str], log_level=None):
    start_time = time.time()
    if log_level == 'info':
      self.print_time(start_time)
      print(f'Checkin if {source} reaches only {targets}.')

    paths = nx.single_source_shortest_path(self._graph, source)
    paths_no_topics = dict()
    for key, val in paths.items():
      if type(key) is not Node:
        paths_no_topics[key] = val
        
    if set(paths_no_topics) == set([source] + targets):
      if log_level == 'info':
        self.print_time(start_time)
        print(f'Correct: {source} reaches only {targets}.')
      return True
    else:
      if log_level == 'info':
        diff = set(paths_no_topics) - set([source] + targets)
        if len(diff) != 0:
          self.print_time(start_time)
          print(f'Found the following unexpected paths ({len(diff)}):')
          for node in diff:
            self.print_path(paths[node])
            print()
            
        diff = set([source] + targets) - set(paths_no_topics)
        if len(diff) != 0:
          self.print_time(start_time)
          print('No path found for the nodes:')
          for node in diff:
            print(f'\t\t{node}')
      return False, paths
  
  def only_reached_by(self, target: str, sources: list[str], log_level=None):
    start_time = time.time()
    if log_level == 'info':
      self.print_time(start_time)
      print(f'Checking if {target} is only reached by {sources}.')
    
    paths = nx.single_target_shortest_path(self._graph, target)
    paths_no_topics = dict()
    for key, val in paths.items():
      if type(key) is not Node:
        paths_no_topics[key] = val

    if set(paths_no_topics) == set([target] + sources):
      if log_level == 'info':
        self.print_time(start_time)
        print(f'Correct: {target} is only reached by {sources}.')
      return True
    else:
      if log_level == 'info':
        self.print_time(start_time)
        diff = set(paths_no_topics) - set([target] + sources)
        if len(diff) != 0:
          print(f'Found the following unexpected paths ({len(diff)}):')
          for node in diff:
            self.print_path(paths[node])
            print()
            
        diff = set([target] + sources) - set(paths_no_topics)
        if len(diff) != 0:
          print('No path found for the nodes:')
          for node in diff:
            print(f'\t\t{node}')
      return False, paths
  
  def isolated(self, sys1:list[str], sys2: list[str], log_level=None):
    start_time = time.time()
    if log_level == 'info':
      self.print_time(start_time)
      print(f'Checking if the subsystems {sys1} and {sys2} are isolated.')
    
    intersection = set(sys1).intersection(sys2)
    if len(intersection) != 0:
      if log_level == 'info':
        self.print_time(start_time)
        print(f'Not isolated since both contain: {intersection}')
        return False
    
    for dev1 in sys1:
      for dev2 in sys2:
        if self.reach(dev1, dev2):
          if log_level == 'info':
            self.print_time(start_time)
            print(f'Not isolated since {dev1} can reach {dev2} with the path:')
          return False, self.reach(dev1, dev2, log_level=log_level)[1]
        if self.reach(dev2, dev1):
          if log_level == 'info':
            self.print_time(start_time)
            print(f'Not isolated since {dev2} can reach {dev1} with the path:')
          return False, self.reach(dev2, dev1, log_level=log_level)[1]
          
    if log_level == 'info':
      self.print_time(start_time)
      print(f'The subsystems {sys1} and {sys2} are isolated')
    return True
  
  def isolated_old(self, sys1:list[str], sys2: list[str],
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