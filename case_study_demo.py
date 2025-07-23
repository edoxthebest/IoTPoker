import argparse
import json
import logging
import time
from policytool import Certificate, PolicyGraph, PolicyReader, Prover, Thing

parser = argparse.ArgumentParser(description='Evaluates the case study.')
parser.add_argument('--fixed', action='store_true',
                    help='Uses the corrected policy version')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()
if args.debug:
  logging.getLogger('IoT:Poker').setLevel(logging.DEBUG)

case_study_dir = 'tests/policies/case-study/'
things_dir = 'tests/things/'
cfg_filename = 'case_study_fixed.config' if args.fixed else 'case_study.config'

things = []
certs = []
start_time = time.time()
with open(cfg_filename) as config_file:
  config = json.load(config_file)
  for thing_json in config['things']:
    thing_pol = PolicyReader.read_policy_file(case_study_dir + thing_json['policy'])
    thing = Thing.from_file(things_dir + thing_json['file'], thing_pol)
    things.append(thing)
  for cert_json in config['certs']:
    cert_pol = PolicyReader.read_policy_file(case_study_dir + cert_json['policy'])
    cert = Certificate([cert_pol], cert_json['name'])
    certs.append(cert)
print(f'[{time.time() - start_time:.4f}] '
      f'Read {len(certs)} policy certificates and {len(things)} things.')

start_time = time.time()
policy_graph = PolicyGraph(certs + things)
policy_graph.build_sym_graph()
print(f'[{time.time() - start_time:.4f}] '
      f'Built symbolic information flow graph of {policy_graph.size} nodes.')

# policy_graph.draw_tree(['floor1_badge_reader'])

prover = Prover(policy_graph.graph)
if args.fixed:
  prover.reach('presenceSensor1','light1', log_level='info') 
else:
  prover.reach('presenceSensor1','floor1_light', log_level='info') 
prover.reach('floor1_smoke_sensor','elevator', log_level='info')                      
prover.reach('floor1_door_lock', 'floor2_light', log_level='info')
prover.reach('elevator', 'floor1_door_lock', log_level='info')

prover.reach_only('elevator', [], log_level='info')
if args.fixed:
  prover.reach_only('floor1_door_lock', ['light1', 'presenceSensor1', 'lambda_logger'], log_level='info')
else:
  prover.reach_only('floor1_door_lock', ['floor1_light', 'presenceSensor1', 'lambda_logger'], log_level='info')
prover.reach_only('floor1_smoke_sensor', ['elevator', 'floor1_door_lock'], log_level='info')
prover.reach_only('elevator', ['floor2_water_pump'], log_level='info')

prover.only_reached_by('elevator', [
    'lambda_fire_alarm', 
    'floor1_smoke_sensor', 
    'floor2_smoke_sensor',
    'floor1_fire_alarm',
    'floor2_fire_alarm'
  ], log_level='info')
prover.only_reached_by('floor1_fire_siren', [
    'floor1_smoke_sensor',
    'floor2_smoke_sensor',
    'floor1_fire_alarm',
    'floor2_fire_alarm',
    'lambda_fire_alarm',
    'elevator'
    ], log_level='info')
if args.fixed:
  prover.only_reached_by('light1', ['lambda_fire_alarm'], log_level='info')
else:
  prover.only_reached_by('floor1_light', ['lambda_fire_alarm'], log_level='info')

prover.isolated(['floor1_badge_reader'], ['floor1_water_pump', 'elevator'], log_level='info')
prover.isolated(['floor2_badge_reader'],
                ['lambda_fire_alarm', 'elevator', 'floor2_smoke_sensor'], log_level='info')
if args.fixed:
    prover.isolated(['light1', 'light2'],
                ['lambda_fire_alarm', 'elevator', 'floor2_smoke_sensor'], log_level='info')
else:
  prover.isolated(['floor1_light', 'floor2_light'],
                ['lambda_fire_alarm', 'elevator', 'floor2_smoke_sensor'], log_level='info')
