"""
This module implements an array-based MinHeap from scratch.
It acts as a priority queue for building the Huffman tree.
"""

from typing import Any, List

class MinHeap:
    """
    An array-based MinHeap implementation.
    The elements stored in this heap must support the '<' operator (via __lt__).
    """
    def __init__(self) -> None:
        """Initialize an empty MinHeap."""
        self.heap: List[Any] = []

    def __len__(self) -> int:
        """Return the number of elements in the heap."""
        return len(self.heap)

    def insert(self, node: Any) -> None:
        """
        Insert a node into the heap and bubble it up to the correct position.
        """
        self.heap.append(node)
        self.heapify_up()

    def extract_min(self) -> Any:
        """
        Remove and return the minimum node from the heap.
        Raises an IndexError if the heap is empty.
        """
        if not self.heap:
            raise IndexError("extract_min from an empty heap")
        
        min_node = self.heap[0]
        last_node = self.heap.pop()
        
        if self.heap:
            self.heap[0] = last_node
            self.heapify_down()
            
        return min_node

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
