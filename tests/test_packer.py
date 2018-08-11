import pytest

from pandamonium.constants import (
    msgtypes,
    field_types,
)
from pandamonium.packers import (
    DatagramIncomplete,
    BasePacker,
    AIPacker,
    ClientPacker,
)


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
