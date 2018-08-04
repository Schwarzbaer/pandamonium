from pandamonium.constants import (
    field_policies,
    msgtypes,
)
from pandamonium.dobject import (
    create_class_definitions,
    DistributedObject,
)


demo_dclasses = {'auth_service': {'userpass': ((str, str),
                                               (field_policies.CLIENT_SEND |
                                                field_policies.AI_RECEIVE))},
                 'avatar': {'move_command': ((float, float),
                                             (field_policies.OWNER_SEND,
                                              field_policies.AI_RECEIVE)),
                            'position': ((float, float),
                                         (field_policies.AI_SEND,
                                          field_policies.OWNER_RECEIVE))}}
dclasses = create_class_definitions(demo_dclasses)


class AuthServiceAI(DistributedObject):
    def creation_hook(self):
        pass


class AuthServiceClient(DistributedObject):
    def creation_hook(self):
        self.send_auth("user", "pass")

    def send_auth(self, username, password):
        self.repo.send_message(
            msgtypes.SET_FIELD,
            self.dobject_id,
            self.dclass.field_id_by_name['userpass'],  # FIXME: Use properties
            (username, password),
        )


class AvatarAI(DistributedObject):
    pass


class AvatarClient(DistributedObject):
    pass


view_classes_ai = {'auth_service': AuthServiceAI,
                   'avatar': AvatarAI}
view_classes_client = {'auth_service': AuthServiceClient,
                       'avatar': AvatarClient}
