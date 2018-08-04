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


dobject management
------------------

* AIRepository to StateServer
  * SET_INTEREST(recipient, zone): Set recipient interest in zone
  * UNSET_INTEREST(recipient, zone): Revoke recipient interest in zone
  * CREATE_DOBJECT(dclass, fields, token)
  * ADD_TO_ZONE(dobject_id, zone)
  * REMOVE_FROM_ZONE(dobject_id, zone)
  * SET_AI(ai_channel, dobject_id)
  * SET_OWNER(owner_channel, dobject_id)
* StateServer to AIRepository
  * DOBJECT_CREATED(dobject_id, token): The token will be the one given by
    CREATE_DOBJECT.
  * CREATE_AI_VIEW(dobject_id, dclass, fields)
* StateServer to Interest recipients
  * CREATE_DOBJECT_VIEW(dobject_id, dclass, fields): Create a basic view of a
    dobject that has been added to a zone that a recipient has interest in, or
    which is already in a zone that the recipient has just gotten interest in.
  * DESTROY_DOBJECT_VIEW(dobject_id)
* Repository to StateServer
  * SET_FIELD(dobject_id, field, values)