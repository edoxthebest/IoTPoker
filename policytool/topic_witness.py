import z3

class TopicWitness:
  def __init__(self, cert1, cert2, solver):
    self.cert1 = cert1
    self.cert2 = cert2
    self.solver = solver
    # TODO: can i still use the solver, regardless from where i created it?
    
    model = solver.model()
    self.id1 = str(model[z3.String('id_1')]).strip('\"')
    self.id2 = str(model[z3.String('id_2')]).strip('\"')
    if model[z3.String('topic')] != None:
      topic = str(model[z3.String('topic')]).strip('\"')
    else:
      topic_lvs = []
      for i in range(8):
        level = model[z3.String('topic_lv_' + str(i))]
        if level is not None:
          topic_lvs.append(str(level).strip('\"'))
              # topic_lvs = [str(model[z3.String('topic_lv_' + str(0))]).strip('\"'),
              #      str(model[z3.String('topic_lv_1')]).strip('\"'),
              #      str(model[z3.String('topic_lv_2')]).strip('\"'),
              #      str(model[z3.String('topic_lv_3')]).strip('\"'),
              #      str(model[z3.String('topic_lv_4')]).strip('\"'),
              #      str(model[z3.String('topic_lv_5')]).strip('\"'),
              #      str(model[z3.String('topic_lv_6')]).strip('\"'),
              #      str(model[z3.String('topic_lv_7')]).strip('\"')]
      # topic_lvs = [x for x in topic_lvs if x is not None]
      topic = '/'.join(topic_lvs)
    self.topic = topic
    self.topic_filter = str(model[z3.String('topic_filter')]).strip('\"')