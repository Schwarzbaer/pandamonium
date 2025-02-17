from threading import Lock
from queue import Queue, Empty
import logging

from pandamonium.base import BaseComponent
from pandamonium.constants import channels, msgtypes
from pandamonium.constants import field_policies as fp
from pandamonium.dobject import Recipient, Zone
from pandamonium.util import IDGenerator, AssociativeTable, BijectiveMap


logger = logging.getLogger(__name__)


class BaseStateKeeper:
    def set_interest(self, recipient, zone):
        raise NotImplementedError

    def unset_interest(self, recipient, zone):
        raise NotImplementedError

    def get_dobject_fields(self, dobject_id):
        raise NotImplementedError
        self.state_server.get_dobject_fields(dobject_id)


class SimpleStateKeeper(BaseStateKeeper):
    def __init__(self, dclasses):
        self.dclasses = [dclasses[dclass_name]
                         for dclass_name in sorted(dclasses)]
        for dclass_id, dclass in enumerate(self.dclasses):
            dclass.dclass_id = dclass_id
        self.state = AssociativeTable('recipients', 'zones', 'dobjects')
        # FIXME: Recipients and zones should be BijectiveMaps as well.
        self.recipients = AssociativeTable('r_id', 'r_object')
        self.zones = AssociativeTable('z_id', 'z_object')
        self.dobjects = BijectiveMap()
        # TODO: For the moment, we'll use a single lock to protect the whole of
        # the state; dobject existence, presence in zones, and interest. This is
        # a topic ripe for optimization, if you can do it without creating
        # deadlocks. Maybe do optimistic concurrency? Have a nifty planner
        # that'll schedule event processing into isolated parallelity?
        self.state_lock = Lock()
        self.emission_queue = Queue()

    def get_dobject_fields(self, dobject_id):
        with self.state_lock:
            dobject = self.dobjects[dobject_id].dfields
        return dobject

    def _queue_message(self, *message):
        # FIXME: Make sure that all data is copies.
        self.emission_queue.put(message)

    def _work_emission_queue(self):
        working = True
        while working:
            try:
                message = self.emission_queue.get(block=False)
                self.message_director.create_message(*message)
            except Empty:
                working = False

    def emit_create_dobject_view(self, recipients, dobject_maps):
        for recipient in recipients:
            for dobject_id, dobject in dobject_maps:
                self._queue_message(
                    self.individual_channel,
                    recipient,
                    msgtypes.CREATE_DOBJECT_VIEW,
                    dobject_id,
                    dobject.dclass_id,
                    dobject.storage,
                )

    def emit_destroy_dobject_view(self, recipients, dobject_ids):
        for recipient in recipients:
            for dobject_id in dobject_ids:
                self._queue_message(
                    self.individual_channel,
                    recipient,
                    msgtypes.DESTROY_DOBJECT_VIEW,
                    dobject_id,
                )

    def create_recipient(self, recipient_id):
        with self.state_lock:
            recipient = Recipient(recipient_id)
            self.recipients.r_id.add(recipient_id)
            self.recipients.r_object.add(recipient)
            self.recipients._assoc(recipient_id, recipient)
            self.state.recipients.add(recipient)

    def create_dobject(self, dobject_id, dclass_id, fields):
        with self.state_lock:
            dclass = self.dclasses[dclass_id]
            dobject = dclass(
                dobject_id,
                fields,
            )
            self.dobjects[dobject_id] = dobject
            self.state.dobjects.add(dobject)

    def create_zone(self, zone_id):
        with self.state_lock:
            zone = Zone(zone_id)
            self.zones.z_id.add(zone_id)
            self.zones.z_object.add(zone)
            self.zones._assoc(zone_id, zone)
            self.state.zones.add(zone)

    def _dobjects_seen(self, recipient):
        return self.state.get(
            recipient,
            path=(self.state.zones, self.state.dobjects),
        )

    def _dobject_seen_by(self, dobject):
        return self.state.get(
            dobject,
            path=(self.state.zones, self.state.recipients),
        )

    def _dobject_to_emittable(self, dobject):
        dobject_id = self.dobjects.getreverse(dobject)
        return (dobject_id, dobject)

    def _dobject_id_to_emittable(self, dobject_id):
        dobject = self.dobjects[dobject_id]
        return (dobject_id, dobject)

    def set_interest(self, recipient_id, zone_id):
        if recipient_id not in self.recipients:
            self.create_recipient(recipient_id)
        if zone_id not in self.zones:
            self.create_zone(zone_id)
        with self.state_lock:
            (recipient, ) = self.recipients[recipient_id]
            (zone, ) = self.zones[zone_id]
            dobjects_before = self._dobjects_seen(recipient)
            self.state._assoc(recipient, zone)
            dobjects_after = self._dobjects_seen(recipient)
            new_dobjects = dobjects_after - dobjects_before
            emittables = [self._dobject_to_emittable(dobject)
                          for dobject in new_dobjects]
            self.emit_create_dobject_view([recipient_id], emittables)
        self._work_emission_queue()
        return [new_dobject_id for (new_dobject_id, _) in emittables]

    def unset_interest(self, recipient_id, zone_id):
        with self.state_lock:
            (recipient, ) = self.recipients[recipient_id]
            (zone, ) = self.zones[zone_id]
            dobjects_before = self._dobjects_seen(recipient)
            self.state._dissoc(recipient, zone)
            dobjects_after = self._dobjects_seen(recipient)
            lost_dobjects = dobjects_before - dobjects_after
            self.emit_destroy_dobject_view([recipient_id], lost_dobjects)
        self._work_emission_queue()
        return lost_dobject_ids

    def add_presence(self, dobject_id, zone_id):
        if zone_id not in self.zones:
            self.create_zone(zone_id)
        with self.state_lock:
            dobject = self.dobjects[dobject_id]
            (zone, ) = self.zones[zone_id]
            recipients_before = self._dobject_seen_by(dobject)
            self.state._assoc(dobject, zone)
            recipients_after = self._dobject_seen_by(dobject)
            new_recipients = recipients_after - recipients_before
            new_recipient_ids = {next(iter(self.recipients[nr]))
                                 for nr in new_recipients}
            emittable = [self._dobject_id_to_emittable(dobject_id)]
            self.emit_create_dobject_view(new_recipient_ids, emittable)
        self._work_emission_queue()
        return new_recipient_ids

    def remove_presence(self, dobject_id, zone_id):
        with self.state_lock:
            dobject = self.dobjects[dobject_id]
            (zone, ) = self.zones[zone_id]
            recipients_before = self._dobject_seen_by(dobject)
            self.state._dissoc(dobject, zone)
            recipients_after = self._dobject_seen_by(dobject)
            lost_recipients = recipients_before - recipients_after
            lost_recipient_ids = {next(iter(self.recipients[nr]))
                                  for nr in lost_recipients}
            self.emit_destroy_dobject_view(lost_recipient_ids, [dobject_id])
        self._work_emission_queue()
        return lost_recipient_ids

    def set_ai(self, ai_channel, dobject_id):
        with self.state_lock:
            self.dobjects[dobject_id].set_ai(ai_channel)
        # self.message_director.create_message(
        #     self.all_connections,  # FIXME: This individual StateServer's ID
        #     ai_channel,
        #     msgtypes.CREATE_AI_VIEW,
        #     dobject_id,  # FIXME: Either we also need to add all state
        #                  # information, or, better (because later updates)
        #                  # assure that the dobject is already in the AI's
        #                  # interest.
        # )

    def set_owner(self, owner_channel, dobject_id):
        with self.state_lock:
            # TODO: Destroy owner view if another owner was set.
            # TODO: Check whether dobject is even visible to client
            self.dobjects[dobject_id].set_owner(owner_channel)
            self._queue_message(
                self.all_connections,  # FIXME: This individual StateServer's ID
                owner_channel,
                msgtypes.BECOME_OWNER,
                dobject_id,
            )
        self._work_emission_queue()


    def set_field(self, source, dobject_id, field_id, value):
        with self.state_lock:
            dobject = self.dobjects[dobject_id]
            # FIXME: Jam this into DClass somehow?
            _, field_type, policy = dobject._dfields[field_id]
            # Is the source even allowed to set this field?
            if (policy & fp.CLIENT_SEND) or \
               ((policy & fp.OWNER_SEND) and source == dobject.owner) or \
               ((policy & fp.AI_SEND) and source == dobject.ai):
                # If it's a storage field, set its value
                if policy & (fp.RAM | fp.PERSIST):
                    pass  # FIXME
                # Emit
                if policy & fp.CLIENT_RECEIVE:
                    for recipient in self._dobject_seen_by(dobject):
                        self._queue_message(
                            source,
                            recipient,
                            msgtypes.FIELD_UPDATE,
                            dobject_id,
                            field_id,
                            value
                        )
                elif policy & fp.OWNER_RECEIVE:
                    self._queue_message(
                        source,
                        dobject.owner,
                        msgtypes.FIELD_UPDATE,
                        dobject_id,
                        field_id,
                        value
                    )
                elif policy & fp.AI_RECEIVE:
                    self._queue_message(
                        source,
                        dobject.ai,
                        msgtypes.FIELD_UPDATE,
                        dobject_id,
                        field_id,
                        value
                    )
                # NOTE: else? I mean, there MUST be a sending policy?
            else:
                raise Exception("{} tried to set {} field {} to {}. "
                                "".format(source, dobject, field_id, value))
        self._work_emission_queue()


class BaseStateServer(BaseComponent):
    all_connections = channels.ALL_STATE_SERVERS
    individual_channel = 17  # FIXME: Override in internal sample. Also, assign
                            # a free channel dynamically.
    dobject_ids = (0, 999999)

    def __init__(self):
        self.id_gen = IDGenerator(id_range=self.dobject_ids)

    def __repr__(self):
        return "StateServer {}".format(self.individual_channel)

    def shutdown(self):
        pass

    def handle_message(self, from_channel, to_channel, message_type, *args):
        logger.debug("StateServer received: {} -> {} ({})".format(
            from_channel, to_channel, message_type,
        ))
        if message_type == msgtypes.CREATE_DOBJECT:
            dclass = args[0]
            fields = args[1]
            creator =  from_channel
            token = args[2]
            self.handle_create_dobject(dclass, fields, creator, token)
        elif message_type == msgtypes.SET_INTEREST:
            recipient = args[0]
            zone = args[1]
            self.handle_set_interest(recipient, zone)
        elif message_type == msgtypes.UNSET_INTEREST:
            recipient = args[0]
            zone = args[1]
            self.handle_unset_interest(recipient, zone)
        elif message_type == msgtypes.ADD_TO_ZONE:
            dobject_id = args[0]
            zone = args[1]
            self.handle_add_to_zone(dobject_id, zone)
        elif message_type == msgtypes.REMOVE_FROM_ZONE:
            dobject_id = args[0]
            zone = args[1]
            self.remove_from_zone(dobject_id, zone)
        elif message_type == msgtypes.SET_AI:
            ai_channel = args[0]
            dobject_id = args[1]
            self.handle_set_ai(ai_channel, dobject_id)
        elif message_type == msgtypes.SET_OWNER:
            owner_channel = args[0]
            dobject_id = args[1]
            self.handle_set_owner(owner_channel, dobject_id)
        elif message_type == msgtypes.SET_FIELD:
            source = from_channel
            dobject_id = args[0]
            field_id = args[1]
            value = args[2]
            self.handle_set_field(source, dobject_id, field_id, value)
        else:
            raise NotImplementedError

    def handle_create_dobject(self, dclass, fields, creator, token):
        dobject_id = self.id_gen.get_new()
        self.create_dobject(dobject_id, dclass, fields)
        self.message_director.create_message(
            self.individual_channel,
            creator,
            msgtypes.DOBJECT_CREATED,
            dobject_id,
            token,
        )

    def handle_set_interest(self, recipient, zone):
        logger.debug("StateServer sets interest for {} in {}".format(
            recipient,
            zone,
        ))
        new_dobjects = self.set_interest(recipient, zone)

    def handle_unset_interest(self, recipient, zone):
        logger.debug("StateServer revokes interest for {} in {}".format(
            recipient,
            zone,
        ))
        lost_dobjects = self.unset_interest(recipient, zone)

    def handle_add_to_zone(self, dobject_id, zone):
        logger.info("Adding dobject {} to zone {}".format(dobject_id, zone))
        new_recipients = self.add_presence(dobject_id, zone)

    def handle_remove_from_zone(self, dobject_id, zone):
        logger.info("Removing dobject {} from zone {}".format(dobject_id, zone))
        lost_recipients = self.remove_presence(dobject_id, zone)

    def handle_set_ai(self, ai_channel, dobject_id):
        self.set_ai(ai_channel, dobject_id)

    def handle_set_owner(self, owner_channel, dobject_id):
        self.set_owner(owner_channel, dobject_id)

    def handle_set_field(self, source, dobject_id, field_id, value):
        logger.debug("{} sets {}'s field {} to {}".format(
            source,
            dobject_id,
            field_id,
            value,
        ))
        self.set_field(source, dobject_id, field_id, value)

class StateServer(BaseStateServer, SimpleStateKeeper):
    def __init__(self, dclasses):
        SimpleStateKeeper.__init__(self, dclasses)
        BaseStateServer.__init__(self)
