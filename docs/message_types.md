* Client to ClientAgent
  DISCONNECT
* ClientAgent to Client
  CREATE_DOBJECT_VIEW
  CREATE_OWNER_VIEW
  DISCONNECT(reason)

--------------------------------------------------------------------------------

* ClientAgent to network
  CLIENT_CONNECT
* Network to ClientAgent

--------------------------------------------------------------------------------

* AIAgent to network
  AI_CONNECT
* AI to StateServer
  SET_INTEREST([(client, zone), ...])
  REMOVE_INTEREST([(client, zone), ...])
