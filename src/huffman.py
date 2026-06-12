"""
SPECIFICATION:
  Rule 1: Tree Construction - Constructs the Huffman tree using greedy merging of
          minimum frequency nodes via a custom MinHeap.
  Rule 2: Parent Node Frequencies - The frequency of any internal parent node is
          always the exact sum of the frequencies of its left and right children.
  Edge cases handled: Empty frequency dictionary returns None; single-unique-character
          dictionary returns a single leaf node.
"""

# Overall complexity: O(n + k log k) where n=file chars, k=unique chars

from typing import Dict, Optional, Any
from heap import MinHeap

class HuffmanNode:
    """
    A node in the Huffman tree.
    Supports comparison using '<' for MinHeap operations.

    Class Invariants:
      1. Frequency Sign: Frequency (`self.freq`) is always a non-negative integer.
      2. Leaf Character: If it is a leaf (both left and right are None), `self.char`
         must not be None (except in empty-tree context).
      3. Internal Node: If it is an internal node, both left and right must be present
         and `self.char` must be None.
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


# Complexity: Time O(k log k), Space O(k) where k is the number of unique characters
# Invariant: Frequencies of merged nodes equal the sum of children's frequencies. Heap size decreases by 1 each merge.
def build_tree(freq_dict: Dict[str, int]) -> Optional[HuffmanNode]:
    """
    Build a Huffman tree from a frequency dictionary and return the root node.
    
    Algorithm:
        - Strategy: Greedy merging using a binary MinHeap as a Priority Queue.
        - Rationale: Extracts two minimum frequency nodes in O(log k) and re-inserts their parent in O(log k). Runs in O(k log k) overall.
        - Alternatives: Repeatedly sorting a list/array of nodes takes O(k^2) time due to element shifting, which was rejected as sub-optimal.

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

    root = heap.extract_min()
    
    # Assert Step 2 Domain Invariant: Root frequency must equal the sum of all character frequencies
    assert root.freq == sum(freq_dict.values()), "Root freq must equal total chars"
    
    return root
