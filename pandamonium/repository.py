import socket

from pandamonium.constants import msgtypes


class BaseRepository:
    def connected(self):
        """Message handler: Network has acknowledged our connection."""
        pass


class ClientRepository(BaseRepository):
    def handle_message(self, message_type, *args):
        """Message received, needs to be handled."""
        if message_type == msgtypes.CONNECTED:
            self.connected()
        elif message_type == msgtypes.DISCONNECTED:
            reason = args[0]
            self.handle_disconnected(reason)
        else:
            # FIXME: Better to log it and drop it on the floor?
            raise NotImplementedError

    def handle_connected(self):
        """Connection to client agent has been established."""
        pass

    def handle_disconnected(self, reason):
        """Connection will be terminated shortly by the other end."""
        pass


class AIRepository(BaseRepository):
    channel = None

    def handle_message(self, from_channel, to_channel, message_type, *args):
        """Message received, needs to be handled."""
        # TODO: Validation
        if message_type == msgtypes.AI_CHANNEL_ASSIGNED:
            channel = args[0]
            self.handle_channel_assigned(channel)
        elif message_type == msgtypes.AI_CONNECTED:
            channel = args[0]
            self.handle_ai_connected(channel)
        elif message_type == msgtypes.CLIENT_CONNECTED:
            client_id = args[0]
            self.handle_client_connected(client_id)
        elif message_type == msgtypes.CLIENT_DISCONNECTED:
            client_id = args[0]
            self.handle_client_disconnected(client_id)
        else:
            # FIXME: Better to log it and drop it on the floor?
            raise NotImplementedError

    def handle_channel_assigned(self, channel):
        """A channel was assigned to this repository connection."""
        self.channel = channel

    def handle_ai_connected(self, channel):
        """An AI repository has connected to the network. That may be
        this repository, too."""
        pass

    def handle_client_connected(self, client_id):
        """A client repository has connected to the network."""
        pass

    def handle_client_disconnected(self, client_id):
        """Message handler: A client has disconnected from the network."""
        pass

    def disconnect_client(self, client_id, reason):
        """Send a disconnection message to the client. The ClientAgent should
        also execute the disconnection forcefully."""
        self.send_message(
            self.channel,
            client_id,
            msgtypes.DISCONNECT_CLIENT,
            reason,
        )
