Doable immediately
------------------

[ ] Agents should subscribe new connections to their channels.
[ ] `IDGenerator` should adhere to channel ranges defined in `constants.py`
[ ] `MessageDirector`: Implement ai_connected, client_connected
    [ ] `MessageDirector`, agents, repos: Implement disconnect
        [ ] test: Let AI repo disconnect client repo on connect.
[ ] `simple_sample_server`: Handle `C-c` with graceful shutdown.
[ ] Message packing / unpacking
    [ ] JSON
    [ ] binary (protobuf?)
[ ] Repositories creating dobjects
    [ ] JSON DC declarations
    [ ] Panda3D dcparser
[ ] Review design document and distill it into to-dos
[ ] Rewrite InternalSocket from scratch


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
