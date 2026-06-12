"""
SPECIFICATION:
  Rule 1: Code Assignment - Traverses the Huffman tree, assigning '0' for left
          branches and '1' for right branches.
  Rule 2: Prefix-Free Guarantee - No character code is a prefix of any other code,
          ensuring unambiguous decompression.
  Edge cases handled: Single unique character tree is assigned code '0'; empty input
          text returns an empty bitstring; decoding empty bitstring or with a null
          tree returns an empty string. Invalid bit representations or premature
          ends of bitstrings raise ValueError.
"""

from typing import Dict, Optional
from huffman import HuffmanNode

# Complexity: Time O(k), Space O(k) where k is the number of unique characters
# Invariant: Recursion-free stack-based preorder traversal paths map exactly to prefix-free codes.
def generate_codes(root: Optional[HuffmanNode]) -> Dict[str, str]:
    """
    Generate Huffman codes for each character in the tree using iterative DFS.
    
    Algorithm:
        - Strategy: Iterative Depth-First Search (DFS) using an explicit stack.
        - Rationale: DFS naturally builds paths sequentially. The stack avoids Python's stack recursion depth limit.
        - Alternatives: Recursive DFS was rejected to prevent recursion stack overflow on highly skewed trees. BFS was rejected because storing path states in a queue requires more memory.
        
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


# Complexity: Time O(n), Space O(n) where n is the length of input text
# Invariant: The generated bitstring is the concatenation of the valid codes of the input characters.
def encode(text: str, codes: Dict[str, str]) -> str:
    """
    Encode the input text into a bitstring (string of '0's and '1's)
    using the provided codes dictionary.
    
    Algorithm:
        - Strategy: Direct dictionary lookup table.
        - Rationale: Retrieving codes in O(1) time per character yields an optimal O(n) total runtime.
        - Alternatives: Re-traversing the tree from the root for each character would run in O(n * depth) which is slow and was rejected.

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


# Complexity: Time O(b), Space O(n) where b is the length of bitstring and n is text length
# Invariant: Traversing the tree bit-by-bit yields the exact original character sequence when terminating at leaf nodes.
def decode(bitstring: str, root: Optional[HuffmanNode]) -> str:
    """
    Decode a Huffman-encoded bitstring back to the original text.
    
    Algorithm:
        - Strategy: Huffman tree traversal via bit-based branching.
        - Rationale: Sequentially navigates tree nodes using constant O(1) operations per bit, which is memory-efficient.
        - Alternatives: Matching bit segments against a lookup table of codes (dictionary inversion) was rejected because prefix-free codes are variable-length, necessitating expensive substring parsing/backtracking.

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
