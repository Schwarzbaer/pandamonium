import sys
import logging

from direct.showbase.ShowBase import ShowBase

from pandamonium.sockets import NetworkClientConnector
from pandamonium.packers import ClientPacker
from pandamonium.repository import ClientRepository

from game_code import (
    GameClientRepository,
    dclasses,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DemoClientRepository(ClientPacker, NetworkClientConnector,
                           GameClientRepository):
    dclasses = dclasses

    def __init__(self):
        NetworkClientConnector.__init__(self)
        GameClientRepository.__init__(self)

    def connected(self):
        print("Client repo has connected.")

    def disconnected(self, reason):
        print("Disconnected: {}".format(reason))


class DemoClient(ShowBase):
    def __init__(self):
        super().__init__()
        self.disable_mouse()
        self.accept("escape", sys.exit)
        logger.info("Starting Client")
        self.client_repository = DemoClientRepository()
        self.client_repository.connect()
        base.taskMgr.add(self.read_network_messages, "Network read")

    def read_network_messages(self, task):
        self.client_repository._read_socket()
        return task.cont


demo_client = DemoClient()
demo_client.run()
