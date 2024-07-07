class TopicWitness:
  def __init__(self, cert1, cert2, solver):
    self.cert1 = cert1
    self.cert2 = cert2
    self.solver = solver
    # TODO: can i still use the solver, regardless from where i created it?
    
    model = solver.model()
    self.id1 = model['id_1']
    self.id2 = model['id_2']
    self.topic = model['topic']
    self.topic_filter = model['topic_filter']