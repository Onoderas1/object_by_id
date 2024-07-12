import ctypes
import struct
import typing as tp
import enum

LONG_LEN = 8
INT_LEN = 4
CHAR_LEN = 1

ULONG_CHAR = "L" if ctypes.sizeof(ctypes.c_ulong) == 8 else "Q"
LONG_CHAR = "l" if ctypes.sizeof(ctypes.c_long) == 8 else "q"


class Id(enum.Enum):
    int = id(int)
    str = id(str)
    bool = id(bool)
    float = id(float)
    list = id(list)
    tuple = id(tuple)


def get_object_by_id_with_id_map(object_id: int, map_id: dict[int, tp.Any]) -> (int | float | tuple[tp.Any, ...] |
                                                                                list[tp.Any] | str | bool):
    """
    Restores object by id.
    :param object_id: Object Id.
    :param map_id: dict with Id.
    :return: An object that corresponds to object_id.
    """
    LL: str = ULONG_CHAR + ULONG_CHAR
    LLl: str = LL + LONG_CHAR
    ans: list[tp.Any] = []
    match struct.unpack(LL, ctypes.string_at(object_id, 16))[1]:
        case Id.int.value:
            count = struct.unpack(LLl, ctypes.string_at(object_id, 24))[2]
            format: str = (LLl + 'i' * abs(count))
            numbers = struct.unpack(format, ctypes.string_at(object_id, 24 + 4 * abs(count)))[3::]
            ans_int = 0
            for i in range(len(numbers)):
                ans_int += numbers[i] * ((2 ** 30) ** i)
            return ans_int if count >= 0 else -ans_int
        case Id.float.value:
            return struct.unpack(LL + "d", ctypes.string_at(object_id, 24))[2]
        case Id.bool.value:
            return True if struct.unpack(LLl, ctypes.string_at(object_id, 24))[2] else False
        case Id.str.value:
            LLL: str = LL + ULONG_CHAR
            count = struct.unpack(LLL, ctypes.string_at(object_id, 24))[2]
            LLLl16scs: str = LLL + LONG_CHAR + "16" + 's' + str(count) + 's'
            return struct.unpack(LLLl16scs, ctypes.string_at(object_id, 48 + count))[5].decode('ascii')
        case Id.list.value:
            data1 = struct.unpack('5' + ULONG_CHAR, ctypes.string_at(object_id, 40))
            count = data1[2]
            data2 = struct.unpack(str(count) + ULONG_CHAR, ctypes.string_at(data1[3], 8 * count))
            map_id[object_id] = ans
            for i in data2:
                if i in map_id:
                    ans.append(map_id[i])
                else:
                    el = get_object_by_id_with_id_map(i, map_id)
                    map_id[i] = el
                    ans.append(el)
            return ans
        case Id.tuple.value:
            count = struct.unpack('3' + ULONG_CHAR, ctypes.string_at(object_id, 24))[2]
            data1 = struct.unpack(str(3 + count) + ULONG_CHAR, ctypes.string_at(object_id, 24 + 8 * count))[3::]
            map_id[object_id] = ans
            for i in data1:
                if i in map_id:
                    ans.append(map_id[i])
                else:
                    el = get_object_by_id_with_id_map(i, map_id)
                    map_id[i] = el
                    ans.append(el)
            return tuple(ans)
        case _:
            print((struct.unpack(LL, ctypes.string_at(object_id, 16))[1]))
    return 5


def get_object_by_id(object_id: int) -> int | float | tuple[tp.Any, ...] | list[tp.Any] | str | bool:
    """
    Restores object by id.
    :param object_id: Object Id.
    :return: An object that corresponds to object_id.
    """
    return get_object_by_id_with_id_map(object_id, {})
