import sys

from direct.showbase.ShowBase import ShowBase

from pandamonium.core import ClientAgent, AIAgent, MessageDirector
from pandamonium.sockets import make_internal_socket
from pandamonium.repository import ClientRepository, AIRepository


client_socket, client_agent_socket = make_internal_socket()
ai_socket, ai_agent_socket = make_internal_socket()

client_agent = ClientAgent(socket=client_agent_socket)
ai_agent = AIAgent(socket=ai_agent_socket)
message_director = MessageDirector(client_agent=client_agent, ai_agent=ai_agent)

client_repository = ClientRepository(socket=client_socket)


class DemoAIRepository(AIRepository):
    def connected(self):
        print("AI repo has connected.")

    def client_connected(self, client_id):
        print("Client {} has connected".format(client_id))

    def client_disconnected(self, client_id):
        print("Client {} has connected".format(client_id))


ai_repository = DemoAIRepository(socket=ai_socket)


class Demo(ShowBase):
    def __init__(self):
        super().__init__()
        self.accept("escape", sys.exit)


demo = Demo()
demo.run()
