import json
from policytool import Certificate, PolicyGraph, PolicyReader, Thing

case_study_dir = 'tests/policies/case-study/'
things_dir = 'tests/things/'

things = []
certs = []
with open('case_study.config') as config_file:
  config = json.load(config_file)
  for thing_json in config['things']:
    thing_pol = PolicyReader.read_policy_file(case_study_dir + thing_json['policy'])
    thing = Thing.from_file(things_dir + thing_json['file'], thing_pol)
    things.append(thing)
  for cert_json in config['certs']:
    cert_pol = PolicyReader.read_policy_file(case_study_dir + cert_json['policy'])
    cert = Certificate([cert_pol], cert_json['name'])
    certs.append(cert)

policy_graph = PolicyGraph(certs + things)
policy_graph.build_sym_graph()
# policy_graph.draw_tree(['floor1_badge_reader'])
