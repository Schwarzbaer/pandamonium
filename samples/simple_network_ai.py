import sys

from pandamonium.repository import AIRepository
from pandamonium.sockets import AIConnector


class DemoAIRepository(AIRepository, AIConnector):
    def connected(self):
        print("AI repo has connected.")

    def client_connected(self, client_id):
        print("Client {} has connected".format(client_id))

    def client_disconnected(self, client_id):
        print("Client {} has connected".format(client_id))


ai_repository = DemoAIRepository()
ai_repository.connect()
