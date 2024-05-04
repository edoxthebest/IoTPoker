from z3 import *

q_mark = AllChar(ReSort(StringSort()))
star = Star(q_mark)

# topicexpression per id = (B/?)
# topicexpression per subscribe topic = (/A/topic${id})
id1 = String('id_1')
topic1 = String('topic_1')
topic2 = String('topic_2')
id1_re = Const('id_1_re', ReSort(StringSort()))

re_id1 = Concat(Re('B/'), q_mark)
re_sub = Concat(Re('/A/topic'), id1_re)

s = Solver()
s.add(InRe(id1, re_id1))
s.add(InRe(topic1, re_sub))
s.add(InRe(topic2, re_sub))
s.add(Not(topic1 == topic2))

plus_cons = id1_re == Concat(
  If(SubString(id1, 0, 1) == StringVal("+"), q_mark, Re(SubString(id1, 0, 1))),
  If(SubString(id1, 1, 1) == StringVal("+"), q_mark, Re(SubString(id1, 1, 1))),
  If(SubString(id1, 2, 1) == StringVal("+"), q_mark, Re(SubString(id1, 2, 1))),
  If(SubString(id1, 3, 1) == StringVal("+"), q_mark, Re(SubString(id1, 3, 1))),
  If(SubString(id1, 4, 1) == StringVal("+"), q_mark, Re(SubString(id1, 4, 1))),
)
s.add(plus_cons)

print(s.check())
print(s.model())
