import socket
from queue import Queue, Empty
from threading import Thread, Lock
import logging

from pandamonium.util import IDGenerator
from pandamonium.constants import channels, msgtypes


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


class NetworkListener(BaseListener):
    def __init__(self):
        # FIXME: Infer this from channels attribute instead.
        self.id_gen = IDGenerator(id_range=self.connection_ids)

        self.socket = socket.socket()
        self.socket.bind((self.interface, self.port))
        self.socket.listen()
        self.socket.settimeout(self.timeout)

        self.listener_thread = None
        self.keep_running = True
        self.connections = {}
        self.connections_lock = Lock()

    def listen(self):
        logger.debug("{} starting listener".format(self))
        t = Thread(target=self._await_connection)
        self.listener_thread = t
        t.start()
        logger.info("{} started listener".format(self))
        # FIXME: if not self.threaded_connections: self._start_single_reader()

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
        connection_id = self.id_gen.get_new()
        logger.info("{} opens connection from {} (id {})"
                    "".format(self, addr, connection_id))
        # TODO: Check addr against a blacklist
        if self.threaded_connections:
            thread = Thread(target=self._threaded_read, args=(connection_id, ))
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
        self.message_director.subscribe_to_channel(connection_id, self)
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

    def _threaded_read(self, connection_id):
        full_connection = self.connections[connection_id]
        sock, addr, thread, read_lock, write_lock = full_connection
        logger.info("Starting thread for connection {} ({})".format(
            connection_id, addr))
        # FIXME: If connection has been closed, stop loop too, and clean up.
        message = b''
        try:
            while self.keep_running:
                with read_lock:
                    try:
                        incoming = sock.recv(1024)
                        if incoming == b'':
                            raise ConnectionResetError
                        message += incoming
                        print(message)
                    except socket.timeout:
                        pass
        except ConnectionResetError:
            self.close_connection(connection_id)
        logger.info("Stopping thread for connection {}".format(connection_id))

    def close_connection(self, connection_id):
        logger.fatal("Implement closing for connection {}, please"
                      "".format(connection_id))

    def shutdown(self):
        self.keep_running = False
        self.listener_thread.join()
        # TODO: Close open connections, after unsubscribing them from MD
        # TODO: if self.threaded_connections: reader_threads.join()
        self.socket.shutdown(socket.SHUT_RDWR)

    def handle_connection(self, connection_id, addr):
        """A connection has been made. This is implemented by the agent."""
        raise NotImplementedError


class NetworkAIListener(NetworkListener):
    interface = '127.0.0.1'
    port = 50550
    timeout = 5.0
    threaded_connections = True

    def handle_connection_message(self, from_channel, to_channel, message_type,
                                  *args):
        logger.info("AIAgent got connection message to handle: {} -> {} ({})"
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

    def handle_incoming_message(self, from_channel, to_channel, message_type,
                                  *args):
        logger.info("AIAgent got incoming message to handle: {} -> {} ({})"
                    "".format(
                        from_channel, to_channel, message_type,
                    )
        )
        # if from_channel is None:
        #     from_channel = self.channel
        # self.message_director.create_message(
        #     from_channel,
        #     to_channel,
        #     message_type,
        #     *args,
        # )

    def send_message(self, connection, from_channel, to_channel, message_type,
                     *args):
        (sock, addr, thread, read_lock, write_lock) = connection
        message = self.pack_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        )
        print(message)
        with write_lock:
            sock.send(message)


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

    def handle_incoming_message(self, connection_id, message_type, *args):
        logger.debug("ClientAgent got incoming message to handle: "
                     "{} -> {} ({})".format(
                         from_channel, to_channel, message_type,
                    )
        )
        # if message_type == msgtypes.DISCONNECT:
        #     client_id = from_channel
        #     self.handle_disconnect(client_id)
        # elif message_type == msgtypes.SET_FIELD:
        #     self.message_director.create_message(
        #         connection_id,
        #         channels.ALL_STATE_SERVERS,  # FIXME: *ALL*?
        #         message_type,
        #         *args,
        #     )
        # else:
        #     raise NotImplementedError

    def __repr__(self):
        return "<client agent listener>"


class NetworkConnector(BaseConnector):
    def __init__(self):
        self.socket = socket.socket()

    def connect(self):
        self.socket.connect((self.host, self.port))
        #logger.debug("{} starting reader thread".format(self))
        self.keep_reading = True
        #self.read_thread = Thread(target=self._read_socket)
        #self.read_thread.start()

    def _read_socket(self):
        datagram = b''
        try:
            while self.keep_reading:
                try:
                    incoming = self.socket.recv(1024)
                    datagram += incoming
                    print(datagram)
                    datagram = self.handle_incoming_datagram(datagram)
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
        pass


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

    def handle_incoming_message(self, from_channel, to_channel, message_type,
                                  *args):
        if from_channel is None:
            from_channel = self.channel
        self.message_director.create_message(
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

    def handle_incoming_message(self, connection_id, message_type, *args):
        if message_type == msgtypes.DISCONNECT:
            client_id = from_channel
            self.handle_disconnect(client_id)
        elif message_type == msgtypes.SET_FIELD:
            self.message_director.create_message(
                connection_id,
                channels.ALL_STATE_SERVERS,  # FIXME: *ALL*?
                message_type,
                *args,
            )
        else:
            raise NotImplementedError

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
