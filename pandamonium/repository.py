import socket
import logging

from pandamonium.constants import channels, msgtypes
from pandamonium.dobject import DistributedObject


logger = logging.getLogger(__name__)


class BaseRepository:
    def __init__(self):
        self.dobjects = {}

    def connected(self):
        """Message handler: Network has acknowledged our connection."""
        pass

    def handle_create_dobject_view(self, dobject_id, dclass, fields):
        self.dobjects[dobject_id] = self.views[dclass.name](
            dobject_id,
            dclass,
            fields,
            repo=self,
        )

class ClientRepository(BaseRepository):
    def handle_message(self, message_type, *args):
        """Message received, needs to be handled."""
        logger.debug("ClientRepository got message to handle: {}".format(
            message_type
        ))
        if message_type == msgtypes.CONNECTED:
            self.connected()
        elif message_type == msgtypes.DISCONNECTED:
            reason = args[0]
            self.handle_disconnected(reason)
        elif message_type == msgtypes.CREATE_DOBJECT_VIEW:
            dobject_id = args[0]
            dclass = args[1]
            fields = args[2]
            self.handle_create_dobject_view(dobject_id, dclass, fields)
        elif message_type == msgtypes.BECOME_OWNER:
            dobject_id = args[0]
            self.handle_become_owner(dobject_id)
        else:
            # FIXME: Better to log it and drop it on the floor?
            raise NotImplementedError

    def handle_connected(self):
        """Connection to client agent has been established."""
        logger.info("ClientRepository has connected to network.")

    def handle_disconnected(self, reason):
        """Connection will be terminated shortly by the other end."""
        logger.info("ClientRepository is being disconnected, reason: {}".format(
            reason,
        ))

    def handle_create_dobject_view(self, dobject_id, dclass, fields):
        logger.info("ClientRepository creates view for "
              "dobject \"{}\"".format(dobject_id))
        super().handle_create_dobject_view(dobject_id, dclass, fields)

    def handle_become_owner(self, dobject_id):
        dobject = self.dobjects[dobject_id]
        dobject.become_owner()


class AIRepository(BaseRepository):
    channel = None

    def handle_message(self, from_channel, to_channel, message_type, *args):
        """Message received, needs to be handled."""
        logger.debug("{} received message: {} -> {} ({})".format(
            self, from_channel, to_channel, message_type,
        ))
        # TODO: Validation
        if message_type == msgtypes.AI_CHANNEL_ASSIGNED:
            channel = args[0]
            self.handle_channel_assigned(channel)
        elif message_type == msgtypes.AI_CONNECTED:
            channel = args[0]
            self.handle_ai_connected(channel)
        elif message_type == msgtypes.CLIENT_CONNECTED:
            client_id = args[0]
            self.handle_client_connected(client_id)
        elif message_type == msgtypes.CLIENT_DISCONNECTED:
            client_id = args[0]
            self.handle_client_disconnected(client_id)
        elif message_type == msgtypes.DOBJECT_CREATED:
            dobject_id = args[0]
            token = args[1]
            self.handle_dobject_created(dobject_id, token)
        elif message_type == msgtypes.CREATE_DOBJECT_VIEW:
            dobject_id = args[0]
            dclass = args[1]
            fields = args[2]
            self.handle_create_dobject_view(dobject_id, dclass, fields)
        elif message_type == msgtypes.CREATE_AI_VIEW:
            dobject_id = args[0]
            dclass = args[1]
            fields = args[2]
            self.handle_create_ai_view(dobject_id, dclass, fields)
        elif message_type == msgtypes.FIELD_UPDATE:
            source = from_channel
            dobject_id = args[0]
            field_id = args[1]
            values = args[2]
            self.handle_field_update(source, dobject_id, field_id, values)
        else:
            # FIXME: Better to log it and drop it on the floor?
            raise NotImplementedError

    def handle_channel_assigned(self, channel):
        """A channel was assigned to this repository connection."""
        logger.debug("AIRepository was assigned channel {}".format(channel))
        self.channel = channel

    def handle_ai_connected(self, channel):
        """An AI repository has connected to the network. That may be
        this repository, too."""
        logger.debug("AIRepository {} learned that AI repo {} connected".format(
            self.channel,
            channel,
        ))

    def handle_client_connected(self, client_id):
        """A client repository has connected to the network."""
        logger.debug("AIRepository {} learned that "
              "client repo {} connected".format(
            self.channel,
            client_id,
        ))

    def handle_client_disconnected(self, client_id):
        """Message handler: A client has disconnected from the network."""
        logger.debug("Client {} has disconnected".format(client_id))

    def handle_dobject_created(self, dobject_id, token):
        """A dobject has been created, probably on request by this repo."""
        logger.debug("AIRepository {} learned that dobject {} was created with "
              "token \"{}\"".format(self.channel, dobject_id, token))

    def disconnect_client(self, client_id, reason):
        """Send a disconnection message to the client. The ClientAgent should
        also execute the disconnection forcefully."""
        self.send_message(
            self.channel,
            client_id,
            msgtypes.DISCONNECT_CLIENT,
            reason,
        )

    def set_interest(self, recipient, zone):
        """Set interest of recipient in channel."""
        self.send_message(
            self.channel,
            channels.ALL_STATE_SERVERS,  # FIXME: Just the specific?
            msgtypes.SET_INTEREST,
            recipient,
            zone,
        )

    def unset_interest(self, recipient, zone):
        """Set interest of recipient in channel."""
        self.send_message(
            self.channel,
            channels.ALL_STATE_SERVERS,  # FIXME: Just the specific?
            msgtypes.UNSET_INTEREST,
            recipient,
            zone,
        )

    def create_dobject(self, dclass, fields, token=None):
        self.send_message(
            self.channel,
            channels.ALL_STATE_SERVERS,  # FIXME: Just the specific?
            msgtypes.CREATE_DOBJECT,
            dclass,
            fields,
            token,
        )

    def handle_create_dobject_view(self, dobject_id, dclass, fields):
        logger.info("AIRepository {} creates view for "
              "dobject \"{}\"".format(self.channel, dobject_id))
        super().handle_create_dobject_view(dobject_id, dclass, fields)

    def add_to_zone(self, dobject_id, zone_id):
        self.send_message(
            self.channel,
            channels.ALL_STATE_SERVERS,  # FIXME: Just the specific?
            msgtypes.ADD_TO_ZONE,
            dobject_id,
            zone_id,
        )

    def set_ai(self, ai_channel, dobject_id):
        self.send_message(
            self.channel,
            channels.ALL_STATE_SERVERS,  # FIXME: Just the specific?
            msgtypes.SET_AI,
            ai_channel,
            dobject_id,
        )

    def set_owner(self, owner_channel, dobject_id):
        self.send_message(
            self.channel,
            channels.ALL_STATE_SERVERS,  # FIXME: Just the specific?
            msgtypes.SET_OWNER,
            owner_channel,
            dobject_id,
        )

    def handle_create_ai_view(self, dobject_id, dclass, fields):
        """This AI has been made the controlling AI for the dobject."""
        logger.debug("AIRepository {} has been made the controlling AI "
              "for dobject \"{}\"".format(self.channel, dobject_id))
        # TODO: Well, create that AI view!
        pass

    def handle_field_update(self, source, dobject_id, field_id, values):
        dobject = self.dobjects[dobject_id]
        dobject.handle_field_update(source, dobject_id, field_id, values)
