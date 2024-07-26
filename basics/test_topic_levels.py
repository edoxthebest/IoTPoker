import z3
import time
z3.set_option(verbose=9) 

topic = z3.String('topic')
topic_levels = z3.Strings('topic_lv_0 topic_lv_1 topic_lv_2 topic_lv_3')

s = z3.Solver()
s.add(z3.InRe(topic, z3.Re('a/b/c/d')))
# s.add(z3.InRe(topic, z3.Re('aaaaaaaaaa/bbbbbbbb/ccccccccc/dddddddddd')))
s.add(topic == z3.Concat(topic_levels[0],
                         '/',
                         topic_levels[1],
                         '/',
                         topic_levels[2],
                         '/',
                         topic_levels[3]))
s.add(z3.Not(z3.Or(z3.Contains(topic_levels[0], '/'),
                   z3.Contains(topic_levels[1], '/'),
                   z3.Contains(topic_levels[2], '/'),
                   z3.Contains(topic_levels[3], '/'))))

t = time.time()
print(s.check())
print(s.model())
print(time.time() - t)