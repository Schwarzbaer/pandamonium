from pandamonium.constants import field_policies
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
        print("Let's authenticate ourselves!")


class AvatarAI(DistributedObject):
    pass


class AvatarClient(DistributedObject):
    pass


view_classes_ai = {'auth_service': AuthServiceAI,
                   'avatar': AvatarAI}
view_classes_client = {'auth_service': AuthServiceClient,
                       'avatar': AvatarClient}
