import sys

from pandamonium.repository import AIRepository
from pandamonium.sockets import NetworkConnector


ai_socket = NetworkConnector(host='127.0.0.1', port=50550)


class DemoAIRepository(AIRepository):
    def connected(self):
        print("AI repo has connected.")

    def client_connected(self, client_id):
        print("Client {} has connected".format(client_id))

    def client_disconnected(self, client_id):
        print("Client {} has connected".format(client_id))


ai_repository = DemoAIRepository(socket=ai_socket)
ai_repository.connect()
