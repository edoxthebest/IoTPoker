import logging
from .certificate import Certificate
from .iot import IoT
from .iot_policy import IoTPolicy
from .policy_reader import PolicyReader
from .prover import Prover
from .re_exp import ReExp
from .thing import Thing
from .topic_witness import TopicWitness

from .policy_graph import PolicyGraph
from .node import Node

logger = logging.getLogger('IoT:Poker')
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
handler = logging.StreamHandler()
# handler.terminator = '\r'
handler.setFormatter(logFormatter)
logger.addHandler(handler)
