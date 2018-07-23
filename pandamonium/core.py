from threading import Lock

from pandamonium.config import config
from pandamonium.constants import channels, msgtypes


class BaseComponent:
    def set_message_director(self, message_director):
        self.message_director = message_director
        self.message_director.subscribe_to_channel(self.all_connections, self)

    def handle_message(self, from_channel, to_channel, message_type, *args):

        raise NotImplementedError


class StateServer(BaseComponent):
    all_connections = channels.ALL_STATE_SERVERS

    def __init__(self):
        self.objects = {}
        self.interests = {}
        # TODO: For the moment, we'll use a single lock to protect the whole of
        # the state; dobject existence, presence in zones, and interest. This is
        # a topic ripe for optimization, if you can do it without creating
        # deadlocks. Maybe do optimistic concurrency? Have a nifty planner
        # that'll schedule event processing into isolated parallelity?
        self.state_lock = Lock()

    def shutdown(self):
        pass

    def handle_message(self, from_channel, to_channel, message_type, *args):
        print("StateServer received: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        if message_type == msgtypes.SET_INTEREST:
            recipient = args[0]
            zone = args[1]
            self._handle_set_interest(recipient, zone)
        elif message_type == msgtypes.UNSET_INTEREST:
            recipient = args[0]
            zone = args[1]
            self._handle_unset_interest(recipient, zone)
        else:
            raise NotImplementedError

    def _handle_set_interest(self, recipient, zone):
        print("StateServer sets interest for {} in {}".format(
            recipient,
            zone,
        ))
        with self.state_lock:
            recipients = self.interests.get(zone, set())
            recipients.add(recipient)
            self.interests[zone] = recipients

    def _handle_unset_interest(self, recipient, zone):
        print("StateServer revokes interest for {} in {}".format(
            recipient,
            zone,
        ))
        with self.state_lock:
            recipients = self.interests[zone]
            recipients.remove(recipient)


# FIXME: Add _handle_incoming_message()?
class BaseAgent(BaseComponent):
    def handle_connection(self, conn_id, addr):
        """Agent's socket has received a new connection. Broadcast info."""
        raise NotImplementedError

    def handle_message(self, from_channel, to_channel, message_type, *args):
        """Message for the agent, or one of its connections."""
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


class ClientAgent(BaseAgent):
    all_connections = channels.ALL_CLIENTS
    connection_ids = channels.CLIENTS

    def handle_connection(self, client_id, addr):
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


class AIAgent(BaseAgent):
    all_connections = channels.ALL_AIS
    connection_ids = channels.AIS

    def handle_connection(self, ai_id, addr):
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
        self.ai_agent.listen()
        self.client_agent.listen()

    def shutdown(self):
        """Shut down the whole server."""
        self.ai_agent.shutdown()
        self.client_agent.shutdown()
        self.state_server.shutdown()

    def subscribe_to_channel(self, channel, listener):
        print("DEBUG: New subscriber to {}: {}".format(channel, listener))
        with self.channels_lock:
            listeners = self.channels.get(channel, set())
            listeners.add(listener)
            self.channels[channel] = listeners

    def unsubscribe_from_channel(self, channel, listener):
        print("DEBUG: Unsubscribing from {}: {}".format(channel, listener))
        with self.channels_lock:
            # TODO: And if some key error occurs?
            listeners = self.channels[channel]
            listeners.remove(listener)

    def create_message(self, from_channel, to_channel, message_type, *args):
        print("DEBUG: {} -> {}: {}".format(
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
