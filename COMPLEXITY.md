# Computational Complexity Analysis

This document details the time complexity, space complexity, and real-world impact of each primary operation in the Huffman Encoding compression tool, matching the Intellect Framework Step 7 specifications.

## Complexity Breakdown Table

| Operation | Time Complexity | Space Complexity | Real-World Impact |
| :--- | :--- | :--- | :--- |
| **Frequency Table Creation** | $O(n)$ | $O(k)$ | Reads the input file and tallies character frequencies. A single linear pass scales efficiently with arbitrarily large files. |
| **Heap Build (Initialization)** | $O(k \log k)$ | $O(k)$ | Populates the priority queue (MinHeap) with initial character leaf nodes. Highly optimal for typical alphabets (e.g., $k \le 256$ for ASCII). |
| **Tree Construction** | $O(k \log k)$ | $O(k)$ | Merges leaf nodes into a full binary prefix tree. Restricting to iterative merges ensures execution stability. |
| **Code Generation (DFS)** | $O(k)$ | $O(k)$ | Traverses the tree to generate prefix-free variable-length codes. An iterative stack-based DFS guarantees no call stack overflow even for skewed trees. |
| **Encode (Text to Bitstring)** | $O(n)$ | $O(n)$ | Converts input text into a bitstring via fast dictionary lookup, running in linear time. |
| **Bit Packing (Bits to Bytes)**| $O(b)$ | $O(b)$ | Groups bit sequences into 8-bit bytes using memory-efficient Python `bytearray` operations for compact binary serialization. |
| **Decode (Bitstring to Text)**| $O(b)$ | $O(n)$ | Traverses the Huffman tree bit-by-bit to reconstruct the original text. Linear runtime relative to bit length $b$. |
| **Overall** | $O(n + k \log k)$| $O(n + k)$ | Standard linear-time scaling relative to file length $n$, dominated by the single-pass reading and writing steps. |

### Definition of Variables
- $n$: The number of characters in the input file text.
- $k$: The number of unique characters in the input file text (for ASCII, $k \le 256$).
- $b$: The length of the generated Huffman encoded bitstring ($b \le n$ for typical compression).
