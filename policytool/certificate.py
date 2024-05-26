from policytool.iot_policy import IoTPolicy

class Certificate:
  @property
  def name(self):
    return self._name
  
  @property
  def policy(self):
    return self._policy
  
  def __init__(self, policies: list[IoTPolicy], name: str = None):
    self._policy = IoTPolicy.get_union(policies)
    self._name = name if not name is None else self.policy.get_client()