# Assume we are given a file consisting of policy paths
# Each policy corresponds to a single certificate
# 
# We parse them, the construct the information flow graph
import json
import re
import sys
from z3 import String, Solver, InRe, Union, Re, Not, sat, Empty, StringSort, ReSort, And
from policyuniverse.policy import Policy
from policyuniverse.arn import ARN

# Pairs (Filename, Policy) -- as substitute for certificates
policies = []

nodes = []
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
  nodes = [name for (name, _) in policies]
  edges = []
  
  for (cert1, pol1) in policies:
    for (cert2, pol2) in policies:
      id1 = String('id_1')
      id2 = String('id_2')
      topic = String('common_topic')
      
      re_id1 = buildReConnect(pol1)
      re_id2 = buildReConnect(pol2)
      
      s = Solver()
      s.add(InRe(id1, re_id1))
      s.add(InRe(id2, re_id2))
      s.add(InRe(topic, buildRePub(pol1)))
      s.add(And(InRe(topic, buildReSub(pol2)), InRe(topic, buildReRec(pol2))))
      
      print(f'-- {cert1}  &  {cert2} --')

      print(s.check())
      if s.check() == sat:
        print(s.model())
      # if sat
        # add edge
        # add node
        
def buildReConnect(policy: Policy):
  re_con = re_empty
  
  for stmt in policy.statements:
    if not 'iot:Connect' in stmt.actions:
      continue
    
    if len(stmt.resources) > 1:
      re_res = Union([parseRe(res) for res in stmt.resources])
    else:
      re_res = parseRe(stmt.resources.pop())
         
    if stmt.effect == 'Allow':
      re_con = Union(re_con, re_res)
    elif stmt.effect == 'Deny':
      re_con = Union(re_con, Not(re_res))
  
  print(re_con)
  return re_con

def buildRePub(policy: Policy):
  re_pub = re_empty
  
  for stmt in policy.statements:
    if not 'iot:Publish' in stmt.actions:
      continue
    
    if len(stmt.resources) > 1:
      re_res = Union([parseRe(res) for res in stmt.resources])
    else:
      re_res = parseRe(stmt.resources.pop())
        
    if stmt.effect == 'Allow':
      re_pub = Union(re_pub, re_res)
    elif stmt.effect == 'Deny':
      pass
      # re_pub = Union(re_pub, Not(re_res))
  
  print(re_pub)
  return re_pub

def buildReSub(policy: Policy):
  re_sub = re_empty
  
  for stmt in policy.statements:
    if not 'iot:Publish' in stmt.actions:
      continue
    
    if len(stmt.resources) > 1:
      re_res = Union([parseRe(res) for res in stmt.resources])
    else:
      re_res = parseRe(stmt.resources.pop())  
            
    if stmt.effect == 'Allow':
      re_sub = Union(re_sub, re_res)
    elif stmt.effect == 'Deny':
      pass
      # re_sub = Union(re_sub, Not(re_res))
  
  print(re_sub)
  return re_sub

def buildReRec(policy: Policy):
  re_rec = re_empty
  
  for stmt in policy.statements:
    if not 'iot:Publish' in stmt.actions:
      continue
    
    if len(stmt.resources) > 1:
      re_res = Union([parseRe(res) for res in stmt.resources])
    else:
      re_res = parseRe(stmt.resources.pop())        
    
    if stmt.effect == 'Allow':
      re_rec = Union(re_rec, re_res)
    elif stmt.effect == 'Deny':
      pass
      # re_rec = Union(re_rec, Not(re_res))
  
  print(re_rec)
  return re_rec


def parseRe(arn):
  res = ARN(arn).name
  res = re.sub('^(client|topic|topicfilter)\/', '', res)
  return Re(res)
            
def buildF_c1_c2():
  # AND F_out_c1 F_in_c2
  pass

def buildF_out():
  pass

def main():
  print(sys.argv)
  
  for line in open(sys.argv[1]):
    line = line.strip()
    file = open(line)
    policy = Policy(json.load(file))
    policies.append((line, policy))
  
  printPols()
  buildReConnect(policies[5][1])
  
  buildSymGraph()
  
if __name__ == '__main__':
  main()