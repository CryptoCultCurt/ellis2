import http.server
import socketserver
import subprocess
import sys
import os

PORT = 8000

class GameHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/start-game':
            self.send_response(200)
            self.end_headers()
            # Start the game using the virtual environment's Python
            venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python3')
            subprocess.Popen([venv_python, 'battle_royale.py'])
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
