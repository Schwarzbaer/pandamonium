Doable immediately
------------------

[ ] Repositories creating dobjects
    [ ] Panda3D dcparser
[ ] Agents shouldn't use ALL_* as their channels, and the MessageDirector should
    route messages to ALL_* accordingly.
[ ] `IDGenerator` should adhere to channel ranges, and reuse released IDs.
    [ ] Client IDs should be independent of channels.
[ ] All components: shutdown()
[ ] Message packing / unpacking
    [ ] JSON
    [ ] binary (protobuf?)
[ ] Review design document and distill it into to-dos
[ ] Handle OSError on socket.bind() if socket is in use already
    [ ] Clean up socket in shutdown
    [ ] Handle "Can't connect" in connectors while you're at it
[ ] Agent connections should keep track of the dclasses that their connectees
    can see, so that they don't need to look it up in the state server. This
    will allow for multiple state servers.


Near-Future Plans
-----------------

[ ] Python package
[ ] Ponder persistance and reloading
[ ] TLS
[ ] Hybrid TCP / UDP networking


Far-Future Plans
----------------

[ ] Ponder clustering and redundancy
[ ] Ponder transactions


"Ha-ha, yeah, right..."
-----------------------

[ ] Demo game: "The Right to Arm Bears"
