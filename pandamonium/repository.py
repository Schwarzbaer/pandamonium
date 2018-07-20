import socket


class BaseRepository:
    def connected(self):
        """Message handler: Network has acknowledged our connection."""
        pass


class ClientRepository(BaseRepository):
    def disconnected(self, reason):
        """Message handler: Network has disconnected the client."""
        pass

    def handle_message(self, message_type, *args):
        """Message received, needs to be handled."""
        raise NotImplementedError


class AIRepository(BaseRepository):
    def client_connected(self, client_id):
        """Message handler: A client has connected to the network."""
        pass

    def client_disconnected(self, client_id):
        """Message handler: A client has disconnected from the network."""
        pass

    def handle_message(self, from_channel, to_channel, message_type, *args):
        """Message received, needs to be handled."""
        raise NotImplementedError
