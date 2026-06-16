"""
SPECIFICATION:
  Rule 1: Decompression Gate - Tree structure is serialized using iterative preorder
          DFS traversal, writing '0' for internal nodes and '1' followed by the 8-bit
          binary representation of the character's ASCII code for leaf nodes.
  Rule 2: No-Recursion constraint - Serialization and deserialization must be performed
          using explicit stacks to guarantee protection against Python's maximum recursion limit.
  Edge cases handled: Empty tree serializes to/deserializes from an empty string; invalid
          bitstrings (unexpected end of string) during deserialization raise ValueError.
"""

from typing import Tuple, Optional
from huffman import HuffmanNode

# Complexity: Time O(k), Space O(k) where k is the number of unique characters
# Invariant: Output bitstring corresponds exactly to preorder sequence of nodes (Root, Left, Right).
def serialize_tree(root: Optional[HuffmanNode]) -> str:
    """
    Serialize the Huffman tree into a bitstring (string of '0's and '1's)
    using an iterative preorder DFS traversal.
    
    Algorithm:
        - Strategy: Preorder depth-first traversal (DFS) using an explicit stack.
        - Rationale: Standard binary tree structures are naturally flattened by preorder sequence. Stack-based iteration avoids recursion depth limit.
        - Alternatives: Level-order (BFS) serialization was rejected because it requires structural layout metadata / null markers, making it less compact. Adjacency lists or JSON representations were rejected due to verbose overhead.
        
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
            
            utf8_bytes = node.char.encode("utf-8")
            num_bytes = len(utf8_bytes)
            if num_bytes < 1 or num_bytes > 4:
                raise ValueError(f"Character {node.char!r} UTF-8 length ({num_bytes}) is not between 1 and 4 bytes")
            
            # 2-bit binary for length (0 to 3 mapping to 1 to 4 bytes)
            len_bits = f"{(num_bytes - 1):02b}"
            
            # 8-bit binary representation for each byte
            byte_bits = "".join(f"{b:08b}" for b in utf8_bytes)
            
            bits.append("1" + len_bits + byte_bits)
        else:
            # Internal node
            bits.append("0")
            # Push right first, then left, so left is popped first (preorder traversal)
            # Verified: Root -> Left -> Right is preserved exactly.
            if node.right is not None:
                stack.append(node.right)
            if node.left is not None:
                stack.append(node.left)
                
    return "".join(bits)


# Complexity: Time O(k), Space O(k) where k is the number of unique characters
# Invariant: Reconstruction stack state mirrors the active structural hierarchy of the tree.
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
        if len(bitstring) < idx + 3:
            raise ValueError("Unexpected end of bitstring during tree deserialization")
        len_bits = bitstring[idx + 1 : idx + 3]
        num_bytes = int(len_bits, 2) + 1
        if len(bitstring) < idx + 3 + num_bytes * 8:
            raise ValueError("Unexpected end of bitstring during tree deserialization")
        
        char_bits = bitstring[idx + 3 : idx + 3 + num_bytes * 8]
        byte_list = []
        for i in range(0, len(char_bits), 8):
            byte_list.append(int(char_bits[i : i + 8], 2))
        char = bytes(byte_list).decode("utf-8")
        return HuffmanNode(freq=0, char=char), 3 + num_bytes * 8

    # Root is an internal node
    root = HuffmanNode(freq=0, char=None)
    idx += 1
    
    # Stack stores tuples of (parent_node, child_slot) where child_slot is 'left' or 'right'
    # Since we want to build the left branch first, we push 'right' then 'left'
    # Verified: Left child is popped and processed first, matching preorder serialization.
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
            if len(bitstring) < idx + 3:
                raise ValueError("Unexpected end of bitstring during tree deserialization")
            len_bits = bitstring[idx + 1 : idx + 3]
            num_bytes = int(len_bits, 2) + 1
            
            if len(bitstring) < idx + 3 + num_bytes * 8:
                raise ValueError("Unexpected end of bitstring during tree deserialization")
                
            char_bits = bitstring[idx + 3 : idx + 3 + num_bytes * 8]
            byte_list = []
            for i in range(0, len(char_bits), 8):
                byte_list.append(int(char_bits[i : i + 8], 2))
            char = bytes(byte_list).decode("utf-8")
            node = HuffmanNode(freq=0, char=char)
            idx += 3 + num_bytes * 8
            
            if slot == "left":
                parent.left = node
            else:
                parent.right = node

    return root, idx
