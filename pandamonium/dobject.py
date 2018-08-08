import logging

from pandamonium.constants import (
    msgtypes,
    channels,
)
from pandamonium.constants import field_policies as fp


logger = logging.getLogger(__name__)


class Recipient:
    def __init__(self, recipient_id):
        self.recipient_id = recipient_id


class Zone:
    def __init__(self, zone_id):
        self.zone_id = zone_id


class DClass:
    def __init__(self, dobject_id, fields, state_server=None):
        self.dobject_id = dobject_id
        self.state_server = state_server
        attr_names = sorted([field for field in dir(self)
                              if field.startswith('dfield_')])
        dfields = []
        for field_id, attr_name in enumerate(attr_names):
            field_name = attr_name.partition('dfield_')[2]
            field_attr = getattr(self, attr_name)
            field_type = field_attr[0]
            field_policy = field_attr[1]
            dfields.append((field_name, field_type, field_policy))
        self._dfields = dfields
        # TODO: set initial field values
        self.storage = fields

        self.owner = None
        self.ai = None

    def set_owner(self, owner):
        self.owner = owner

    def set_ai(self, ai_channel):
        self.ai = ai_channel


class AIView:
    def _dfield_sending_field_sender(self, dobject_id, field_id, f):
        def inner(*args):
            values = f(*args)
            self.repository.send_message(
                self.repo.ai_channel,
                channels.ALL_STATE_SERVERS,
                msgtypes.SET_FIELD,
                self.dobject_id,
                field_id,
                args,
            )
        return inner

    # FIXME: Copypasted from ClientView
    def __init__(self, repository, dobject_id, fields):
        self.repository = repository
        super().__init__(dobject_id, fields)
        self.receiver_methods = [None] * len(self._dfields)
        for field_id, (name, _, policy) in enumerate(self._dfields):
            sender_name = 'do_' + name
            receiver_name = 'on_' + name
            if policy & fp.AI_SEND:
                if not hasattr(self, sender_name):
                    raise Exception("Method {} is missing".format(sender_name))
                sender_wrapper = self._dfield_sending_field_sender(
                    dobject_id,
                    field_id,
                    getattr(self, sender_name),
                )
                setattr(self, method_name, wrapper)
                if hasattr(self, receiver_name):
                    raise Exception("Method {} should not be set on a field "
                                    "with client-side sender policy"
                                    "".format(receiver_name))
            elif policy & fp.AI_RECEIVE:
                if hasattr(self, sender_name):
                    raise Exception("Method {} should not be set on a field "
                                    "with client-side receiver policy"
                                    "".format(sender_name))
                if not hasattr(self, receiver_name):
                    raise Exception("Method {} is missing"
                                    "".format(receiver_name))
                self.receiver_methods[field_id] = getattr(self, receiver_name)
        self.creation_hook()

    def creation_hook(self):
        pass

    def handle_field_update(self, source, field_id, values):
        self.receiver_methods[field_id](source, *values)

    def disconnect_client(self, client_id, reason):
        self.repository.disconnect_client(client_id, reason)

    def create_dobject(self, dclass_id, fields, callback=None):
        if callback is None:
            self.repository.create_dobject(
                dclass_id,
                fields,
            )
        else:
            self.repository.create_dobject(
                dclass_id,
                fields,
                callback,
            )

    def add_to_zone(self, dobject_id, zone_id):
        self.repository.add_to_zone(dobject_id, zone_id)

    def set_interest(self, client_id, zone_id):
        self.repository.set_interest(client_id, zone_id)

    def set_owner(self, client_id, dobject_id):
        self.repository.set_owner(client_id, dobject_id)

    def set_ai(self, ai_channel, dobject_id):
        self.repository.set_ai(ai_channel, dobject_id)

    def set_self_as_ai(self, dobject_id):
        self.set_ai(self.repository.channel, dobject_id)


class ClientView:
    def _dfield_sending_field_sender(self, dobject_id, field_id, f):
        def inner(*args):
            values = f(*args)
            self.repository.send_message(
                msgtypes.SET_FIELD,
                self.dobject_id,
                field_id,
                args,
            )
        return inner

    def __init__(self, repository, dobject_id, fields):
        self.repository = repository
        super().__init__(dobject_id, fields)
        self.receiver_methods = [None] * len(self._dfields)
        for field_id, (name, _, policy) in enumerate(self._dfields):
            sender_name = 'do_' + name
            receiver_name = 'on_' + name
            if policy & (fp.CLIENT_SEND|fp.OWNER_SEND):
                if not hasattr(self, sender_name):
                    raise Exception("Method {} is missing".format(sender_name))
                sender_wrapper = self._dfield_sending_field_sender(
                    dobject_id,
                    field_id,
                    getattr(self, sender_name),
                )
                setattr(self, sender_name, sender_wrapper)
                if hasattr(self, receiver_name):
                    raise Exception("Method {} should not be set on a field "
                                    "with client-side sender policy"
                                    "".format(receiver_name))
            elif policy & (fp.CLIENT_RECEIVE|fp.OWNER_RECEIVE):
                if hasattr(self, sender_name):
                    raise Exception("Method {} should not be set on a field "
                                    "with client-side receiver policy"
                                    "".format(sender_name))
                if not hasattr(self, receiver_name):
                    raise Exception("Method {} is missing"
                                    "".format(receiver_name))
                self.receiver_methods[field_id] = getattr(self, receiver_name)
        self.creation_hook()

    def creation_hook(self):
        pass

    def handle_field_update(self, field_id, values):
        self.receiver_methods[field_id](*values)

    def become_owner(self):
        pass
