import unittest
from policytool import PolicyReader
from policyuniverse.policy import Policy


class TestPolicyReader(unittest.TestCase):
  def test_read_aws_samples_dir(self):
    """
    Test reading policies from aws-samples directory
    """
    directory = 'tests/policies/aws-samples'
    reader = PolicyReader()
    reader.read_policy_dir(directory)
    
    self.assertEqual(len(reader._policies), 8)
    for policy in reader._policies:
      self.assertIsInstance(policy, Policy)
      
  def test_read_bench_flaw1(self):
    """
    Test reading policies from benchmark FLAW 1
    """
    directory = 'tests/policies/policy_benchmark/FLAW1'
    reader = PolicyReader()
    reader.read_policy_dir(directory)
    
    for policy in reader._policies:
      self.assertIsInstance(policy, Policy)