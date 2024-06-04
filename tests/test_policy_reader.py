import unittest
import os.path
from policytool import IoT, IoTPolicy, PolicyReader
from policyuniverse.policy import Policy

class TestPolicyReader(unittest.TestCase):
  def setUp(self):
    PolicyReader._policies = []
    
  def test_read_policy_file(self):
    """
    Test reading policy file
    """
    filename = 'tests/policies/aws-samples/unreg_connect.json'
    policy = PolicyReader.read_policy_file(filename)
    
    self.assertIsInstance(policy, IoTPolicy)
    self.assertSetEqual(policy.statements[0].actions, {IoT.CON})
    
  def test_read_aws_samples_dir(self):
    """
    Test reading policies from aws-samples directory
    """
    directory = 'tests/policies/aws-samples'
    policies = PolicyReader.read_policy_dir(directory)
    
    self.assertEqual(len(policies), len([f for f in os.listdir(directory)]))
    for policy in policies:
      self.assertIsInstance(policy, Policy)
      
  def test_read_stored_dir(self):
    """
    Test stored policy after directory reading
    """
    directory = 'tests/policies/policy_benchmark/FLAW1'
    reader = PolicyReader()
    reader.read_policy_dir(directory)
    
    for policy in reader.policies:
      self.assertIsInstance(policy, Policy)