from z3 import *

aws_q_mark = AllChar(ReSort(StringSort()))
aws_star = Star(aws_q_mark)


def eval(res):
  print(res)
  return Re(res)

# def replaceMQTT(res):
#   if simplify(Contains(res, '#')):
#     print(res)

  


id1 = String('id_1')
id2 = String('id_2')
topic = String('common_topic')

re_id1 = eval('#')           # eval(c1, id, conn, id)
# re_id2 = eval(c2, id, conn, id)

# f_out_1 = eval(c1, id, pub, t) and eval(c1, id, conn, id)
# f_in_2  = eval(c2, id, sub, t) and eval(c2, id, rec, t) and eval(c2, id, conn, id)
# f_c1_c2 = f_out_1 and f_in_2

# replaceMQTT(id1)


s = Solver()
# IDs can connect
s.add(InRe(id1, re_id1))

# ID1 can publish
mqtt_free_id = Re(Replace(id1, StringVal('#'), Re('s')))
print(mqtt_free_id)
s.add(InRe(topic, Concat(Re('/topic/'), mqtt_free_id)))

# ID2 can subscribe & receive


print(s.check())
if (s.check() == sat):
  print(s.model())


