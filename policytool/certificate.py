import z3
from policytool.iot_policy import IoTPolicy
from policytool.topic_witness import TopicWitness
# z3.set_option(verbose=10) 

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
  
  def get_topic_witness(self, other: 'Certificate') -> TopicWitness:
    id1 = z3.String('id_1')
    id2 = z3.String('id_2')
    topic = z3.String('topic')
    topic_filter = z3.String('topic_filter')

    # Init solver and test for the following necessary conditions:
    s = z3.Solver()
    s.add(self.get_connect(id1))                    # c1 can connect
    s.add(other.get_connect(id2))                   # c2 can connect
    s.add(self.get_publish(topic, id1))             # c1 can publish on a topic t
    s.add(other.get_receive(topic, id2))            # c2 can receive on the same topic t
    s.add(other.get_subscribe(topic_filter, id2))   # c2 can subscribe to some topic filter
    if s.check() == z3.unsat:
      return None
    
    # Test for an easy solution: c2 can subscribe to t
    s.push()
    s.add(topic == topic_filter)
    if s.check() == z3.sat:
      return TopicWitness(self, other, s)
    s.pop()
    
    # TOPIC LEVELS
    # topic_levels = z3.Strings('topic_lv_0 topic_lv_1 '
    #                           'topic_lv_2 topic_lv_3 '
    #                           'topic_lv_4 topic_lv_5 '
    #                           'topic_lv_6 topic_lv_7')
    topic_levels = z3.Strings('topic_lv_0 topic_lv_1 topic_lv_2 topic_lv_3 topic_lv_4 topic_lv_5 topic_lv_6 topic_lv_7')
    for level in topic_levels:
      s.add(z3.Not(z3.Contains(level, '/')))

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
    for level in tf_levels:
      s.add(z3.Not(z3.Contains(level, '/')))

    def get_tf_for_level(level):
      topic_filter = ['', tf_levels[0]]
      for tf_level in range(level):
        topic_filter.append('/')
        topic_filter.append(tf_levels[tf_level + 1])
      return z3.Concat(topic_filter)

    s_asserts = s.assertions()
    for topic_level in range(8):
      # s.push()
      s_new = z3.Solver()
      s_new.add(s_asserts)
      s_new.add(topic == get_topic_for_level(topic_level))
      if s_new.check() == z3.unsat:
        print(f'#{topic_level+1} topic levels is {z3.unsat}')
        # s.pop()
        continue
      print(f'#{topic_level+1} topic levels is {z3.sat}')
      print(s_new.model())
      
      # CASE1: same length
      print('-- CASE1')
      # s.push()
      s_case_1 = z3.Solver()
      s_case_1.add(s_new.assertions())
      s_case_1.add(topic_filter == get_tf_for_level(topic_level))
      for level in range(topic_level+1):
        s_case_1.add(z3.Or(tf_levels[level] == topic_levels[level],
                    tf_levels[level] == '+',
                    tf_levels[level] == '#' if level == topic_level else False)) 
      if s_case_1.check() == z3.sat:
        print('FOUND')
        print(s_case_1.model())
        return TopicWitness(self, other, s_case_1)
      # s.pop()

      print('--- CASE2')
      # CASE 2: using # at the end of a shorter tf
      for tf_level in range(topic_level):
        # s.push()
        s_case_2 = z3.Solver()
        s_case_2.add(s_new.assertions())
        s_case_2.add(topic_filter == get_tf_for_level(tf_level))
        s_case_2.add(tf_levels[tf_level] == '#')
        for level in range(tf_level):
          s_case_2.add(z3.Or(tf_levels[level] == topic_levels[level],
                      tf_levels[level] == '+'))
        if s_case_2.check() == z3.sat:
          print('FOUND')
          print(s_new.model())
          return TopicWitness(self, other, s_new)
        # s.pop()

      # s.pop()
    
    print('---- None found')
    return None
  # TODO: might be smart to add here method that takes solver and adds correct queries to it