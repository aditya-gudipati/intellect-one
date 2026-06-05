"""
This module handles serialization and deserialization of the Huffman tree.
It uses preorder bit encoding (0 for internal nodes, 1 + 8 bits for leaf nodes)
without any recursive functions.
"""

from typing import Tuple, Optional
from huffman import HuffmanNode

def serialize_tree(root: Optional[HuffmanNode]) -> str:
    """
    Serialize the Huffman tree into a bitstring (string of '0's and '1's)
    using an iterative preorder DFS traversal.
    
    Format:
        - Internal Node: '0'
        - Leaf Node: '1' followed by 8-bit binary representation of character ASCII
        
    Args:
        root: The root of the Huffman tree.
        
    Returns:
        The preorder serialized bitstring.
    """
    if root is None:
        return ""

    bits = []
    stack = [root]
    
    while stack:
        node = stack.pop()
        
        if node.left is None and node.right is None:
            # Leaf node
            if node.char is None:
                raise ValueError("Leaf node must contain a character")
            val = ord(node.char)
            if val < 0 or val > 255:
                raise ValueError(f"Character {node.char!r} is not standard 8-bit ASCII")
            
            # Format ordinal as 8-bit binary string
            bits.append("1" + f"{val:08b}")
        else:
            # Internal node
            bits.append("0")
            # Push right first, then left, so left is popped first (preorder traversal)
            if node.right is not None:
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)
                
    return "".join(bits)


def deserialize_tree(bitstring: str) -> Tuple[Optional[HuffmanNode], int]:
    """
    Deserialize a preorder bitstring back into a Huffman tree structure.
    Implements an iterative reconstruction to avoid recursion limits.
    
    Args:
        bitstring: A string of '0's and '1's representing the preorder traversal.
        
    Returns:
        A tuple of (root_node, bits_consumed).
        
    Raises:
        ValueError: If the bitstring is malformed or ends unexpectedly.
    """
    if not bitstring:
        return None, 0

    idx = 0
    
    # Handle single node tree or initial node
    if bitstring[idx] == "1":
        if len(bitstring) < idx + 9:
            raise ValueError("Unexpected end of bitstring during tree deserialization")
        char_bits = bitstring[idx + 1 : idx + 9]
        char = chr(int(char_bits, 2))
        return HuffmanNode(freq=0, char=char), 9

    # Root is an internal node
    root = HuffmanNode(freq=0, char=None)
    idx += 1
    
    # Stack stores tuples of (parent_node, child_slot) where child_slot is 'left' or 'right'
    # Since we want to build the left branch first, we push 'right' then 'left'
    stack = [(root, "right"), (root, "left")]
    
    while stack:
        if idx >= len(bitstring):
            raise ValueError("Unexpected end of bitstring: stack is not empty but bitstring is exhausted")
            
        parent, slot = stack.pop()
        
        if bitstring[idx] == "0":
            # Internal node
            node = HuffmanNode(freq=0, char=None)
            idx += 1
            
            if slot == "left":
                parent.left = node
            else:
                parent.right = node
                
            # Internal node has 2 children; push them to stack
            stack.append((node, "right"))
            stack.append((node, "left"))
        else:
            # Leaf node
            if len(bitstring) < idx + 9:
                raise ValueError("Unexpected end of bitstring during tree deserialization")
            char_bits = bitstring[idx + 1 : idx + 9]
            char = chr(int(char_bits, 2))
            node = HuffmanNode(freq=0, char=char)
            idx += 9
            
            if slot == "left":
                parent.left = node
            else:
                parent.right = node

    return root, idx
