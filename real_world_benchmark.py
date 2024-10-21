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
parser.add_argument('-c', type=int, default=1, help='Number of tests carried out for each cert count.')
parser.add_argument('--debug', action='store_true')
parser.add_argument('--info', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()
if args.debug:
  logging.getLogger('IoT:Poker').setLevel(logging.DEBUG)
if args.info:
  logging.getLogger('IoT:Poker').setLevel(logging.INFO)

bench_dir = args.dir
start_time = time.time()
PolicyReader.read_policy_dir(bench_dir)
policies = PolicyReader._policies
print(f'[{time.time() - start_time:.4f}] '
      f'Read {len(policies)} policies from {bench_dir}.')

for test_n in range(args.min, args.n):
  print(f'[0.0000] Starting tests with 2^{test_n} = {pow(2, test_n)} certificates).')
  build_times = []
  query_times = []
  nodes_no = []

  for test_c in range(args.c):
    if args.verbose or test_n > 5:
      print(f'[0.0000] Starting test_{test_c}.')
    start_time_c = time.time()

    certs = []
    for cert_count in range(pow(2, test_n)):
      pol_name, pol = random.choice(list(policies.items()))
      cert = Certificate([pol], f'cert_{cert_count}')
      certs.append(cert)

    start_time = time.time()
    policy_graph = PolicyGraph(certs)
    policy_graph.build_sym_graph()
    build_time_c = time.time() - start_time
    build_times.append(build_time_c)
    nodes_no.append(policy_graph.size)
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
  print(f'[END   ] Run {args.c} test for 2^{test_n} certs with the following averages:')
  print(f'\t Average build time: \t{mean_build_times}')
  print(f'\t Average number of nodes: \t{mean_nodes_no}')
  print(f'\t Average query times: \t{mean_query_times}')
