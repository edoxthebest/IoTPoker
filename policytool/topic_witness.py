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
    self.topic = str(model[z3.String('topic')]).strip('\"')
    self.topic_filter = str(model[z3.String('topic_filter')]).strip('\"')