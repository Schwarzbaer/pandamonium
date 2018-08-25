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


class FixedSizeFieldType:
    def __init__(self, ftype, length, name):
        self.ftype = ftype
        self.length = length
        self.name = name

    def __repr__(self):
        return self.name


class VariableSizeFieldType:
    def __init__(self, ftype, name):
        self.ftype = ftype
        self.name = name

    def __repr__(self):
        return self.name


class ListFieldType:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class field_types:
    CHANNEL = FixedSizeFieldType(int, 4, "CHANNEL")
    ZONE = FixedSizeFieldType(int, 4, "ZONE")
    DCLASS = FixedSizeFieldType(int, 2, "DCLASS")
    DOBJECT_ID = FixedSizeFieldType(int, 4, "DOBJECT_ID")
    FIELD_ID = FixedSizeFieldType(int, 2, "FIELD_ID")
    FIELD_VALUE = ListFieldType("FIELD_VALUE")
    FIELD_VALUES = ListFieldType("FIELD_VALUES")
    MESSAGE_TYPE = FixedSizeFieldType(int, 2, "MESSAGE_TYPE")
    STRING = VariableSizeFieldType(str, "STRING")
    FLOAT = FixedSizeFieldType(float, 4, "FLOAT")
    TOKEN = FixedSizeFieldType(int, 4, "TOKEN")


class MsgType:
    def __init__(self, num_id, str_repr, *fields):
        self.num_id = num_id
        self.str_repr = str_repr
        self.fields = fields

    def __eq__(self, other):
        return self.num_id == other.num_id

    def __repr__(self):
        return self.str_repr


class msgtypes:
    # These are just for testing
    # FIXME: Get them their own number space
    TEST_NO_ARGS = MsgType(1234, "TEST_NO_ARGS")
    TEST_THREE_CHANNEL_ARGS = MsgType(
        1235,
        "TEST_THREE_CHANNEL_ARGS",
        field_types.CHANNEL,
        field_types.CHANNEL,
        field_types.CHANNEL,
    )
    # Announce to all AIs that an AI has connected
    AI_CONNECTED = MsgType(0, "AI_CONNECTED", field_types.CHANNEL)
    # Tell an AI its own channel
    AI_CHANNEL_ASSIGNED = MsgType(1, "AI_CHANNEL_ASSIGNED", field_types.CHANNEL)
    # Announce to all AIs that a client has connected
    CLIENT_CONNECTED = MsgType(10, "CLIENT_CONNECTED", field_types.CHANNEL)
    # Annouce that a client has disconnected
    CLIENT_DISCONNECTED = MsgType(
        11,
        "CLIENT_DISCONNECTED",
        field_types.CHANNEL, # client
    )
    # Force a client's disconnection
    DISCONNECT_CLIENT = MsgType(
        12,
        "DISCONNECT_CLIENT",
        field_types.CHANNEL, # client
        field_types.STRING, # reason
    )
    # -> client repo
    CONNECTED = MsgType(1000, "CONNECTED")
    # -> client repo
    DISCONNECTED = MsgType(
        1001,
        "DISCONNECTED",
        field_types.STRING, # reason
    )
    # client repo -> client agent
    DISCONNECT = MsgType(
        1002,
        "DISCONNECT",
        field_types.CHANNEL, # client
        field_types.STRING, # reason
    )
    # ai repo -> state server
    SET_INTEREST = MsgType(
        2000,
        "SET_INTEREST",
        field_types.CHANNEL, # client / AI
        field_types.ZONE,
    )
    # ai repo -> state server
    UNSET_INTEREST = MsgType(
        2001,
        "UNSET_INTEREST",
        field_types.CHANNEL, # client / AI
        field_types.ZONE,
    )
    # ai repo -> state server
    CREATE_DOBJECT = MsgType(
        2002,
        "CREATE_DOBJECT",
        field_types.DCLASS,
        field_types.FIELD_VALUES,
        field_types.TOKEN,
    )
    # state server -> ai repo
    DOBJECT_CREATED = MsgType(
        2002,
        "DOBJECT_CREATED",
        field_types.DOBJECT_ID,
        field_types.TOKEN,
    )
    # ai -> state server
    ADD_TO_ZONE = MsgType(
        2003,
        "ADD_TO_ZONE",
        field_types.DOBJECT_ID,
        field_types.ZONE,
    )
    # ai -> state server
    REMOVE_FROM_ZONE = MsgType(
        2004,
        "REMOVE_FROM_ZONE",
        field_types.DOBJECT_ID,
        field_types.ZONE,
    )
    # ai repo -> state server
    SET_AI = MsgType(
        2010,
        "SET_AI",
        field_types.CHANNEL, # ai
        field_types.DOBJECT_ID,
    )
    # ai repo -> state server
    SET_OWNER = MsgType(
        2011,
        "SET_OWNER",
        field_types.CHANNEL, # owner
        field_types.DOBJECT_ID,
    )
    # state server -> interested
    CREATE_DOBJECT_VIEW = MsgType(
        2020,
        "CREATE_DOBJECT_VIEW",
        field_types.DOBJECT_ID,
        field_types.DCLASS,
        field_types.FIELD_VALUES,
    )
    # state server -> ai repo
    CREATE_AI_VIEW = MsgType(
        2021,
        "CREATE_AI_VIEW",
        field_types.DOBJECT_ID,
        field_types.DCLASS,
        field_types.FIELD_VALUES,
    )
    # state server -> owner repo
    BECOME_OWNER = MsgType(
        2022,
        "BECOME_OWNER",
        field_types.DOBJECT_ID,
    )
    # repo -> state_server
    SET_FIELD = MsgType(
        2030,
        "SET_FIELD",
        field_types.DOBJECT_ID,
        field_types.FIELD_ID,
        field_types.FIELD_VALUE,
    )
    # state server -> repo
    FIELD_UPDATE = MsgType(
        2031,
        "FIELD_UPDATE",
        field_types.DOBJECT_ID,
        field_types.FIELD_ID,
        field_types.FIELD_VALUE,
    )

all_message_types = [
    msgtypes.TEST_NO_ARGS,
    msgtypes.TEST_THREE_CHANNEL_ARGS,
    msgtypes.AI_CONNECTED,
    msgtypes.AI_CHANNEL_ASSIGNED,
    msgtypes.CLIENT_CONNECTED,
    msgtypes.CLIENT_DISCONNECTED,
    msgtypes.DISCONNECT_CLIENT,
    msgtypes.CONNECTED,
    msgtypes.DISCONNECTED,
    msgtypes.DISCONNECT,
    msgtypes.SET_INTEREST,
    msgtypes.UNSET_INTEREST,
    msgtypes.CREATE_DOBJECT,
    msgtypes.DOBJECT_CREATED,
    msgtypes.ADD_TO_ZONE,
    msgtypes.REMOVE_FROM_ZONE,
    msgtypes.SET_AI,
    msgtypes.SET_OWNER,
    msgtypes.CREATE_DOBJECT_VIEW,
    msgtypes.CREATE_AI_VIEW,
    msgtypes.BECOME_OWNER,
    msgtypes.SET_FIELD,
    msgtypes.FIELD_UPDATE,
]


message_type_by_id = {message_type.num_id: message_type
                      for message_type in all_message_types}
