import z3

id1 = z3.String('id_1')
id2 = z3.String('id_2')
topic = z3.String('topic')
topic_filter = z3.String('topic_filter')

RE_STAR = z3.Star(z3.AllChar(z3.ReSort(z3.StringSort()))) # .*

re_id1 = z3.Concat(z3.Re('A'), RE_STAR) # A*
re_id2 = z3.Concat(z3.Re('B'), RE_STAR) # B*
re_pub = z3.Re('room/status/test')
re_sub = z3.Re('+/status/#')
re_rec = z3.Concat(z3.Re('room/'), RE_STAR)

s = z3.Solver()
s.add(z3.InRe(id1, re_id1))
s.add(z3.InRe(id2, re_id2))
s.add(z3.InRe(topic, re_pub))
s.add(z3.InRe(topic, re_rec))
s.add(z3.InRe(topic_filter, re_sub))

print(s.check())
if s.check() == z3.sat:
  print(s.model())
  
s.push()
s.add(topic == topic_filter)
print(s.check())
if s.check() == z3.sat:
  print(s.model())
s.pop()

# TOPIC LEVELS
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
tf_levels = z3.Strings('tf_lv_0 tf_lv_1 tf_lv_2 tf_lv_3 tf_lv_4 tf_lv_5 tf_lv_6 tf_lv_7')
for level in tf_levels:
  s.add(z3.Not(z3.Contains(level, '/')))

def get_tf_for_level(level):
  topic_filter = ['', tf_levels[0]]
  for tf_level in range(level):
    topic_filter.append('/')
    topic_filter.append(tf_levels[tf_level + 1])
  
  return z3.Concat(topic_filter)
      
for topic_level in range(8):
  s.push()
  s.add(topic == get_topic_for_level(topic_level))
  if s.check() == z3.unsat:
    print(f'#{topic_level+1} topic levels is {z3.unsat}')
    s.pop()
    continue
  print(f'#{topic_level+1} topic levels is {z3.sat}')
  print(s.model())
  
  # CASE1: same length
  s.push()
  s.add(topic_filter == get_tf_for_level(topic_level))
  for level in range(topic_level+1):
    s.add(z3.Or(tf_levels[level] == topic_levels[level],
                tf_levels[level] == '+',
                tf_levels[level] == '#' if level == topic_level else False)) 
  if s.check() == z3.sat:
    print('FOUND')
    print(s.model())
    # Should stop here
  s.pop()

  # CASE 2: using # at the end of a shorter tf
  for tf_level in range(topic_level):
    s.push()
    s.add(topic_filter == get_tf_for_level(tf_level))
    s.add(tf_levels[tf_level] == '#')
    for level in range(tf_level):
      s.add(z3.Or(tf_levels[level] == topic_levels[level],
                  tf_levels[level] == '+'))
    if s.check() == z3.sat:
      print('FOUND')
      print(s.model())
      # Should stop here
    s.pop()

  s.pop()
