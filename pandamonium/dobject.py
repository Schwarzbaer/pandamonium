import logging


logger = logging.getLogger(__name__)


class DistributedObject:
    def __init__(self, dobject_id, dclass, fields):
        logger.debug("dobject {} (class {}) created with: {}".format(
            dobject_id,
            dclass,
            fields,
        ))

        self.dobject_id = dobject_id
        self.dclass = dclass
        self.fields = fields
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
