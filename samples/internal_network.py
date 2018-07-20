# import sys
#
# from direct.showbase.ShowBase import ShowBase

from pandamonium.core import ClientAgent, AIAgent, MessageDirector
from pandamonium.sockets import (
    InternalAIListener,
    InternalClientListener,
    InternalConnector,
)
from pandamonium.repository import ClientRepository, AIRepository


class InternalClientAgent(ClientAgent, InternalClientListener):
    def handle_message(self, from_channel, to_channel, message_type, *args):
        print("ClientAgent got message to handle:")
        print("  {} -> {} ({})".format(from_channel, to_channel, message_type))
        super().handle_message(from_channel, to_channel, message_type, *args)


class InternalAIAgent(AIAgent, InternalAIListener):
    def handle_message(self, from_channel, to_channel, message_type, *args):
        print("AIAgent got message to handle:")
        print("  {} -> {} ({})".format(from_channel, to_channel, message_type))
        super().handle_message(from_channel, to_channel, message_type, *args)


client_agent = InternalClientAgent()
ai_agent = InternalAIAgent()
message_director = MessageDirector(client_agent=client_agent, ai_agent=ai_agent)


class DemoAIRepository(AIRepository, InternalConnector):
    def connected(self):
        print("AI repo has connected.")

    def client_connected(self, client_id):
        print("Client {} has connected".format(client_id))

    def client_disconnected(self, client_id):
        print("Client {} has connected".format(client_id))

    def handle_message(self, from_channel, to_channel, message_type, *args):
        print("DemoAIRepository got message to handle:")
        print("  {} -> {} ({})".format(from_channel, to_channel, message_type))


ai_repository = DemoAIRepository(ai_agent)
ai_repository.connect()


class DemoClientRepository(ClientRepository, InternalConnector):
    def connected(self):
        print("Client repo has connected.")

    def disconnected(self, reason):
        print("Disconnected: {}".format(reason))

    def handle_message(self, message_type, *args):
        print("DemoClientRepository got message to handle:")
        print("  ({})".format(message_type))
        # super().handle_message(from_channel, to_channel, message_type, *args)


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
