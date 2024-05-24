import json
import os
import uuid
from policytool.certificate import Certificate
from policytool.iot_policy import IoTPolicy
from policyuniverse.arn import ARN

class Thing(Certificate):  
  def __init__(self, name: str, id: uuid, arn: ARN, attrs: dict[str, str], policy: IoTPolicy):
    super().__init__(name, policy)
    self.id = id
    self.arn = arn
    self.attrs = attrs
    
  def from_json(thing_json: json, policy: IoTPolicy):
    name = thing_json['thingName']
    id = uuid.UUID(thing_json['thingId'])
    arn = ARN(thing_json['thingArn'])
    attrs = thing_json['attributes']
    return Thing(name, id, arn, attrs, policy)
  
  def from_file(filename: str, policy: IoTPolicy):
    file = open(filename)
    return Thing.from_json(json.load(file), policy)