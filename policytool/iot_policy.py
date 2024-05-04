import z3
from policyuniverse.policy import Policy
from policytool.iot import IoT
from policytool.re_exp import ReExp

class IoTPolicy(Policy):
  def buildConnect(self, id):
    return self.buildConsVarAllowed(id, IoT.CON)
  
  def buildPublish(self, topic, client_id):
    return self.buildConsVarAllowed(topic, IoT.PUB, client_id)

  def buildSubscribe(self, topic, client_id):
    return self.buildConsVarAllowed(topic, IoT.SUB, client_id)

  def buildReceive(self, topic, client_id):
    return self.buildConsVarAllowed(topic, IoT.REC, client_id)

 
  def buildConsVarAllowed(self, variable, action, client_id = None):
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

    re_allow = z3.Union([ReExp.parse(res, client_id) for res in allow_res]) if allow_res else ReExp.RE_EMPTY
    re_deny = z3.Union([ReExp.parse(res, client_id) for res in deny_res]) if deny_res else ReExp.RE_EMPTY

    return z3.And(z3.InRe(variable, re_allow), z3.Not(z3.InRe(variable, re_deny)))