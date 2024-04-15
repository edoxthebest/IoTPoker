import json
from policyuniverse.arn import ARN
from policyuniverse.policy import Policy
from policyuniverse.statement import Statement

file = open('policies/aws-samples/connect-unregistered.json')
policy = Policy(json.load(file))
statement: Statement = policy.statements[0]

print(statement.effect)
print(statement.actions)
print(statement.resources)

res = ARN(statement.resources.pop())
print(res.name)