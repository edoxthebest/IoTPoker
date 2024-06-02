import z3
from policytool.iot_policy import IoTPolicy

class Certificate:
  @property
  def name(self):
    return self._name
  
  @property
  def policy(self):
    return self._policy
  
  #TODO: check order here -- might result in errors
  def __init__(self, policies: list[IoTPolicy], name: str = None):
    self._policy = IoTPolicy.union(policies)
    self._name = name if not name is None else self.policy.client
    
  def get_connect(self, id: z3.SeqRef):
    return self.policy.build_connect(id)
  
  def get_publish(self, topic: z3.SeqRef, id: z3.SeqRef):
    return self.policy.build_publish(topic, id)
  
  def get_subscribe(self, topic: z3.SeqRef, id: z3.SeqRef):
    return self.policy.build_subscribe(topic, id)
    
  def get_receive(self, topic: z3.SeqRef, id: z3.SeqRef):
    return self.policy.build_receive(topic, id)
  
  # TODO: might be smart to add here method that takes solver and adds correct queries to it