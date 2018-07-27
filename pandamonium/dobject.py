import logging


logger = logging.getLogger(__name__)


class DistributedObject:
    def __init__(self, state_server, dobject_id, dclass, fields):
        logger.debug("dobject {} (class {}) created with: {}".format(
            dobject_id,
            dclass,
            fields,
        ))
        self.state_server = state_server
        self.dobject_id = dobject_id
        self.dclass = dclass
        self.fields = fields
        self.owner = None
        self.ai_channel = None

    def set_owner(self, owner):
        self.owner = owner

    def set_ai(self, ai_channel):
        self.ai_channel = ai_channel
