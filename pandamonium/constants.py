class channels:
    ALL_MESSAGE_DIRECTORS = 0
    ALL_STATE_SERVERS = 1
    ALL_AIS = 2
    ALL_CLIENTS = 3
    MESSAGE_DIRECTORS = (10, 99)
    STATE_SERVERS = (100, 999)
    AIS = (1000, 9999)
    CLIENTS = (100000, 999999)


class MsgType:
    def __init__(self, num_id, str_repr):
        self.num_id = num_id
        self.str_repr = str_repr

    def __eq__(self, other):
        return self.num_id == other.num_id

    def __repr__(self):
        return self.str_repr


class msgtypes:
    # Announce to all AIs that an AI has connected
    AI_CONNECTED = MsgType(0, "AI_CONNECTED")
    # Tell an AI its own channel
    AI_CHANNEL_ASSIGNED = MsgType(1, "AI_CHANNEL_ASSIGNED")
    # Announce to all AIs that a client has connected
    CLIENT_CONNECTED = MsgType(10, "CLIENT_CONNECTED")
    # Annouce that a client has disconnected
    CLIENT_DISCONNECTED = MsgType(11, "CLIENT_DISCONNECTED")
    # Force a client's disconnection
    DISCONNECT_CLIENT = MsgType(12, "DISCONNECT_CLIENT")
    # -> client repo
    CONNECTED = MsgType(1000, "CONNECTED")
    # -> client repo
    DISCONNECTED = MsgType(1001, "DISCONNECTED")
    # client repo -> client agent
    DISCONNECT = MsgType(1002, "DISCONNECT")
