import logging

from pandamonium.constants import field_policies


# TODO: Think about whether relevant optimization is achieved when the dicts in
# DCD and DC are replaced with lists.


logger = logging.getLogger(__name__)


def create_class_definitions(manifest):
    # Sort classes alphabetically by name
    return {d_id: DistributedClass(d_name, manifest[d_name])
            for d_id, d_name in enumerate(sorted(manifest))}


class DistributedClass:
    def __init__(self, dclass_name, dclass_def):
        self.name = dclass_name
        self.fields = [DistributedField(f_name, dclass_def[f_name])
                       for f_name in sorted(dclass_def)]
        self.field_id_by_name = {field.name: field_id
                                 for field_id, field in enumerate(self.fields)}

    def __repr__(self):
        return "<dclass '{}'>".format(self.name)


class DistributedField:
    def __init__(self, field_name, field_def):
        self.name = field_name
        types, policy = field_def
        self.types = types
        self.policy = policy


class FieldStorage:
    def __init__(self, types, policy, values):
        self.types = types
        self.policy = policy
        self.values = values  # FIXME: Number- and typecheck given values!

    def set(self, values):
        self.values = values


class DistributedObject:
    def __init__(self, dobject_id, dclass, fields, repo=None):
        logger.info("Creating dobject {} (class {}) with fields: {}".format(
            dobject_id,
            dclass,
            fields,
        ))
        self.dobject_id = dobject_id
        self.dclass = dclass
        self.repo = repo

        # We only store a subset of the values, based on the persistence policy.
        # So we need a map of field_id -> storage_index
        self.storage_map = [field_id
                            for field_id, field in enumerate(self.dclass.fields)
                            if field.policy & (field_policies.RAM |
                                               field_policies.PERSIST)]
        if len(fields) != len(self.storage_map):
            raise ValueError
        self.storage = [None for storage_id, value in enumerate(fields)]
        for storage_id, values in enumerate(fields):
            field_id = self.storage_map[storage_id]
            self.storage[storage_id] = FieldStorage(
                self.dclass.fields[field_id].types,
                self.dclass.fields[field_id].policy,
                values,
            )

        self.owner = None
        self.is_owner = False
        self.ai = None

        self.creation_hook()

    def creation_hook(self):
        """Overwrite this to do things when a dobject view has been created."""
        pass

    def set_owner(self, owner):
        self.owner = owner

    def become_owner(self):
        self.is_owner = True

    def set_ai(self, ai_channel):
        self.ai = ai_channel

    def handle_field_update(self, source, dobject_id, field_id, values):
        field = self.dclass.fields[field_id]
        if (field.policy & (field_policies.RAM | field_policies.PERSIST)):
            storage_id = self.storage_map[field_id]
            self.storage[storage_id].set(values)
        field_name = self.dclass.fields[0].name
        method_name = 'update_' + field_name
        if hasattr(self, method_name):
            getattr(self, method_name)(source, *values)


class Recipient:
    def __init__(self, recipient_id):
        self.recipient_id = recipient_id


class Zone:
    def __init__(self, zone_id):
        self.zone_id = zone_id
