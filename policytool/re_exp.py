import re
import z3
from policytool.iot import IoT

class ReExp:
  RE_EMPTY = z3.Empty(z3.ReSort(z3.StringSort()))
  RE_QMARK = z3.Union(z3.Range('a', 'z'),
                      z3.Range('A', 'Z'),
                      z3.Range('0', '9'),
                      z3.Re('+'),
                      z3.Re('#'),
                      z3.Re('/'))
  RE_STAR = z3.Star(z3.Union(RE_QMARK, z3.Range('α', 'ω'))) #TODO: rewrite this into unicode
  TOKENS = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'ς', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']

  # Encoding the special tokens
  AWS_WILDS = r'(\?|\*)'
  VAR_CID = r'(\$\{iot:ClientId\})'
  WILDS_RE = re.compile('%s|%s' % (AWS_WILDS, VAR_CID))

  #TODO: probably should remove effect
  @staticmethod
  def parse(resource: str, tokenable_string: list = [], client_id: str | z3.SeqRef = None,
            thing_name: str = None, thing_attrs: dict[str, str] = None):    
    # Handle things
    if thing_name is not None:
      resource = ReExp.parse_thing(resource, thing_name, thing_attrs)
         
    res = []
    first = True
    for res_split in resource.split('/'):
      if first:
        first = False
      else:
        res.append(z3.Re('/'))
        
      if '?' in res_split or '*' in res_split or '${iot:ClientId}' in res_split:
        x_split = [y for y in re.split(ReExp.WILDS_RE, res_split) if y]
        for z in x_split:
          match z:
            case '?':
              res.append(ReExp.RE_QMARK)
            case '*':
              res.append(ReExp.RE_STAR)
            case '${iot:ClientId}':
              res.append(z3.Re(client_id))
            case _:
              res.append(z3.Re(z))
      # elif res_split == '+' or res_split == '#':
      elif len(res_split) == 1:
        res.append(z3.Re(res_split))
      elif res_split in tokenable_string:
        current_token_index = tokenable_string.index(res_split)
        current_token = ReExp.TOKENS[current_token_index]
        res.append(z3.Re(current_token))
      else:
        res.append(z3.Re(res_split))

      # else:
      #   if res_split in tokenable_string:
      #     current_token_index = tokenable_string.index(res_split)
      #   else:
      #     current_token_index = len(tokenable_string)
      #     tokenable_string.append(res_split)
      #   current_token = ReExp.TOKENS[current_token_index]
      #   res.append(z3.Re(current_token))
                
    return res.pop() if len(res) == 1 else z3.Concat(res)
  
  @staticmethod
  def parse_thing(res: str, thing_name: str, thing_attrs: dict[str, str]):
    # Replace thing name
    res = re.sub(r'\$\{iot:Connection\.Thing\.ThingName\}', thing_name, res)
    
    # Replace each attribute with its value -- Assuming things are correcly specified
    for attr in re.findall(r'\$\{iot:Connection\.Thing\.Attributes\[([a-zA-Z]+)\]\}', res):
      res = re.sub(r'\$\{iot:Connection\.Thing\.Attributes\[' + re.escape(attr) + r'\]\}',
                   thing_attrs[attr], res)
      
    return res
