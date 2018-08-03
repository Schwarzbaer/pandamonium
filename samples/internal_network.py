# import sys
#
# from direct.showbase.ShowBase import ShowBase

# Here's a quick overview of what this sample does:
# * Cobble together the server, consisting of StateServer, AIAgent, ClientAgent,
#   and MessageDirector.
# * Create and "connect" an AIRepository.
# * When the AIRepository gets a channel assignment message, which is for now
#   doubling as its "You're ready to go" signal, it
#   * sets interest in the "first contact zone"
#   * creates a dobject of dclass 0; for now, that means nothing, since I
#     haven't implemented dclasses and dobject behavior yet.
# * When the AIRepository is notified that the dobject creation has happened, it
#   sets itself as the dobject's AI.
#   TODO: What *should* happen, to enforce better causality, is that the repo
#   sets itself as AI once it is told to create a view for the dobject. That way
#   there's no need to juggle the "What if we're set as AI before we even see
#   the dobject?" case.
# * When the AIRepository learns that a client has connected to the server, it
#   sets interest for the client in the first contact zone. Now the client sees
#   the dobject in it, too.
# TODO:
# * Demonstrate that the dobject works by sending messages for it back and
#   forth.
# * Break it all down again.
# * A Panda3D sample (without auth, which is what this first dobject would
#   typically be for) should have the AI create a dobject for each client, set
#   that client as owner, and let them all move around in 3D space until the
#   client disconnects.


import logging

from pandamonium.constants import field_policies
from pandamonium.state_server import StateServer
from pandamonium.core import (
    ClientAgent,
    AIAgent,
    MessageDirector,
)
from pandamonium.sockets import (
    InternalAIListener,
    InternalClientListener,
    InternalAIConnector,
    InternalClientConnector,
)
from pandamonium.repository import ClientRepository, AIRepository
from pandamonium.dobject import DistributedObject


logging.basicConfig(level=logging.DEBUG)
# logging.basicConfig(level=logging.INFO)


# {dclass_id: {field_id: (type, keywords)}}
# type = ((type_1, type2, ...), KEYWORDS)
demo_classes = {'auth_service': {'userpass': ((str, str),
                                              (field_policies.CLIENT_SEND |
                                               field_policies.AI_RECEIVE))},
                'avatar': {'move_command': ((float, float),
                                            (field_policies.OWNER_SEND,
                                             field_policies.AI_RECEIVE)),
                           'position': ((float, float),
                                        (field_policies.AI_SEND,
                                         field_policies.OWNER_RECEIVE))}}


FIRST_CONTACT_ZONE = 0


class DemoAIAgent(AIAgent, InternalAIListener):
    pass


class DemoClientAgent(ClientAgent, InternalClientListener):
    pass


state_server = StateServer()
client_agent = DemoClientAgent()
ai_agent = DemoAIAgent()
message_director = MessageDirector(
    state_server=state_server,
    client_agent=client_agent,
    ai_agent=ai_agent,
)


class DemoAIRepository(AIRepository, InternalAIConnector):
    def __init__(self):
        self.token_callbacks = {}

    def handle_channel_assigned(self, channel):
        super().handle_channel_assigned(channel)
        self.set_interest(self.channel, FIRST_CONTACT_ZONE)
        self.create_dobject(
            0,
            {},
            self.demo_dobject_creation_callback,
        )

    def handle_client_connected(self, client_id):
        super().handle_client_connected(client_id)
        # self.disconnect_client(client_id, "For demonstration purposes.")
        self.set_interest(client_id, FIRST_CONTACT_ZONE)

    def create_dobject(self, dclass, fields, callback):
        token = "token" # FIXME: This should *really* be an incremental ID.
        self.token_callbacks[token] = callback
        super().create_dobject(dclass, fields, token)

    def handle_dobject_created(self, dobject_id, token):
        super().handle_dobject_created(dobject_id, token)
        callback = self.token_callbacks[token]
        del self.token_callbacks[token]
        callback(dobject_id)

    def demo_dobject_creation_callback(self, dobject_id):
        print("AIRepository {} dobject creation callback executed for "
              "dobject \"{}\"".format(self.channel, dobject_id))
        # TODO : Make dobject present in FIRST_CONTACT_ZONE
        self.add_to_zone(dobject_id, FIRST_CONTACT_ZONE)
        #self.set_ai(self.channel, dobject_id)


ai_repository = DemoAIRepository()
ai_repository.connect(ai_agent)


class DemoClientRepository(ClientRepository, InternalClientConnector):
    pass


client_repository = DemoClientRepository()
client_repository.connect(client_agent)





## client_repository.disconnect()
print("-----------------------------------------------------------------------")


# class Demo(ShowBase):
#     def __init__(self):
#         super().__init__()
#         self.accept("escape", sys.exit)
# 
# 
# demo = Demo()
# demo.run()
