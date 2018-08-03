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

    def __repr__(self):
        return "<dclass '{}'>".format(self.name)


class DistributedField:
    def __init__(self, field_name, field_def):
        self.name = field_name
        types, policy = field_def
        self.types = types
        self.policy = policy


class DistributedObject:
    def __init__(self, dobject_id, dclass, fields):
        logger.info("Creating dobject {} (class {}) with fields: {}".format(
            dobject_id,
            dclass,
            fields,
        ))
        self.dobject_id = dobject_id
        self.dclass = dclass

        storage_fields = [field.name
                          for field in self.dclass.fields
                          if field.policy & (field_policies.RAM |
                                             field_policies.PERSIST)]
        print(storage_fields)
        if len(fields) != len(storage_fields):
            raise ValueError
        # TODO: Now set the fields!
        self.fields = []

        self.owner = None
        self.ai_channel = None

    def set_owner(self, owner):
        self.owner = owner

    def set_ai(self, ai_channel):
        self.ai_channel = ai_channel


class Recipient:
    def __init__(self, recipient_id):
        self.recipient_id = recipient_id


class Zone:
    def __init__(self, zone_id):
        self.zone_id = zone_id
