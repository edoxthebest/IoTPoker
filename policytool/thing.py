import json
import os
import uuid
import z3
from policytool.certificate import Certificate
from policytool.iot_policy import IoTPolicy
from policyuniverse.arn import ARN
from typing import Self

class Thing(Certificate):  
  @staticmethod
  def from_json(thing_json: json, policy: IoTPolicy) -> Self:
    name = thing_json['thingName']
    id = uuid.UUID(thing_json['thingId'])
    arn = ARN(thing_json['thingArn'])
    attrs = thing_json['attributes']
    return Thing(name, id, arn, attrs, policy)
  
  @staticmethod
  def from_file(filename: str, policy: IoTPolicy) -> Self:
    file = open(filename)
    return Thing.from_json(json.load(file), policy)
  
  def __init__(self, name: str, id: uuid, arn: ARN, attrs: dict[str, str], policy: IoTPolicy):
    super().__init__([policy], name)
    self.id = id
    self.arn = arn
    self.attrs = attrs
  
  def get_connect(self, id: z3.SeqRef):
    return self.policy.build_connect(id, self.safe_strings, self.name, self.attrs)
  
  def get_publish(self, topic: z3.SeqRef, id: z3.SeqRef):
    return self.policy.build_publish(topic, id, self.safe_strings, self.name, self.attrs)
  
  def get_subscribe(self, topic: z3.SeqRef, id: z3.SeqRef):
    return self.policy.build_subscribe(topic, id, self.safe_strings, self.name, self.attrs)
    
  def get_receive(self, topic: z3.SeqRef, id: z3.SeqRef):
    return self.policy.build_receive(topic, id, self.safe_strings, self.name, self.attrs)
  
  # TODO: might be smart to add here method that takes solver and adds correct queries to it