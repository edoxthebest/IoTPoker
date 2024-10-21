class Node():
  @property
  def label(self):
    return f'{self.first}->{self.second}'
  
  def __init__(self, first, second, id1, id2, topic):
    self.first = first
    self.second = second
    self.id1 = id1
    self.id2 = id2
    self.topic = topic
    
  def __str__(self) -> str:
    topic = self.topic.__str__()[1:-1]
    return f'({self.id1}) -> {self.topic} -> ({self.id2})'
  
  def __repr__(self):
    return self.__str__()