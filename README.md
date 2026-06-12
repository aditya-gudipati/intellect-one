# Huffman Encoding File Compression Tool

A complete, modular, and dependency-free Huffman encoding file compression and decompression tool built in Python 3.10+.

---

## 1. Problem Definition Document (PDD)

### Problem Statement
Lossless text compression of standard text files (.txt) utilizing the Huffman Coding algorithm. The tool must compress files by assigning shorter variable-length binary codes to more frequent characters and serialize the tree and data into a compact binary format, ensuring exact byte-identical recovery during decompression.

### Scope & Preconditions
- **Scope**: Serves as a modular, pure-Python library and CLI utility for encoding and decoding standard text.
- **Preconditions**: The input to be compressed must be a valid text file. Characters must map to 8-bit ASCII characters (0–255) for serialization support.

### Expected Behavior & Constraints
- **Compression**: Given an input text file, output a compressed binary file containing the serialized prefix tree and encoded bitstream.
- **Decompression**: Given a compressed binary file, extract the tree and bitstream, and output a reconstructed text file.
- **Constraints**: No standard library priority queue modules (like `heapq`) can be used. Code generation, tree building, and serialization must be strictly iterative (no recursion) to prevent stack overflow on deep/skewed trees.

### Assumptions
- The input file is readable and fit into memory.
- The compressed file is not modified or corrupted unless testing corrupt format handlers.

### Edge Cases Table
| Edge Case | Description | Expected Tool Behavior |
| :--- | :--- | :--- |
| **Empty File** | File size is 0 bytes. | Writes a 0-byte `.huf` file; decompressing it recovers an empty file. |
| **Single-Char File** | File contains exactly 1 character (e.g., `"z"`). | Assigns code `"0"`, serializes tree, and correctly decompresses. |
| **Single-Unique-Char Repeating** | Repeating identical char (e.g., `"aaaaaaa"`). | Assigns code `"0"`, encodes to a sequence of zeros, and decompresses. |
| **All-256 ASCII** | Contains all 256 ASCII characters with varying frequencies. | Reconstructs a full tree, correctly encodes and deserializes. |
| **Equal Frequency** | Multiple characters with identical frequencies. | Breaks ties consistently using custom `__lt__` comparisons. |
| **Large File (>1MB)** | File size exceeding 1 megabyte. | Processes without stack overflow or memory exhaustion. |

### Success Criteria
- **Byte-Identical Round-Trip**: The decompressed output file must be identical to the original input file byte-for-byte.
- **Compression Ratio**: The compression ratio (compressed size / original size) must be `< 1` (i.e. space savings `> 0%`) for typical English text files.

---

## 2. Solution Documentation Report (SDR)
- **What was built**: A command-line file compression utility utilizing custom binary MinHeap and Huffman trees with zero external dependencies.
- **How it works**: Analyzes character frequencies, builds a binary MinHeap to construct an optimal Huffman tree, generates prefix-free codes using iterative DFS, packs the tree structure and encoded data into a custom binary layout, and writes to disk. Decompression reads the custom header, reconstructs the tree, and traverses it bit-by-bit to restore the original text.
- **Why it is correct**: Proved via a comprehensive unit test suite validating edge cases (empty files, single characters, full 256-ASCII set) and asserting byte-by-byte equivalence for all compression-decompression cycles.

---

## 3. Project Structure & Architecture Overview
- [heap.py](file:///c:/Users/adity/intellect_internship/src/heap.py) — A custom, array-based binary minimum heap implemented from scratch to act as a priority queue.
- [huffman.py](file:///c:/Users/adity/intellect_internship/src/huffman.py) — Defines the `HuffmanNode` tree nodes and implements the greedy tree construction algorithm.
- [codec.py](file:///c:/Users/adity/intellect_internship/src/codec.py) — Generates prefix-free variable-length codes and handles text encoding and decoding.
- [serializer.py](file:///c:/Users/adity/intellect_internship/src/serializer.py) — Implements recursion-free preorder serialization and deserialization of the Huffman tree.
- [fileio.py](file:///c:/Users/adity/intellect_internship/src/fileio.py) — Manages binary packing, padding counts, and custom binary structure reading/writing.
- [main.py](file:///c:/Users/adity/intellect_internship/src/main.py) — CLI application interface providing `compress`, `decompress`, and `test` commands.

---

## 4. Performance & Complexity Analysis

For a mathematical analysis of the time and space complexity of each operation, please refer to [COMPLEXITY.md](file:///c:/Users/adity/intellect_internship/COMPLEXITY.md).

### Compression Ratio Table
Below is the performance data gathered by running the tool on three sample text files:

| File Name | Description | Original Size (Bytes) | Compressed Size (Bytes) | Space Saved (%) | Compression Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `src/sample_short.txt` | Short description of Huffman coding | 244 | 178 | 27.05% | 1.37x |
| `src/input.txt` | Standard project sample file | 1260 | 766 | 39.21% | 1.64x |
| `src/sample_long.txt` | Repeating "quick brown fox" sentences | 1800 | 1072 | 40.44% | 1.68x |

---

## 5. Installation & Usage

### Installation
No external libraries are required. Clone the repository and run using Python 3.10+:
```bash
git clone https://github.com/aditya-gudipati/intellect-internship.git
cd intellect-internship
```

### Usage Examples

#### Compress a file
Compress a text file into a `.huf` binary file:
```bash
python src/main.py compress src/input.txt src/output.huf
```

Compress a file and print statistics:
```bash
python src/main.py compress src/input.txt src/output.huf --stats
```

#### Decompress a file
Decompress a `.huf` binary file back into its original text format:
```bash
python src/main.py decompress src/output.huf src/recovered.txt
```

Decompress and print decompression statistics:
```bash
python src/main.py decompress src/output.huf src/recovered.txt --stats
```

Decompress and verify byte-for-byte correctness against original:
```bash
python src/main.py decompress src/output.huf src/recovered.txt --verify src/input.txt
```

#### Running Standalone CLI Tests
Run the built-in quick integration tests:
```bash
python src/main.py test
```

#### Running the Unittest Suite
Run the comprehensive test suite:
```bash
python -m unittest discover -s tests
```

---

## 6. References
- **CLRS Chapter 16.3**: Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press. Section 16.3 discusses the design and correctness of Huffman codes.
- **Huffman 1952**: Huffman, D. A. (1952). A Method for the Construction of Minimum-Redundancy Codes. *Proceedings of the IRE*, 40(9), 1098-1101.
