class field_policies:
    CLIENT_SEND = 1 << 0  # Any client or AI can send to this field
    OWNER_SEND = 1 << 1  # Only the owner can send
    AI_SEND = 1 << 2  # Only the AI can send
    CLIENT_RECEIVE = 1 << 3  # All recipients will receive updates
    OWNER_RECEIVE = 1 << 4  # Only the dobject's owner receives updates
    AI_RECEIVE = 1 << 5  # Only the dobject's AI receives updates
    RAM = 1 << 6  # State is stored for the server's runtime
    PERSIST = 1 << 7  # State is persisted, i.e. on disk


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
    # ai repo -> state server
    SET_INTEREST = MsgType(2000, "SET_INTEREST")
    # ai repo -> state server
    UNSET_INTEREST = MsgType(2001, "UNSET_INTEREST")
    # ai repo -> state server
    CREATE_DOBJECT = MsgType(2002, "CREATE_DOBJECT")
    # state server -> ai repo
    DOBJECT_CREATED = MsgType(2002, "DOBJECT_CREATED")
    # ai -> state server
    ADD_TO_ZONE = MsgType(2003, "ADD_TO_ZONE")
    # ai -> state server
    REMOVE_FROM_ZONE = MsgType(2004, "REMOVE_FROM_ZONE")
    # ai repo -> state server
    SET_AI = MsgType(2010, "SET_AI")
    # ai repo -> state server
    SET_OWNER = MsgType(2011, "SET_OWNER")
    # state server -> interested
    CREATE_DOBJECT_VIEW = MsgType(2020, "CREATE_DOBJECT_VIEW")
    # state server -> ai repo
    CREATE_AI_VIEW = MsgType(2021, "CREATE_AI_VIEW")
    # state server -> owner repo
    CREATE_OWNER_VIEW = MsgType(2022, "CREATE_OWNER_VIEW")
