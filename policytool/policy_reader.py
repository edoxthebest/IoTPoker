import json
import os
from policytool.iot_policy import IoTPolicy

class PolicyReader:
  _policies = {}
  
  @property
  def policies(self):
    return list(self._policies.values())
  
  @staticmethod
  def read_policy_file(filename):
    with open(filename) as file:
      return IoTPolicy(json.load(file))
   
  @classmethod 
  def read_policy_dir(cls, dir) -> list[IoTPolicy]:
    for filename in os.listdir(dir):
      file = os.path.join(dir, filename)
      
      if os.path.isfile(file):
        cls._policies.update({filename: cls.read_policy_file(file)})
    
    return list(cls._policies.values())
