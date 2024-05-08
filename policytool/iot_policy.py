import z3
from policyuniverse.policy import Policy
from policytool.iot import IoT
from policytool.re_exp import ReExp

class IoTPolicy(Policy):
  def build_connect(self, id):
    return self.build_allow_constraint(id, IoT.CON)
  
  def build_publish(self, topic, client_id):
    return self.build_allow_constraint(topic, IoT.PUB, client_id)

  def build_subscribe(self, topic, client_id):
    return self.build_allow_constraint(topic, IoT.SUB, client_id)

  def build_receive(self, topic, client_id):
    return self.build_allow_constraint(topic, IoT.REC, client_id)

 
  def build_allow_constraint(self, variable, action, client_id = None):
    allow_res = []
    deny_res = []
    
    for stmt in self.statements:
      if not action in stmt.actions:
        continue
      
      if stmt.effect == IoT.ALLOW:
        for res in stmt.resources:
          allow_res.append(res)
      elif stmt.effect == IoT.DENY:
        for res in stmt.resources:
          deny_res.append(res)
          
    parsed_allow = [ReExp.parse(res, client_id) for res in allow_res]
    parsed_deny = [ReExp.parse(res, client_id) for res in deny_res]

    re_allow = z3.Union(parsed_allow) if allow_res else ReExp.RE_EMPTY
    re_deny = z3.Union(parsed_deny) if deny_res else ReExp.RE_EMPTY

    return z3.And(z3.InRe(variable, re_allow), z3.Not(z3.InRe(variable, re_deny)))