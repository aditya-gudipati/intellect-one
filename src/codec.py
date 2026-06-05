"""
This module contains functions for generating Huffman codes from a tree,
encoding input text into a bitstring, and decoding a bitstring back to text.
"""

from typing import Dict, Optional
from huffman import HuffmanNode

def generate_codes(root: Optional[HuffmanNode]) -> Dict[str, str]:
    """
    Generate Huffman codes for each character in the tree using iterative DFS.
    
    Args:
        root: The root of the Huffman tree.
        
    Returns:
        A dictionary mapping characters to their Huffman bitstring code.
    """
    if root is None:
        return {}

    # Handle edge case: single unique character tree
    if root.left is None and root.right is None:
        if root.char is not None:
            return {root.char: "0"}
        return {}

    codes: Dict[str, str] = {}
    # Stack stores tuples of (node, current_code_string)
    stack = [(root, "")]
    
    while stack:
        node, code = stack.pop()
        
        # If we reached a leaf node, record its code
        if node.left is None and node.right is None:
            if node.char is not None:
                codes[node.char] = code
        else:
            # Push right first, then left, so left is processed first
            if node.right is not None:
                stack.append((node.right, code + "1"))
            if node.left is not None:
                stack.append((node.left, code + "0"))
                
    return codes


def encode(text: str, codes: Dict[str, str]) -> str:
    """
    Encode the input text into a bitstring (string of '0's and '1's)
    using the provided codes dictionary.
    
    Args:
        text: The input string to encode.
        codes: A dictionary mapping characters to their bitstring codes.
        
    Returns:
        A string of '0's and '1's representing the encoded text.
        
    Raises:
        ValueError: If a character in the text is not found in the codes dict.
    """
    if not text:
        return ""
        
    encoded_chars = []
    for char in text:
        if char not in codes:
            raise ValueError(f"Character {char!r} not found in Huffman codes dictionary")
        encoded_chars.append(codes[char])
        
    return "".join(encoded_chars)


def decode(bitstring: str, root: Optional[HuffmanNode]) -> str:
    """
    Decode a Huffman-encoded bitstring back to the original text.
    
    Args:
        bitstring: A string of '0's and '1's representing the encoded text.
        root: The root of the Huffman tree used to encode the text.
        
    Returns:
        The decoded text.
        
    Raises:
        ValueError: If the bitstring contains invalid characters or the tree is invalid.
    """
    if not bitstring or root is None:
        return ""

    # Handle edge case: single unique character tree
    if root.left is None and root.right is None:
        if root.char is not None:
            # Each bit in the bitstring corresponds to this character
            for bit in bitstring:
                if bit not in ('0', '1'):
                    raise ValueError(f"Invalid bit '{bit}' in bitstring")
            return root.char * len(bitstring)
        return ""

    decoded_chars = []
    current = root
    
    for bit in bitstring:
        if bit == "0":
            if current.left is None:
                raise ValueError("Malformed bitstring or invalid Huffman tree structure")
            current = current.left
        elif bit == "1":
            if current.right is None:
                raise ValueError("Malformed bitstring or invalid Huffman tree structure")
            current = current.right
        else:
            raise ValueError(f"Invalid bit '{bit}' in bitstring")

        # If we reached a leaf, append the character and reset to the root
        if current.left is None and current.right is None:
            if current.char is not None:
                decoded_chars.append(current.char)
            current = root

    if current is not root:
        raise ValueError("Bitstring ended prematurely: does not terminate at a leaf node")

    return "".join(decoded_chars)
