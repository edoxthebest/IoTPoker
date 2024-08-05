import z3
import time
# z3.set_option(verbose=8) 
z3.set_param('smt.string_solver','z3str3')


RE_QMARK = z3.Union(z3.Range('a', 'z'),
                    z3.Range('A', 'Z'),
                    z3.Range('0', '9'),
                    z3.Re('+'),
                    z3.Re('#'),
                    z3.Re('/'))
RE_STAR = z3.Star(RE_QMARK)

RE_QMARK_NO_SLASH = z3.Union(z3.Range('a', 'z'),
                             z3.Range('A', 'Z'),
                             z3.Range('0', '9'),
                             z3.Re('+'),
                             z3.Re('#'))
RE_STAR_NO_SLASH = z3.Star(RE_QMARK_NO_SLASH)
RE_SLASH = z3.Concat(RE_STAR_NO_SLASH, z3.Re('/'), RE_STAR_NO_SLASH)

id1 = z3.String('id_1')
id2 = z3.String('id_2')
topic = z3.String('topic')
topic_filter = z3.String('topic_filter')

topic_levels = z3.Strings('topic_lv_0 topic_lv_1 topic_lv_2 topic_lv_3 topic_lv_4 topic_lv_5 topic_lv_6 topic_lv_7')
tf_levels = z3.Strings('tf_lv_0 tf_lv_1 tf_lv_2 tf_lv_3 tf_lv_4 tf_lv_5 tf_lv_6 tf_lv_7')

s = z3.Solver()

# TODO: check whether the z3.not has any impact on performance (when empty)
# ID1
s.add(z3.And(z3.InRe(id1, z3.Concat(z3.Re("badgeReader"),
                                    RE_QMARK, RE_QMARK)),
             z3.Not(z3.InRe(id1, z3.Empty(z3.ReSort(z3.StringSort()))))))

# ID2
s.add(z3.And(z3.InRe(id2, z3.Re('aaa')),
             z3.Not(z3.InRe(id2, z3.Empty(z3.ReSort(z3.StringSort()))))))

# PUB
s.add(z3.And(z3.InRe(topic,z3.Concat(z3.Re("physicalAC/floor1/"), z3.Re(id1), z3.Re("/check"))),
             z3.Not(z3.InRe(topic, z3.Empty(z3.ReSort(z3.StringSort()))))))

# REC
s.add(z3.And(z3.InRe(topic, RE_STAR),
             z3.Not(z3.InRe(topic, z3.Empty(z3.ReSort(z3.StringSort()))))))

# SUB
s.add(z3.And(z3.InRe(topic_filter, z3.Concat(z3.Re('physicalAC/floor'), RE_QMARK, z3.Re('/detectedMovement/'), z3.Re(id2))),
             z3.Not(z3.InRe(topic_filter, z3.Empty(z3.ReSort(z3.StringSort()))))))

#TODO: can we do this any differently
for level in topic_levels:
  s.add(z3.Not(z3.Contains(level, '/')))
# for level in tf_levels:
#   s.add(z3.Not(z3.Contains(level, '/')))
  
# Is this the problem?
def get_topic_for_level(level):
  topic_T = ['', topic_levels[0]]
  for topic_level in range(level):
    topic_T.append('/')
    topic_T.append(topic_levels[topic_level + 1])
  return z3.Concat(topic_T)
def get_tf_for_level(level):
  topic_filter = ['', tf_levels[0]]
  for tf_level in range(level):
    topic_filter.append('/')
    topic_filter.append(tf_levels[tf_level + 1])
  return z3.Concat(topic_filter)


assertions = s.assertions()

def print_model(model):
  for k,v in sorted([(k, model[k]) for k in model], key = lambda x: str(x[0])):
    print(f'\t{k}\t->\t{v}')

t = time.time()
for topic_level in range(8):
  s1 = z3.Solver()
  s1.add(assertions)
  s1.add(topic == get_topic_for_level(topic_level))
  # if topic_level == 0:
  #   s1.add(z3.Not(z3.Contains(topic, '/')))
  # else:
  #   s1.add(z3.InRe(topic, z3.Loop(RE_SLASH, topic_level, topic_level)))

  # print(s1.assertions())
  # for i,v in enumerate(s1.assertions()):
  #   print(f'{i} -> {v}')

  start_time = time.time()
  if s1.check() == z3.unsat:
    print(f'T:{time.time() - start_time} -- #{topic_level+1} topic levels is {z3.unsat}')
    continue
  print(f'T:{time.time() - start_time} -- #{topic_level+1} topic levels is {z3.sat}')
  print_model(s1.model())
  
  # CASE1: same length
  start_time = time.time()
  s_case_1 = z3.Solver()
  s_case_1.add(s1.assertions())
  s_case_1.add(topic_filter == get_tf_for_level(topic_level))
  if topic_level == 0:
    s_case_1.add(z3.Not(z3.Contains(topic_filter, '/')))
  else:
    s_case_1.add(z3.InRe(topic_filter, z3.Loop(RE_SLASH, topic_level, topic_level)))

  for level in range(topic_level+1):
    s_case_1.add(z3.Or(tf_levels[level] == topic_levels[level],
                tf_levels[level] == '+',
                tf_levels[level] == '#' if level == topic_level else False))

  if s_case_1.check() == z3.sat:
    print(f'T:{time.time() - start_time} -- CASE 1 -- FOUND')
    print_model(s_case_1.model())
    exit()
  print(f'T:{time.time() - start_time} -- CASE 1 -- DONE')

  # CASE 2: using # at the end of a shorter tf
  start_time = time.time()
  for tf_level in range(topic_level):
    s_case_2 = z3.Solver()
    s_case_2.add(s1.assertions())
    s_case_2.add(topic_filter == get_tf_for_level(tf_level))
    s_case_2.add(tf_levels[tf_level] == '#')
    for level in range(tf_level):
      s_case_2.add(z3.Or(tf_levels[level] == topic_levels[level],
                  tf_levels[level] == '+'))
    if s_case_2.check() == z3.sat:
      print(f'T:{time.time() - start_time} -- CASE 2 -- FOUND')
      print_model(s_case_2.model())
      exit()
    print(f'T:{time.time() - start_time} -- CASE 2 -- DONE')
    
print(f'T:{time.time() - t} -- NONE FOUND')
exit()

