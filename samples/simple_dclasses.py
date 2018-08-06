from functools import partial

from panda3d.core import NodePath

from direct.showbase.DirectObject import DirectObject
from direct.actor.Actor import Actor

from pandamonium.constants import (
    field_policies,
    msgtypes,
)
from pandamonium.dobject import (
    create_class_definitions,
    DistributedObject,
)


PLAYING_FIELD_ZONE = 1


demo_dclasses = {'auth_service': {'userpass': ((str, str),
                                               (field_policies.CLIENT_SEND |
                                                field_policies.AI_RECEIVE))},
                 'avatar': {'move_command': ((float, float),
                                             (field_policies.OWNER_SEND |
                                              field_policies.AI_RECEIVE)),
                            'position': ((float, float),
                                         (field_policies.AI_SEND |
                                          field_policies.OWNER_RECEIVE |
                                          field_policies.RAM))}}
dclasses = create_class_definitions(demo_dclasses)


class AuthServiceAI(DistributedObject):
    def creation_hook(self):
        pass

    def update_userpass(self, source, username, password):
        if username == "user" and password == "pass":
            # Create avatar and assign ownership
            self.repo.create_dobject(
                1, #"avatar",
                [[0.0, 0.0]],
                partial(self.avatar_created_callback, source),
            )
        else:
            self.repo.send_message(
                self.repo.channel,
                source,
                msgtypes.DISCONNECT_CLIENT,
                "Because!")

    def avatar_created_callback(self, client, dobject_id):
        self.repo.add_to_zone(dobject_id, PLAYING_FIELD_ZONE)
        self.repo.set_ai(self.repo.channel, dobject_id)
        self.repo.set_interest(client, PLAYING_FIELD_ZONE)
        self.repo.set_owner(client, dobject_id)


class AuthServiceClient(DistributedObject, DirectObject):
    def creation_hook(self):
        self.accept("a", self.send_auth, ["user", "pass"])

    def send_auth(self, username, password):
        self.ignore("a")
        self.repo.send_message(
            msgtypes.SET_FIELD,
            self.dobject_id,
            self.dclass.field_id_by_name['userpass'],  # FIXME: Use properties
            (username, password),
        )


class AvatarAI(DistributedObject):
    pass


class AvatarClient(DistributedObject):
    def creation_hook(self):
        self.avatar = NodePath("Player Avatar")
        self.avatar.reparent_to(base.render)
        # TODO: set_pos
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
        # TODO: map controls


view_classes_ai = {'auth_service': AuthServiceAI,
                   'avatar': AvatarAI}
view_classes_client = {'auth_service': AuthServiceClient,
                       'avatar': AvatarClient}
