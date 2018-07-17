class channels:
    ALL_MESSAGE_DIRECTORS = 0
    ALL_STATE_SERVERS = 1
    ALL_AIS = 2
    ALL_CLIENTS = 3
    MESSAGE_DIRECTORS = (10, 99)
    STATE_SERVERS = (100, 999)
    AIS = (1000, 9999)
    CLIENTS = (100000, 999999)


class msgtypes:
    AI_CONNECTED = 0  # Announce to all AIs that an AI has connected
    AI_CHANNEL_ASSIGNED = 1  # Tell an AI its own channel
    CLIENT_CONNECTED = 10  # Announce to all AIs that a client has connected
    CLIENT_DISCONNECTED = 11  # Annouce that a client has disconnected
    DISCONNECT_CLIENT = 12  # Force a client's disconnection
