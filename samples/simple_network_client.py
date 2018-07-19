import sys

from direct.showbase.ShowBase import ShowBase

from pandamonium.sockets import ClientConnector
from pandamonium.repository import ClientRepository


class DemoClientRepository(ClientRepository, ClientConnector):
    def connected(self):
        print("Client repo has connected.")

    def disconnected(self, reason):
        print("Disconnected: {}".format(reason))


client_repository = DemoClientRepository(host='127.0.0.1', port=50551)
client_repository.connect()


# class Demo(ShowBase):
#     def __init__(self):
#         super().__init__()
#         self.accept("escape", sys.exit)
#         client_repository.connect()
# 
# 
# demo = Demo()
# demo.run()
