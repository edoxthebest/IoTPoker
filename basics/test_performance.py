import z3
import time
z3.set_option(verbose=9) 


RE_QMARK = z3.Union(z3.Range('a', 'z'),
                    z3.Range('A', 'Z'),
                    z3.Range('0', '9'),
                    z3.Re('+'),
                    z3.Re('#'),
                    z3.Re('/'))
RE_STAR = z3.Star(RE_QMARK)


id1 = z3.String('id_1')
topic = z3.String('topic')

topic_levels = z3.Strings('topic_lv_0 topic_lv_1 topic_lv_2')
tf_levels = z3.Strings('tf_lv_0 tf_lv_1 tf_lv_2 tf_lv_3 tf_lv_4 tf_lv_5 tf_lv_6 tf_lv_7')


s = z3.Solver()

s.add(z3.And(z3.InRe(id1, z3.Concat(z3.Re("badgeReader"),
                                    RE_QMARK, RE_QMARK))),
     z3.Not(z3.InRe(id1, z3.Empty(z3.ReSort(z3.StringSort())))))

s.add(z3.And(z3.InRe(topic,z3.Concat(z3.Re("physicalAC/floor1/"), z3.Re(id1), z3.Re("/check"))),
      z3.Not(z3.InRe(topic, z3.Empty(z3.ReSort(z3.StringSort()))))))

s.add(z3.And(z3.InRe(topic, RE_STAR)),
      z3.Not(z3.InRe(topic, z3.Empty(z3.ReSort(z3.StringSort()))))),

for level in topic_levels:
  s.add(z3.Not(z3.Contains(level, '/')))
for level in tf_levels:
  s.add(z3.Not(z3.Contains(level, '/')))


s.add(topic == z3.Concat("",topic_levels[0], "/", topic_levels[1], "/", topic_levels[2]))

# print(s.assertions())
# for i,v in enumerate(s.assertions()):
#   print(f'{i} -> {v}')

start_time = time.time()
check = s.check()
print(check)
if check == z3.sat:
  print(s.model())
  
print(time.time() - start_time)

