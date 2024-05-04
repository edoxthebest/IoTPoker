from policytool.iot_policy import IoTPolicy

class Certificate:
  count = 0
  
  def __init__(self, name, policies: IoTPolicy):
    self.name = name
    self.policies = policies

  def __init__(self, policy: IoTPolicy):
    self.name = f'cert{Certificate.count}'
    self.policies = policy
    Certificate.count += 1