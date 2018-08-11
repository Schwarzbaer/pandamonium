from pandamonium.constants import field_types, message_type_by_id


class DatagramIncomplete(Exception):
    Exception


class BasePacker:
    def _to_network(self, value, field_type):
        if field_type.ftype in [int]:
            return value.to_bytes(field_type.length, 'big')

    def _from_network(self, datagram, field_type):
        if len(datagram) < field_type.length:
            raise DatagramIncomplete
        field_bytes = datagram[0:field_type.length]
        value = field_type.ftype.from_bytes(field_bytes, 'big')
        return value, datagram[field_type.length:]

    def pack_args(self, message_type, *args):
        message = b''
        if len(args) != len(message_type.fields):
            raise Exception  # FIXME?
        for field_type, arg in zip(message_type.fields, args):
            message += self._to_network(arg, field_type)
        return message

    def unpack_args(self, message_type, datagram):
        args = []
        for field_type in message_type.fields:
            arg, datagram = self._from_network(datagram, field_type)
            args.append(arg)
        return args, datagram


class AIPacker(BasePacker):
    def pack_message(self, from_channel, to_channel, message_type, *args):
        message = b''.join([
            self._to_network(from_channel, field_types.CHANNEL),
            self._to_network(to_channel, field_types.CHANNEL),
            self._to_network(message_type.num_id, field_types.MESSAGE_TYPE),
            self.pack_args(message_type, *args)
        ])
        return message

    def unpack_message(self, datagram):
        from_channel, datagram = self._from_network(
            datagram,
            field_types.CHANNEL,
        )
        to_channel, datagram = self._from_network(
            datagram,
            field_types.CHANNEL,
        )
        message_type_id, datagram = self._from_network(
            datagram,
            field_types.MESSAGE_TYPE,
        )
        message_type = message_type_by_id[message_type_id]
        args, datagram = self.unpack_args(message_type, datagram)
        return ([from_channel, to_channel, message_type] + args, datagram)


class ClientPacker(BasePacker):
    def pack_message(self, message_type, *args):
        message = b''.join([
            self._to_network(message_type.num_id, field_types.MESSAGE_TYPE),
            self.pack_args(message_type, *args)
        ])
        return message

    def unpack_message(self, datagram):
        message_type_id, datagram = self._from_network(
            datagram,
            field_types.MESSAGE_TYPE,
        )
        message_type = message_type_by_id[message_type_id]
        args, datagram = self.unpack_args(message_type, datagram)
        return ([message_type] + args, datagram)
