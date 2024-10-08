import re
import z3
from policyuniverse.arn import ARN
from policytool.iot import IoT

class ReExp:
  RE_EMPTY = z3.Empty(z3.ReSort(z3.StringSort()))
  RE_QMARK = z3.Union(z3.Range('a', 'z'),
                      z3.Range('A', 'Z'),
                      z3.Range('0', '9'),
                      z3.Re('+'),
                      z3.Re('#'),
                      z3.Re('/'),
                      z3.Range('α', 'ω'))
  # z3.Diff(z3.AllChar(z3.ReSort(z3.StringSort())),
                    #  z3.Union(z3.Re('*'), z3.Re('?')))
  RE_STAR = z3.Star(RE_QMARK)
  # RE_PLUS = z3.Plus(z3.Diff(z3.AllChar(z3.ReSort(z3.StringSort())),
  #                           z3.Union(z3.Re('*'), z3.Re('?'), z3.Re('/'))))
  # RE_HASH = z3.Union(RE_EMPTY, z3.Concat(z3.Re('/'), RE_STAR))
  
  token_list = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'ς', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']

  @staticmethod
  def parse(arn: str, client_id: str | z3.SeqRef,
            effect: str, string_tokens: list,
            thing_name: str = None, thing_attrs: dict[str, str] = None):
    # Only care about resource-id
    res = ARN(arn).name or arn
    # action_is_subscribe = re.match('^topicfilter\/', res)
    res = re.sub('^(client|topic|topicfilter)\/', '', res)
    
    # Handle things
    if thing_name is not None:
      res = ReExp.parse_thing(res, thing_name, thing_attrs)
      
    # Encoding the special tokens
    # TODO: maybe rewrite this
    # maybe mqtt = compile(aws | extra)
    aws_wildcards = r'(\?|\*)'
    # mqtt_plus = r'(\+)'
    # mqtt_hash = r'(^#$|\/#$)'
    var_cid = r'(\$\{iot:ClientId\})'
    # aws_mqtt_wildcards = re.compile('%s|%s|%s|%s'
    #                                 % (aws_wildcards, mqtt_plus, mqtt_hash, var_cid))
    aws_only_wildcards = re.compile('%s|%s' % (aws_wildcards, var_cid))
    
    # if action_is_subscribe and effect == IoT.ALLOW:
      #Both AWS and MQTT Wildcards
      # res_split = [x for x in re.split(aws_mqtt_wildcards, res) if x]
    # else:
      # Only AWS Wildcards - substitute ? and * with their regular expressions
      
    res_split = res.split('/')
    # res_split = [x for x in re.split(aws_only_wildcards, res) if x]
    res = []
    first = True
    for x in res_split:
      if first:
        first = False
      else:
        res.append(z3.Re('/'))
        
      if '?' in x or '*' in x or '${iot:ClientId}' in x:
        x_split = [y for y in re.split(aws_only_wildcards, x) if y]
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
      elif x == '+' or x == '#':
        res.append(z3.Re(x))
      else:
        if x in string_tokens:
          current_token_index = string_tokens.index(x)
        else:
          current_token_index = len(string_tokens)
          string_tokens.append(x)
        current_token = ReExp.token_list[current_token_index]
        res.append(z3.Re(current_token))
        

        # current_token_index = string_tokens.index(x) if x in string_tokens else len(string_tokens)
        # current_token = ReExp.token_list[current_token_index]
        # res.append(z3.Re(current_token))
        # string_tokens.append(x)
        
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
