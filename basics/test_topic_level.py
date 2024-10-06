import z3
import time
# z3.set_option(verbose=10)

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
RE_QMARK_CHARS_ONLY = z3.Union(z3.Range('a', 'z'),
                             z3.Range('A', 'Z'),
                             z3.Range('0', '9'))
RE_STAR_CHARS_ONLY = z3.Star(RE_QMARK_CHARS_ONLY)
RE_SLASH = [RE_STAR_NO_SLASH, z3.Re('/')]

id1 = z3.String('id_1')
id2 = z3.String('id_2')
# topic = z3.String('topic')
topic_filter = z3.String('topic_filter')

topic_levels = z3.Strings('topic_lv_0 topic_lv_1 topic_lv_2 topic_lv_3 topic_lv_4 topic_lv_5 topic_lv_6 topic_lv_7')
# tf_levels = z3.Strings('tf_lv_0 tf_lv_1 tf_lv_2 tf_lv_3 tf_lv_4 tf_lv_5 tf_lv_6 tf_lv_7')

def get_topic_for_level(level):
  if level == 0:
    return topic_levels[0]
  
  topic_T = [topic_levels[0]]
  for topic_level in range(level):
    topic_T.append('/')
    topic_T.append(topic_levels[topic_level + 1])
  return z3.Concat(topic_T)

# def get_tf_for_level(level):
#   topic_filter = ['', tf_levels[0]]
#   for tf_level in range(level):
#     topic_filter.append('/')
#     topic_filter.append(tf_levels[tf_level + 1])
#   return z3.Concat(topic_filter)

# TODO: check whether the z3.not has any impact on performance (when empty)
def get_basic_solver(level):
  topic = get_topic_for_level(level)
  # topic_filter = get_tf_for_level(level)
  
  solver = z3.Solver()
  solver.add(z3.Length(topic) < 30)

  for i in range(level+1):
    solver.add(z3.InRe(topic_levels[i], RE_STAR_CHARS_ONLY))
  
  # ID1
  solver.add(z3.And(z3.InRe(id1, z3.Concat(z3.Re("badgeReader"),
                                      RE_QMARK, RE_QMARK)),
              z3.Not(z3.InRe(id1, z3.Empty(z3.ReSort(z3.StringSort()))))))
  # ID2
  solver.add(z3.And(z3.InRe(id2, RE_STAR), #z3.Re('aaa')),
              z3.Not(z3.InRe(id2, z3.Empty(z3.ReSort(z3.StringSort()))))))
  # PUB
  solver.add(z3.And(z3.InRe(topic,z3.Concat(z3.Re("physicalAC/floor1/"), z3.Re(id1), z3.Re("/check"))),
              z3.Not(z3.InRe(topic, z3.Empty(z3.ReSort(z3.StringSort()))))))
  
  # REC
  solver.add(z3.And(z3.InRe(topic, RE_STAR),
              z3.Not(z3.InRe(topic, z3.Empty(z3.ReSort(z3.StringSort()))))))
  # SUB
  solver.add(z3.And(z3.InRe(topic_filter, z3.Concat(z3.Re('physicalAC/floor'), RE_QMARK, z3.Re('/detectedMovement/'), z3.Re(id2))),
              z3.Not(z3.InRe(topic_filter, z3.Empty(z3.ReSort(z3.StringSort()))))))
  
  
  return solver

#TODO: can we do this any differently
# for level in topic_levels:
#   s.add(z3.Not(z3.Contains(level, '/')))
#   s.add(z3.InRe(level, RE_STAR_NO_SLASH))
  #TODO: look into this. think issue is here
# for level in tf_levels:
#   s.add(z3.Not(z3.Contains(level, '/')))
  
# Is this the problem?




def print_model(model):
  for k,v in sorted([(k, model[k]) for k in model], key = lambda x: str(x[0])):
    print(f'\t{k}\t->\t{v}')

t = time.time()
for topic_level in range(8):
  
  s1 = get_basic_solver(topic_level)
  # s1.add(topic == get_topic_for_level(topic_level))
  # if topic_level == 0:
  #   s1.add(z3.Not(z3.Contains(topic, '/')))
  # else:
  #   s1.add(z3.InRe(topic, z3.Concat(z3.Loop(z3.Concat(RE_STAR_NO_SLASH, z3.Re('/')), topic_level, topic_level), RE_STAR_NO_SLASH)))
  case_1 = []
  for i in range(topic_level):
    case_1.append(z3.Union(z3.Re(topic_levels[i]), z3.Re('+')))
    case_1.append(z3.Re('/'))
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

  s1.add(z3.Or(z3.InRe(topic_filter, z3.Concat(case_1) if topic_level != 0 else case_1[0]),
               z3.Or(case_2 if topic_level != 0 else False)))
  start_time = time.time()
  if s1.check() == z3.unsat:
    print(f'T:{time.time() - start_time} -- #{topic_level+1} topic levels is {z3.unsat}')
    continue
  print(f'T:{time.time() - start_time} -- #{topic_level+1} topic levels is {z3.sat}')
  print_model(s1.model())
  
  continue
  # CASE1: same length
  # z3.set_param('smt.string_solver','z3str3')
  start_time = time.time()
  s_case_1 = z3.Solver()
  s_case_1.set('timeout', 20000)
  s_case_1.add(s1.assertions())

  # s_case_1.add(topic == get_topic_for_level(topic_level))
  # s_case_1.add(topic_filter == get_tf_for_level(topic_level))

  s_case_1.add(z3.InRe(topic_filter, z3.Concat(z3.Loop(z3.Concat(RE_STAR_NO_SLASH, z3.Re('/')), topic_level, topic_level), RE_STAR_NO_SLASH)))

  # for level in range(topic_level + 1):
  #   s_case_1.add(z3.Not(z3.Contains(topic_levels[level], '/')))
    # s_case_1.add(z3.Not(z3.Contains(tf_levels[level], '/')))
    
  for level in range(topic_level+1):
    s_case_1.add(z3.Or(tf_levels[level] == topic_levels[level],
                tf_levels[level] == '+',
                tf_levels[level] == '#' if level == topic_level else False))
  # s_case_1.add(topic_filter == get_tf_for_level(topic_level))


  if s_case_1.check() == z3.sat:
    print(f'T:{time.time() - start_time} -- CASE 1 -- FOUND')
    print_model(s_case_1.model())
    # exit()
  elif s_case_1.check() == z3.unknown:
    print(f'T:{time.time() - start_time} -- CASE 1 -- UNKNOWN')
  print(f'T:{time.time() - start_time} -- CASE 1 -- DONE')


  continue
  # continue
  # CASE1: same length
  start_time = time.time()
  s_case_1 = get_basic_solver()
  s_case_1.add(topic == get_topic_for_level(topic_level))
  for level in topic_levels[:topic_level + 1]:
    s_case_1.add(z3.InRe(level, RE_STAR_NO_SLASH))
  # s_case_1 = z3.Solver()
  s_case_1.set('timeout', 10000)
  # s_case_1.add(s1.assertions())
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
    exit()
  elif s_case_1.check() == z3.unknown:
    print(f'T:{time.time() - start_time} -- CASE 1 -- UNKNOWN')
  print(f'T:{time.time() - start_time} -- CASE 1 -- DONE')

  continue

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

