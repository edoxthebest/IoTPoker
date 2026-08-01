import argparse
import logging
import numpy
import random
import time
from policytool import Certificate, PolicyGraph, PolicyReader, Prover, Thing

parser = argparse.ArgumentParser(description='Evaluates the performance of each solver used.')
parser.add_argument('dir', type=str)
parser.add_argument('--debug', action='store_true')
parser.add_argument('--info', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()
if args.debug:
  # logging.StreamHandler.terminator = '\r'
  logging.getLogger('IoT:Poker').setLevel(logging.DEBUG)
if args.info:
  logging.StreamHandler.terminator = '\r'
  logging.getLogger('IoT:Poker').setLevel(logging.INFO)


bench_dir = args.dir
start_time = time.time()
PolicyReader.read_policy_dir(bench_dir)
policies = PolicyReader._policies
print(f'[{time.time() - start_time:.4f}] '
      f'Read {len(policies)} policies from {bench_dir}.')

policies_nos = range(1, 259)
print(f'[0.0000] Starting tests with {len(policies_nos)} certificates.')

nodes_no = []
start_time_c = time.time()

certs = []
for pol_no in policies_nos:
  if pol_no > 216:
    pol_name = f'FLAW1-Secure-{pol_no - 216}.json'
  else:
    pol_name = f'FLAW1-Error-{pol_no}.json'
  pol = policies[pol_name]
  cert = Certificate([pol], f'cert_{pol_no}({pol_name})')
  certs.append(cert)

start_time = time.time()
policy_graph = PolicyGraph(certs)
policy_graph.build_sym_graph()
build_time = time.time() - start_time
nodes_no = policy_graph.size

prover = Prover(policy_graph.graph)
start_time = time.time()
for test_reach_count in range(1000):
  cert1 = random.choice(certs)
  cert2 = random.choice(certs)
  result = prover.reach(cert1.name, cert2.name)
query_time = time.time() - start_time


print(f'\t Build time: \t \t{build_time:.4f}')
print(f'\t Nodes: \t\t {nodes_no}')
print(f'\t Queries time: \t \t{query_time:.4f}')

print('\t -------------------- Solver Execution Details -------------------- ')
print(f'\t Known witnesses: \t \t{policy_graph.known_witness_count}')

early_exit_solver_invokes = policy_graph.early_exit_solver_invokes + policy_graph.radix_solver_invokes
early_exit_solver_times = policy_graph.early_exit_solver_times + policy_graph.radix_solver_times
early_success_solver_invokes = policy_graph.early_success_solver_invokes
early_success_solver_times = policy_graph.early_success_solver_times
hard_solver_invokes = policy_graph.hard_solver_invokes
hard_solver_times = policy_graph.hard_solver_times
tot_solvers_invokes = early_exit_solver_invokes + early_success_solver_invokes + hard_solver_invokes

if early_exit_solver_invokes:
  print(f'\t Early exits: \t \t{early_exit_solver_invokes} -- {100 * early_exit_solver_invokes / tot_solvers_invokes}')
  print(f'\t Average early exit solver times: \t \t{numpy.mean(early_exit_solver_times):.4f} -- \t{["{:.4f}".format(i) for i in early_exit_solver_times]}')
  
if early_success_solver_invokes:
  print(f'\t Early successes: \t \t{early_success_solver_invokes} -- {100 * early_success_solver_invokes / tot_solvers_invokes}')
  print(f'\t Average early success solver times: \t \t{numpy.mean(early_success_solver_times):.4f} -- \t{["{:.4f}".format(i) for i in early_success_solver_times]}')

if hard_solver_invokes:
  print(f'\t Hard solvers: \t \t{hard_solver_invokes} -- {100 * hard_solver_invokes / tot_solvers_invokes}')
  print(f'\t Average hard solver times: \t \t{numpy.mean(hard_solver_times):.4f} -- \t{["{:.4f}".format(i) for i in hard_solver_times]}')
