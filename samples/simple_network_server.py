# TODO: Handle C-c with graceful shutdown.

import sys

from pandamonium.core import ClientAgent, AIAgent, MessageDirector
from pandamonium.sockets import AIListener, ClientListener


class DemoAIAgent(AIAgent, AIListener):
    def handle_connection(self, conn_id, addr):
        print("AI {} connected from {}".format(conn_id, addr))
        super().handle_connection(conn_id, addr)


class DemoClientAgent(ClientAgent, ClientListener):
    def handle_connection(self, conn_id, addr):
        print("Client {} connected from {}".format(conn_id, addr))
        super().handle_connection(conn_id, addr)


client_agent = DemoClientAgent()
ai_agent = DemoAIAgent()
message_director = MessageDirector(client_agent=client_agent, ai_agent=ai_agent)

message_director.startup()
