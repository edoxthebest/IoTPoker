import networkx as nx
import z3
from policytool.certificate import Certificate
from policytool.policy_reader import PolicyReader
import matplotlib.pyplot as plt
from networkx.algorithms import bipartite

class PolicyGraph:
  def __init__(self, certificates: list[Certificate]):
    self._graph = nx.DiGraph()
    self._simple_graph = nx.DiGraph()
    self._certs = certificates
  
  # Algorithm 1
  def build_sym_graph(self):
    for cert1 in self._certs:
      # self._graph.add_node(cert1.name, bipartite=0)
      for cert2 in self._certs:
        id1 = z3.String('id_1')
        id2 = z3.String('id_2')
        topic = z3.String('common_topic')
        
        solver = z3.Solver()
        solver.add(cert1.policies.build_connect(id1))
        solver.add(cert2.policies.build_connect(id2))
        solver.add(cert1.policies.build_publish(topic, id1))
        solver.add(z3.And(cert2.policies.build_subscribe(topic, id2),
                          cert2.policies.build_receive(topic, id2)))
        
        print(f'-- {cert1.name}  &  {cert2.name} --')

        print(solver.check())
        if solver.check() == z3.sat:
          model = solver.model()
          print(model)
          
          node = f'{cert1.name}->{cert2.name}'  
          # self._graph.add_node(node, bipartite=1)
          self._graph.add_edge(cert1.name, node, weight=model[topic])
          self._graph.add_edge(node, cert2.name, weight=model[topic])
          self._simple_graph.add_edge(cert1.name, cert2.name, topic=model[topic])
  
  def draw(self):
    pos = nx.bipartite_layout(self._graph, bipartite.sets(self._graph)[0])
    nx.draw_networkx_nodes(self._graph, pos)
    nx.draw_networkx_labels(self._graph, pos)
    nx.draw_networkx_edge_labels(self._graph, pos, 
                                nx.get_edge_attributes(self._graph, 'weight'), 
                                connectionstyle='arc3, rad = 0.1')
    nx.draw_networkx_edges(self._graph, pos, arrows=True, 
                           connectionstyle='arc3, rad = 0.1')
    
    # nx.draw(self._graph)
    plt.show()

  def draw_min(self):
    pos = nx.spring_layout(self._simple_graph)
    nx.draw_networkx_nodes(self._simple_graph, pos)
    nx.draw_networkx_labels(self._simple_graph, pos)
    nx.draw_networkx_edge_labels(self._simple_graph, pos, 
                                nx.get_edge_attributes(self._simple_graph, 'topic'), 
                                connectionstyle='arc3, rad = 0.1')
    nx.draw_networkx_edges(self._simple_graph, pos, arrows=True, 
                           connectionstyle='arc3, rad = 0.1')
    plt.show()


if __name__ == '__main__':
  reader = PolicyReader()
  reader.read_policy_dir('C:/Users/edolu/git/IMT/Proposal/IoT/ToolIoT/policies/policy_benchmark/FLAW1')
  
  certs =[Certificate(pol) for pol in reader._policies[:18]]
  
  g = PolicyGraph(certs)
  g.build_sym_graph()
  g.draw()
