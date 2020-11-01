import sys
import logging

from direct.showbase.ShowBase import ShowBase

from pandamonium.sockets import NetworkAIConnector
from pandamonium.packers import AIPacker, DatagramIncomplete
from game_code import (
    GameAIRepository,
    dclasses,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoAIRepository(AIPacker, NetworkAIConnector, GameAIRepository):
    dclasses = dclasses

    def __init__(self):
        NetworkAIConnector.__init__(self)
        GameAIRepository.__init__(self)

    def connected(self):
        print("AI repo has connected.")

    def client_connected(self, client_id):
        print("Client {} has connected".format(client_id))

    def client_disconnected(self, client_id):
        print("Client {} has connected".format(client_id))


class DemoAI(ShowBase):
    dclasses = dclasses

    def __init__(self):
        super().__init__()
        self.disable_mouse()
        self.accept("escape", sys.exit)
        logger.info("Starting AI")
        self.ai_repository = DemoAIRepository()
        self.ai_repository.connect()
        base.taskMgr.add(self.read_network_messages, "Network read")

    def read_network_messages(self, task):
        self.ai_repository._read_socket()
        return task.cont


demo_ai = DemoAI()
demo_ai.run()
