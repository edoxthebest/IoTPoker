import json
import os
from policytool.iot_policy import IoTPolicy

class PolicyReader:
  _policies = []
  
  def read_policy(self, file):
    parsed_policy = IoTPolicy(json.load(file))
    self._policies.append(parsed_policy)
    
  def read_policy_file(self, filename):
    file = open(filename)
    self.read_policy(file)
    file.close()
    
  def read_policy_dir(self, dir):
    for filename in os.listdir(dir):
      file = os.path.join(dir, filename)
      
      if os.path.isfile(file):
        self.read_policy_file(file)
