import http.server
import socketserver
import sys
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8088
DIRECTORY = "/opt/deco/downloads/windows"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def translate_path(self, path):
        if path.startswith("/agent/windows"):
            return os.path.join(DIRECTORY, "DecoSecurityAgentSetup.exe")
        if path.startswith("/manifest/windows"):
            return os.path.join(DIRECTORY, "manifest.json")
        return super().translate_path(path)

    def do_HEAD(self):
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Length", os.path.getsize(path))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    def end_headers(self):
        self.send_header("Accept-Ranges", "none")
        super().end_headers()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

print(f"Serving {DIRECTORY} on port {PORT}")
with ReusableTCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
