# import sys
#
# from direct.showbase.ShowBase import ShowBase

# Here's a quick overview of what this sample does:
# * Cobble together the server, consisting of StateServer, AIAgent, ClientAgent,
#   and MessageDirector.
# * Create and "connect" an AIRepository.
# * When the AIRepository gets a channel assignment message, which is for now
#   doubling as its "You're ready to go" signal, it
#   * sets interest in the "first contact zone"
#   * creates a dobject of dclass 0; for now, that means nothing, since I
#     haven't implemented dclasses and dobject behavior yet.
# * When the AIRepository is notified that the dobject creation has happened, it
#   sets itself as the dobject's AI.
#   TODO: What *should* happen, to enforce better causality, is that the repo
#   sets itself as AI once it is told to create a view for the dobject. That way
#   there's no need to juggle the "What if we're set as AI before we even see
#   the dobject?" case.
# * When the AIRepository learns that a client has connected to the server, it
#   sets interest for the client in the first contact zone. Now the client sees
#   the dobject in it, too.
# TODO:
# * Demonstrate that the dobject works by sending messages for it back and
#   forth.
# * Break it all down again.
# * A Panda3D sample (without auth, which is what this first dobject would
#   typically be for) should have the AI create a dobject for each client, set
#   that client as owner, and let them all move around in 3D space until the
#   client disconnects.


import sys
import logging
from functools import partial

from panda3d.core import NodePath
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor
from direct.showbase.ShowBase import ShowBase

from pandamonium.constants import (
    msgtypes,
)
from pandamonium.constants import field_policies as fp
from pandamonium.util import IDGenerator
from pandamonium.core import (
    ClientAgent,
    AIAgent,
    MessageDirector,
)
from pandamonium.state_server import StateServer
from pandamonium.sockets import (
    InternalAIListener,
    InternalClientListener,
    InternalAIConnector,
    InternalClientConnector,
)
from pandamonium.dobject import (
    DClass,
    AIView,
    ClientView,
)
from pandamonium.repository import ClientRepository, AIRepository


# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


FIRST_CONTACT_ZONE = 0
PLAYING_FIELD_ZONE = 1


# Distributed Classes and their Views


class AuthService(DClass):
    dfield_userpass = ((str, str), fp.CLIENT_SEND|fp.AI_RECEIVE)


class AuthServiceAIView(AIView, AuthService):
    def on_userpass(self, source, username, password):
        if username == "user" and password == "pass":
            # Create avatar and assign ownership
            # FIXME: Make these methods of Dobject
            self.create_dobject(
                1, #"avatar",
                [[0.0, 0.0]],
                partial(self.avatar_created_callback, source),
            )
        else:
            self.disconnect_client(
                source,
                "Because!",
            )

    def avatar_created_callback(self, client_id, dobject_id):
        self.add_to_zone(dobject_id, PLAYING_FIELD_ZONE)
        self.set_self_as_ai(dobject_id)
        self.set_interest(client_id, PLAYING_FIELD_ZONE)
        self.set_owner(client_id, dobject_id)


class AuthServiceClientView(ClientView, AuthService, DirectObject):
    def creation_hook(self):
        #self.accept("a", self.do_userpass, ["user", "pass"])
        self.do_userpass("user", "pass")

    def do_userpass(self, username, password):
        self.ignore("a")
        return (username, password)


class Avatar(DClass):
    dfield_move_command = ((float, float), fp.OWNER_SEND|fp.AI_RECEIVE)
    dfield_position = ((float, float), fp.AI_SEND|fp.OWNER_RECEIVE|fp.RAM)


class AvatarAIView(Avatar, AIView):
    def creation_hook(self):
        # self.repository.avatars.add(self)
        pass

    def on_move_command(self, source, forward, right):
        print(source, forward, right)


class AvatarClientView(ClientView, Avatar, DirectObject):
    def creation_hook(self):
        self.avatar = NodePath("Player Avatar")
        self.avatar.reparent_to(base.render)
        self.actor = Actor("models/panda-model",
                           {"walk": "models/panda-walk4"})
        self.actor.reparent_to(self.avatar)
        self.actor.set_scale(0.002)
        self.actor.set_h(180)

    def become_owner(self):
        super().become_owner()
        base.camera.reparent_to(self.avatar)
        base.camera.set_pos(0, -5, 1.6)
        base.camera.look_at(0, 0, 1.2)
        self.movement = [0.0, 0.0]
        self.accept("arrow_up", self.do_move_command, [1.0, 0.0])
        self.accept("arrow_up-up", self.do_move_command, [-1.0, 0.0])
        self.accept("arrow_down", self.do_move_command, [-1.0, 0.0])
        self.accept("arrow_down-up", self.do_move_command, [1.0, 0.0])
        self.accept("arrow_left", self.do_move_command, [0.0, -1.0])
        self.accept("arrow_left-up", self.do_move_command, [0.0, 1.0])
        self.accept("arrow_right", self.do_move_command, [0.0, 1.0])
        self.accept("arrow_right-up", self.do_move_command, [0.0, -1.0])
        # TODO: map controls

    def do_move_command(self, forward, right):
        self.movement[0] = self.movement[0] + forward
        self.movement[1] = self.movement[1] + right
        return tuple(self.movement)

    def on_position(self, x, y):
        self.avatar.set_pos(x, y, 0)


# This is merely needed for sorting to derive class IDs, and should hopefully
# vanish in the future. FIXME: Also, not all dclasses may have client views.
dclasses = {'auth_service': AuthService,
            'avatar': Avatar}
view_classes_ai = {'auth_service': AuthServiceAIView,
                   'avatar': AvatarAIView}
view_classes_client = {'auth_service': AuthServiceClientView,
                       'avatar': AvatarClientView}


# Server


class DemoAIAgent(AIAgent, InternalAIListener):
    pass


class DemoClientAgent(ClientAgent, InternalClientListener):
    pass


state_server = StateServer(dclasses)
client_agent = DemoClientAgent()
ai_agent = DemoAIAgent()
message_director = MessageDirector(
    state_server=state_server,
    client_agent=client_agent,
    ai_agent=ai_agent,
)


# Repositories


class DemoAIRepository(AIRepository, InternalAIConnector):
    views = [view_classes_ai[view_name]
             for view_name in sorted(view_classes_ai)]

    def __init__(self):
        self.token_callbacks = {}
        self.token_gen = IDGenerator((1234,5678))
        self.avatars = set()
        base.taskMgr.add(self.update_avatars, "Update avatars")
        super().__init__()

    def update_avatars(self, task):
        for avatar in self.avatars:
            print(".")
        return task.cont

    def handle_channel_assigned(self, channel):
        super().handle_channel_assigned(channel)
        self.set_interest(self.channel, FIRST_CONTACT_ZONE)
        self.set_interest(self.channel, PLAYING_FIELD_ZONE)
        self.create_dobject(
            0, #"auth_service",
            [],
            self.demo_dobject_creation_callback,
        )

    def handle_client_connected(self, client_id):
        super().handle_client_connected(client_id)
        # self.disconnect_client(client_id, "For demonstration purposes.")
        self.set_interest(client_id, FIRST_CONTACT_ZONE)

    def create_dobject(self, dclass_id, fields, callback=None):
        # FIXME: Resolve dclass_id from name
        if callback is not None:
            token = self.token_gen.get_new()
            self.token_callbacks[token] = callback
            super().create_dobject(dclass_id, fields, token)
        else:
            super().create_dobject(dclass_id, fields)

    def handle_dobject_created(self, dobject_id, token):
        super().handle_dobject_created(dobject_id, token)
        callback = self.token_callbacks[token]
        del self.token_callbacks[token]
        callback(dobject_id)

    def demo_dobject_creation_callback(self, dobject_id):
        print("AIRepository {} dobject creation callback executed for "
              "dobject \"{}\"".format(self.channel, dobject_id))
        # TODO : Make dobject present in FIRST_CONTACT_ZONE
        self.add_to_zone(dobject_id, FIRST_CONTACT_ZONE)
        self.set_ai(self.channel, dobject_id)


class DemoClientRepository(ClientRepository, InternalClientConnector):
    views = [view_classes_client[view_name]
             for view_name in sorted(view_classes_client)]

    def handle_connected(self):
        base.camera.set_pos(0, -250, 250)
        base.camera.look_at(0, 0, 0)
        pancake = base.loader.load_model("models/environment")
        pancake.reparent_to(base.render)
        pancake.set_pos(-8, 42, 0)
        pancake.set_scale(0.25)


class DemoGame(ShowBase):
    def __init__(self):
        super().__init__()
        self.disable_mouse()
        self.ai_repository = DemoAIRepository()
        self.ai_repository.connect(ai_agent)
        # self.accept("c", self.connect)
        # TODO: Text on screen "Press c to connect"
        self.accept("escape", sys.exit)
        self.auth_service = None
        self.connect()

    def connect(self):
        self.ignore("c")
        print("Connecting")
        self.client_repository = DemoClientRepository()
        self.client_repository.connect(client_agent)


demo_game = DemoGame()
demo_game.run()


## client_repository.disconnect()
print("-----------------------------------------------------------------------")


# class Demo(ShowBase):
#     def __init__(self):
#         super().__init__()
#         self.accept("escape", sys.exit)
# 
# 
# demo = Demo()
# demo.run()
