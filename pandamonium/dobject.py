class DistributedObject:
    def __init__(self, state_server, dobject_id, dclass, fields):
        self.state_server = state_server
        self.dobject_id = dobject_id
        self.dclass = dclass
        self.fields = fields
        self.ai_channel = None

    def set_ai(self, ai_channel):
        self.ai_channel = ai_channel
