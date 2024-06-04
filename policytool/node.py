class Node():
  @property
  def label(self):
    return f'{self.first}->{self.second}'
  
  def __init__(self, first, second, solver, id1, id2, topic):
    self.first = first
    self.second = second
    self.solver = solver
    self.id1 = id1
    self.id2 = id2
    self.topic = topic