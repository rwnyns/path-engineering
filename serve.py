"""Serve the site and proxy /ollama/* to the local Ollama server (same origin, so no CORS setup).

Usage: python3 serve.py   then open http://localhost:8000
"""
import http.client
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

OLLAMA_HOST, OLLAMA_PORT = "127.0.0.1", 11434
import sys
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(SimpleHTTPRequestHandler):
    def _proxy(self):
        body = None
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            body = self.rfile.read(length)
        try:
            conn = http.client.HTTPConnection(OLLAMA_HOST, OLLAMA_PORT, timeout=600)
            conn.request(self.command, self.path[len("/ollama"):], body, {"Content-Type": "application/json"})
            resp = conn.getresponse()
        except OSError:
            self.send_error(502, "Ollama is not running on %s:%s" % (OLLAMA_HOST, OLLAMA_PORT))
            return
        self.send_response(resp.status)
        self.send_header("Content-Type", resp.getheader("Content-Type", "application/json"))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        while chunk := resp.read1(4096):  # forward as it arrives so replies stream
            self.wfile.write(chunk)
            self.wfile.flush()
        conn.close()

    def do_GET(self):
        self._proxy() if self.path.startswith("/ollama/") else super().do_GET()

    def do_POST(self):
        if self.path.startswith("/ollama/"):
            self._proxy()
        else:
            self.send_error(404)


if __name__ == "__main__":
    print("Open http://localhost:%d" % PORT)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
