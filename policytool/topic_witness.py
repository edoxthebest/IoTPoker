import z3

class TopicWitness:
  # token_list = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'ς', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']
  token_list = ['\\u{3b1}', 
                '\\u{3b2}', 
                '\\u{3b3}', 
                '\\u{3b4}', 
                '\\u{3b5}', 
                '\\u{3b6}', 
                '\\u{3b7}', 
                '\\u{3b8}', 
                'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'ς', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']

  def __init__(self, cert1, cert2, solver, string_tokens):
    self.cert1 = cert1
    self.cert2 = cert2
    self.solver = solver
    self.tokens = string_tokens
    # TODO: can i still use the solver, regardless from where i created it?
    
    model = solver.model()
    self.id1 = self._token_replace('id_1')
    self.id2 = self._token_replace('id_2')
    if model[z3.String('topic')] != None:
      topic = self._token_replace('topic')
    else:
      topic_lvs = []
      for i in range(8):
        if model[z3.String('topic_lv_' + str(i))] is not None:
          topic_lvs.append(self._token_replace('topic_lv_' + str(i)))
      topic = '/'.join(topic_lvs)
    self.topic = topic
    self.topic_filter = self._token_replace('topic_filter')
    
  def _token_replace(self, string_for):
    model = self.solver.model()
    base_string = str(model[z3.String(string_for)]).strip('"')

    result_string = []
    for sub_string in base_string.split('/'):
      for i, token in enumerate(self.tokens):
        sub_string = (sub_string.replace(TopicWitness.token_list[i], token))
    
      result_string.append(sub_string)
      
    return '/'.join(result_string)