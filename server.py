import http.server
import socketserver
import subprocess
import sys
import os

PORT = 8050

class GameHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/start-game':
            self.send_response(200)
            self.end_headers()
            # Start the game using the system Python
            subprocess.Popen([sys.executable, 'battle_royale.py'])
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

with socketserver.TCPServer(("", PORT), GameHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
