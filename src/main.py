"""
CLI entry point for the Huffman Encoding file compression tool.
Provides commands to compress and decompress files, along with statistics tracking.
"""

import argparse
import os
import sys
from collections import Counter

from huffman import build_tree
from codec import generate_codes, encode, decode
from serializer import deserialize_tree, serialize_tree
from fileio import write_compressed, read_compressed

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
    # 1. Read input text (handling potential empty file)
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


def run_decompress(input_path: str, output_path: str) -> None:
    """
    Read compressed file, deserialize tree, decode bitstring,
    and write the original text.
    """
    # 1. Read compressed file format
    tree_bits, data_bits = read_compressed(input_path)

    # 2. Deserialize tree
    root, _ = deserialize_tree(tree_bits)

    # 3. Decode bitstring
    decoded_text = decode(data_bits, root)

    # 4. Write output text
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(decoded_text)


def main() -> None:
    """Parse command line arguments and execute the compression/decompression flow."""
    parser = argparse.ArgumentParser(
        description="Modular Huffman Encoding file compression and decompression tool."
    )
    
    parser.add_argument(
        "mode",
        choices=["compress", "decompress"],
        help="Execution mode: 'compress' or 'decompress'."
    )
    parser.add_argument(
        "input",
        help="Path to the input file."
    )
    parser.add_argument(
        "output",
        help="Path to the output file."
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print compression stats (only applicable for 'compress' mode)."
    )
    
    args = parser.parse_args()
    
    if args.mode == "compress":
        run_compress(args.input, args.output, args.stats)
    elif args.mode == "decompress":
        if args.stats:
            print("Warning: --stats flag is only applicable in 'compress' mode.", file=sys.stderr)
        run_decompress(args.input, args.output)


if __name__ == "__main__":
    main()
