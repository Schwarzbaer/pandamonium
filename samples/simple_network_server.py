# TODO: Handle C-c with graceful shutdown.

import sys

from pandamonium.core import ClientAgent, AIAgent, MessageDirector
from pandamonium.sockets import NetworkListener


client_agent_socket = NetworkListener(interface='0.0.0.0', port=50551)
ai_agent_socket = NetworkListener(interface='127.0.0.1', port=50550)


class DemoAIAgent(AIAgent):
    def handle_connection(self, conn_id, addr):
        print("AI {} connected from {}".format(conn_id, addr))
        super().handle_connection(conn_id, addr)


class DemoClientAgent(ClientAgent):
    def handle_connection(self, conn_id, addr):
        print("Client {} connected from {}".format(conn_id, addr))
        super().handle_connection(conn_id, addr)


client_agent = DemoClientAgent(socket=client_agent_socket)
ai_agent = DemoAIAgent(socket=ai_agent_socket)
message_director = MessageDirector(client_agent=client_agent, ai_agent=ai_agent)

message_director.startup()
