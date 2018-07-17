import sys

from direct.showbase.ShowBase import ShowBase

from pandamonium.sockets import NetworkConnector
from pandamonium.repository import ClientRepository


client_socket = NetworkConnector(host='127.0.0.1', port=50551)
client_repository = ClientRepository(socket=client_socket)
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
