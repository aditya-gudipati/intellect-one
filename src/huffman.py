"""
This module defines the HuffmanNode class and the build_tree function
to construct a Huffman tree from a frequency table.
"""

from typing import Dict, Optional, Any
from heap import MinHeap

class HuffmanNode:
    """
    A node in the Huffman tree.
    Supports comparison using '<' for MinHeap operations.
    """
    def __init__(
        self,
        freq: int,
        char: Optional[str] = None,
        left: Optional["HuffmanNode"] = None,
        right: Optional["HuffmanNode"] = None
    ) -> None:
        """
        Initialize a HuffmanNode.
        
        Args:
            freq: Frequency of the character or combined frequency of children.
            char: The character associated with the node (None for internal nodes).
            left: Left child node.
            right: Right child node.
        """
        self.freq: int = freq
        self.char: Optional[str] = char
        self.left: Optional[HuffmanNode] = left
        self.right: Optional[HuffmanNode] = right

    def __lt__(self, other: Any) -> bool:
        """
        Compare nodes by frequency to support sorting/heap operations.
        If frequencies are equal, breaks ties using character comparison.
        """
        if not isinstance(other, HuffmanNode):
            return NotImplemented
        
        if self.freq != other.freq:
            return self.freq < other.freq
        
        # Tie-breaker when frequencies are equal to avoid comparing None with str
        if self.char is not None and other.char is not None:
            return self.char < other.char
        if self.char is not None:
            return True  # Leaves take precedence/consistent ordering
        return False

    def __repr__(self) -> str:
        """Return a string representation of the node for debugging."""
        return f"HuffmanNode(freq={self.freq}, char={self.char!r})"


def build_tree(freq_dict: Dict[str, int]) -> Optional[HuffmanNode]:
    """
    Build a Huffman tree from a frequency dictionary and return the root node.
    
    Args:
        freq_dict: A dictionary mapping characters to their frequencies.
        
    Returns:
        The root HuffmanNode of the constructed tree, or None if the input is empty.
    """
    if not freq_dict:
        return None

    heap = MinHeap()
    
    # Create a leaf node for each unique character and insert into the heap
    for char, freq in freq_dict.items():
        heap.insert(HuffmanNode(freq=freq, char=char))

    # Loop until only one node remains (the root of the tree)
    while len(heap) > 1:
        left = heap.extract_min()
        right = heap.extract_min()
        
        # Merge the two minimum frequency nodes into a new internal node
        parent_freq = left.freq + right.freq
        parent_node = HuffmanNode(freq=parent_freq, char=None, left=left, right=right)
        
        heap.insert(parent_node)

    return heap.extract_min()
