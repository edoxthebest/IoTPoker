import z3
import time
z3.set_option(verbose=10) 
z3.set_param('smt.string_solver','z3str3')
# z3.set_param('proof', True)

# alphabet_sort, _ = z3.EnumSort('alphabet', ['a','b','c','d'])
# id = z3.Const('id', z3.SeqSort(alphabet_sort))
id = z3.String('id')
topic = z3.String('topic')
topic_levels = z3.Strings('topic_lv_0 topic_lv_1 topic_lv_2 topic_lv_3')
qmarks = z3.Strings('qmark_0 qmark_1 qmark_2')

s = z3.Solver()
# s.add(z3.InRe(topic, z3.Re('a/b/c/d')))
s.add(topic == z3.Concat('a/b/', id))
# for qmark in qmarks:
#   s.add(z3.Length(qmark) == 1)
# s.add(id == z3.Concat('badgeReader', qmarks[0], qmarks[1]))
# s.add(topic == z3.Concat('physicalAC/floor1/', id, '/check'))
# s.add(topic == z3.Concat(topic_levels[0],
#                          '/',
#                          topic_levels[1],
#                          '/',
#                          topic_levels[2],
#                          '/',
#                          topic_levels[3]))
s.add(topic == z3.Concat(topic_levels[0],
                         '/',
                         topic_levels[1]))
s.add(z3.Not(z3.Or(z3.Contains(topic_levels[0], '/'),
                   z3.Contains(topic_levels[1], '/'))))
                  #  z3.Contains(topic_levels[2], '/'),
                  #  z3.Contains(topic_levels[3], '/'))))

# s.add(z3.Length(topic) < 35)
s.set('timeout', 1000)
t = time.time()
check = s.check()
print(check)
if check == z3.sat:
  print(s.model())
# elif check == z3.unsat:
#   with open('proof.txt', 'w') as f:
#     print(s.proof(), file=f)
print(time.time() - t)