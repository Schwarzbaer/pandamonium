# import sys
#
# from direct.showbase.ShowBase import ShowBase

from pandamonium.core import (
    StateServer,
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


FIRST_CONTACT_ZONE = 0


class DemoDistributedObject(DistributedObject):
    def __init__(self, state_server, dobject_id, dclass, fields):
        print("dobject {} (class {}) created with: {}".format(
            dobject_id,
            dclass,
            fields,
        ))
        super().__init__(state_server, dobject_id, dclass, fields)


class DemoClientAgent(ClientAgent, InternalClientListener):
    # This override is a bit spammy.
    # def handle_message(self, from_channel, to_channel, message_type, *args):
    #     print("ClientAgent got message to handle: {} -> {} ({})".format(
    #         from_channel, to_channel, message_type,
    #     ))
    #     super().handle_message(
    #         from_channel,
    #         to_channel,
    #         message_type,
    #         *args,
    #     )

    def handle_broadcast_message(self, from_channel, to_channel, message_type,
                                 *args):
        print("ClientAgent got broadcast to handle: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        super().handle_broadcast_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        )

    def handle_connection_message(self, from_channel, to_channel, message_type,
                                 *args):
        print("ClientAgent got connection message to handle: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        super().handle_connection_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        )


class DemoAIAgent(AIAgent, InternalAIListener):
    # This override is a bit spammy.
    # def handle_message(self, from_channel, to_channel, message_type, *args):
    #     print("AIAgent got message to handle: {} -> {} ({})".format(
    #         from_channel, to_channel, message_type,
    #     ))
    #     super().handle_message(
    #         from_channel,
    #         to_channel,
    #         message_type,
    #         *args,
    #     )

    def handle_broadcast_message(self, from_channel, to_channel, message_type,
                                 *args):
        print("AIAgent got broadcast to handle: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        super().handle_broadcast_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        )

    def handle_connection_message(self, from_channel, to_channel, message_type,
                                 *args):
        print("AIAgent got connection message to handle: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        super().handle_connection_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        )


class DemoStateServer(StateServer):
    dobject_class = DemoDistributedObject

    def handle_message(self, from_channel, to_channel, message_type, *args):
        print("StateServer received: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        super().handle_message(from_channel, to_channel, message_type, *args)

    def _handle_set_interest(self, recipient, zone):
        print("StateServer sets interest for {} in {}".format(
            recipient,
            zone,
        ))
        super()._handle_set_interest(recipient, zone)

    def _handle_unset_interest(self, recipient, zone):
        print("StateServer revokes interest for {} in {}".format(
            recipient,
            zone,
        ))
        super()._handle_unset_interest(recipient, zone)


state_server = DemoStateServer()
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

    def handle_message(self, from_channel, to_channel, message_type, *args):
        print("AIRepository got message to handle: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        super().handle_message(from_channel, to_channel, message_type, *args)

    def handle_channel_assigned(self, channel):
        print("AIRepository was assigned channel {}".format(channel))
        super().handle_channel_assigned(channel)
        self.create_dobject(
            0,
            {},
            self.demo_dobject_creation_callback,
        )

    def handle_ai_connected(self, channel):
        print("AIRepository {} learned that AI repo {} connected".format(
            self.channel,
            channel,
        ))

    def handle_client_connected(self, client_id):
        print("AIRepository {} learned that "
              "client repo {} connected".format(
            self.channel,
            client_id,
        ))
        # self.disconnect_client(client_id, "For demonstration purposes.")
        self.set_interest(client_id, FIRST_CONTACT_ZONE)

    def handle_client_disconnected(self, client_id):
        print("Client {} has disconnected".format(client_id))

    def create_dobject(self, dclass, fields, callback):
        token = "token" # FIXME: This should *really* be an incremental ID.
        self.token_callbacks[token] = callback
        super().create_dobject(dclass, fields, token)

    def handle_dobject_created(self, dobject_id, token):
        print("AIRepository {} learned that dobject {} was created with "
              "token \"{}\"".format(self.channel, dobject_id, token))
        callback = self.token_callbacks[token]
        del self.token_callbacks[token]
        callback(dobject_id)

    def demo_dobject_creation_callback(self, dobject_id):
        print("AIRepository {} dobject creation callback executed for "
              "dobject \"{}\"".format(self.channel, dobject_id))


ai_repository = DemoAIRepository()
ai_repository.connect(ai_agent)


class DemoClientRepository(ClientRepository, InternalClientConnector):
    def handle_message(self, message_type, *args):
        print("ClientRepository got message to handle: {}".format(
            message_type
        ))
        super().handle_message(message_type, *args)

    def handle_connected(self):
        print("ClientRepository has connected to network.")

    def handle_disconnected(self, reason):
        print("ClientRepository is being disconnected, reason: {}".format(
            reason,
        ))


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
