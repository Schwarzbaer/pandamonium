import socket
from queue import Queue, Empty
from threading import Thread, Lock

from pandamonium.util import IDGenerator


class Connection:
    """An active connection."""
    def __init__(self, socket, message_director, connection_id):
        self.socket = socket
        self.message_director = message_director
        self.connection_id = connection_id
        if self.threaded_connections:
            # TODO: Sart autonomous thread to read() messages
            pass

    def disconnect(self, reason):
        # TODO: Implement? Or let it exist only implicitly?
        pass

    def read(self):
        # TODO: Read message (with timeout), interpret, call:
        # self.message_director.create_message(
        #     self.connection_id,
        #     to_channel,
        #     message_type,
        #     *[args],
        # )
        pass


class NetworkListener:
    def __init__(self):
        self.id_gen = None

        self.socket = socket.socket()
        self.socket.bind((self.interface, self.port))
        self.socket.listen()
        self.socket.settimeout(self.timeout)

        self.listening_sockets = []
        self.listeners = self.listeners
        self.lock = Lock()
        self.keep_running = True
        self.connected_sockets = {}

        # FIXME: Infer this from channels attribute instead.
        self.id_gen = IDGenerator(start_id=self.connection_start_id)

    def listen(self):
        for _ in range(self.listeners):
            self.add_listener()
        # TODO: Start the read_sockets loop.

    def add_listener(self):
        print("INFO: Adding listener")
        t = Thread(target=self.await_connection)
        self.listening_sockets.append(t)
        t.start()
        print("INFO: Started listener thread {}".format(t.name))

    def await_connection(self):
        while self.keep_running:
            try:
                sock, addr = self.socket.accept()
                print("INFO: Connection from {}".format(addr))
                with self.lock:
                    conn_id = self.id_gen.get_new()
                    self.connected_sockets[conn_id] = (sock, addr)
                self.handle_connection(conn_id, addr)
            except socket.timeout:
                pass
        print("INFO: Stopping listener.")

    def shutdown(self):
        self.keep_running = False
        for t in self.listening_sockets:
            t.join()
        # TODO: Close open connections.
        self.socket.shutdown(socket.SHUT_RDWR)

    def read_sockets(self):
        """Read what messages have come in on the established connections,
        and remove stale connections."""
        with self.lock:
            for sock, addr in self.connected_sockets:
                pass

    def handle_connection(self, connection_id, addr):
        """A connection has been made. This should be handled by the agent."""
        raise NotImplementedError


class NetworkConnector:
    def __init__(self, host='127.0.0.1', port=50550):
        self.socket = socket.socket()
        self.host = host
        self.port = port

    def connect(self):
        self.socket.connect((self.host, self.port))
