Doable immediately
------------------

[ ] Agents shouldn't use ALL_* as their channels, and the MessageDirector should
    route messages to ALL_* accordingly.
[ ] `IDGenerator` should adhere to channel ranges, and reuse released IDs.
[ ] All components: shutdown()
[ ] `MessageDirector`: Compose better default agents
[ ] `MessageDirector`, agents, repos: Implement disconnect
    [ ] test: Let AI repo disconnect client repo on connect.
[ ] Message packing / unpacking
    [ ] JSON
    [ ] binary (protobuf?)
[ ] Repositories creating dobjects
    [ ] JSON DC declarations
    [ ] Panda3D dcparser
[ ] Review design document and distill it into to-dos
[ ] Rewrite InternalSocket from scratch
    [X] Mimic Listener API for compatibility
    [X] Pass listener/Agent instance to connector/repo constructor
    [ ] ...? (Just map method calls?)
    [ ] Profit!
[ ] Handle OSError on socket.bind() if socket is in use already
    [ ] Clean up socket in shutdown
    [ ] Handle "Can't connect" in connectors while you're at it


Near-Future Plans
-----------------

[ ] Python package
[ ] Ponder persistance and reloading


Far-Future Plans
----------------

[ ] Ponder clustering and redundancy
[ ] Ponder transactions


"Ha-ha, yeah, right..."
-----------------------

[ ] Demo game: "The Right to Arm Bears"
