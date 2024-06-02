import z3
from policyuniverse.arn import ARN
from policyuniverse.policy import Policy
from policytool.iot import IoT
from policytool.re_exp import ReExp

class IoTPolicy(Policy):
  @staticmethod
  def union(policies: list['IoTPolicy']):
    # TODO: implement this
    return policies[0]
  
  # TODO: test this
  @property
  def client(self):
    for stmt in self.statements:
      if not IoT.CON in stmt.actions:
        continue
      
      return ARN(stmt.resources.pop()).name
    
  def build_connect(self, id: z3.SeqRef, thing_name: str = None, thing_attrs: dict[str, str] = None):
    return self.build_allow_constraint(id, IoT.CON, thing_name=thing_name, thing_attrs=thing_attrs)
  
  def build_publish(self, topic: z3.SeqRef, client_id: z3.SeqRef,
                    thing_name: str = None, thing_attrs: dict[str, str] = None):
    return self.build_allow_constraint(topic, IoT.PUB, client_id, thing_name, thing_attrs)

  def build_subscribe(self, topic: z3.SeqRef, client_id: z3.SeqRef,
                      thing_name: str = None, thing_attrs: dict[str, str] = None):
    return self.build_allow_constraint(topic, IoT.SUB, client_id, thing_name, thing_attrs)

  def build_receive(self, topic: z3.SeqRef, client_id: z3.SeqRef,
                    thing_name: str = None, thing_attrs: dict[str, str] = None):
    return self.build_allow_constraint(topic, IoT.REC, client_id, thing_name, thing_attrs)

  def build_allow_constraint(self, variable: z3.SeqRef, action: IoT, client_id: z3.SeqRef = None,
                             thing_name: str = None, thing_attrs: dict[str, str] = None):
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
          
    parsed_allow = [ReExp.parse(res, client_id, thing_name, thing_attrs) for res in allow_res]
    parsed_deny = [ReExp.parse(res, client_id, thing_name, thing_attrs) for res in deny_res]

    re_allow = z3.Union(parsed_allow) if allow_res else ReExp.RE_EMPTY
    re_deny = z3.Union(parsed_deny) if deny_res else ReExp.RE_EMPTY

    return z3.And(z3.InRe(variable, re_allow), z3.Not(z3.InRe(variable, re_deny)))