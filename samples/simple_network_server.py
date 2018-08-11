import sys
import logging
import signal

from pandamonium.core import ClientAgent, AIAgent, MessageDirector
from pandamonium.state_server import StateServer
from pandamonium.sockets import NetworkAIListener, NetworkClientListener
from pandamonium.packers import AIPacker, ClientPacker

from game_code import (
    dclasses,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoAIAgent(AIPacker, AIAgent, NetworkAIListener):
    timeout = 0.2

    def handle_connection(self, conn_id, addr):
        print("AI {} connected from {}".format(conn_id, addr))
        super().handle_connection(conn_id, addr)


class DemoClientAgent(ClientPacker, ClientAgent, NetworkClientListener):
    timeout = 0.2

    def handle_connection(self, conn_id, addr):
        print("Client {} connected from {}".format(conn_id, addr))
        super().handle_connection(conn_id, addr)


state_server = StateServer(dclasses)
client_agent = DemoClientAgent()
ai_agent = DemoAIAgent()
message_director = MessageDirector(
    state_server=state_server,
    client_agent=client_agent,
    ai_agent=ai_agent,
)


def signal_sigint(sig, frame):
    logger.warning("Shutdown initiated")
    message_director.shutdown()
    logger.info("Shutdown complete.")


signal.signal(signal.SIGINT, signal_sigint)
message_director.startup()
