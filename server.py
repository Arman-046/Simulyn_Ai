import http.server
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 3000

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

with socketserver.TCPServer(("", PORT), NoCacheHTTPRequestHandler) as httpd:
    print(f"Serving HTTP on port {PORT} with no caching...")
    httpd.serve_forever()
