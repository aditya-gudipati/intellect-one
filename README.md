# Huffman Encoding File Compression Tool

A complete, modular, and dependency-free Huffman encoding file compression and decompression tool built in Python 3.10+.

## Project Structure
- `src/heap.py` — A custom, array-based binary minimum heap implemented from scratch (replaces standard `heapq` / `PriorityQueue`).
- `src/huffman.py` — `HuffmanNode` class and the tree builder using the custom heap. Handles all edge cases (like repeating single-character inputs).
- `src/codec.py` — Iterative depth-first search (DFS) code generation, encoding, and decoding algorithms.
- `src/serializer.py` — Preorder tree serialization/deserialization logic (`0` for internal nodes, `1` + 8-bit ASCII representations for leaf nodes) using an iterative stack approach.
- `src/fileio.py` — Memory-efficient byte-packing using Python's `bytearray`, custom headers (uint16 big-endian tree length), and binary file reading/writing.
- `src/main.py` — CLI entry point using `argparse`.
- `tests/test_huffman.py` — Comprehensive unit and integration test suite.

---

## Features
- **Zero standard-library dependencies** for heap logic (built entirely from scratch).
- **No recursion** in code generation, tree building, or tree serialization/deserialization to guarantee compliance with high/deep tree requirements without exceeding Python's call-stack limit.
- **Windows-safe I/O** employing `newline=""` to prevent auto-translation of CRLF newlines.
- **Detailed statistics** displaying original size, compressed size, space saved, and compression ratio.
- Handles empty files, single-character inputs, and files containing all 256 ASCII characters correctly.

---

## Usage

### Compression
Compress a text file into a `.huf` binary file:
```bash
python src/main.py compress input.txt output.huf
```

Compress a file and print statistics:
```bash
python src/main.py compress input.txt output.huf --stats
```

### Decompression
Decompress a `.huf` binary file back into its original text format:
```bash
python src/main.py decompress output.huf recovered.txt
```

---

## Running Tests
Run the comprehensive test suite using Python's built-in `unittest` module:
```bash
python -m unittest discover -s tests
```
