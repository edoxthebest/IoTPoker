# Assume we are given a file consisting of policy paths
# Each policy corresponds to a single certificate
# 
# We parse them, the construct the information flow graph
import json
import matplotlib.pyplot as plt
import networkx as nx
import re
import sys
from networkx.algorithms import bipartite
from policyuniverse.arn import ARN
from policyuniverse.policy import Policy
from z3 import String, Solver, InRe, Union, Re, Not, sat, Empty, StringSort, ReSort, And

# Pairs (Filename, Policy) -- as substitute for certificates
policies = []

# Actions
class iot:
  con = 'iot:Connect'
  pub = 'iot:Publish'
  sub = 'iot:Subscribe'
  rec = 'iot:Receive'

nodes_certs = []
nodes_formulas = []
edges = []

re_empty = Empty(ReSort(StringSort()))

def printPols():
  for (name, pol) in policies:
    print(name)
    white = ''
    for stmt in pol.statements:
      print(white + repr(stmt.actions))
      white += '  '

# Algorithm 1
def buildSymGraph():
  nodes_certs = [name for (name, _) in policies]
  
  for (cert1, pol1) in policies:
    for (cert2, pol2) in policies:
      id1 = String('id_1')
      id2 = String('id_2')
      topic = String('common_topic')
      
      s = Solver()
      s.add(buildConnect(id1, pol1))
      s.add(buildConnect(id2, pol2))
      s.add(buildPublish(topic, pol1))
      s.add(And(buildSubscribe(topic, pol2), buildReceive(topic, pol2)))
      
      print(f'-- {cert1}  &  {cert2} --')

      print(s.check())
      if s.check() == sat:
        model = s.model()
        print(model)
        
        node = f'{cert1}->{cert2}({model[topic]})'
        
        nodes_formulas.append(node)
        edges.append((cert1, node))
        edges.append((node, cert2))
      # if sat
        # add edge
        # add node
        
def buildConnect(id, policy: Policy):
  return buildConsVarAllowed(id, policy, iot.con)

def buildPublish(topic, policy: Policy):
  return buildConsVarAllowed(topic, policy, iot.pub)

def buildSubscribe(topic, policy: Policy):
  return buildConsVarAllowed(topic, policy, iot.sub)

def buildReceive(topic, policy: Policy):
  return buildConsVarAllowed(topic, policy, iot.rec)


def buildConsVarAllowed(variable, policy: Policy, action):
  allow_res = []
  deny_res = []
  
  for stmt in policy.statements:
    if not action in stmt.actions:
      continue
    
    if stmt.effect == 'Allow':
      for res in stmt.resources:
        allow_res.append(res)
    elif stmt.effect == 'Deny':
      for res in stmt.resources:
        deny_res.append(res)

  re_allow = Union([parseRe(res) for res in allow_res]) if allow_res else re_empty
  re_deny = Union([parseRe(res) for res in deny_res]) if deny_res else re_empty

  return And(InRe(variable, re_allow), Not(InRe(variable, re_deny)))

def parseRe(arn):
  res = ARN(arn).name
  res = re.sub('^(client|topic|topicfilter)\/', '', res)
  return Re(res)
            

def main():
  print(sys.argv)
  
  for line in open(sys.argv[1]):
    line = line.strip().split(' ')
    file = open(line[1])
    policy = Policy(json.load(file))
    policies.append((line[0], policy))
  
  printPols()
  
  buildSymGraph()
  
  G = nx.DiGraph()
  G.add_nodes_from(nodes_certs, bipartite=0)
  G.add_nodes_from(nodes_formulas, bipartite=1)
  G.add_edges_from(edges)
  
  pos = nx.bipartite_layout(G, bipartite.sets(G)[1])
  nx.draw_networkx_nodes(G, pos,)
  nx.draw_networkx_labels(G, pos)
  nx.draw_networkx_edges(G, pos, arrows=True, connectionstyle='arc3, rad = 0.1')

  plt.show()
  
if __name__ == '__main__':
  main()