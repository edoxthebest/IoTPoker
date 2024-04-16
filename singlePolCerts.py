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
from z3 import String, Not, Empty, StringSort, ReSort, And
from z3 import Re, InRe, Union, Complement, Star, Concat, AllChar, Intersect, Plus
from z3 import Solver, sat

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
re_qmark = Intersect(AllChar(ReSort(StringSort())),Complement(Union(Re('*'), Re('?'))))
re_star = Star(re_qmark)
re_plus = Plus(Intersect(AllChar(ReSort(StringSort())),Complement(Union(Re('*'), Re('?'), Re('/')))))
re_hash = Union(re_empty, Concat(Re('/'), re_star))

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
      s.add(buildPublish(topic, pol1, id1))
      s.add(And(buildSubscribe(topic, pol2, id2), buildReceive(topic, pol2, id2)))
      
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
  return buildConsVarAllowed(id, policy, iot.con, None)

def buildPublish(topic, policy: Policy, client_id):
  return buildConsVarAllowed(topic, policy, iot.pub, client_id)

def buildSubscribe(topic, policy: Policy, client_id):
  return buildConsVarAllowed(topic, policy, iot.sub, client_id)

def buildReceive(topic, policy: Policy, client_id):
  return buildConsVarAllowed(topic, policy, iot.rec, client_id)


def buildConsVarAllowed(variable, policy: Policy, action, client_id):
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

  re_allow = Union([parseRe(res, client_id) for res in allow_res]) if allow_res else re_empty
  re_deny = Union([parseRe(res, client_id) for res in deny_res]) if deny_res else re_empty

  return And(InRe(variable, re_allow), Not(InRe(variable, re_deny)))

def parseRe(arn, client_id):
  res = ARN(arn).name
  is_sub_action = re.match('^topicfilter\/', res)
  res = re.sub('^(client|topic|topicfilter)\/', '', res)
  
  aws_wildcards = r'(\?|\*)'
  mqtt_plus = r'(\+)'
  mqtt_hash = r'(^#$|\/#$)'
  cid_var = r'(\$\{iot:ClientId\})'
  aws_mqtt_wildcards = re.compile('%s|%s|%s|%s' % (aws_wildcards, mqtt_plus, mqtt_hash, cid_var))
  aws_only_wildcards = re.compile('%s|%s' % (aws_wildcards, cid_var))
  if is_sub_action:
    #Both AWS and MQTT Wildcards
    res_split = [x for x in re.split(aws_mqtt_wildcards, res) if x]
  else:
    # Only AWS Wildcards - substitute ? and * with their regular expressions
    res_split = [x for x in re.split(aws_only_wildcards, res) if x]
  res = []
  for x in res_split:
    match x:
      case '?':
        res.append(re_qmark)
      case '*':
        res.append(re_star)
      case '+':
        res.append(re_plus)
      case '#' | '/#' :
        res.append(re_hash)
      case '${iot:ClientId}':
        # Does not handle possible mqtt wildcards in the client id
        res.append(Re(client_id))
      case _:
        res.append(Re(x))

  return res.pop() if len(res) == 1 else Concat(res)
            

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