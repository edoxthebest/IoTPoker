import cvc5.pythonic as cvc5
import logging
import re
import z3
from collections import namedtuple
from policyuniverse.arn import ARN
from policyuniverse.policy import Policy
from policytool.iot import IoT
from policytool.re_exp import ReExp

logger = logging.getLogger('IoT:Poker')

class IoTPolicy(Policy):
  Resource = namedtuple('Resource', 'allow deny')

  @staticmethod
  def union(policies: list['IoTPolicy']):
    # TODO: implement this
    return policies[0]

  
  def __init__(self, policy):
    super().__init__(policy)
    
    self._con_alw_res = set()
    self._con_den_res = set()
    self._pub_alw_res = set()
    self._pub_den_res = set()
    self._sub_alw_res = set()
    self._sub_den_res = set()
    self._rec_alw_res = set()
    self._rec_den_res = set()
    self._strings_literal = set()
    self._strings_literals_unsafe = set()
    self._strings_literal_safe = set()

    self.init_resources()
  
  @property
  def connect(self):
    return IoTPolicy.Resource(frozenset(self._con_alw_res), frozenset(self._con_den_res))
  
  @property
  def publish(self):
    return IoTPolicy.Resource(frozenset(self._pub_alw_res), frozenset(self._pub_den_res))
  
  @property
  def subscribe(self):
    return IoTPolicy.Resource(frozenset(self._sub_alw_res), frozenset(self._sub_den_res))
  
  @property
  def receive(self):
    return IoTPolicy.Resource(frozenset(self._rec_alw_res), frozenset(self._rec_den_res))
  
  @property
  def strings(self):
    return self._strings_literal
  
  @property
  def danger_strings(self):
    return self._strings_literals_unsafe

  @property
  def safe_strings(self):
    return self._strings_literal_safe
  
  @property
  def is_tokenable(self):
    return not self._qmark_near_star
  
  # TODO: test this
  # TODO: change this implementation
  @property
  def client(self):
    for stmt in self.statements:
      if not IoT.CON in stmt.actions:
        continue
      
      return ARN(stmt.resources.pop()).name
    
  def init_resources(self):
    for stmt in self.statements:
      resources = set()
      for res in stmt.resources:
        arn = ARN(res)
        if not arn.error:
          arn = re.sub('^(client|topic|topicfilter)\/', '', arn.name)
        elif res == '*':
          arn = res
        elif ':' in res:
          arn = res[res.rfind(':')+1:]
          arn = re.sub('^(client|topic|topicfilter)\/', '', arn)
        else:
          logger.warning(f'ARN not formatted correctly: {arn.arn}.')
        resources.add(arn)
      
      for action in stmt.actions:
        match(action, stmt.effect):
          case (IoT.CON, IoT.ALLOW):
            self._con_alw_res.update(resources)
          case (IoT.CON, IoT.DENY):
            self._con_den_res.update(resources)
            
          case (IoT.PUB, IoT.ALLOW):
            self._pub_alw_res.update(resources)
          case (IoT.PUB, IoT.DENY):
            self._pub_den_res.update(resources)
            
          case (IoT.SUB, IoT.ALLOW):
            self._sub_alw_res.update(resources)
          case (IoT.SUB, IoT.DENY):
            self._sub_den_res.update(resources)
            
          case (IoT.REC, IoT.ALLOW):
            self._rec_alw_res.update(resources)
          case (IoT.REC, IoT.DENY):
            self._rec_den_res.update(resources)
            
          case (IoT.STAR, IoT.ALLOW):
            self._con_alw_res.update(resources)
            self._pub_alw_res.update(resources)
            self._sub_alw_res.update(resources)
            self._rec_alw_res.update(resources)
          case (IoT.STAR, IoT.DENY):
            self._con_den_res.update(resources)
            self._pub_den_res.update(resources)
            self._sub_den_res.update(resources)
            self._rec_den_res.update(resources)
          
          case _:
            logger.debug(f'Unrecognised action: {action}.')
    
    res_union = self._con_alw_res   \
                | self._pub_alw_res \
                | self._sub_alw_res \
                | self._rec_alw_res \
                | self._con_den_res \
                | self._pub_den_res \
                | self._sub_den_res \
                | self._rec_den_res
    self._max_no_of_qmarks = 0
    self._qmark_near_star = False
    for res in res_union:
      if '?*' in res or '*?' in res:
        self._qmark_near_star = True
      
      self._max_no_of_qmarks = max(len(max(re.compile(r'(\?+\?)*').findall(res))), self._max_no_of_qmarks)
      for res_split in res.split('/'):
        if '?' in res_split or '*' in res_split or '${iot:ClientId}' in res_split:
          for wild_substring in [x for x in re.split(ReExp.WILDS_RE, res_split) if x]:
            match wild_substring:
              case '?' | '*' | '${iot:ClientId}':
                continue
              case _:
                self._strings_literals_unsafe.add(wild_substring)
        elif res in self._con_alw_res or res in self._con_den_res:
          self._strings_literals_unsafe.add(res_split)
        elif len(res_split) != 1:
          self._strings_literal.add(res_split)
          
    for string in self._strings_literal:
      string_has_danger = any([string_danger in string for string_danger in self._strings_literals_unsafe])
      if not string_has_danger and len(string) > self._max_no_of_qmarks:
        self._strings_literal_safe.add(string)
        
  def get_safe_strings_for(self, other: 'IoTPolicy'):
    if not(self.is_tokenable and other.is_tokenable):
      return {}
    
    safe_strings = set()
    for string in self._strings_literal_safe:
      string_has_danger = any([string_danger in string for string_danger in other._strings_literals_unsafe])
      if not string_has_danger and len(string) > other._max_no_of_qmarks:
        safe_strings.add(string)
        
    for string in other._strings_literal_safe:
      string_has_danger = any([string_danger in string for string_danger in self._strings_literals_unsafe])
      if not string_has_danger and len(string) > self._max_no_of_qmarks:
        safe_strings.add(string)

    return safe_strings

    
  def build_connect(self, id: z3.SeqRef, tokenable_strings:list = [], 
                    thing_name: str = None, thing_attrs: dict[str, str] = None):
    return self.build_allow_constraint(self._con_alw_res, self._con_den_res, id, 
                                       tokenable_strings, thing_name=thing_name, thing_attrs=thing_attrs)
  
  def build_publish(self, topic: z3.SeqRef, client_id: z3.SeqRef, 
                    tokenable_strings:list = [],
                    thing_name: str = None, thing_attrs: dict[str, str] = None):
    return self.build_allow_constraint(self._pub_alw_res, self._pub_den_res, topic, 
                                       tokenable_strings, client_id, thing_name, thing_attrs)

  def build_subscribe(self, topic: z3.SeqRef, client_id: z3.SeqRef, 
                      tokenable_strings:list = [],
                      thing_name: str = None, thing_attrs: dict[str, str] = None):
    return self.build_allow_constraint(self._sub_alw_res, self._sub_den_res, topic, 
                                       tokenable_strings, client_id, thing_name, thing_attrs)

  def build_receive(self, topic: z3.SeqRef, client_id: z3.SeqRef,
                    tokenable_strings:list = [],
                    thing_name: str = None, thing_attrs: dict[str, str] = None):
    return self.build_allow_constraint(self._rec_alw_res, self._rec_den_res, topic,
                                       tokenable_strings, client_id, thing_name, thing_attrs)

  def build_allow_constraint(self, allow_res: list, deny_res: list, for_variable: z3.SeqRef, 
                             tokenable_strings: list = [], client_id: z3.SeqRef = None,
                             thing_name: str = None, thing_attrs: dict[str, str] = None,
                             ):
          
    parsed_allow = [ReExp.parse(res, tokenable_strings, client_id, thing_name, thing_attrs) for res in allow_res]
    parsed_deny = [ReExp.parse(res, tokenable_strings, client_id, thing_name, thing_attrs) for res in deny_res]

    re_allow = cvc5.Union(parsed_allow) if allow_res else '' #ReExp.RE_EMPTY
    re_deny = cvc5.Union(parsed_deny) if deny_res else ''#ReExp.RE_EMPTY

    return cvc5.And(cvc5.InRe(for_variable, re_allow) if allow_res else False, 
                    cvc5.Not(cvc5.InRe(for_variable, re_deny) if deny_res else False))
    
  def build_publish_radix(self, topic: cvc5.ExprRef):
    return self.build_radix(self._pub_alw_res, topic)
  
  def build_subscribe_radix(self, topic: cvc5.ExprRef):
    return self.build_radix(self._sub_alw_res, topic)

  def build_receive_radix(self, topic: cvc5.ExprRef):
    return self.build_radix(self._rec_alw_res, topic)
    
  def build_radix(self, allow_res: list, topic: cvc5.ExprRef):
    if len(allow_res) == 0:
      return False, 0
    radix_allows = []
    shortest_lenght = 100
    for res in allow_res:
      re_exp, lenght = ReExp.radix(res)
      radix_allows.append(re_exp)
      shortest_lenght = lenght if lenght < shortest_lenght else shortest_lenght
    return cvc5.InRe(topic, cvc5.Union(radix_allows)), shortest_lenght