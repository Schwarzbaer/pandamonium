import socket
from queue import Queue, Empty
from threading import Thread, Lock

from pandamonium.util import IDGenerator


class NetworkListener:
    def __init__(self):
        # FIXME: Infer this from channels attribute instead.
        self.id_gen = IDGenerator(id_range=self.connection_ids)

        self.socket = socket.socket()
        self.socket.bind((self.interface, self.port))
        self.socket.listen()
        self.socket.settimeout(self.timeout)

        self.listening_sockets = []
        self.listeners = self.listeners
        self.keep_running = True
        self.connections = {}
        self.connections_lock = Lock()

    def listen(self):
        for _ in range(self.listeners):
            print("INFO: Adding listener")
            t = Thread(target=self.await_connection)
            self.listening_sockets.append(t)
            t.start()
            print("INFO: Started listener thread {}".format(t.name))

    def await_connection(self):
        """Used internally by the listener threads. Accept new connections and
        have them set up. Also check periodically for the shutdown."""
        while self.keep_running:
            try:
                connection = self.socket.accept()
                sock, addr = connection
                print("INFO: Connection from {}".format(addr))
                self.setup_connection(connection)
            except socket.timeout:
                pass
        print("INFO: Stopping listener.")

    def setup_connection(self, connection):
        connection_id = self.id_gen.get_new()
        sock, addr = connection
        if self.threaded_connections:
            thread = Thread(target=self.threaded_read, args=(connection_id, ))
            read_lock = Lock() # Since only one thread reads the socket, maybe
                               # only have the write lock?
            write_lock = Lock()
        else:
            thread = None
            read_lock = None
            write_lock = None
        full_connection = (sock, addr, thread, read_lock, write_lock)
        with self.connections_lock:
            self.connections[connection_id] = full_connection
        self.handle_connection(connection_id, addr)
        if self.threaded_connections:
            thread.start()

    def read_sockets(self):
        """Unthreaded reading. Read what messages have come in on the
        established connections, and remove stale connections."""
        with self.connections_lock:
            stale_connections = []
            for sock, _, _, _, _ in self.connections:
                # TODO: Implement reading and cleanup.
                pass
            for connection in stale_connections:
                # TODO: Announce staleness
                # FIXME: What if a message to a stale connection comes in later?
                del self.connections[connection]

    def threaded_read(self, connection_id):
        full_connection = self.connections[connection_id]
        sock, addr, thread, read_lock, write_lock = full_connection
        print("INFO: Starting thread for connection {} ({})".format(
            connection_id, addr))
        # FIXME: If connection has been closed, stop loop too, and clean up.
        while self.keep_running:
            with read_lock:
                try:
                    # TODO: Implement reading.
                    pass
                except socket.timeout:
                    pass
        print("INFO: Stopping thread for connection {}".format(connection_id))

    def shutdown(self):
        self.keep_running = False
        for t in self.listening_sockets:
            t.join()
        # TODO: Close open connections.
        # TODO: if self.threaded_connections: reader_threads.join()
        self.socket.shutdown(socket.SHUT_RDWR)

    def handle_connection(self, connection_id, addr):
        """A connection has been made. This is implemented by the agent."""
        raise NotImplementedError


class AIListener(NetworkListener):
    interface = '127.0.0.1'
    port = 50550
    listeners = 1
    timeout = 5.0
    threaded_connections = False


class ClientListener(NetworkListener):
    interface = '0.0.0.0'
    port = 50551
    listeners = 1
    timeout = 5.0
    threaded_connections = False


class NetworkConnector:
    def __init__(self):
        self.socket = socket.socket()

    def connect(self):
        self.socket.connect((self.host, self.port))
        # TODO: Start reader thread


class AIConnector(NetworkConnector):
    host ='127.0.0.1'
    port = 50550


class ClientConnector(NetworkConnector):
    def __init__(self, host='127.0.0.1', port=50551):
        self.host = host
        self.port = port
        super().__init__()


class InternalListener:
    def __init__(self):
        # FIXME: As in NetworkListener. Maybe move it into a BaseListener?
        self.id_gen = IDGenerator(id_range=self.connection_ids)
        self.listeners = {}

    def listen(self):
        pass  # Not necessary, as repos will just call setup_connection().

    def setup_connection(self, listener):
        connection_id = self.id_gen.get_new()
        self.listeners[connection_id] = listener
        self.handle_connection(connection_id, 'internal')

    def shutdown(self):
        pass

    def handle_connection(self, connection_id, addr):
        """A connection has been made. This is implemented by the agent."""
        raise NotImplementedError


class InternalConnector:
    def __init__(self, listener):
        self.listener = listener

    def connect(self):
        self.listener.setup_connection(self)
