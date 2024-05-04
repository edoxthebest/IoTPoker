from z3 import *

q_mark = AllChar(ReSort(StringSort()))
star = Star(q_mark)
print(star)

# topicexpression per id = (B/*)
# topicexpression per subscribe topic = (/A/?/topic${id})
# topicexpression per publish topic = (/?/C/topic${id})
id1 = String('id_1')
id2 = String('id_2')
topic = String('common_topic')

re_id1 = Concat(Re('B/'), star)
re_id2 = re_id1

re_sub = Concat(Re('/A/'), q_mark, Re('/topic'), Re(id1))
re_pub = Concat(Re('/'), q_mark, Re('/C/topic'), Re(id2))

s = Solver()
s.add(InRe(id1, re_id1))
s.add(InRe(id2, re_id2))
s.add(InRe(topic, re_sub))
s.add(InRe(topic, re_pub))

print(s.check())
print(s.model())
