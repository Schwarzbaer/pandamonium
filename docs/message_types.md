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


Interest management
-------------------

* AIRepository to StateServer
  * SET_INTEREST(recipient, zone): Set recipient interest in zone
  * UNSET_INTEREST(recipient, zone): Revoke recipient interest in zone


dobject management
------------------

* AIRepository to StateServer
  * CREATE_DOBJECT(dclass, fields, token)
* StateServer to AIRepository
  * DOBJECT_CREATED(dobject_id, token): The token will be the one given by
    CREATE_DOBJECT.
