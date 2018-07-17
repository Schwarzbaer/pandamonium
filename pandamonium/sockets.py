import socket
from queue import Queue, Empty
from threading import Thread, Lock

from pandamonium.util import IDGenerator


# TODO: Overhaul from scratch!
def make_internal_socket():
    class InternalSocket:
        def __init__(self, inbound, outbound):
            self.inbound = inbound
            self.outbound = outbound

        def set_agent(self, agent):
            self.agent = agent

        def listen(self):
            pass

        def connect(self):
            pass

        def send(self, message):
            self.outbound.put(message)

        def read(self):
            try:
                return self.inbound.get_nowait()
            except Empty:
                return

    client_to_agent = Queue()
    agent_to_client = Queue()

    client_socket = InternalSocket(agent_to_client, client_to_agent)
    agent_socket = InternalSocket(client_to_agent, agent_to_client)

    return (client_socket, agent_socket)


class NetworkListener:
    def __init__(self, interface='127.0.0.1', port=50550, listeners=1,
                 timeout=5.0):
        self.agent = None
        self.id_gen = None

        self.socket = socket.socket()
        self.socket.bind((interface, port))
        self.socket.listen()
        self.socket.settimeout(timeout)

        self.listening_sockets = []
        self.listeners = listeners
        self.lock = Lock()
        self.keep_running = True
        self.connected_sockets = {}

    def set_agent(self, agent):
        self.agent = agent
        self.id_gen = IDGenerator(start_id=self.agent.start_id)

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
                self.agent.handle_connection(conn_id, addr)
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
        """A connection has been made."""
        pass


class AIListener(NetworkListener):
    def handle_connection(self, ai_id, addr):
        self.agent.message_director.ai_connected(ai_id)


class ClientListener(NetworkListener):
    def handle_connection(self, client_id, addr):
        self.agent.message_director.client_connected(client_id)


class NetworkConnector:
    def __init__(self, host='127.0.0.1', port=50550):
        self.socket = socket.socket()
        self.host = host
        self.port = port

    def connect(self):
        self.socket.connect((self.host, self.port))
