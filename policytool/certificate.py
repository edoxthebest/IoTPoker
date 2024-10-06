import time
import z3
from policytool.iot_policy import IoTPolicy
from policytool.topic_witness import TopicWitness
# z3.set_option(verbose=10)


RE_QMARK_NO_SLASH = z3.Union(z3.Range('a', 'z'),
                    z3.Range('A', 'Z'),
                    z3.Range('0', '9'),
                    z3.Re('+'),
                    z3.Re('#'))
RE_STAR_NO_SLASH = z3.Star(RE_QMARK_NO_SLASH)
RE_QMARK_CHARS_ONLY = z3.Union(z3.Range('a', 'z'),
                             z3.Range('A', 'Z'),
                             z3.Range('0', '9'))
RE_STAR_CHARS_ONLY = z3.Star(RE_QMARK_CHARS_ONLY)
RE_SLASH = [RE_STAR_NO_SLASH, z3.Re('/')]

def print_model(model):
  for k,v in sorted([(k, model[k]) for k in model], key = lambda x: str(x[0])):
    print(f'\t{k}\t->\t{v}')

class Certificate:
  @property
  def name(self):
    return self._name
  
  @property
  def policy(self):
    return self._policy
  
  #TODO: check order here -- might result in errors
  def __init__(self, policies: list[IoTPolicy], name: str = None):
    self._policy = IoTPolicy.union(policies)
    self._name = name if not name is None else self.policy.client
    
  def get_connect(self, id: z3.SeqRef):
    return self.policy.build_connect(id)
  
  def get_publish(self, topic: z3.SeqRef, id: z3.SeqRef):
    return self.policy.build_publish(topic, id)
  
  def get_subscribe(self, topic: z3.SeqRef, id: z3.SeqRef):
    return self.policy.build_subscribe(topic, id)
    
  def get_receive(self, topic: z3.SeqRef, id: z3.SeqRef):
    return self.policy.build_receive(topic, id)
  
  def _get_basic_solver(self, other, id1, id2, topic, topic_filter, topic_lvls = []):
    s = z3.Solver()
    s.add(z3.Length(topic) < 15)
    for topic_level in topic_lvls:
      s.add(z3.InRe(topic_level, RE_STAR_CHARS_ONLY))
    s.add(self.get_connect(id1))                    # c1 can connect
    s.add(other.get_connect(id2))                   # c2 can connect
    s.add(self.get_publish(topic, id1))             # c1 can publish on a topic t
    s.add(other.get_receive(topic, id2))            # c2 can receive on the same topic t
    s.add(other.get_subscribe(topic_filter, id2))   # c2 can subscribe to some topic filter
    return s
  
  def get_topic_witness(self,other: 'Certificate') -> TopicWitness:
    id1 = z3.String('id_1')
    id2 = z3.String('id_2')
    topic = z3.String('topic')
    topic_filter = z3.String('topic_filter')
    
    # Init solver and test for the following necessary conditions:
    easy_solver = self._get_basic_solver(other, id1, id2, topic, topic_filter)
    if easy_solver.check() == z3.unsat:
      return None
    
    # Test for an easy solution: c2 can subscribe to t
    easy_solver.add(topic == topic_filter)
    if easy_solver.check() == z3.sat:
      return TopicWitness(self, other, easy_solver)
    
    topic_levels = z3.Strings('topic_lv_0 topic_lv_1 topic_lv_2 '
                              'topic_lv_3 topic_lv_4 topic_lv_5 '
                              'topic_lv_6 topic_lv_7')
    def get_topic_for_level(level):
      if level == 0:
        return topic_levels[0]
      
      topic_T = [topic_levels[0]]
      for topic_level in range(level):
        topic_T.append('/')
        topic_T.append(topic_levels[topic_level + 1])
      return z3.Concat(topic_T)
    
    global_t = time.time()
    for topic_level in range(8):
      hard_solver = self._get_basic_solver(other, id1, id2, get_topic_for_level(topic_level), topic_filter, topic_levels[0:topic_level+1])
      case_1 = []
      for i in range(topic_level):
        # hard_solver.add(z3.InRe(topic_levels[i], RE_STAR_NO_SLASH))
        case_1.append(z3.Union(z3.Re(topic_levels[i]), z3.Re('+')))
        case_1.append(z3.Re('/'))
      # hard_solver.add(z3.InRe(topic_levels[topic_level], RE_STAR_NO_SLASH))
      case_1.append(z3.Union(z3.Re(topic_levels[topic_level]),
                          z3.Re('+'),
                          z3.Re('#')))

      case_2 = []
      for i in range(topic_level):
        sub_case_2 = []
        for j in range(i):
          sub_case_2.append(z3.Union(z3.Re(topic_levels[j]), z3.Re('+')))
          sub_case_2.append(z3.Re('/'))
        sub_case_2.append(z3.Re('#'))
        case_2.append(z3.InRe(topic_filter, z3.Concat(sub_case_2) if i != 0 else sub_case_2[0]))

      hard_solver.add(z3.Or(z3.InRe(topic_filter, z3.Concat(case_1) if topic_level != 0 else case_1[0]),
                            z3.Or(case_2 if topic_level != 0 else False)))


      # hard_solver.add(z3.InRe(topic_filter, z3.Concat(case_1) if topic_level != 0 else case_1[0]))

      start_time = time.time()
      if hard_solver.check() == z3.unsat:
        print(f'T:{time.time() - start_time} -- #{topic_level+1} topic levels is {z3.unsat}')
        continue
      print(f'T:{time.time() - start_time} -- #{topic_level+1} topic levels is {z3.sat}')
      print_model(hard_solver.model())
      return TopicWitness(self, other, hard_solver)

    print(f'T:{time.time() - global_t} -- NONE FOUND')
    return None

  
  def get_topic_witness_old(self, other: 'Certificate') -> TopicWitness:
    id1 = z3.String('id_1')
    id2 = z3.String('id_2')
    topic = z3.String('topic')
    topic_filter = z3.String('topic_filter')

    # Init solver and test for the following necessary conditions:
    # s = z3.Solver()
    # s.add(self.get_connect(id1))                    # c1 can connect
    # s.add(other.get_connect(id2))                   # c2 can connect
    # s.add(self.get_publish(topic, id1))             # c1 can publish on a topic t
    # s.add(other.get_receive(topic, id2))            # c2 can receive on the same topic t
    # s.add(other.get_subscribe(topic_filter, id2))   # c2 can subscribe to some topic filter
    s = self._get_basic_solver(other, id1, id2, topic, topic_filter)
    if s.check() == z3.unsat:
      return None
    
    # Test for an easy solution: c2 can subscribe to t
    s.add(topic == topic_filter)
    if s.check() == z3.sat:
      return TopicWitness(self, other, s)
        
    # TOPIC LEVELS
    # topic_levels = z3.Strings('topic_lv_0 topic_lv_1 '
    #                           'topic_lv_2 topic_lv_3 '
    #                           'topic_lv_4 topic_lv_5 '
    #                           'topic_lv_6 topic_lv_7')
    topic_levels = z3.Strings('topic_lv_0 topic_lv_1 topic_lv_2 topic_lv_3 topic_lv_4 topic_lv_5 topic_lv_6 topic_lv_7')
    # for level in topic_levels:
    #   s.add(z3.Not(z3.Contains(level, '/')))

    def get_topic_for_level(level):
      topic_T = ['', topic_levels[0]]
      for topic_level in range(level):
        topic_T.append('/')
        topic_T.append(topic_levels[topic_level + 1])
      return z3.Concat(topic_T)

    # TOPIC FILTER LEVELS
    # tf_levels = z3.Strings('tf_lv_0 tf_lv_1 tf_lv_2 tf_lv_3 '
    #                        'tf_lv_4 tf_lv_5 tf_lv_6 tf_lv_7')
    tf_levels = z3.Strings('tf_lv_0 tf_lv_1 tf_lv_2 tf_lv_3 tf_lv_4 tf_lv_5 tf_lv_6 tf_lv_7')
    # for level in tf_levels:
    #   s.add(z3.Not(z3.Contains(level, '/')))

    def get_tf_for_level(level):
      topic_filter = ['', tf_levels[0]]
      for tf_level in range(level):
        topic_filter.append('/')
        topic_filter.append(tf_levels[tf_level + 1])
      return z3.Concat(topic_filter)

    global_t = time.time()
    for topic_level in range(8):
      z3.set_param('smt.string_solver','seq')
      s_tlevels = z3.Solver()
      # s_tlevels.add(s.assertions())
      # s_tlevels.add(self.get_connect(id1))                    # c1 can connect
      # s_tlevels.add(other.get_connect(id2))                   # c2 can connect
      # s_tlevels.add(self.get_publish(topic, id1))             # c1 can publish on a topic t
      # s_tlevels.add(other.get_receive(topic, id2))            # c2 can receive on the same topic t
      # s_tlevels.add(other.get_subscribe(topic_filter, id2))   # c2 can subscribe to some topic filter
      s_tlevels = self._get_basic_solver(other, id1, id2, topic, topic_filter)

      s_tlevels.add(topic == get_topic_for_level(topic_level))
      for level in topic_levels[:topic_level + 1]:
        s_tlevels.add(z3.Not(z3.Contains(level, '/')))

      # if topic_level == 0:
      #   s_tlevels.add(z3.Not(z3.Contains(topic, '/')))
      # else:
      #   s_tlevels.add(z3.InRe(topic, z3.Concat(RE_SLASH * topic_level + [RE_STAR_NO_SLASH])))
      #   # s_tlevels.add(z3.InRe(topic, z3.Loop(RE_SLASH, topic_level, topic_level)))

      start_time = time.time()
      if s_tlevels.check() == z3.unsat:
        print(f'T:{time.time() - start_time} -- #{topic_level+1} topic levels is {z3.unsat}')
        continue
      print(f'T:{time.time() - start_time} -- #{topic_level+1} topic levels is {z3.sat}')
      print_model(s_tlevels.model())
        
      
      # CASE1: same length
      z3.set_param('smt.string_solver','z3str3')
      start_time = time.time()
      s_case_1 = z3.Solver()
      s_case_1.add(s_tlevels.assertions())
      # s_case_1 = self._get_basic_solver(other, id1, id2, topic, topic_filter)
      # s_case_1.add(topic == get_topic_for_level(topic_level))
      # for level in topic_levels[:topic_level + 1]:
      #   s_case_1.add(z3.Not(z3.Contains(level, '/')))
      s_case_1.add(topic_filter == get_tf_for_level(topic_level))
      if topic_level == 0:
        s_case_1.add(z3.Not(z3.Contains(topic_filter, '/')))
      else:
        s_case_1.add(z3.InRe(topic_filter, z3.Concat(RE_SLASH * topic_level + [RE_STAR_NO_SLASH])))
        # s_case_1.add(z3.InRe(topic_filter, z3.Loop(RE_SLASH, topic_level, topic_level)))

      for level in range(topic_level+1):
        s_case_1.add(z3.Or(tf_levels[level] == topic_levels[level],
                    tf_levels[level] == '+',
                    tf_levels[level] == '#' if level == topic_level else False))

      if s_case_1.check() == z3.sat:
        print(f'T:{time.time() - start_time} -- CASE 1 -- FOUND')
        print_model(s_case_1.model())
        return TopicWitness(self, other, s_case_1)
      print(f'T:{time.time() - start_time} -- CASE 1 -- DONE')

      continue
      # CASE 2: using # at the end of a shorter tf
      start_time = time.time()
      for tf_level in range(topic_level):
        s_case_2 = z3.Solver()
        s_case_2.add(s_tlevels.assertions())
        s_case_2.add(topic_filter == get_tf_for_level(tf_level))
        s_case_2.add(tf_levels[tf_level] == '#')
        for level in range(tf_level):
          s_case_2.add(z3.Or(tf_levels[level] == topic_levels[level],
                      tf_levels[level] == '+'))
        if s_case_2.check() == z3.sat:
          print(f'T:{time.time() - start_time} -- CASE 2 -- FOUND')
          print_model(s_case_2.model())
          return TopicWitness(self, other, s_case_2)
        print(f'T:{time.time() - start_time} -- CASE 2 -- DONE')
    
    print(f'T:{time.time() - global_t} -- NONE FOUND')
    return None
  # TODO: might be smart to add here method that takes solver and adds correct queries to it
  
  #TODO: should commit this then work backwards -> check what makes the solver take more time and optimise
  #      this works tho
  #      CASE2 should be better tested.