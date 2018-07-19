# import sys
#
# from direct.showbase.ShowBase import ShowBase

from pandamonium.core import ClientAgent, AIAgent, MessageDirector
from pandamonium.sockets import InternalListener, InternalConnector
from pandamonium.repository import ClientRepository, AIRepository


client_agent = type('InternalClientAgent', (ClientAgent, InternalListener), {})()
ai_agent = type('InternalAIAgent', (AIAgent, InternalListener), {})()
message_director = MessageDirector(client_agent=client_agent, ai_agent=ai_agent)


class DemoAIRepository(AIRepository, InternalConnector):
    def connected(self):
        print("AI repo has connected.")

    def client_connected(self, client_id):
        print("Client {} has connected".format(client_id))

    def client_disconnected(self, client_id):
        print("Client {} has connected".format(client_id))


ai_repository = DemoAIRepository(ai_agent)
ai_repository.connect()


class DemoClientRepository(ClientRepository, InternalConnector):
    def connected(self):
        print("Client repo has connected.")

    def disconnected(self, reason):
        print("Disconnected: {}".format(reason))


client_repository = DemoClientRepository(client_agent)
client_repository.connect()


# class Demo(ShowBase):
#     def __init__(self):
#         super().__init__()
#         self.accept("escape", sys.exit)
# 
# 
# demo = Demo()
# demo.run()
