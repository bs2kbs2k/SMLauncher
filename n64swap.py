# Original code by Brawl345(https://github.com/Brawl345/N64Swap)
# Modified by bs2k
# It's originally The Unlicense so I don't need to credit him but whatever I'm doing it

from enum import Enum, auto
from typing import BinaryIO, TextIO, Generator
import sys
import numpy


class RomType(Enum):
    Z64 = auto()
    V64 = auto()
    N64 = auto()
    UNKNOWN = auto()


def read_in_chunks(file_object: BinaryIO, chunk_size: int = 1024) -> Generator[bytes, None, None]:
    """
    Lazy function (generator) to read a file piece by piece.

    :param file_object: the file object to read in chunks
    :param chunk_size: the size of the chunk in bytes. defaults to 1kiB(1024 bytes)"""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def get_rom_format(rom_header: bytes) -> RomType:
    """
    A function to guess the ROM type from the header.

    :param rom_header: the header of the ROM
    :return: the guessed type of the ROM
    """
    if rom_header == b"\x40\x12\x37\x80":
        return RomType.N64
    elif rom_header == b"\x80\x37\x12\x40":
        return RomType.Z64
    elif rom_header == b"\x37\x80\x40\x12":
        return RomType.V64
    else:
        return RomType.UNKNOWN


def swap_bytes(b: bytes) -> bytearray:
    """
    A function to swap the bytes' order

    :param b: the original bytes to be swapped
    :return: the swapped bytes
    """
    chunk_bytearray = bytearray(b)
    byteswapped = bytearray(len(b))
    byteswapped[0::2] = chunk_bytearray[1::2]
    byteswapped[1::2] = chunk_bytearray[0::2]
    return byteswapped


def convert(rom_file: BinaryIO, out_file: BinaryIO, out_type: RomType = RomType.Z64, log_file: TextIO = sys.stdout):
    """
    Converts one type of ROM to another. The main high-level API.

    :param rom_file: The original ROM file.
    :param out_file: The file to write the converted output to.
    :param out_type: The type to convert to. defaults to Z64.
    :param log_file: The file to write the logs. defaults to stdout.
    """
    rom_header: bytes = rom_file.read(4)
    rom_type: RomType = get_rom_format(rom_header)
    if rom_type == RomType.UNKNOWN:
        raise ValueError('Unknown ROM type or not a ROM')
    rom_file.seek(0)

    print("{0} -> {1}".format(rom_type, out_type), file=log_file)
    if rom_type == out_type:  # Just copy it
        for chunk in read_in_chunks(rom_file):
            out_file.write(chunk)

    if rom_type == RomType.Z64:  # Big Endian
        if out_type == RomType.N64:  # Big Endian -> Little Endian
            for chunk in read_in_chunks(rom_file):
                out_file.write(numpy.frombuffer(chunk, numpy.float32).byteswap())
        elif out_type == RomType.V64:  # Big Endian -> Byteswapped
            for chunk in read_in_chunks(rom_file):
                out_file.write(swap_bytes(chunk))

    elif rom_type == RomType.N64:  # Little Endian
        if out_type == RomType.Z64:  # Little Endian -> Big Endian
            for chunk in read_in_chunks(rom_file):
                out_file.write(numpy.frombuffer(chunk, numpy.float32).byteswap())
        elif out_type == RomType.V64:  # Little Endian -> Big Endian -> Byteswapped
            for chunk in read_in_chunks(rom_file):
                endian_swapped = numpy.frombuffer(chunk, numpy.float32).byteswap()
                out_file.write(swap_bytes(endian_swapped.tobytes()))

    elif rom_type == RomType.V64:  # Byteswapped
        if out_type == RomType.N64:  # Byteswapped -> Big Endian -> Little Endian
            for chunk in read_in_chunks(rom_file):
                endian_swapped = numpy.frombuffer(chunk, numpy.float32).byteswap()
                out_file.write(swap_bytes(endian_swapped.tobytes()))
        elif out_type == RomType.Z64:  # Byteswapped -> Big Endian
            for chunk in read_in_chunks(rom_file):
                out_file.write(swap_bytes(chunk))

    print("Conversion finished.", file=log_file)
