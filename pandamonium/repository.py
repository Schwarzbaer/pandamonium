import socket


class BaseRepository:
    def connect(self):
        """Connect to the network server."""
        self.socket.connect((self.host, self.port))

    def connected(self):
        """Message handler: Network has acknowledged our connection."""
        pass


class ClientRepository(BaseRepository):
    def disconnected(self, reason):
        """Message handler: Network has disconnected the client."""
        pass


class AIRepository(BaseRepository):
    def client_connected(self, client_id):
        """Message handler: A client has connected to the network."""
        pass

    def client_disconnected(self, client_id):
        """Message handler: A client has disconnected from the network."""
        pass
