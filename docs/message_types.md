AI connection messages
----------------------

* AIAgent to all AIRepositories
  AI_CONNECTED
* AIAgent to AIRepository
  AI_CHANNEL_ASSIGNED


Client connection messages
--------------------------

* ClientAgent to ClientRepository
  * CONNECTED: The client's connection has been established.
  * DISCONNECTED(reason): The client's connection is being terminated
* ClientRepository to ClientAgent
  * DISCONNECT: The client wants to disconnect. This will be replied to with a
    DISCONNECTED("Client-requested disconnect.").
* ClientAgent to all AIRepositories
  * CLIENT_CONNECTED
  * CLIENT_DISCONNECTED
* AIRepository to ClientAgent
  * DISCONNECT_CLIENT
