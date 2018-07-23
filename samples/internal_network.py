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
        print("ClientAgent got message to handle: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        super().handle_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        )

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


class InternalAIAgent(AIAgent, InternalAIListener):
    def handle_message(self, from_channel, to_channel, message_type, *args):
        print("AIAgent got message to handle: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        super().handle_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        )

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


client_agent = InternalClientAgent()
ai_agent = InternalAIAgent()
message_director = MessageDirector(client_agent=client_agent, ai_agent=ai_agent)


class DemoAIRepository(AIRepository, InternalConnector):
    def handle_message(self, from_channel, to_channel, message_type, *args):
        print("DemoAIRepository got message to handle: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        super().handle_message(from_channel, to_channel, message_type, *args)

    def handle_channel_assigned(self, channel):
        print("DemoAIRepository was assigned channel {}".format(channel))
        super().handle_channel_assigned(channel)

    def handle_ai_connected(self, channel):
        print("DemoAIRepository {} learned that AI repo {} connected".format(
            self.channel,
            channel,
        ))

    def handle_client_connected(self, client_id):
        print("DemoAIRepository {} learned that "
              "client repo {} connected".format(
            self.channel,
            client_id,
        ))
        # self.disconnect_client(client_id, "For demonstration purposes.")

    def handle_client_disconnected(self, client_id):
        print("Client {} has disconnected".format(client_id))


ai_repository = DemoAIRepository(ai_agent)
ai_repository.connect()


class DemoClientRepository(ClientRepository, InternalConnector):
    def handle_message(self, message_type, *args):
        print("DemoClientRepository got message to handle: {}".format(
            message_type
        ))
        super().handle_message(message_type, *args)

    def handle_connected(self):
        print("DemoClientRepository has connected to network.")

    def handle_disconnected(self, reason):
        print("DemoClientRepository is being disconnected, reason: {}".format(
            reason,
        ))


client_repository = DemoClientRepository(client_agent)
client_repository.connect()
client_repository.disconnect()


# class Demo(ShowBase):
#     def __init__(self):
#         super().__init__()
#         self.accept("escape", sys.exit)
# 
# 
# demo = Demo()
# demo.run()
