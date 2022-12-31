from struct import pack as spack


def pack_f64(x) -> bytes:
    return spack('<d', x)


def pack_u32(x) -> bytes:
    return spack('<I', x)


def pack_str(x) -> bytes:
    bb = x.encode('utf-8')
    return pack_vu32(len(bb)) + bb


def pack_vs64(x) -> bytes:
    bb = encode_signed_leb128(x)
    assert len(bb) <= 8
    return bb


def pack_vs32(x) -> bytes:
    bb = encode_signed_leb128(x)
    assert len(bb) <= 4
    return bb


def pack_vu32(x) -> bytes:
    bb = encode_unsigned_leb128(x)
    assert len(bb) <= 4
    return bb


def pack_vu7(x) -> bytes:
    bb = encode_unsigned_leb128(x)
    assert len(bb) == 1
    return bb


def pack_vu1(x) -> bytes:
    bb = encode_unsigned_leb128(x)
    assert len(bb) == 1
    return bb


def encode_signed_leb128(value) -> bytes:
    bb = []
    if value < 0:
        unsigned_ref_value = (1 - value) * 2
    else:
        unsigned_ref_value = value * 2
    while True:
        byte = value & 0x7F
        value >>= 7
        unsigned_ref_value >>= 7
        if unsigned_ref_value != 0:
            byte = byte | 0x80
        bb.append(byte)
        if unsigned_ref_value == 0:
            break
    return bytes(bb)


def encode_unsigned_leb128(value) -> bytes:
    bb = []  # ints, really
    while True:
        byte = value & 0x7F
        value >>= 7
        if value != 0:
            byte = byte | 0x80
        bb.append(byte)
        if value == 0:
            break
    return bytes(bb)
