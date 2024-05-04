import re
import z3
from policyuniverse.arn import ARN

class ReExp:
  RE_EMPTY = z3.Empty(z3.ReSort(z3.StringSort()))
  RE_QMARK = z3.Diff(z3.AllChar(z3.ReSort(z3.StringSort())),
                     z3.Union(z3.Re('*'), z3.Re('?')))
  RE_STAR = z3.Star(RE_QMARK)
  RE_PLUS = z3.Plus(z3.Diff(z3.AllChar(z3.ReSort(z3.StringSort())),
                            z3.Union(z3.Re('*'), z3.Re('?'), z3.Re('/'))))
  RE_HASH = z3.Union(RE_EMPTY, z3.Concat(z3.Re('/'), RE_STAR))


  def parse(arn, client_id):
    res = ARN(arn).name or arn
    is_sub_action = re.match('^topicfilter\/', res)
    res = re.sub('^(client|topic|topicfilter)\/', '', res)
    
    aws_wildcards = r'(\?|\*)'
    mqtt_plus = r'(\+)'
    mqtt_hash = r'(^#$|\/#$)'
    cid_var = r'(\$\{iot:ClientId\})'
    aws_mqtt_wildcards = re.compile('%s|%s|%s|%s' 
                                    % (aws_wildcards, mqtt_plus, mqtt_hash, cid_var))
    aws_only_wildcards = re.compile('%s|%s' % (aws_wildcards, cid_var))
    if is_sub_action:
      #Both AWS and MQTT Wildcards
      res_split = [x for x in re.split(aws_mqtt_wildcards, res) if x]
    else:
      # Only AWS Wildcards - substitute ? and * with their regular expressions
      res_split = [x for x in re.split(aws_only_wildcards, res) if x]
    res = []
    for x in res_split:
      match x:
        case '?':
          res.append(ReExp.RE_QMARK)
        case '*':
          res.append(ReExp.RE_STAR)
        case '+':
          res.append(ReExp.RE_PLUS)
        case '#' | '/#' :
          res.append(ReExp.RE_HASH)
        case '${iot:ClientId}':
          # Does not handle possible mqtt wildcards in the client id
          res.append(z3.Re(client_id))
        case _:
          res.append(z3.Re(x))

    return res.pop() if len(res) == 1 else z3.Concat(res)
