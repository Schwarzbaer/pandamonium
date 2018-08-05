Doable immediately
------------------

[ ] Internal network demo
[ ] Repositories creating dobjects
    [ ] Panda3D dcparser
[ ] Agents shouldn't use ALL_* as their channels, and the MessageDirector should
    route messages to ALL_* accordingly.
[ ] `IDGenerator` should adhere to channel ranges, and reuse released IDs.
[ ] All components: shutdown()
[ ] Message packing / unpacking
    [ ] JSON
    [ ] binary (protobuf?)
[ ] Review design document and distill it into to-dos
[ ] Handle OSError on socket.bind() if socket is in use already
    [ ] Clean up socket in shutdown
    [ ] Handle "Can't connect" in connectors while you're at it


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
