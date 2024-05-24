import json
import unittest
import uuid
from policytool import Thing, PolicyReader
from policyuniverse.arn import ARN


class TestThing(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    policy_file = 'tests/policies/aws-samples/unreg_connect.json'
    reader = PolicyReader()
    cls.policy = reader.read_policy_file(policy_file)
    
  def test_thing_init(self):
    """
    Test creating a Thing
    """
    name = 'TestThing'
    id = uuid.uuid4()
    arn = ARN('arn:aws:iot:us-east-1:123456789012:thing/TestThing')
    attrs = {'attr1': 1, 'attr2': 'testAttr'}
    test_thing = Thing(name, id, arn, attrs, self.policy)
    
    self.assertEqual(test_thing.name, name)
    self.assertEqual(test_thing.id, id)
    self.assertEqual(test_thing.arn.name, 'thing/TestThing')
    self.assertDictEqual(test_thing.attrs, attrs)
    self.assertEqual(test_thing.policies, self.policy)

  def test_thing_from_json(self):
    """
    Test creating a Thing from json
    """
    thing_json = """{
                      "defaultClientId": "TestJson",
                      "thingName": "TestJson",
                      "thingId": "ba6bb237-014a-4f88-821c-8af8993620cf",
                      "thingArn": "arn:aws:iot:us-east-1:123456789012:thing/TestJson",
                      "attributes": {
                        "floor": "2"
                      },
                      "version": 2
                    }"""
    test_thing = Thing.from_json(json.loads(thing_json), self.policy)
    
    self.assertEqual(test_thing.name, 'TestJson')
    self.assertEqual(test_thing.id, uuid.UUID('ba6bb237-014a-4f88-821c-8af8993620cf'))
    self.assertEqual(test_thing.arn.name, 'thing/TestJson')
    self.assertDictEqual(test_thing.attrs, {'floor':'2'})
    self.assertEqual(test_thing.policies, self.policy)
    
  def test_thing_from_file(self):
    """
    Test creating a Thing from file
    """
    thing_file = 'tests/things/thing_presence_sensor_floor1.json'
    test_thing = Thing.from_file(thing_file, self.policy)
    
    self.assertEqual(test_thing.name, 'presenceSensor1')
    self.assertEqual(test_thing.id, uuid.UUID('ba6bb237-014a-4f88-821c-8af8993620cf'))
    self.assertEqual(test_thing.arn.name, 'thing/presenceSensor1')
    self.assertDictEqual(test_thing.attrs, {'floor':'1'})
    self.assertEqual(test_thing.policies, self.policy)
