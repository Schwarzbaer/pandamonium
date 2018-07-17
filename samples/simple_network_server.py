# TODO: Handle C-c with graceful shutdown.

import sys

from pandamonium.core import ClientAgent, AIAgent, MessageDirector
from pandamonium.sockets import NetworkListener


class DemoAIAgent(AIAgent, NetworkListener):
    interface = '127.0.0.1'
    port = 50550
    listeners = 1
    timeout = 5.0
    threaded_connections = False

    def handle_connection(self, conn_id, addr):
        print("AI {} connected from {}".format(conn_id, addr))
        super().handle_connection(conn_id, addr)


class DemoClientAgent(ClientAgent, NetworkListener):
    interface = '0.0.0.0'
    port = 50551
    listeners = 1
    timeout = 5.0
    threaded_connections = False

    def handle_connection(self, conn_id, addr):
        print("Client {} connected from {}".format(conn_id, addr))
        super().handle_connection(conn_id, addr)


client_agent = DemoClientAgent()
ai_agent = DemoAIAgent()
message_director = MessageDirector(client_agent=client_agent, ai_agent=ai_agent)

message_director.startup()
