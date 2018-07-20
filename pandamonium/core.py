from threading import Lock

from pandamonium.config import config
from pandamonium.constants import channels, msgtypes


class StateServer:
    def __init__(self, message_director):
        self.message_director = message_director
        self.zones = {}
        self.objects = {}
        self.interests = {}

    def shutdown(self):
        pass

    def create_object(self):
        pass

    def destroy_object(self):
        pass

    def add_object_to_zone(self, dobject, zone):
        pass

    def remove_object_from_zone(self, dobject, zone):
        pass

    def set_interest(self, client, zone):
        pass

    def remove_interest(self, client, zone):
        pass


class BaseAgent:
    def set_message_director(self, message_director):
        self.message_director = message_director
        self.message_director.subscribe_to_channel(self.own_channel, self)

    def handle_connection(self, conn_id, addr):
        """Agent's socket has received a new connection. Broadcast info."""
        raise NotImplementedError

    def handle_message(self, from_channel, to_channel, message_type, *args):
        """Message for the agent, or one of its connections."""
        if to_channel == self.own_channel:
            # message to the agent
            self.handle_agent_message(
                from_channel,
                to_channel,
                message_type,
                *args,
            )
        else:
            # message to a connection
            self.handle_connection_message(
                from_channel,
                to_channel,
                message_type,
                *args,
            )

    def handle_agent_message(self, from_channel, to_channel, message_type,
                             *args):
        raise NotImplementedError


class ClientAgent(BaseAgent):
    own_channel = channels.ALL_CLIENTS
    connection_ids = channels.CLIENTS

    def handle_connection(self, client_id, addr):
        self.message_director.create_message(
            client_id,
            channels.ALL_AIS,
            msgtypes.CLIENT_CONNECTED,
        )

    def handle_agent_message(self, from_channel, to_channel, message_type,
                             *args):
        # FIXME: Implement
        print("DEBUG: ClientAgent received {} -> {} ()".format(
            from_channel,
            to_channel,
            message_type,
        ))


class AIAgent(BaseAgent):
    own_channel = channels.ALL_AIS
    connection_ids = channels.AIS

    def handle_connection(self, ai_id, addr):
        self.message_director.create_message(
            self.own_channel,
            ai_id,
            msgtypes.AI_CHANNEL_ASSIGNED,
        )
        self.message_director.create_message(
            ai_id,
            channels.ALL_AIS,
            msgtypes.AI_CONNECTED,
        )

    def handle_agent_message(self, from_channel, to_channel, message_type,
                             *args):
        # FIXME: Implement!
        print("DEBUG: AIAgent received {} -> {} ()".format(
            from_channel,
            to_channel,
            message_type,
        ))


# TODO
# _ Implement wait_for_ai: If True, don't start up the client agent before an
#   AIRepository has connected. The idea is to let that repo do necessary
#   initial setup before a client has the chance to connect. Maybe there should
#   be a whole sub-protocol about this setup phase?
class MessageDirector:
    def __init__(self, client_agent=None, ai_agent=None, wait_for_ai=True):
        self.channels = {}
        self.channels_lock = Lock()

        if client_agent is None:
            client_agent = ClientAgent()
        self.client_agent = client_agent
        self.client_agent.set_message_director(self)

        if ai_agent is None:
            ai_agent = AIAgent()
        self.ai_agent = ai_agent
        self.ai_agent.set_message_director(self)

        self.state_server = StateServer(self)

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
