from pandamonium.config import config
from pandamonium.constants import channels, msgtypes


class StateServer:
    def __init__(self, message_director):
        self.message_director = message_director
        self.zones = {}
        self.objects = {}
        self.interests = {}

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

    def handle_connection(self, conn_id, addr):
        """"Agent's socket has received a new connection. Broadcast info."""
        raise NotImplementedError


class ClientAgent(BaseAgent):
    connection_start_id = 100000

    def handle_connection(self, client_id, addr):
        self.message_director.create_message(
            client_id,
            channels.ALL_AIS,
            msgtypes.CLIENT_CONNECTED,
        )


class AIAgent(BaseAgent):
    connection_start_id = 1000

    def handle_connection(self, ai_id, addr):
        self.message_director.create_message(
            ai_id,
            ai_id,
            msgtypes.AI_CHANNEL_ASSIGNED,
        )
        self.message_director.create_message(
            ai_id,
            channels.ALL_AIS,
            msgtypes.AI_CONNECTED,
        )


# TODO
# _ Implement wait_for_ai: If True, don't start up the client agent before an
#   AIRepository has connected. The idea is to let that repo do necessary
#   initial setup before a client has the chance to connect. Maybe there should
#   be a whole sub-protocol about this setup phase?
class MessageDirector:
    def __init__(self, client_agent=None, ai_agent=None, wait_for_ai=True):
        self.channels = {}

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

    def create_message(self, from_channel, to_channel, message_type, *args):
        pass


def start_server():
    try:
        md = MessageDirector()
    except:
        raise
