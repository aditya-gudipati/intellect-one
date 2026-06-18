import http.server
import socketserver
import json
import os
import sys
import base64
import tempfile
import email
from collections import Counter

# Add current directory to path so we can import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import local Huffman modules
from huffman import build_tree
from codec import generate_codes, encode, decode
from serializer import deserialize_tree, serialize_tree
from fileio import write_compressed, read_compressed
from docx_reader import extract_text_from_docx
from main import run_compress, run_decompress

PORT = 8000

class HuffmanHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Override to log cleanly to stdout
        sys.stdout.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format%args))

    def do_GET(self):
        # Serve static frontend files
        path = self.path
        if path in ('/', '/index.html'):
            self.serve_file(os.path.join(current_dir, 'index.html'), 'text/html')
        elif path == '/index.css':
            self.serve_file(os.path.join(current_dir, 'index.css'), 'text/css')
        elif path == '/index.js':
            self.serve_file(os.path.join(current_dir, 'index.js'), 'application/javascript')
        else:
            self.send_error(404, "File Not Found")

    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")

    def do_POST(self):
        if self.path == '/api/process':
            self.handle_api_process()
        else:
            self.send_error(404, "API endpoint not found")

    def handle_api_process(self):
        try:
            # 1. Parse Multipart Form Data
            content_type = self.headers.get('Content-Type')
            if not content_type or 'multipart/form-data' not in content_type:
                self.send_json_error("Content-Type must be multipart/form-data", 400)
                return

            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_json_error("Empty request body", 400)
                return

            body = self.rfile.read(content_length)

            # Build mock email message to parse boundary parts
            msg_bytes = f"Content-Type: {content_type}\r\n\r\n".encode('utf-8') + body
            msg = email.message_from_bytes(msg_bytes)

            parts = {}
            for part in msg.walk():
                disposition = part.get('Content-Disposition', '')
                if not disposition:
                    continue
                
                # Parse content-disposition key-value pairs
                params = {}
                for item in disposition.split(';'):
                    if '=' in item:
                        k, v = item.strip().split('=', 1)
                        params[k.lower()] = v.strip('"')

                name = params.get('name')
                if not name:
                    continue

                filename = params.get('filename')
                if filename is not None:
                    file_data = part.get_payload(decode=True)
                    parts[name] = {
                        'filename': filename,
                        'data': file_data
                    }
                else:
                    parts[name] = part.get_payload(decode=True).decode('utf-8').strip()

            # Validate fields
            if 'file' not in parts:
                self.send_json_error("Missing 'file' field", 400)
                return
            if 'mode' not in parts:
                self.send_json_error("Missing 'mode' field", 400)
                return

            file_info = parts['file']
            mode = parts['mode']
            orig_filename = file_info['filename']
            file_data = file_info['data']

            # 2. Setup temp files for processing
            with tempfile.TemporaryDirectory() as tmpdir:
                # Retain original suffix so docx reader or file extensions check correctly
                base, ext = os.path.splitext(orig_filename)
                temp_in = os.path.join(tmpdir, f"input{ext}")
                
                with open(temp_in, "wb") as f:
                    f.write(file_data)

                if mode == 'compress':
                    temp_out = os.path.join(tmpdir, "output.huf")
                    
                    # Run compression
                    try:
                        run_compress(temp_in, temp_out, show_stats=False)
                    except SystemExit:
                        self.send_json_error("Compression failed. Please make sure the input file is readable and valid.", 400)
                        return
                    
                    # Read compressed data
                    with open(temp_out, "rb") as f:
                        compressed_data = f.read()

                    # Calculate stats
                    orig_size = len(file_data)
                    proc_size = len(compressed_data)
                    savings = (1.0 - (proc_size / orig_size)) * 100 if orig_size > 0 else 0.0
                    ratio = orig_size / proc_size if proc_size > 0 else 0.0

                    # Extract character frequencies
                    if orig_filename.lower().endswith(".docx"):
                        try:
                            text = extract_text_from_docx(temp_in)
                        except Exception:
                            text = file_data.decode('utf-8', errors='replace')
                    else:
                        text = file_data.decode('utf-8', errors='replace')

                    frequencies = Counter(text)
                    # Fetch top 10 most common characters
                    top_frequencies = frequencies.most_common(10)

                    response_data = {
                        "success": True,
                        "filename": f"{base}.huf",
                        "content_base64": base64.b64encode(compressed_data).decode('utf-8'),
                        "stats": {
                            "orig_size": orig_size,
                            "proc_size": proc_size,
                            "savings": savings,
                            "ratio": ratio,
                            "frequencies": top_frequencies
                        }
                    }

                elif mode == 'decompress':
                    temp_out = os.path.join(tmpdir, "output.txt")
                    
                    # Run decompression
                    try:
                        run_decompress(temp_in, temp_out, show_stats=False)
                    except SystemExit:
                        self.send_json_error("Decompression failed. Please make sure the uploaded file is a valid .huf compressed file.", 400)
                        return
                    
                    # Read decompressed data
                    with open(temp_out, "rb") as f:
                        decompressed_data = f.read()

                    # Calculate stats
                    comp_size = len(file_data)
                    decomp_size = len(decompressed_data)
                    factor = decomp_size / comp_size if comp_size > 0 else 0.0

                    # If the file originally was compressed from docx, we output text.
                    # Standard decompression restores raw bytes written during compression.
                    response_data = {
                        "success": True,
                        "filename": f"{base}_recovered.txt",
                        "content_base64": base64.b64encode(decompressed_data).decode('utf-8'),
                        "stats": {
                            "comp_size": comp_size,
                            "decomp_size": decomp_size,
                            "factor": factor
                        }
                    }
                else:
                    self.send_json_error("Invalid mode. Must be 'compress' or 'decompress'", 400)
                    return

                self.send_json_response(response_data)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.send_json_error(f"Error processing file: {e}", 500)

    def send_json_response(self, data, status_code=200):
        try:
            response_bytes = json.dumps(data).encode('utf-8')
            self.send_response(status_code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(response_bytes))
            self.end_headers()
            self.wfile.write(response_bytes)
        except Exception as e:
            sys.stderr.write(f"Error sending JSON response: {e}\n")

    def send_json_error(self, message, status_code=500):
        self.send_json_response({
            "success": False,
            "error": message
        }, status_code)

def run_server():
    # Allow port reuse to avoid 'address already in use' during quick restarts
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), HuffmanHTTPRequestHandler) as httpd:
        print(f"==================================================")
        print(f" Huffman Studio Server running at: http://localhost:{PORT}")
        print(f" Press Ctrl+C to terminate the server.")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == "__main__":
    run_server()
