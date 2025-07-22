import cvc5.pythonic as cvc5
import re
import string
import z3
from policytool.iot import IoT
from cvc5 import Kind

class ReExp:
  RE_EMPTY = cvc5.ReRef(cvc5.main_ctx().tm.mkTerm(Kind.REGEXP_NONE))
  RE_QMARK = cvc5.Union(cvc5.Range('a', 'z'),
                      cvc5.Range('A', 'Z'),
                      cvc5.Range('0', '9'),
                      cvc5.Re('+'),
                      cvc5.Re('#'),
                      cvc5.Re('/'))
  RE_STAR = cvc5.Star(cvc5.Union( cvc5.Range('α', 'ω'),RE_QMARK, )) #TODO: rewrite this into unicode
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
        res.append(cvc5.Re('/'))
        
      if '?' in res_split or '*' in res_split or '${iot:ClientId}' in res_split:
        x_split = [y for y in re.split(ReExp.WILDS_RE, res_split) if y]
        for z in x_split:
          match z:
            case '?':
              res.append(ReExp.RE_QMARK)
            case '*':
              res.append(ReExp.RE_STAR)
            case '${iot:ClientId}':
              res.append(cvc5.Re(client_id))
            case _:
              res.append(cvc5.Re(z))
      # elif res_split == '+' or res_split == '#':
      elif len(res_split) == 1:
        res.append(cvc5.Re(res_split))
      elif res_split in tokenable_string:
        current_token_index = tokenable_string.index(res_split)
        current_token = ReExp.TOKENS[current_token_index]
        res.append(cvc5.Re(current_token))
      else:
        res.append(cvc5.Re(res_split))

      # else:
      #   if res_split in tokenable_string:
      #     current_token_index = tokenable_string.index(res_split)
      #   else:
      #     current_token_index = len(tokenable_string)
      #     tokenable_string.append(res_split)
      #   current_token = ReExp.TOKENS[current_token_index]
      #   res.append(z3.Re(current_token))
                
    return res.pop() if len(res) == 1 else cvc5.Concat(res)
  
  @staticmethod
  def parse_thing(res: str, thing_name: str, thing_attrs: dict[str, str]):
    # Replace thing name
    res = re.sub(r'\$\{iot:Connection\.Thing\.ThingName\}', thing_name, res)
    
    # Replace each attribute with its value -- Assuming things are correcly specified
    for attr in re.findall(r'\$\{iot:Connection\.Thing\.Attributes\[([a-zA-Z]+)\]\}', res):
      res = re.sub(r'\$\{iot:Connection\.Thing\.Attributes\[' + re.escape(attr) + r'\]\}',
                   thing_attrs[attr], res)
      
    return res
  
  @staticmethod
  def radix(resource: str):
    resource = resource.replace('$aws', 'aws')
    non_problematic = list(string.ascii_letters + string.digits + '/')
    first_problematic_index = next((i for i, v in enumerate(resource) if v not in non_problematic), -1)
    
    if first_problematic_index == -1:
      res = resource
    else:
      res = resource[:first_problematic_index]

    non_problematic_cvc5 = cvc5.Union(cvc5.Range('a', 'z'), 
                                      cvc5.Range('A', 'Z'), 
                                      cvc5.Range('0', '9'), 
                                      cvc5.Re('/'))
    return cvc5.Concat(cvc5.Re(res), cvc5.Star(non_problematic_cvc5)), len(res)