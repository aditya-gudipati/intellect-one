"""
Unit and integration tests for the Huffman Encoding file compression tool.
"""

import os
import sys
import unittest
import tempfile
import zipfile
from collections import Counter

# Add src to the path so we can import modules correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from heap import MinHeap
from huffman import HuffmanNode, build_tree
from codec import generate_codes, encode, decode
from serializer import serialize_tree, deserialize_tree
from fileio import bits_to_bytes, bytes_to_bits, write_compressed, read_compressed


class TestMinHeap(unittest.TestCase):
    """Test cases for the custom MinHeap implementation."""

    def test_insert_and_extract_min(self):
        heap = MinHeap()
        values = [5, 3, 8, 1, 2, 9, 4, 7, 6]
        for v in values:
            heap.insert(v)
            
        self.assertEqual(len(heap), len(values))
        
        extracted = []
        while len(heap) > 0:
            extracted.append(heap.extract_min())
            
        self.assertEqual(extracted, sorted(values))

    def test_extract_min_empty_raises(self):
        heap = MinHeap()
        with self.assertRaises(IndexError):
            heap.extract_min()

    def test_heapify_complex_tie_break(self):
        # Insert HuffmanNode to check tie-breaking via __lt__
        heap = MinHeap()
        node1 = HuffmanNode(freq=5, char='b')
        node2 = HuffmanNode(freq=5, char='a')
        node3 = HuffmanNode(freq=10, char='c')
        
        heap.insert(node3)
        heap.insert(node1)
        heap.insert(node2)
        
        first = heap.extract_min()
        second = heap.extract_min()
        third = heap.extract_min()
        
        self.assertEqual(first.char, 'a')
        self.assertEqual(second.char, 'b')
        self.assertEqual(third.char, 'c')

    def test_heap_extract_ordering(self):
        """1. test_heap_extract_ordering - insert nodes with freq [5,3,8,1], assert extraction order is 1,3,5,8"""
        heap = MinHeap()
        nodes = [
            HuffmanNode(freq=5, char='a'),
            HuffmanNode(freq=3, char='b'),
            HuffmanNode(freq=8, char='c'),
            HuffmanNode(freq=1, char='d')
        ]
        for node in nodes:
            heap.insert(node)
            
        extracted = []
        while len(heap) > 0:
            extracted.append(heap.extract_min().freq)
            
        self.assertEqual(extracted, [1, 3, 5, 8])


class TestHuffmanTree(unittest.TestCase):
    """Test cases for tree construction and HuffmanNode class."""

    def test_build_tree_normal(self):
        freq = {'a': 5, 'b': 9, 'c': 12, 'd': 13, 'e': 16, 'f': 45}
        root = build_tree(freq)
        self.assertIsNotNone(root)
        self.assertEqual(root.freq, 100)

    def test_build_tree_empty(self):
        root = build_tree({})
        self.assertIsNone(root)

    def test_build_tree_single_char(self):
        root = build_tree({'a': 10})
        self.assertIsNotNone(root)
        self.assertEqual(root.char, 'a')
        self.assertEqual(root.freq, 10)
        self.assertIsNone(root.left)
        self.assertIsNone(root.right)


class TestCodec(unittest.TestCase):
    """Test cases for encoding and decoding Huffman bitstrings."""

    def test_generate_codes_normal(self):
        freq = {'a': 5, 'b': 9, 'c': 12}
        root = build_tree(freq)
        codes = generate_codes(root)
        
        # Check that all chars are in codes
        self.assertIn('a', codes)
        self.assertIn('b', codes)
        self.assertIn('c', codes)
        
        # Verify prefix-free property
        for char1, code1 in codes.items():
            for char2, code2 in codes.items():
                if char1 != char2:
                    self.assertFalse(code1.startswith(code2), f"{code1} and {code2} share prefix")

    def test_generate_codes_single_char(self):
        root = build_tree({'a': 10})
        codes = generate_codes(root)
        self.assertEqual(codes, {'a': '0'})

    def test_encode_decode_cycle(self):
        text = "abracadabra"
        freq = Counter(text)
        root = build_tree(freq)
        codes = generate_codes(root)
        
        bitstring = encode(text, codes)
        decoded = decode(bitstring, root)
        
        self.assertEqual(decoded, text)

    def test_encode_decode_single_char(self):
        text = "aaaaaaa"
        freq = Counter(text)
        root = build_tree(freq)
        codes = generate_codes(root)
        
        self.assertEqual(codes, {'a': '0'})
        bitstring = encode(text, codes)
        self.assertEqual(bitstring, "0000000")
        
        decoded = decode(bitstring, root)
        self.assertEqual(decoded, text)

    def test_decode_invalid_bit_raises(self):
        root = build_tree({'a': 5, 'b': 5})
        with self.assertRaises(ValueError):
            decode("01021", root)

    def test_decode_incomplete_bitstring_raises(self):
        # We need a tree with depth > 1 to test split bits
        root = build_tree({'a': 5, 'b': 2, 'c': 2})
        # If we feed it a bitstring that doesn't terminate at a leaf
        with self.assertRaises(ValueError):
            decode("0", root)

    def test_prefix_free_property(self):
        """2. test_prefix_free_property - for any 5-char input, assert no code in generate_codes() is a prefix of another"""
        text = "abcde"
        freq = Counter(text)
        root = build_tree(freq)
        codes = generate_codes(root)
        
        for char1, code1 in codes.items():
            for char2, code2 in codes.items():
                if char1 != char2:
                    self.assertFalse(
                        code1.startswith(code2),
                        f"Code '{code1}' for '{char1}' is prefixed by '{code2}' for '{char2}'"
                    )

    def test_all_equal_frequency_prefix_free(self):
        """7. test_all_equal_frequency_prefix_free - 26 chars freq=10 each, assert prefix-free property"""
        import string
        freq = {char: 10 for char in string.ascii_lowercase}
        root = build_tree(freq)
        codes = generate_codes(root)
        self.assertEqual(len(codes), 26)
        
        for char1, code1 in codes.items():
            for char2, code2 in codes.items():
                if char1 != char2:
                    self.assertFalse(
                        code1.startswith(code2),
                        f"Code '{code1}' for '{char1}' is prefixed by '{code2}' for '{char2}'"
                    )


class TestSerializer(unittest.TestCase):
    """Test cases for tree serialization and deserialization."""

    def test_serialize_deserialize_empty(self):
        bitstring = serialize_tree(None)
        self.assertEqual(bitstring, "")
        root, consumed = deserialize_tree(bitstring)
        self.assertIsNone(root)
        self.assertEqual(consumed, 0)

    def test_serialize_deserialize_single(self):
        node = HuffmanNode(freq=0, char='a')
        bitstring = serialize_tree(node)
        
        # 1 (leaf) + 2-bit length (00) + 8-bit UTF-8 representation of 'a' (97 = 01100001)
        expected = "10001100001"
        self.assertEqual(bitstring, expected)
        
        root, consumed = deserialize_tree(bitstring)
        self.assertIsNotNone(root)
        self.assertEqual(root.char, 'a')
        self.assertIsNone(root.left)
        self.assertIsNone(root.right)
        self.assertEqual(consumed, 11)

    def test_serialize_deserialize_complex(self):
        # Construct a tree manually
        left_leaf = HuffmanNode(freq=0, char='x')
        right_leaf = HuffmanNode(freq=0, char='y')
        root = HuffmanNode(freq=0, char=None, left=left_leaf, right=right_leaf)
        
        bitstring = serialize_tree(root)
        # Expected under UTF-8 serialization: 
        # internal (0) + left (1 + 00 + UTF8(x)) + right (1 + 00 + UTF8(y))
        # 'x' = 120 (01111000)
        # 'y' = 121 (01111001)
        # Expected: "0" + "10001111000" + "10001111001"
        expected = "01000111100010001111001"
        self.assertEqual(bitstring, expected)
        
        reconstructed_root, consumed = deserialize_tree(bitstring)
        self.assertIsNotNone(reconstructed_root)
        self.assertIsNone(reconstructed_root.char)
        self.assertEqual(reconstructed_root.left.char, 'x')
        self.assertEqual(reconstructed_root.right.char, 'y')
        self.assertEqual(consumed, len(expected))


class TestFileIO(unittest.TestCase):
    """Test cases for bit-to-byte packing and binary file writing/reading."""

    def test_bits_to_bytes_and_back(self):
        # 11 bits: requires padding to 16 bits (2 bytes), padding count = 5
        bitstring = "10110000101"
        packed_bytes, padding = bits_to_bytes(bitstring)
        
        self.assertEqual(padding, 5)
        self.assertEqual(len(packed_bytes), 2)
        
        unpacked_bits = bytes_to_bits(packed_bytes, padding)
        self.assertEqual(unpacked_bits, bitstring)

    def test_empty_bits_to_bytes(self):
        packed, padding = bits_to_bytes("")
        self.assertEqual(packed, b"")
        self.assertEqual(padding, 0)
        self.assertEqual(bytes_to_bits(packed, padding), "")

    def test_read_write_cycle_normal(self):
        tree_bits = "0101100001101100010"
        data_bits = "0110011100"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.huf")
            write_compressed(filepath, tree_bits, data_bits)
            
            read_tree, read_data = read_compressed(filepath)
            
            self.assertEqual(read_tree, tree_bits)
            self.assertEqual(read_data, data_bits)

    def test_read_write_cycle_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "empty.huf")
            write_compressed(filepath, "", "")
            
            # Should have created a 0-byte file
            self.assertEqual(os.path.getsize(filepath), 0)
            
            read_tree, read_data = read_compressed(filepath)
            self.assertEqual(read_tree, "")
            self.assertEqual(read_data, "")

    def test_byte_packing_padding(self):
        """4. test_byte_packing_padding - encode a string that produces a non-multiple-of-8 bitstring, assert padding_count > 0, assert decompression is correct"""
        text = "abracadabra"
        freq = Counter(text)
        root = build_tree(freq)
        codes = generate_codes(root)
        bitstring = encode(text, codes)
        
        # Verify it's not a multiple of 8
        self.assertNotEqual(len(bitstring) % 8, 0)
        
        packed, padding = bits_to_bytes(bitstring)
        self.assertGreater(padding, 0)
        
        unpacked_bits = bytes_to_bits(packed, padding)
        self.assertEqual(unpacked_bits, bitstring)
        decoded = decode(unpacked_bits, root)
        self.assertEqual(decoded, text)

    def test_corrupt_header_raises(self):
        """5. test_corrupt_header_raises - write a 3-byte file to disk, call read_compressed(), assert raises ValueError"""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "corrupt.huf")
            # Write a 3-byte malformed file (insufficient for 4-byte tree length)
            with open(filepath, "wb") as f:
                f.write(b"\x00\x05\x00")
            
            with self.assertRaises(ValueError):
                read_compressed(filepath)


class TestIntegrationEndToEnd(unittest.TestCase):
    """End-to-end compression and decompression tests."""

    def assert_compress_decompress(self, original_text: str):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "input.txt")
            compressed_file = os.path.join(tmpdir, "output.huf")
            recovered_file = os.path.join(tmpdir, "recovered.txt")
            
            with open(input_file, "w", encoding="utf-8", newline="") as f:
                f.write(original_text)
                
            # Perform compression
            freq = Counter(original_text)
            root = build_tree(freq)
            codes = generate_codes(root)
            data_bits = encode(original_text, codes)
            tree_bits = serialize_tree(root)
            
            write_compressed(compressed_file, tree_bits, data_bits)
            
            # Perform decompression
            read_tree_bits, read_data_bits = read_compressed(compressed_file)
            reconstructed_root, _ = deserialize_tree(read_tree_bits)
            decoded_text = decode(read_data_bits, reconstructed_root)
            
            with open(recovered_file, "w", encoding="utf-8", newline="") as f:
                f.write(decoded_text)
                
            with open(recovered_file, "r", encoding="utf-8", newline="") as f:
                recovered_text = f.read()
                
            self.assertEqual(recovered_text, original_text)

    def test_end_to_end_typical(self):
        text = "The quick brown fox jumps over the lazy dog! 1234567890. ABRA CADABRA."
        self.assert_compress_decompress(text)

    def test_end_to_end_empty(self):
        self.assert_compress_decompress("")

    def test_end_to_end_single_char(self):
        self.assert_compress_decompress("a")

    def test_end_to_end_single_char_repeating(self):
        self.assert_compress_decompress("bbbbbbbbbbbbbbbb")

    def test_end_to_end_all_256_ascii(self):
        # We construct a text containing all 256 ASCII characters
        text = "".join(chr(i) for i in range(256))
        self.assert_compress_decompress(text)

    def test_equal_frequency(self):
        """3. test_equal_frequency - build_tree({'a':10,'b':10,'c':10,'d':10,'e':10}), assert valid tree + correct round-trip"""
        freq = {'a': 10, 'b': 10, 'c': 10, 'd': 10, 'e': 10}
        root = build_tree(freq)
        self.assertIsNotNone(root)
        self.assertEqual(root.freq, 50)
        
        codes = generate_codes(root)
        text = "abcde"
        bitstring = encode(text, codes)
        decoded = decode(bitstring, root)
        self.assertEqual(decoded, text)

    def test_large_file_roundtrip(self):
        """6. test_large_file_roundtrip - generate a 50KB string of random printable ASCII, assert byte-identical round-trip"""
        import random
        import string
        random.seed(42)
        # Generate 50KB of random printable ASCII characters
        text = "".join(random.choices(string.printable, k=50 * 1024))
        self.assert_compress_decompress(text)

    def test_single_byte_file(self):
        """8. test_single_byte_file - compress/decompress a 1-byte file ('z'), assert identity"""
        self.assert_compress_decompress("z")


class TestDocxSupport(unittest.TestCase):
    """Test cases for docx reader and Unicode Huffman serialization."""

    def test_extract_text_from_docx_valid(self):
        # Create a mock docx in memory/temp file
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = tmp.name
            
        try:
            with zipfile.ZipFile(tmp_path, "w") as docx:
                docx.writestr("word/document.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:t>Hello world from docx!</w:t>
    </w:p>
    <w:p>
      <w:t>This is the second paragraph.</w:t>
    </w:p>
  </w:body>
</w:document>""")
            
            from docx_reader import extract_text_from_docx
            text = extract_text_from_docx(tmp_path)
            self.assertEqual(text, "Hello world from docx!\nThis is the second paragraph.")
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_extract_text_from_docx_invalid(self):
        # Create a non-docx zip file
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            with zipfile.ZipFile(tmp_path, "w") as docx:
                docx.writestr("not_document.xml", "some text")
            from docx_reader import extract_text_from_docx
            with self.assertRaises(ValueError):
                extract_text_from_docx(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_unicode_serialize_deserialize(self):
        # Test 3-byte unicode character: ₹
        node = HuffmanNode(freq=0, char='₹')
        bitstring = serialize_tree(node)
        
        # Expected: 1 (leaf) + 10 (3 bytes) + UTF-8 of ₹ (e2 82 b9)
        # e2: 11100010
        # 82: 10000010
        # b9: 10111001
        expected = "110111000101000001010111001"
        self.assertEqual(bitstring, expected)
        
        root, consumed = deserialize_tree(bitstring)
        self.assertIsNotNone(root)
        self.assertEqual(root.char, '₹')
        self.assertEqual(consumed, 27)

    def test_emoji_serialize_deserialize(self):
        # Test 4-byte unicode character: 😊
        node = HuffmanNode(freq=0, char='😊')
        bitstring = serialize_tree(node)
        
        # Expected: 1 (leaf) + 11 (4 bytes) + UTF-8 of 😊 (f0 9f 98 8a)
        # f0: 11110000
        # 9f: 10011111
        # 98: 10011000
        # 8a: 10001010
        expected = "11111110000100111111001100010001010"
        self.assertEqual(bitstring, expected)
        
        root, consumed = deserialize_tree(bitstring)
        self.assertIsNotNone(root)
        self.assertEqual(root.char, '😊')
        self.assertEqual(consumed, 35)

    def test_docx_compression_integration(self):
        # Create docx file with unicode characters
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            with zipfile.ZipFile(tmp_path, "w") as docx:
                docx.writestr("word/document.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:t>Virat Kohli earned ₹634 crore 😊.</w:t>
    </w:p>
  </w:body>
</w:document>""")
            
            comp_path = tmp_path + ".huf"
            recovered_path = tmp_path + "_rec.txt"
            
            # Run CLI compress and decompress
            from main import run_compress, run_decompress
            run_compress(tmp_path, comp_path, show_stats=False)
            run_decompress(comp_path, recovered_path, show_stats=False, verify_path=tmp_path)
            
            with open(recovered_path, "r", encoding="utf-8") as f:
                recovered_text = f.read()
                
            self.assertEqual(recovered_text, "Virat Kohli earned ₹634 crore 😊.")
        finally:
            for p in (tmp_path, comp_path, recovered_path):
                if os.path.exists(p):
                    os.remove(p)


class TestBinarySupport(unittest.TestCase):
    """Test cases for binary file (PDF, images) byte-for-byte compression support."""

    def test_binary_roundtrip_bytes(self):
        # Generate arbitrary binary data with bytes 0 to 255
        raw_bytes = bytes(range(256)) * 4 + b"\x00\xff\x7f\x80"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = os.path.join(tmpdir, "input.bin")
            comp_path = os.path.join(tmpdir, "output.huf")
            recovered_path = os.path.join(tmpdir, "recovered.bin")
            
            with open(input_path, "wb") as f:
                f.write(raw_bytes)
                
            from main import run_compress, run_decompress
            run_compress(input_path, comp_path, show_stats=False)
            run_decompress(comp_path, recovered_path, show_stats=False, verify_path=input_path)
            
            with open(recovered_path, "rb") as f:
                recovered_data = f.read()
                
            self.assertEqual(recovered_data, raw_bytes)


if __name__ == "__main__":
    unittest.main()
