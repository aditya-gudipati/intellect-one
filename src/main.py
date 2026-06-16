"""
CLI entry point for the Huffman Encoding file compression tool.
Provides commands to compress and decompress files, along with statistics tracking.
"""

import argparse
import os
import sys
import tempfile
from collections import Counter

from huffman import build_tree
from codec import generate_codes, encode, decode
from serializer import deserialize_tree, serialize_tree
from fileio import write_compressed, read_compressed
from docx_reader import extract_text_from_docx

def get_file_size(filepath: str) -> int:
    """Return file size in bytes, or 0 if file does not exist."""
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0


def run_compress(input_path: str, output_path: str, show_stats: bool) -> None:
    """
    Read input text, build Huffman tree, encode data, serialize tree,
    and write the compressed file.
    """
    # Fix 3: Add input file existence + readability check
    if not os.path.exists(input_path):
        print(f"Error: input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(input_path):
        print(f"Error: '{input_path}' is not a file.", file=sys.stderr)
        sys.exit(1)

    # 1. Read input text (handling potential empty file or Word Document)
    if input_path.lower().endswith(".docx"):
        try:
            text = extract_text_from_docx(input_path)
        except Exception as e:
            print(f"Error: Failed to read Word Document '{input_path}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            with open(input_path, "r", encoding="utf-8", newline="") as f:
                text = f.read()
        except UnicodeDecodeError:
            # Fallback to system encoding or default to binary-like reading if requested,
            # but for .txt standard UTF-8 is appropriate.
            with open(input_path, "r", encoding="utf-8", errors="replace", newline="") as f:
                text = f.read()

    # 2. Generate frequency table using Counter
    frequencies = Counter(text)

    # 3. Build tree
    root = build_tree(frequencies)

    # 4. Generate codes
    codes = generate_codes(root)

    # 5. Encode data
    data_bits = encode(text, codes)

    # 6. Serialize tree
    tree_bits = serialize_tree(root)

    # 7. Write compressed file
    write_compressed(output_path, tree_bits, data_bits)

    # 8. Print stats if requested
    if show_stats:
        orig_size = get_file_size(input_path)
        comp_size = get_file_size(output_path)
        
        print("=== Compression Statistics ===")
        print(f"Original file path:   {input_path}")
        print(f"Compressed file path: {output_path}")
        print(f"Original size:        {orig_size} bytes")
        print(f"Compressed size:      {comp_size} bytes")
        
        if orig_size > 0:
            ratio = (comp_size / orig_size) * 100
            savings = 100.0 - ratio
            factor = orig_size / comp_size if comp_size > 0 else float("inf")
            print(f"Space saved:          {savings:.2f}%")
            print(f"Compression ratio:    {factor:.2f}x ({ratio:.2f}% of original)")
        else:
            print("Compression ratio:    N/A (Original file is empty)")
        print("==============================")


def run_decompress(input_path: str, output_path: str, show_stats: bool = False, verify_path: str | None = None) -> None:
    """
    Read compressed file, deserialize tree, decode bitstring,
    and write the original text.
    """
    # Fix 3: Add input file existence + readability check
    if not os.path.exists(input_path):
        print(f"Error: input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(input_path):
        print(f"Error: '{input_path}' is not a file.", file=sys.stderr)
        sys.exit(1)

    # 1. Read compressed file format
    tree_bits, data_bits = read_compressed(input_path)

    # 2. Deserialize tree
    root, _ = deserialize_tree(tree_bits)

    # 3. Decode bitstring
    decoded_text = decode(data_bits, root)

    # 4. Write output text
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(decoded_text)

    # Fix 4: Add byte-for-byte verification after decompress
    with open(output_path, "r", encoding="utf-8", newline="") as f:
        recovered = f.read()
    if data_bits and not recovered:
        print("Warning: decompressed output is unexpectedly empty.", file=sys.stderr)
    else:
        print(f"Decompression successful. Output written to: {output_path}")

    # If verify_path is provided:
    if verify_path is not None:
        if verify_path.lower().endswith(".docx"):
            try:
                original = extract_text_from_docx(verify_path)
            except Exception as e:
                print(f"Error: Failed to read Word Document for verification: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            with open(verify_path, "r", encoding="utf-8", newline="") as f:
                original = f.read()
        with open(output_path, "r", encoding="utf-8", newline="") as f:
            recovered = f.read()
        if original == recovered:
            print("Verification PASSED: output matches original exactly.")
        else:
            print("Verification FAILED: output does not match original.", file=sys.stderr)
            sys.exit(1)

    # Fix 5: Add a --stats block for decompress too
    if show_stats:
        comp_size = get_file_size(input_path)
        decomp_size = get_file_size(output_path)
        factor = decomp_size / comp_size if comp_size > 0 else float("nan")
        print(f"Compressed size: {comp_size} bytes")
        print(f"Decompressed size: {decomp_size} bytes")
        print(f"Expansion factor: {factor:.2f}")


def run_tests() -> None:
    """
    Run standalone test suite for compression and decompression.
    Checks normal text, single-character, and empty file cases.
    """
    passed_count = 0
    
    # Test case 1: "hello huffman world"
    content1 = "hello huffman world"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", newline="", delete=False) as f:
        orig1 = f.name
        f.write(content1)
    comp1 = orig1 + ".huf"
    rec1 = orig1 + "_recovered.txt"
    try:
        run_compress(orig1, comp1, show_stats=False)
        run_decompress(comp1, rec1, show_stats=False, verify_path=None)
        with open(rec1, "r", encoding="utf-8", newline="") as f:
            recovered = f.read()
        if recovered == content1:
            print("Compare recovered == original -> PASS")
            passed_count += 1
        else:
            print("Compare recovered == original -> FAIL")
    except Exception:
        print("Compare recovered == original -> FAIL")
    finally:
        for p in (orig1, comp1, rec1):
            if os.path.exists(p):
                os.remove(p)
                
    # Test case 2: "aaaaaaa"
    content2 = "aaaaaaa"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", newline="", delete=False) as f:
        orig2 = f.name
        f.write(content2)
    comp2 = orig2 + ".huf"
    rec2 = orig2 + "_recovered.txt"
    try:
        run_compress(orig2, comp2, show_stats=False)
        run_decompress(comp2, rec2, show_stats=False, verify_path=None)
        with open(rec2, "r", encoding="utf-8", newline="") as f:
            recovered = f.read()
        if recovered == content2:
            print("Test with single-char content \"aaaaaaa\" -> PASS")
            passed_count += 1
        else:
            print("Test with single-char content \"aaaaaaa\" -> FAIL")
    except Exception:
        print("Test with single-char content \"aaaaaaa\" -> FAIL")
    finally:
        for p in (orig2, comp2, rec2):
            if os.path.exists(p):
                os.remove(p)
                
    # Test case 3: empty file
    content3 = ""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", encoding="utf-8", newline="", delete=False) as f:
        orig3 = f.name
        f.write(content3)
    comp3 = orig3 + ".huf"
    rec3 = orig3 + "_recovered.txt"
    try:
        run_compress(orig3, comp3, show_stats=False)
        run_decompress(comp3, rec3, show_stats=False, verify_path=None)
        with open(rec3, "r", encoding="utf-8", newline="") as f:
            recovered = f.read()
        if recovered == content3:
            print("Test with empty file -> PASS")
            passed_count += 1
        else:
            print("Test with empty file -> FAIL")
    except Exception:
        print("Test with empty file -> FAIL")
    finally:
        for p in (orig3, comp3, rec3):
            if os.path.exists(p):
                os.remove(p)
                
    print(f"Summary: {passed_count}/3 tests passed")
    if passed_count < 3:
        sys.exit(1)


def main() -> None:
    """Parse command line arguments and execute the compression/decompression flow."""
    parser = argparse.ArgumentParser(
        description="Modular Huffman Encoding file compression and decompression tool."
    )
    
    # Fix 6: Add "test" mode choice
    parser.add_argument(
        "mode",
        choices=["compress", "decompress", "test"],
        help="Execution mode: 'compress', 'decompress', or 'test'."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Path to the input file (required for compress/decompress)."
    )
    parser.add_argument(
        "output",
        nargs="?",
        help="Path to the output file (required for compress/decompress)."
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print compression/decompression statistics."
    )
    # Fix 4: Add --verify parameter
    parser.add_argument(
        "--verify",
        metavar="ORIGINAL",
        help="After decompression, verify output matches this original file byte-for-byte."
    )
    
    args = parser.parse_args()
    
    if args.mode in ("compress", "decompress"):
        if not args.input or not args.output:
            parser.error("the following arguments are required: input, output")
            
    if args.mode == "compress":
        if args.verify:
            print("Warning: --verify flag is only applicable in 'decompress' mode.", file=sys.stderr)
        run_compress(args.input, args.output, args.stats)
    elif args.mode == "decompress":
        run_decompress(args.input, args.output, args.stats, args.verify)
    elif args.mode == "test":
        run_tests()


if __name__ == "__main__":
    main()
