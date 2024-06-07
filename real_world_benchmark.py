import json
import random
import time
from policytool import Certificate, PolicyGraph, PolicyReader, Prover, Thing

bench_dir = 'tests/policies/policy_benchmark/FLAW1_secure'
# bench_dir = 'tests/policies/case-study/'
start_time = time.time()
PolicyReader.read_policy_dir(bench_dir)
policies = PolicyReader._policies
Prover.print_time(start_time)
print(f'Read {len(policies)} policies from {bench_dir}.')

for test_n in range(8):
  start_time_n = time.time()
  Prover.print_time(start_time_n)
  print(f'Starting Test_{test_n} (2^{test_n} = {pow(2, test_n)} certificates). --')

  certs = []
  for cert_count in range(pow(2, test_n)):
    pol_name, pol = random.choice(list(policies.items()))
    cert = Certificate([pol], f'cert_{cert_count}')
    certs.append(cert)
    # Prover.print_time(start_time_n)
    # print(f'Test_{test_n} -- Created cert {cert.name} from policy {pol_name}.')

  start_time = time.time()
  policy_graph = PolicyGraph(certs)
  policy_graph.build_sym_graph()
  Prover.print_time(start_time)
  print(f'Test_{test_n} -- Built symbolic information flow graph of {policy_graph.size} nodes {time.time() - start_time}s.')

  prover = Prover(policy_graph.graph)
  start_time = time.time()
  for test_reach_count in range(1000):
    cert1 = random.choice(certs)
    cert2 = random.choice(certs)
    result = prover.reach(cert1.name, cert2.name)
    # prover.print_time(start_time)
    # print(f'Test_{test_n} -- Can {cert1.name} reach {cert2.name}? {result}.')
  prover.print_time(start_time_n)
  print(f'Test_{test_n} -- Run 1000 reach queries in {time.time() - start_time}s.')

  Prover.print_time(start_time_n)
  print(f'Test_{test_n} ended ({time.time() - start_time_n}s).')