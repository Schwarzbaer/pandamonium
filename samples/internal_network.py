import sys
import logging
from functools import partial

from panda3d.core import NodePath
from direct.showbase.ShowBase import ShowBase

from pandamonium.core import (
    ClientAgent,
    AIAgent,
    MessageDirector,
)
from pandamonium.state_server import StateServer
from pandamonium.sockets import (
    InternalAIListener,
    InternalClientListener,
    InternalAIConnector,
    InternalClientConnector,
)

from game_code import (
    GameAIRepository,
    GameClientRepository,
    dclasses,
)

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


class DemoAIAgent(AIAgent, InternalAIListener):
    pass


class DemoClientAgent(ClientAgent, InternalClientListener):
    pass


class DemoAIRepository(GameAIRepository, InternalAIConnector):
    pass


class DemoClientRepository(GameClientRepository, InternalClientConnector):
    pass


state_server = StateServer(dclasses)
client_agent = DemoClientAgent()
ai_agent = DemoAIAgent()
message_director = MessageDirector(
    state_server=state_server,
    client_agent=client_agent,
    ai_agent=ai_agent,
)


class DemoGame(ShowBase):
    def __init__(self):
        super().__init__()
        self.disable_mouse()
        self.ai_repository = DemoAIRepository()
        self.ai_repository.connect(ai_agent)
        # self.accept("c", self.connect)
        # TODO: Text on screen "Press c to connect"
        self.accept("escape", sys.exit)
        self.auth_service = None
        self.connect()

    def connect(self):
        self.ignore("c")
        print("Connecting")
        self.client_repository = DemoClientRepository()
        self.client_repository.connect(client_agent)


demo_game = DemoGame()
demo_game.run()
