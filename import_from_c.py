import sys
from megahal import MegaHAL

file_stream = None

def open_file(filename):
    global file_stream
    file_stream = open(filename, 'rb')  # Open in binary mode

def read_uint8():
    """Read an unsigned 8-bit integer (1 byte)"""
    return int.from_bytes(file_stream.read(1), byteorder='little', signed=False)

def read_uint16():
    """Read an unsigned 16-bit integer (2 bytes)"""
    return int.from_bytes(file_stream.read(2), byteorder='little', signed=False)

def read_uint32():
    """Read an unsigned 32-bit integer (4 bytes)"""
    return int.from_bytes(file_stream.read(4), byteorder='little', signed=False)

def assert_cookie():
    COOKIE = "MegaHALv8".encode("utf-8")

    check = file_stream.read(len(COOKIE))

    if (check != COOKIE):
        raise ValueError(f"MegaHAL cookie was not found in file. Expected '{COOKIE}', found '{check}'")

def load_tree(level = 0):

    symbol = read_uint16()
    usage = read_uint32()
    count = read_uint16()
    branch = read_uint16()

    return (symbol, {
        "symbol": symbol,
        "usage": usage,
        "count": count,
        "branches": dict([load_tree(level + 1) for _ in range(branch)])
    })

def load_word():
    len = read_uint8()
    return file_stream.read(len).decode("latin-1")

def load_dictionary():
    size = read_uint32()
    return [load_word() for _ in range(size)]

def import_model(filename):

    open_file(filename)

    assert_cookie()
    order = read_uint8()

    return MegaHAL(order=order,
                   forward=dict([load_tree()])[0],
                   backward=dict([load_tree()])[0],
                   dictionary=load_dictionary())