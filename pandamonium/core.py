from threading import Lock
import logging

from pandamonium.base import BaseComponent
from pandamonium.state_server import StateServer
from pandamonium.constants import channels, msgtypes
from pandamonium.util import IDGenerator


logger = logging.getLogger(__name__)


# FIXME: Add _handle_incoming_message()?
class BaseAgent(BaseComponent):
    def handle_connection(self, conn_id, addr):
        """Agent's socket has received a new connection. Broadcast info."""
        raise NotImplementedError

    def handle_message(self, from_channel, to_channel, message_type, *args):
        """Message for the agent, or one of its connections."""
        logger.debug("Agent {} got message to handle: {} -> {} ({})".format(
            self, from_channel, to_channel, message_type,
        ))
        if to_channel == self.all_connections:
            # message to the agent
            self.handle_broadcast_message(
                from_channel,
                to_channel,
                message_type,
                *args,            )
        else:
            # message to a connection
            self.handle_connection_message(
                from_channel,
                to_channel,
                message_type,
                *args,
            )

    def get_dobject_dclass(self, dobject_id):
        self.state_server.get_dobject_fields(dobject_id)


class AIAgent(BaseAgent):
    all_connections = channels.ALL_AIS
    connection_ids = channels.AIS

    def handle_connection(self, ai_id, addr):
        logger.info("Connection from AI {} ({})".format(ai_id, addr))
        self.message_director.create_message(
            self.all_connections,
            ai_id,
            msgtypes.AI_CHANNEL_ASSIGNED,
            ai_id,
        )
        self.message_director.create_message(
            ai_id,
            channels.ALL_AIS,
            msgtypes.AI_CONNECTED,
            ai_id,
        )

    def handle_incoming_message(self, from_channel, to_channel, message_type,
                                  *args):
        logger.info("AIAgent got incoming message to handle: {} -> {} ({})"
                    "".format(
                        from_channel, to_channel, message_type,
                    )
        )
        if from_channel is None:
            from_channel = self.channel
        self.message_director.create_message(
            from_channel,
            to_channel,
            message_type,
            *args,
        )


class ClientAgent(BaseAgent):
    all_connections = channels.ALL_CLIENTS
    connection_ids = channels.CLIENTS

    def handle_connection(self, client_id, addr):
        logger.info("Connection from client {} ({})".format(client_id, addr))
        self.message_director.create_message(
            client_id,
            client_id,
            msgtypes.CONNECTED,
        )
        self.message_director.create_message(
            client_id,
            channels.ALL_AIS,
            msgtypes.CLIENT_CONNECTED,
            client_id,
        )

    def handle_incoming_message(self, connection_id, message_type, *args):
        logger.debug("ClientAgent got incoming message to handle: "
                     "{} -> {} ({})".format(
                         from_channel, to_channel, message_type,
                    )
        )
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


# TODO
# _ Implement wait_for_ai: If True, don't start up the client agent before an
#   AIRepository has connected. The idea is to let that repo do necessary
#   initial setup before a client has the chance to connect. Maybe there should
#   be a whole sub-protocol about this setup phase?
class MessageDirector:
    def __init__(self, state_server=None,client_agent=None, ai_agent=None,
                 wait_for_ai=True):
        self.channels = {}
        self.channels_lock = Lock()

        if state_server is None:
            state_server = StateServer()
        self.state_server = state_server
        self.state_server.set_message_director(self)

        if client_agent is None:
            client_agent = ClientAgent()
        self.client_agent = client_agent
        self.client_agent.set_message_director(self)

        if ai_agent is None:
            ai_agent = AIAgent()
        self.ai_agent = ai_agent
        self.ai_agent.set_message_director(self)

    def startup(self):
        logger.info("MessageDirector starting up.")
        self.ai_agent.listen()
        self.client_agent.listen()
        logger.info("MessageDirector startup complete.")

    def shutdown(self):
        """Shut down the whole server."""
        logger.info("MessageDirector shutting down.")
        self.ai_agent.shutdown()
        self.client_agent.shutdown()
        self.state_server.shutdown()
        logger.info("MessageDirector shutdown complete.")


    def subscribe_to_channel(self, channel, listener):
        logger.debug("New subscriber to {}: {}".format(channel, listener))
        with self.channels_lock:
            listeners = self.channels.get(channel, set())
            listeners.add(listener)
            self.channels[channel] = listeners

    def unsubscribe_from_channel(self, channel, listener):
        logger.debug("Unsubscribing from {}: {}".format(channel, listener))
        with self.channels_lock:
            # TODO: And if some key error occurs?
            listeners = self.channels[channel]
            listeners.remove(listener)

    def create_message(self, from_channel, to_channel, message_type, *args):
        # TODO: This might also write into a queue, which a thread, representing
        # the MD and/or SS, reads from, isolating the Agent thread to otherwise
        # keep in just the agent module.
        logger.debug("Creating message: {} -> {}: {}".format(
            from_channel, to_channel, message_type,
        ))
        with self.channels_lock:
            listeners = self.channels[to_channel].copy()
        for listener in listeners:
            listener.handle_message(
                from_channel,
                to_channel,
                message_type,
                *args,
            )


def start_server():
    try:
        md = MessageDirector()
    except:
        raise
