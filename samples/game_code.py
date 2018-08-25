import logging
from functools import partial

from panda3d.core import NodePath
from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor

from pandamonium.constants import field_policies as fp
from pandamonium.util import IDGenerator
from pandamonium.dobject import (
    DClass,
    AIView,
    ClientView,
)
from pandamonium.repository import (
    ClientRepository,
    AIRepository,
)


# Here's a quick overview of what this sample does:
# * First, you start the server. It'll import `dclasses` from the game's code,
#   so that it knows about what classes of dobjects there'll be.





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
# * Break it all down again.


FIRST_CONTACT_ZONE = 0
PLAYING_FIELD_ZONE = 1


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
    dfield_position = ((float, float, float, bool), # x, y, h, still_moving
                       fp.AI_SEND|fp.CLIENT_RECEIVE|fp.RAM)


class AvatarAIView(AIView, Avatar):
    def creation_hook(self):
        self.repository.avatars.add(self)
        self.movement = [0.0, 0.0]
        self.nodepath = NodePath("math")  # FIXME: Get x/y/h from field values

    def on_move_command(self, source, forward, right):
        self.movement = [forward, right]

    def do_position(self, x, y, h, still_moving):
        return (x, y, h, still_moving)

    def update_position(self, dt):
        forward_speed = 3.0
        turn_speed = 90.0
        if self.movement != [0.0, 0.0]:
            self.nodepath.set_h(
                self.nodepath,
                self.movement[1] * dt * turn_speed * -1,
            )
            self.nodepath.set_pos(
                self.nodepath,
                0, self.movement[0] * dt * forward_speed, 0,
            )
            self.do_position(
                self.nodepath.get_x(),
                self.nodepath.get_y(),
                self.nodepath.get_h(),
                True,
            )


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

    def do_move_command(self, forward, right):
        self.movement[0] = self.movement[0] + forward
        self.movement[1] = self.movement[1] + right
        return tuple(self.movement)

    def on_position(self, x, y, h, still_moving):
        self.avatar.set_pos(x, y, 0)
        self.avatar.set_h(h)


# This is merely needed for sorting to derive class IDs, and should hopefully
# vanish in the future. FIXME: Also, not all dclasses may have client views.
dclasses = {'auth_service': AuthService,
            'avatar': Avatar}
view_classes_ai = {'auth_service': AuthServiceAIView,
                   'avatar': AvatarAIView}
view_classes_client = {'auth_service': AuthServiceClientView,
                       'avatar': AvatarClientView}


# Repositories


class GameAIRepository(AIRepository):
    views = [view_classes_ai[view_name]
             for view_name in sorted(view_classes_ai)]

    def __init__(self):
        self.token_callbacks = {}
        self.token_gen = IDGenerator((1234,5678))
        self.avatars = set()
        base.taskMgr.add(self.update_avatars, "Update avatars")
        super().__init__()

    def update_avatars(self, task):
        dt = globalClock.get_dt()
        for avatar in self.avatars:
            avatar.update_position(dt)
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
        self.set_interest(client_id, FIRST_CONTACT_ZONE)

    def create_dobject(self, dclass_id, fields, callback=None):
        # FIXME: Move callback mechanism into AIRepository
        # FIXME: Resolve dclass_id from name
        if callback is not None:
            token = self.token_gen.get_new()
            self.token_callbacks[token] = callback
            super().create_dobject(dclass_id, fields, token)
        else:
            super().create_dobject(dclass_id, fields)

    def handle_dobject_created(self, dobject_id, token):
        # FIXME: Move callback mechanism into AIRepository
        super().handle_dobject_created(dobject_id, token)
        callback = self.token_callbacks[token]
        del self.token_callbacks[token]
        callback(dobject_id)

    def demo_dobject_creation_callback(self, dobject_id):
        print("AIRepository {} dobject creation callback executed for "
              "dobject \"{}\"".format(self.channel, dobject_id))
        self.add_to_zone(dobject_id, FIRST_CONTACT_ZONE)
        self.set_ai(self.channel, dobject_id)


class GameClientRepository(ClientRepository):
    views = [view_classes_client[view_name]
             for view_name in sorted(view_classes_client)]

    def handle_connected(self):
        base.camera.set_pos(0, -250, 250)
        base.camera.look_at(0, 0, 0)
        environment = base.loader.load_model("models/environment")
        environment.reparent_to(base.render)
        environment.set_pos(-8, 42, 0)
        environment.set_scale(0.25)
