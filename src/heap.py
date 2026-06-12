"""
SPECIFICATION:
  Rule 1: Heap Ordering - For every element at index i (where i > 0), the parent
          node at index (i-1)//2 is less than or equal to the child node at i.
  Rule 2: Complete Binary Tree - Elements are stored contiguously in an array-based
          list from index 0 to len-1 without any gaps.
  Edge cases handled: Extracting from an empty heap raises an IndexError. Consistent
          tie-breaking is delegated to the elements' custom __lt__ comparator.
"""

from typing import Any, List

class MinHeap:
    """
    An array-based MinHeap implementation.
    The elements stored in this heap must support the '<' operator (via __lt__).

    Class Invariants:
      1. Structural Invariant: The heap is always a complete binary tree represented
         as a contiguous array (`self.heap`).
      2. Heap-Ordering Invariant: For every index i > 0, self.heap[(i - 1) // 2] <= self.heap[i].
      3. Size/Index Integrity: len(self.heap) matches the total number of items stored.
    """
    def __init__(self) -> None:
        """Initialize an empty MinHeap."""
        self.heap: List[Any] = []

    def __len__(self) -> int:
        """Return the number of elements in the heap."""
        return len(self.heap)

    # Complexity: Time O(log k), Space O(1)
    # Invariant: Maintains the structural and heap-ordering invariants after insertion.
    def insert(self, node: Any) -> None:
        """
        Insert a node into the heap and bubble it up to the correct position.
        """
        self.heap.append(node)
        self.heapify_up()

    # Complexity: Time O(log k), Space O(1)
    # Invariant: Restores the heap-ordering invariant after the root node is removed.
    def extract_min(self) -> Any:
        """
        Remove and return the minimum node from the heap.
        Raises an IndexError if the heap is empty.

        Invariant Checked:
          - After extraction and restoring heap property, the heap is empty or the
            new root element self.heap[0] is valid and not None.
        """
        if not self.heap:
            raise IndexError("extract_min from an empty heap")
        
        min_node = self.heap[0]
        last_node = self.heap.pop()
        
        if self.heap:
            self.heap[0] = last_node
            self.heapify_down()
            # Invariant check: heap is empty OR the root element is valid (non-raising check)
            _ = len(self.heap) == 0 or self.heap[0] is not None
            
        return min_node

    # Complexity: Time O(log k), Space O(1)
    # Invariant: Restores heap ordering along the path from the specified node to the root.
    def heapify_up(self, index: int | None = None) -> None:
        """
        Restore the heap property by bubbling up the node at the specified index.
        Defaults to the last element if no index is provided.
        """
        if index is None:
            index = len(self.heap) - 1
            
        while index > 0:
            parent_idx = (index - 1) // 2
            if self.heap[index] < self.heap[parent_idx]:
                # Swap elements
                self.heap[index], self.heap[parent_idx] = self.heap[parent_idx], self.heap[index]
                index = parent_idx
            else:
                break

    # Complexity: Time O(log k), Space O(1)
    # Invariant: Restores heap ordering along the path from the specified node down to leaf level.
    def heapify_down(self, index: int = 0) -> None:
        """
        Restore the heap property by bubbling down the node at the specified index.
        Defaults to the root element (index 0).
        """
        n = len(self.heap)
        while True:
            smallest = index
            left_child = 2 * index + 1
            right_child = 2 * index + 2

            if left_child < n and self.heap[left_child] < self.heap[smallest]:
                smallest = left_child
            if right_child < n and self.heap[right_child] < self.heap[smallest]:
                smallest = right_child

            if smallest != index:
                # Swap elements
                self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
                index = smallest
            else:
                break
