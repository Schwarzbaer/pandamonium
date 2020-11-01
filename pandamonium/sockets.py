import socket
from queue import Queue, Empty
from threading import Thread, Lock
import logging

from pandamonium.util import IDGenerator
from pandamonium.constants import channels, msgtypes
from pandamonium.packers import DatagramIncomplete


logger = logging.getLogger(__name__)


class BaseListener:
    def listen(self):
        """Start to listen for new connections."""
        raise NotImplementedError

    def shutdown(self):
        """Shut down the listener."""
        raise NotImplementedError

    def handle_broadcast_message(self, from_channel, to_channel, message_type,
                                  *args):
        """A message for all connections has occurred."""
        raise NotImplementedError

    def handle_connection_message(self, from_channel, to_channel, message_type,
                                  *args):
        """A message for a connection has occurred."""
        raise NotImplementedError


class BaseConnector:
    def connect(self):
        """Make connection to listener."""
        raise NotImplementedError

    def send_message(self, message_type, *args):
        """Send a message to the listener."""
        raise NotImplementedError

    def disconnect(self):
        """Explicitly disconnect."""
        raise NotImplementedError


# Network classes. These currently do only TCP, but should be extendable to
# hybrid TCP / UDP.


class NetworkListenerConnection:
    def __init__(self, agent, socket, address, connection_id):
        self.agent = agent
        self.socket = socket
        self.address = address
        self.connection_id = connection_id
        self.keep_running = True
        self.keep_enqueueing = True
        self.queue = Queue()
        self.timeout = 2.0
        self.socket.settimeout(self.timeout)

        self.reader_tread = Thread(
            target=self.read_socket,
            name="Reader thread ({})".format(connection_id)
        )
        self.writer_tread = Thread(
            target=self.write_socket,
            name="Writer thread ({})".format(connection_id)
        )
        self.reader_tread.start()
        self.writer_tread.start()

    def __repr__(self):
        return "Connection {}".format(self.connection_id)

    def read_socket(self):
        logger.info("Starting thread for connection {} ({})".format(
            self.connection_id, self.address))
        datagram = b''
        try:
            while self.keep_running:
                try:
                    incoming = self.socket.recv(1024)
                    if incoming == b'':
                        raise ConnectionResetError
                    datagram += incoming
                    try:
                        while True:
                            message, datagram = self.agent.unpack_message(
                                datagram,
                            )
                            self.agent.handle_incoming_message(*message)
                    except DatagramIncomplete:
                        # keep reading
                        pass
                except socket.timeout:
                    pass
        except ConnectionResetError:
            logger.warning("{} lost connection".format(self))
        self.agent.close_connection(self.connection_id)
        logger.info("Stopping reader thread for connection {}"
                    "".format(self.connection_id))

    def write_socket(self):
        # FIXME: Handle socket disconnection with cleanup
        while self.keep_running:
            try:
                message = self.queue.get(block=True, timeout=self.timeout)
                datagram = self.agent.pack_message(*message)
                self.socket.send(datagram)
            except Empty:
                pass
        logger.info("Stopping writer thread for connection {}"
                    "".format(self.connection_id))

    def enqueue(self, *message):
        if self.keep_enqueueing:
            self.queue.put(message)
        else:
            pass

    def shutdown(self):
        self.keep_running = False
        self.keep_enqueueing = False
        # FIXME: Move into cleanup
        self.socket.shutdown(socket.SHUT_RDWR)

    def join(self):
        self.reader_tread.join()
        self.writer_tread.join()


class NetworkListener(BaseListener):
    def __init__(self):
        self.id_gen = IDGenerator(id_range=self.connection_ids)
        self.dclasses_by_id = [self.dclasses[dclass_name]
                               for dclass_name in sorted(self.dclasses)]
        self.dclasses_by_dobject_id = {}
        self.dclasses_lock = Lock()

        self.socket = socket.socket()
        self.socket.bind((self.interface, self.port))
        self.socket.listen()
        self.socket.settimeout(self.timeout)

        self.listener_thread = None
        self.cleanup_thread = None
        self.cleanup_queue = Queue()
        self.keep_running = True
        self.connections = {}
        self.connections_lock = Lock()

    def listen(self):
        logger.debug("{} starting listener thread".format(self))
        self.listener_thread = Thread(
            target=self._await_connection,
            name="Listener thread ({})".format(self),
        )
        self.listener_thread.start()
        logger.debug("{} starting cleanup thread".format(self))
        self.cleanup_thread = Thread(
            target=self._cleanup_loop,
            name="Cleanup thread ({})".format(self),
        )
        self.cleanup_thread.start()
        logger.info("{} started listener".format(self))

    def _await_connection(self):
        """Used internally by the listener threads. Accept new connections and
        have them set up. Also check periodically for the shutdown."""
        while self.keep_running:
            try:
                connection = self.socket.accept()
                sock, addr = connection
                logger.info("Connection from {}".format(addr))
                self._setup_connection(connection)
            except socket.timeout:
                pass
        logger.info("{} stopped listener".format(self))

    def _setup_connection(self, connection):
        sock, addr = connection
        # TODO: Check addr against a blacklist
        connection_id = self.id_gen.get_new()
        logger.info("{} opens connection from {} (id {})"
                    "".format(self, addr, connection_id))
        with self.connections_lock:
            self.connections[connection_id] = NetworkListenerConnection(
                self,
                sock,
                addr,
                connection_id,
            )
        self.message_director.subscribe_to_channel(connection_id, self)
        self.handle_connection(connection_id, addr)

    def close_connection(self, connection_id):
        logger.fatal("Implement closing for connection {}, please"
                      "".format(connection_id))
        self.message_director.unsubscribe_from_channel(connection_id, self)
        # TODO: broadcast ai/client vanishing
        self.cleanup_queue.put(connection_id)

    def _cleanup_loop(self):
        while self.keep_running or self.connections:
            try:
                connection_id = self.cleanup_queue.get(
                    block=True,
                    timeout=self.timeout,
                )
                self.connections[connection_id].shutdown()
                self.connections[connection_id].join()
                del self.connections[connection_id]
                logger.info("Cleaned up connection {}".format(connection_id))
            except Empty:
                pass
        logger.info("Cleanup thread for {} finished".format(self))

    def shutdown(self):
        self.keep_running = False
        logger.info("{} shutting down listener".format(self))
        self.listener_thread.join()
        logger.info("{} shutting down connections".format(self))
        for connection in self.connections.values():
            connection.shutdown()
        logger.info("{} waiting for cleanup to finish".format(self))
        self.cleanup_thread.join()
        logger.info("{} shutting down socket".format(self))
        self.socket.shutdown(socket.SHUT_RDWR)


class NetworkAIListener(NetworkListener):
    interface = '127.0.0.1'
    port = 50550
    timeout = 5.0
    threaded_connections = True

    def handle_connection_message(self, from_channel, to_channel, message_type,
                                  *args):
        logger.info("AIListener got connection message to handle: {} -> {} ({})"
                    "".format(
                        from_channel, to_channel, message_type,
                    )
        )
        self.send_message(
            self.connections[to_channel],
            from_channel,
            to_channel,
            message_type,
            *args,
        )

    def handle_broadcast_message(self, from_channel, to_channel, message_type,
                                  *args):
        logger.info("AIAgent got broadcast message to handle: {} -> {} ({})"
                    "".format(
                        from_channel, to_channel, message_type,
                    )
        )
        for connection in self.connections.values():
            self.send_message(
                connection,
                from_channel,
                to_channel,
                message_type,
                *args,
            )

    def send_message(self, connection, from_channel, to_channel, message_type,
                     *args):
        connection.enqueue(from_channel, to_channel, message_type, *args)


    def __repr__(self):
        return "<AI agent listener>"


class NetworkClientListener(NetworkListener):
    interface = '0.0.0.0'
    port = 50551
    timeout = 5.0
    threaded_connections = True

    def handle_connection_message(self, from_channel, to_channel, message_type,
                                  *args):
        logger.debug("ClientAgent got connection message to handle: "
                     "{} -> {} ({})".format(
                         from_channel, to_channel, message_type,
                    )
        )
        # if message_type == msgtypes.DISCONNECT_CLIENT:
        #     client_id = to_channel
        #     reason = args[0]
        #     self.handle_disconnect_client(client_id, reason)
        # else:
        #     self.listeners[to_channel].handle_message(
        #         message_type,
        #         *args,
        #     )

    def __repr__(self):
        return "<client agent listener>"


class NetworkConnector(BaseConnector):
    def __init__(self):
        self.socket = socket.socket()
        self.dclasses_by_id = [self.dclasses[dclass_name]
                               for dclass_name in sorted(self.dclasses)]
        self.datagram = b''

    def connect(self):
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(0.0001)

    def _read_socket(self):
        try:
            while True:
                incoming = self.socket.recv(1024)
                if incoming == b'':
                    raise ConnectionResetError
                print(incoming)
                self.datagram += incoming
                try:
                    while True:
                        self.datagram = self.handle_incoming_datagram(
                            self.datagram,
                        )
                except DatagramIncomplete:
                    pass
        except socket.timeout:
            pass
        except ConnectionResetError:
            self.close_connection()

    def close_connection(self):
        logger.fatal("Implement close_connection, please")


class NetworkAIConnector(NetworkConnector):
    host ='127.0.0.1'
    port = 50550

    def handle_incoming_datagram(self, datagram):
        message, datagram = self.unpack_message(datagram)
        [from_channel, to_channel, message_type, *args] = message
        self.handle_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        ) # FIXME: This should write into a queue instead, and i.e. a Panda3D
          # task should process what's in it.
        return datagram

    def send_message(self, from_channel, to_channel, message_type, *args):
        datagram = self.pack_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        )
        self.socket.send(datagram)


class NetworkClientConnector(NetworkConnector):
    def __init__(self, host='127.0.0.1', port=50551):
        self.host = host
        self.port = port
        super().__init__()

    def handle_incoming_datagram(self, datagram):
        logger.info("Handling incoming datagram")
        message, datagram = self.unpack_message(datagram)
        [message_type, *args] = message
        self.handle_message(
            message_type,
            *args,
        ) # FIXME: This should write into a queue instead, and i.e. a Panda3D
          # task should process what's in it.
        logger.info("Handled incoming datagram")
        return datagram

    def send_message(self, message_type, *args):
        datagram = self.pack_message(
            message_type,
            *args,
        )
        self.socket.send(datagram)


# "Internal" "network" means that everything is running in the same process, and
# anything networky is done simply by function calls. This should be highly
# efficient, since there's no packing / unpacking of messages, but also means
# that there's no vertical scaling (Thanks, GLI!). Also, there's no concept of
# thread safety implemented on this level, since when a "message sending" call
# of yours returns, it has already been completely processed on the "other
# side".


class InternalListener(BaseListener):
    def __init__(self):
        # FIXME: As in NetworkListener. Maybe move it into a BaseListener?
        self.id_gen = IDGenerator(id_range=self.connection_ids)
        self.listeners = {}

    def listen(self):
        pass  # Not necessary, as repos will just call _setup_connection().

    def _get_connection_id(self):
        return self.id_gen.get_new()

    def _setup_connection(self, listener, connection_id):
        self.listeners[connection_id] = listener
        self.message_director.subscribe_to_channel(connection_id, self)
        self.handle_connection(connection_id, 'internal')
        return connection_id

    def _remove_connection(self, connection_id):
        self.message_director.unsubscribe_from_channel(connection_id, self)
        listener = self.listeners[connection_id]
        del self.listeners[connection_id]

    def shutdown(self):
        raise NotImplemented
        for connection in self.connections.values():
            connection.shutdown()


class InternalAIListener(InternalListener):
    def handle_broadcast_message(self, from_channel, to_channel, message_type,
                                 *args):
        logger.debug("AIAgent got broadcast to handle: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        for listener in self.listeners:
            self.listeners[listener].handle_message(
                from_channel,
                to_channel,
                message_type,
                *args,
            )

    def handle_connection_message(self, from_channel, to_channel, message_type,
                                  *args):
        logger.debug("AIAgent got connection message to handle: {} -> {} ({})"
                     "".format(
                         from_channel, to_channel, message_type,
                    )
        )
        self.listeners[to_channel].handle_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        )


class InternalClientListener(InternalListener):
    def handle_broadcast_message(self, from_channel, to_channel, message_type,
                                 *args):
        logger.debug("ClientAgent got broadcast to handle: {} -> {} ({})"
                     "".format(
                         from_channel, to_channel, message_type,
                     )
        )
        for listener in self.listeners:
            self.listeners[listener].handle_message(
                message_type,
                *args,
            )

    # FIXME: Can special case mapping like for DISCONNECT_CLIENT be moved
    # upwards / sideways in the class hierarchy?
    def handle_connection_message(self, from_channel, to_channel, message_type,
                                  *args):
        logger.debug("ClientAgent got connection message to handle: "
                     "{} -> {} ({})".format(
                         from_channel, to_channel, message_type,
                    )
        )
        if message_type == msgtypes.DISCONNECT_CLIENT:
            client_id = to_channel
            reason = args[0]
            self.handle_disconnect_client(client_id, reason)
        else:
            self.listeners[to_channel].handle_message(
                message_type,
                *args,
            )

    def handle_disconnect(self, client_id):
        self.handle_connection_message(
            client_id,
            client_id,
            msgtypes.DISCONNECT_CLIENT,
            "Client-requested disconnect.",
        )

    def handle_disconnect_client(self, client_id, reason):
        self.listeners[client_id].handle_message(
            msgtypes.DISCONNECTED,
            reason,
        )
        self._remove_connection(client_id)
        self.message_director.create_message(
            client_id,
            channels.ALL_AIS,
            msgtypes.CLIENT_DISCONNECTED,
            client_id,
        )


class InternalConnector(BaseConnector):
    def connect(self, listener):
        logger.debug("{} connecting to {}".format(self, listener))
        self.listener = listener
        # Not having a complicated setup has the consequence that the connector
        # has to know and add the client ID.
        # Word of warning: The repo associated with this connection will receive
        # and handle the CONNECTED message before this call finishes, meaning
        # that you shouldn't react to it in an override of connected() that'll
        # require knowing the connection ID.
        self.connection_id = listener._get_connection_id()
        self.listener._setup_connection(self, self.connection_id)

    def send_message(self, message_type, *args):
        raise NotImplementedError

    def disconnect(self):
        self.send_message(msgtypes.DISCONNECT)


class InternalAIConnector(InternalConnector):
    def send_message(self, from_channel, to_channel, message_type, *args):
        logger.debug("AI sending message {} -> {} ({})".format(
            from_channel,
            to_channel,
            message_type,
        ))
        self.listener.handle_incoming_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        )


class InternalClientConnector(InternalConnector):
    def send_message(self, message_type, *args):
        logger.debug("Client sending message ({})".format(message_type))
        self.listener.handle_incoming_message(
            self.connection_id,
            message_type,
            *args,
        )
