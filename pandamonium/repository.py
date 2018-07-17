# FIXME: There needs to be some cyclical task after connecting that actually
#   reads and executes messages. Either in __init__() (non-blocking setup)
#   or connected() (simplicity).
class BaseRepository:
    def __init__(self, socket=None):
        if socket is None:
            socket = default_socket()
        self.socket = socket

    def connect(self):
        """Connect to the network server."""
        self.socket.connect()

    def connected(self):
        """Message handler: Network has acknowledged our connection."""
        pass


class ClientRepository(BaseRepository):
    default_socket = None  # FIXME

    def disconnected(self, reason):
        """Message handler: Network has disconnected the client."""
        pass


class AIRepository(BaseRepository):
    default_socket = None  # FIXME

    def client_connected(self, client_id):
        """Message handler: A client has connected to the network."""
        pass

    def client_disconnected(self, client_id):
        """Message handler: A client has disconnected from the network."""
        pass
