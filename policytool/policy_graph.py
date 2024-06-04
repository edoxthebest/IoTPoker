import matplotlib.pyplot as plt
import networkx as nx
import z3
from policytool.certificate import Certificate
from policytool.policy_reader import PolicyReader
from policytool.node import Node
from networkx.algorithms import bipartite

class PolicyGraph:
  @property
  def certs(self):
    return [cert.name for cert in self._certs]
  
  @property
  def pseudo_topics(self):
    return [node for node in self._graph.nodes if type(node) is Node]
  
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
        
        # solver = z3.Solver()
        # solver.add(cert1.policies.build_connect(id1))
        # solver.add(cert2.policies.build_connect(id2))
        # solver.add(cert1.policies.build_publish(topic, id1))
        # solver.add(z3.And(cert2.policies.build_subscribe(topic, id2),
        #                   cert2.policies.build_receive(topic, id2)))
        solver = z3.Solver()
        solver.add(cert1.get_connect(id1))
        solver.add(cert2.get_connect(id2))
        solver.add(cert1.get_publish(topic, id1))
        solver.add(z3.And(cert2.get_subscribe(topic, id2),
                          cert2.get_receive(topic, id2)))

        if solver.check() == z3.sat:
          model = solver.model()
          
          # TODO: should change cert.name to cert
          node = Node(cert1.name, cert2.name, solver, model[id1], model[id2], model[topic])
          self._graph.add_edge(cert1.name, node)
          self._graph.add_edge(node, cert2.name)

          # node = f'{cert1.name}->{cert2.name}'  
          # self._graph.add_node(node, bipartite=1)
          # self._graph.add_edge(cert1.name, node, weight=model[topic])
          # self._graph.add_edge(node, cert2.name, weight=model[topic])
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
    
  def draw_v2(self):
    pos = nx.spring_layout(self._graph)
    # pos = {node:[pos[node][0], -pos[node][1]] for node in pos}
    # cert_labels = {cert:cert.name for cert in self._graph.nodes if type(cert) is Certificate}
    cert_labels = {cert:cert for cert in self._graph.nodes if type(cert) is str}
    pseudo_topic_labels = {n:n.topic for n in self.pseudo_topics}
    # label_pos = {node:[pos[node][0], pos[node][1] - .1] for node in pos}
    label_pos = pos
    nx.draw_networkx_nodes(self._graph, pos, self.certs,
                           node_size=600, node_color='red')
    nx.draw_networkx_nodes(self._graph, pos, self.pseudo_topics, 
                           node_size=200, node_color='#00FF00', node_shape='s')
    nx.draw_networkx_edges(self._graph, pos, arrows=True)
    nx.draw_networkx_labels(self._graph, label_pos, labels=cert_labels)
    nx.draw_networkx_labels(self._graph, label_pos, labels=pseudo_topic_labels)
    plt.show()

  def draw_tree(self, roots):
    for root in roots:
      subgraph = self._graph.subgraph(nx.descendants(self._graph, root) | {root})
      certs = [c for c in subgraph.nodes if type(c) is str]
      pseudo_topics = [n for n in subgraph.nodes if type(n) is Node]
      pos = nx.bfs_layout(subgraph, root, align='horizontal', center=[0, 0])
      pos = {node:[pos[node][0], -pos[node][1]] for node in pos}
      cert_labels = {cert:cert for cert in certs}
      pseudo_topic_labels = {n:n.topic for n in pseudo_topics}
      label_pos = {node:[pos[node][0], pos[node][1] + .08] for node in pos}
      nx.draw_networkx_nodes(subgraph, pos, certs,
                           node_size=600, node_color='red')
      nx.draw_networkx_nodes(subgraph, pos, pseudo_topics, 
                             node_size=200, node_color='#00FF00', node_shape='s')
      nx.draw_networkx_edges(subgraph, pos, arrows=True)
      nx.draw_networkx_labels(subgraph, label_pos, labels=cert_labels)
      nx.draw_networkx_labels(subgraph, label_pos, labels=pseudo_topic_labels)
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