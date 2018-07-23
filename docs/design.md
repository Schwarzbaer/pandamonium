Design
------

* Components
  * MessageDirectors constitute the networking backbone. They route messages
    between each other, and to and from their local components.
  * StateServers store and persist object state, and broadcast changes in state
    based on field keywords. Note that some state changes aren't even stored in
    the StateServer, making them pure message passings.
    To facilitate routing, the StateServers also maintain zones, and client
    interests in those zones.
  * ClientAgents accept connections from clients, validate incoming messages,
    and send updates back to them. The protocol that they use is different from,
    and more restrictive, than that used by AIAgents.
  * AIAgents
* dobjects
  * dobjects are distributed objects. The name is chosen to disambiguate them
    from the Python builtin type `object`, and for tersity of code.
  * dobjects are implemented by having StateServers keep a state, and by having
    views of the dobject, meaning Python implementations of the different
    aspects of its behavior, on the client and AI server side.
* Zones and Interest
  * Zones are containers for the presence of dobjects. Interest is the statement
    that a client should be informed about the changes of state of dobjects in a
    given zone.
  * Object creation / destruction / movement and setting / unsetting interest is
    done by AI views only.
  * Presence in a zone and interest in that zone are completely independent from
    each other.
* Security
  * Isolating AI agents from access by non-privileged users is currently no
    concern of this project, and is delegated to the networking layer. The
    trivial and default case is to let ClientAgents listen on 0.0.0.0, and
    AIAgents on 127.0.0.1.
  * On the application layer, this project currently concerns itself with access
    control and type validation, but not value validation. That is to say that
    while it is enforced that clients are given only updates that they are
    explicitly given access to, and that their compliance to the given message
    formats is enforced, it is up to the implementations of AI views of dobjects
    to ensure that the values of fields are within a range (or set) that can be
    considered valid by the application.
  * In contrast to earlier implementations, this application aims to minimize
    client capabilities up front, cutting down on exploitable design flaws. To
    that end, clients are not allowed to create or destroy dobjects, add them to
    or remove them from zones, or set or remove interests in zones. All that has
    to be done by AI views.


Far-sighted design
------------------

These are ideas that we're going to ignore for the moment, hopefully picking
them up again as soon as possible.

* Web frontend: For debugging, monitoring, and maintenance purposes, having a
  web frontend would be nice.
* Interning: Since there will be applications that can be run both locally-only
  and networked (games with both singleplayer and multiplayer modes come to
  mind), it has to be considered that running a local-only application like a
  networked one has both advantages and disadvantages.

  * Developing them as separate projects adds to development time, and the
    complexity of maintenance and further development. Considering the
    local-only version to be a trivial special case of the networked one
    eliminates this price.
  * Function calls are much more time-efficient than using the network or even
    sockets.
  * Running a local application networked means duplicating resources in several
    processes.
  * Networked applications are inherently easy to scale vertically.

  Therefore, it should be possible to intern networked aspects when running an
  application local-only, replacing any network messages by function calls, and
  sharing resources. This means a small added overhead due to the now simulated
  network, and the additional development effort of scaling the application,
  should the need arise.


Lack of Design
--------------

* Transactionability of updates: Since so far we're only concerned with
  individual updates, there is no concept of a transaction, which can encompass
  a multitude of messages, and leave the system in a consistent state, which
  here means that no more processing with regard to the transaction is happening
  in the system. Such a capability would be helpful, if not outright necessary,
  to determine points in time at which snapshots of the stored state can be
  taken for later reloads, should the server / cluster crash.
* Cluster networking: No idea yet on how to let several instances communicate
  efficiently with each other, and make the network failure resistant.
