import argparse
import logging
import numpy
import random
import time
from policytool import Certificate, PolicyGraph, PolicyReader, Prover, Thing

parser = argparse.ArgumentParser(description='Evaluates the given set of policies with multiple tests.')
parser.add_argument('dir', type=str)
parser.add_argument('-n', type=int, default=8, help='Up to 2^n certs will be tested.')
parser.add_argument('-i', '--min', type=int, default=0, help='Starting from 2^i certs.')
parser.add_argument('-s', '--seq', type=int, nargs='+', help='Executing tests for the given sizes.')
parser.add_argument('-c', type=int, default=1, help='Number of tests carried out for each cert count.')
parser.add_argument('--debug', action='store_true')
parser.add_argument('--info', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('-g', '--generate', action='store_true')
parser.add_argument('-C', '--config', action='store_true')
args = parser.parse_args()
if args.debug:
  # logging.StreamHandler.terminator = '\r'
  logging.getLogger('IoT:Poker').setLevel(logging.DEBUG)
if args.info:
  logging.StreamHandler.terminator = '\r'
  logging.getLogger('IoT:Poker').setLevel(logging.INFO)
power_two_tests = args.seq == None
test_range = range(args.min, args.n) if power_two_tests else range(len(args.seq))


if args.generate:
  flaw_secure_max = 258
  
  with open('test.perms', 'w') as file:  
    for test_n in test_range:
      for test_c in range(args.c):
        policies = []
        for cert_count in range(args.seq[test_n]):
          policies_no = str(random.choice(range(flaw_secure_max)) + 1)
          policies.append(policies_no)
        file.write(','.join(policies) + '\n')
  exit(0)
  
if args.config:
  policies_nos = []
  test_counter = 0
  with open('test.perms', 'r') as file:
    for line in file:
      policies_nos.append([int(i) for i in line.split(',')])

bench_dir = args.dir
start_time = time.time()
PolicyReader.read_policy_dir(bench_dir)
policies = PolicyReader._policies
print(f'[{time.time() - start_time:.4f}] '
      f'Read {len(policies)} policies from {bench_dir}.')

for test_n in test_range:
  if power_two_tests:
    max_certs = pow(2, test_n)
    print(f'[0.0000] Starting tests with 2^{test_n} = {max_certs} certificates.')
  else:
    max_certs = args.seq[test_n]
    print(f'[0.0000] Starting tests with {max_certs} certificates.')

  build_times = []
  query_times = []
  nodes_no = []
  hard_solver_invokes = []

  for test_c in range(args.c):
    if args.verbose or test_n > 5:
      print(f'[0.0000] Starting test_{test_c}.')
    start_time_c = time.time()

    certs = []
    if args.config:
      for pol_no in policies_nos[test_counter]:
        if pol_no > 216:
          pol_name = f'FLAW1-Secure-{pol_no - 216}.json'
        else:
          pol_name = f'FLAW1-Error-{pol_no}.json'
        pol = policies[pol_name]
        cert = Certificate([pol], f'cert_{pol_no}({pol_name})')
        certs.append(cert)
      test_counter += 1
    else:
      for cert_count in range(max_certs):
        pol_name, pol = random.choice(list(policies.items()))
        cert = Certificate([pol], f'cert_{cert_count}({pol_name})')
        certs.append(cert)

    start_time = time.time()
    policy_graph = PolicyGraph(certs)
    policy_graph.build_sym_graph()
    build_time_c = time.time() - start_time
    build_times.append(build_time_c)
    nodes_no.append(policy_graph.size)
    hard_solver_invokes.append(policy_graph.hard_solver_invokes)
    if args.verbose or test_n > 5:
      print(f'[{build_time_c:.4f}] '
            f'Test_{test_c} -- Built symbolic information flow graph of {policy_graph.size} nodes.')

    prover = Prover(policy_graph.graph)
    start_time = time.time()
    for test_reach_count in range(1000):
      cert1 = random.choice(certs)
      cert2 = random.choice(certs)
      result = prover.reach(cert1.name, cert2.name)
    query_time_c = time.time() - start_time
    query_times.append(query_time_c)
    if args.verbose or test_n > 5:
      print(f'[{query_time_c:.4f}] '
            f'Test_{test_c} -- Run 1000 reach queries in {query_time_c}s.')
      print(f'[{query_time_c:.4f}] '
            f'Test_{test_c} ended ({time.time() - start_time_c}s).')
  
  mean_build_times = numpy.mean(build_times)
  mean_nodes_no = numpy.mean(nodes_no)
  mean_query_times = numpy.mean(query_times)
  mean_hs_invokes = numpy.mean(hard_solver_invokes)

  if power_two_tests:
    print(f'[END   ] Run {args.c} tests for 2^{test_n} certs with the following averages:')
  else:
    print(f'[END   ] Run {args.c} tests for {max_certs} certs with the following averages:')

  print(f'\t Average build time: \t \t{mean_build_times:.4f} \t -- \t{["{:.2f}".format(i) for i in build_times]}')
  print(f'\t Average nodes: \t\t {mean_nodes_no} \t -- \t{nodes_no} ')
  print(f'\t Average query times: \t \t{mean_query_times:.4f} \t -- \t{["{:.2f}".format(i) for i in query_times]}')
  print(f'\t Average hard solvers: \t \t{mean_hs_invokes} \t -- \t{hard_solver_invokes}')
