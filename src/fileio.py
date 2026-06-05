"""
This module handles binary I/O operations and bit packing/unpacking using bytearrays.
"""

import os
from typing import Tuple

def bits_to_bytes(bitstring: str) -> Tuple[bytes, int]:
    """
    Pad a bitstring to a multiple of 8 with trailing zeros and pack into bytes.
    Uses bytearray for building the byte sequence.
    
    Args:
        bitstring: A string of '0's and '1's.
        
    Returns:
        A tuple of (bytes_object, padding_count).
    """
    if not bitstring:
        return b"", 0

    padding_count = (8 - (len(bitstring) % 8)) % 8
    padded_bitstring = bitstring + "0" * padding_count
    
    barr = bytearray()
    for i in range(0, len(padded_bitstring), 8):
        chunk = padded_bitstring[i : i + 8]
        barr.append(int(chunk, 2))
        
    return bytes(barr), padding_count


def bytes_to_bits(bytes_obj: bytes, padding_count: int) -> str:
    """
    Unpack a bytes object back into a bitstring, stripping the trailing padding bits.
    
    Args:
        bytes_obj: The bytes to unpack.
        padding_count: The number of trailing padding bits to strip.
        
    Returns:
        The unpacked bitstring of '0's and '1's.
    """
    if not bytes_obj:
        return ""

    bit_list = []
    for byte in bytes_obj:
        bit_list.append(f"{byte:08b}")
        
    full_bitstring = "".join(bit_list)
    
    if padding_count > 0:
        full_bitstring = full_bitstring[:-padding_count]
        
    return full_bitstring


def write_compressed(filepath: str, tree_bits: str, data_bits: str) -> None:
    """
    Write tree_bits and data_bits into a compressed file using the specified format.
    Format:
        1. 2 bytes: length of tree_bits (uint16, big-endian)
        2. 1 byte: padding count for tree bits
        3. packed tree bytes
        4. 1 byte: padding count for data bits
        5. packed data bytes
        
    If both tree_bits and data_bits are empty, writes an empty file (0 bytes).
    
    Args:
        filepath: The destination file path.
        tree_bits: The serialized tree bitstring.
        data_bits: The encoded data bitstring.
    """
    if not tree_bits and not data_bits:
        # Empty file edge case: write a 0-byte file
        with open(filepath, "wb") as f:
            pass
        return

    tree_bytes, tree_padding = bits_to_bytes(tree_bits)
    data_bytes, data_padding = bits_to_bytes(data_bits)
    
    tree_len = len(tree_bits)
    if tree_len > 65535:
        raise ValueError(f"Tree bitstring length ({tree_len}) exceeds uint16 limit (65535)")

    with open(filepath, "wb") as f:
        # Write uint16 tree length
        f.write(tree_len.to_bytes(2, byteorder="big"))
        # Write tree padding
        f.write(bytes([tree_padding]))
        # Write tree bytes
        f.write(tree_bytes)
        # Write data padding
        f.write(bytes([data_padding]))
        # Write data bytes
        f.write(data_bytes)


def read_compressed(filepath: str) -> Tuple[str, str]:
    """
    Read a compressed file and reconstruct the tree_bits and data_bits.
    Returns empty strings if the file is empty (0 bytes).
    
    Args:
        filepath: The path to the compressed file.
        
    Returns:
        A tuple of (tree_bits, data_bits).
        
    Raises:
        ValueError: If the file format is malformed or corrupted.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    file_size = os.path.getsize(filepath)
    if file_size == 0:
        return "", ""

    with open(filepath, "rb") as f:
        # Read tree length (2 bytes)
        tree_len_bytes = f.read(2)
        if len(tree_len_bytes) < 2:
            raise ValueError("Malformed file: cannot read tree length")
        tree_len = int.from_bytes(tree_len_bytes, byteorder="big")
        
        # Read tree padding (1 byte)
        tree_padding_byte = f.read(1)
        if not tree_padding_byte:
            raise ValueError("Malformed file: cannot read tree padding byte")
        tree_padding = tree_padding_byte[0]
        
        # Calculate tree bytes length
        # padded tree bits length is tree_len + tree_padding, which must be a multiple of 8
        tree_bytes_len = (tree_len + tree_padding) // 8
        tree_bytes = f.read(tree_bytes_len)
        if len(tree_bytes) < tree_bytes_len:
            raise ValueError("Malformed file: missing tree bytes")
            
        tree_bits = bytes_to_bits(tree_bytes, tree_padding)
        if len(tree_bits) != tree_len:
            raise ValueError("Malformed file: reconstructed tree bits length mismatch")
            
        # Read data padding (1 byte)
        data_padding_byte = f.read(1)
        if not data_padding_byte:
            raise ValueError("Malformed file: cannot read data padding byte")
        data_padding = data_padding_byte[0]
        
        # Read remaining bytes as data bytes
        data_bytes = f.read()
        
        data_bits = bytes_to_bits(data_bytes, data_padding)
        
    return tree_bits, data_bits
