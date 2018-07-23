AI connection messages
----------------------

* AIAgent to AIRepository
  AI_CHANNEL_ASSIGNED(channel)
* AIAgent to all AIRepositories
  AI_CONNECTED(channel)


Client connection messages
--------------------------

* ClientAgent to ClientRepository
  * CONNECTED(): The client's connection has been established.
  * DISCONNECTED(reason): The client's connection is being terminated
* ClientRepository to ClientAgent
  * DISCONNECT: The client wants to disconnect. This will be replied to with a
    DISCONNECTED("Client-requested disconnect.").
* ClientAgent to all AIRepositories
  * CLIENT_CONNECTED(client_id)
  * CLIENT_DISCONNECTED(client_id)
* AIRepository to ClientAgent
  * DISCONNECT_CLIENT(client_id, reason)
