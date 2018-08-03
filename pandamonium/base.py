class BaseComponent:
    def set_message_director(self, message_director):
        self.message_director = message_director
        self.message_director.subscribe_to_channel(self.all_connections, self)

    def handle_message(self, from_channel, to_channel, message_type, *args):
        raise NotImplementedError


