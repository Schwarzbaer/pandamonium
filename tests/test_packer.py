import pytest

from pandamonium.constants import (
    msgtypes,
    field_types,
    field_policies
)
from pandamonium.dobject import DClass
from pandamonium.packers import (
    DatagramIncomplete,
    BasePacker,
    AIPacker,
    ClientPacker,
)


class DemoDClass(DClass):
    dfield_test_0 = ((field_types.CHANNEL, ), field_policies.RAM)
    dfield_test_1 = ((field_types.CHANNEL,
                      field_types.CHANNEL),
                     0) # No policy at all
    dfield_test_2 = ((field_types.CHANNEL, ), field_policies.RAM)


def test_packing():
    packer = BasePacker()
    channel_in = 1234567890
    message = packer._to_network(channel_in, field_types.CHANNEL)
    channel_out, datagram = packer._from_network(message, field_types.CHANNEL)
    assert channel_in == channel_out
    assert datagram == b''


def test_ai_packer_no_args():
    packer = AIPacker()
    from_channel = 1<<0
    to_channel = 1<<30
    message_type = msgtypes.TEST_NO_ARGS
    message = packer.pack_message(from_channel, to_channel, message_type)
    [from_p, to_p, type_p, *args], datagram = packer.unpack_message(message)
    assert from_p == from_channel
    assert to_channel == to_p
    assert message_type == type_p
    assert datagram == b''


def test_ai_packer_int_args():
    packer = AIPacker()
    from_channel = 1<<0
    to_channel = 1<<30
    message_type = msgtypes.TEST_THREE_CHANNEL_ARGS
    channel_1 = 1
    channel_2 = 2
    channel_3 = 3
    message = packer.pack_message(
        from_channel,
        to_channel,
        message_type,
        channel_1,
        channel_2,
        channel_3,
    )
    [from_p, to_p, type_p, *args], datagram = packer.unpack_message(message)
    assert from_p == from_channel
    assert to_channel == to_p
    assert message_type == type_p
    assert datagram == b''
    assert len(args) == 3
    assert channel_1 == args[0]
    assert channel_2 == args[1]
    assert channel_3 == args[2]


def test_client_packer_no_args():
    packer = ClientPacker()
    message_type = msgtypes.TEST_NO_ARGS
    message = packer.pack_message(message_type)
    [type_p], datagram = packer.unpack_message(message)
    assert message_type == type_p
    assert datagram == b''


def test_incomplete_datagram_ai_packer():
    packer = AIPacker()
    message = b''
    with pytest.raises(DatagramIncomplete):
        packer.unpack_message(message)


def test_incomplete_datagram_client_packer():
    packer = ClientPacker()
    message = b''
    with pytest.raises(DatagramIncomplete):
        packer.unpack_message(message)


def test_field_roundtrip():
    packer = type('Packer', (BasePacker, ), {'dclasses': {'foo': DemoDClass}})()
    packer.dclasses_by_id = [packer.dclasses[dclass_name]
                             for dclass_name in sorted(packer.dclasses)]
    dclass_id = 0
    field_id = 2
    field_values = (123, )
    datagram = packer.pack_field(dclass_id, field_id, field_values)
    field_id_p, values_p, datagram = packer.unpack_field(dclass_id, datagram)
    assert datagram == b''
    assert field_id == field_id_p
    assert field_values == values_p


def test_fields_roundtrip():
    packer = type('Packer', (AIPacker, ), {'dclasses': {'foo': DemoDClass}})()
    packer.dclasses_by_id = [packer.dclasses[dclass_name]
                             for dclass_name in sorted(packer.dclasses)]
    dclass_id = 0
    field_values = [(123, ), (345, )]
    datagram = packer.pack_fields(dclass_id, field_values)
    values_p, datagram = packer.unpack_fields(dclass_id, datagram)
    assert datagram == b''
    assert field_values == values_p


def test_unpack_fields_with_wrong_fields():
    packer = type('Packer', (AIPacker, ), {'dclasses': {'foo': DemoDClass}})()
    packer.dclasses_by_id = [packer.dclasses[dclass_name]
                             for dclass_name in sorted(packer.dclasses)]
    dclass_id = 0
    field_value_0 = (123, )
    field_value_1 = (456, 789)
    datagram = b''
    datagram += packer.pack_field(dclass_id, 0, field_value_0)
    datagram += packer.pack_field(dclass_id, 1, field_value_1)
    with pytest.raises(ValueError):
        values_p, datagram = packer.unpack_fields(dclass_id, datagram)


def test_pack_message_with_create_dobject():
    packer = type('Packer', (AIPacker, ), {'dclasses': {'foo': DemoDClass}})()
    packer.dclasses_by_id = [packer.dclasses[dclass_name]
                             for dclass_name in sorted(packer.dclasses)]
    from_channel = 5
    to_channel = 8
    message_type = msgtypes.CREATE_DOBJECT
    dclass_id = 0
    field_values = [(123,), (456,)]
    token = 123456
    datagram = packer.pack_message(
        from_channel,
        to_channel,
        message_type,
        dclass_id,
        field_values,
        token,
    )
    message, datagram = packer.unpack_message(datagram)
    from_p, to_p, message_type_p, dclass_id_p, field_values_p, token_p = message
    assert datagram == b''
    assert from_channel == from_p
    assert to_channel == to_p
    assert dclass_id == dclass_id_p
    assert field_values == field_values_p
    assert token == token_p


# TODO: Test packing/unpacking with CREATE_OBJECT, CREATE_*_VIEW
