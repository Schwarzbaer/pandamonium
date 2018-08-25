import struct

from pandamonium.constants import (
    FixedSizeFieldType,
    VariableSizeFieldType,
    ListFieldType,
    field_types,
    msgtypes,
    message_type_by_id,
)
from pandamonium.constants import field_policies as fp


class DatagramIncomplete(Exception):
    Exception


class BasePacker:
    def _to_network(self, value, field_type):
        if isinstance(field_type, FixedSizeFieldType):
            if field_type.ftype is int and field_type.length == 2:
                return struct.pack('h', value)
            elif field_type.ftype is int and field_type.length == 4:
                return struct.pack('i', value)
            elif field_type.ftype is float:
                # FIXME: Should depend on .length
                return struct.pack('f', value)
        elif isinstance(field_type, VariableSizeFieldType):
            if field_type.ftype is str:
                str_repr = value.encode('UTF-8')
                length = struct.pack('h', len(str_repr))
                return length + str_repr
            else:
                raise Exception  # FIXME
        elif isinstance(field_type, ListFieldType):
            import pdb; pdb.set_trace()

    def _from_network(self, datagram, field_type):
        if isinstance(field_type, FixedSizeFieldType):
            if len(datagram) < field_type.length:
                raise DatagramIncomplete
            field_bytes = datagram[0:field_type.length]
            datagram = datagram[field_type.length:]
            if field_type.ftype is int and field_type.length == 2:
                value = struct.unpack('h', field_bytes)[0]
            elif field_type.ftype is int and field_type.length == 4:
                value = struct.unpack('i', field_bytes)[0]
            elif field_type.ftype is float:
                value = struct.unpack('f', field_bytes)[0] # FIXME: See .length
        elif isinstance(field_type, VariableSizeFieldType):
            if field_type.ftype is str:
                if len(datagram) < 2:
                    raise DatagramIncomplete
                length = struct.unpack('h', len(datagram[0:2]))[0]
                datagram = datagram[2:]
                if len(datagram) < length:
                    raise DatagramIncomplete
                str_repr = datagram[:length]
                datagram = datagram[length:]
                value = str_repr.decode('UTF-8')
            else:
                raise Exception  # FIXME
        elif isinstance(field_type, ListFieldType):
            import pdb; pdb.set_trace()
        return value, datagram

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

    def pack_field(self, dclass_id, field_id, values):
        dclass = self.dclasses_by_id[dclass_id]
        _name, dtypes, _policy = dclass._dfields[field_id]
        datagram = b''
        datagram += self._to_network(field_id, field_types.FIELD_ID)
        for dtype, value in zip(dtypes, values):
            datagram += self._to_network(value, dtype)
        return datagram

    def unpack_field(self, dclass_id, datagram):
        field_id, datagram = self._from_network(datagram, field_types.FIELD_ID)
        dclass = self.dclasses_by_id[dclass_id]
        _name, dtypes, _policy = dclass._dfields[field_id]
        values = []
        for dtype in dtypes:
            value, datagram = self._from_network(datagram, dtype)
            values.append(value)
        return field_id, tuple(values), datagram

    def pack_fields(self, dclass_id, values):
        all_fields = self.dclasses_by_id[dclass_id]._dfields
        storage_ids = [f_id
                       for f_id, (_name, types, policy) in enumerate(all_fields)
                       if policy & (fp.RAM | fp.PERSIST)]
        message = b''.join([self.pack_field(dclass_id, s_id, v)
                            for s_id, v in zip(storage_ids, values)])
        return message

    def unpack_fields(self, dclass_id, datagram):
        all_fields = self.dclasses_by_id[dclass_id]._dfields
        storages = [(f_id, types)
                    for f_id, (_name, types, policy) in enumerate(all_fields)
                    if policy & (fp.RAM | fp.PERSIST)]
        field_values = []
        for field_id, dtypes in storages:
            field_id, field_value, datagram = self.unpack_field(
                dclass_id,
                datagram,
            )
            field_values.append((field_id, field_value))
        field_values = sorted(field_values)
        id_matches = list(zip(
            [s_id for s_id, _ in storages],
            [f_id for f_id, _ in field_values],
        ))
        if not all([s_id == f_id for s_id, f_id in id_matches]):
            mismatches = [(s_id, f_id)
                          for s_id, f_id in id_matches
                          if s_id != f_id]
            # FIXME: Better exception, with text!
            raise ValueError("Storage ID -> Field ID mismatch: {}"
                             "".format(mismatches))
        return [v for _, v in field_values], datagram


class AIPacker(BasePacker):
    def pack_message(self, from_channel, to_channel, message_type, *args):
        header = b''.join([
            self._to_network(from_channel, field_types.CHANNEL),
            self._to_network(to_channel, field_types.CHANNEL),
            self._to_network(message_type.num_id, field_types.MESSAGE_TYPE),
        ])
        if message_type == msgtypes.CREATE_DOBJECT:
            dclass, field_values, token = args
            body = b''.join([
                self._to_network(dclass, field_types.DCLASS),
                self.pack_fields(dclass, field_values),
                self._to_network(token, field_types.TOKEN),
            ])
        elif message_type in [
                msgtypes.CREATE_DOBJECT_VIEW,
                msgtypes.CREATE_AI_VIEW]:
            dobject_id, dclass, fields = args
            with self.dclasses_lock:
                self.dclasses_by_dobject_id[dobject_id] = dclass
            body = b''.join([
                self._to_network(dobject_id, field_type.DOBJECT_ID),
                self.pack_fields(dclass, fields),
            ])
        elif message_type in [msgtypes.SET_FIELD, msgtypes.FIELD_UPDATE]:
            dobject_id, field_id, field_values = args
            with self.dclasses_lock:
                dclass = self.dclasses_by_dobject_id[dobject_id]
            body = b''.join([
                self._to_network(dobject_id, field_type.DOBJECT_ID),
                self._to_network(field_id, field_type.FIELD_ID),
                self.pack_field(dclass, field_id, field_values),
            ])
        else:
            body = self.pack_args(message_type, *args)
        message = b''.join([header, body])
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
        if message_type == msgtypes.CREATE_DOBJECT:
            dclass_id, datagram = self._from_network(
                datagram,
                field_types.DCLASS,
            )
            field_values, datagram = self.unpack_fields(dclass_id, datagram)
            token, datagram = self._from_network(
                datagram,
                field_types.TOKEN,
            )
            args = [dclass_id, field_values, token]
        elif message_type in [
                msgtypes.CREATE_DOBJECT_VIEW,
                msgtypes.CREATE_AI_VIEW]:
            dobject_id, datagram = self._from_network(
                datagram,
                field_types.DOBJECT_ID,
            )
            dclass, datagram = self._from_network(
                datagram,
                field_types.DCLASS,
            )
            field_values, datagram = self.unpack_fields(dclass, datagram)
            args = [dobject_id, dclass, field_values]
        else:
            args, datagram = self.unpack_args(message_type, datagram)
        return ([from_channel, to_channel, message_type] + args, datagram)


class ClientPacker(BasePacker):
    def pack_message(self, message_type, *args):
        header = self._to_network(
            message_type.num_id,
            field_types.MESSAGE_TYPE,
        )
        if message_type in [
                msgtypes.CREATE_DOBJECT_VIEW,
                msgtypes.CREATE_AI_VIEW]:
            dobject_id, dclass, fields = args
            with self.dclasses_lock:
                self.dclasses_by_dobject_id[dobject_id] = dclass
            body = b''.join([
                self._to_network(dobject_id, field_type.DOBJECT_ID),
                self.pack_fields(dclass, fields),
            ])
        elif message_type in [msgtypes.SET_FIELD, msgtypes.FIELD_UPDATE]:
            dobject_id, field_id, field_values = args
            with self.dclasses_lock:
                dclass = self.dclasses_by_dobject_id[dobject_id]
            body = b''.join([
                self._to_network(dobject_id, field_type.DOBJECT_ID),
                self._to_network(field_id, field_type.FIELD_ID),
                self.pack_field(dclass, field_id, field_values),
            ])
        else:
            body = self.pack_args(message_type, *args)
        message = b''.join([header, body])
        return message

    def unpack_message(self, datagram):
        message_type_id, datagram = self._from_network(
            datagram,
            field_types.MESSAGE_TYPE,
        )
        message_type = message_type_by_id[message_type_id]
        args, datagram = self.unpack_args(message_type, datagram)
        return ([message_type] + args, datagram)
