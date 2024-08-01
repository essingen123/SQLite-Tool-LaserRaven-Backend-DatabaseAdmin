# main_route.py
import http.server
from urllib.parse import urlparse, parse_qs
from models.database import handle_query
from queries.query_handler import load_saved_queries

class MainRoute(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body>Welcome to the SQLite server!</body></html>')
        elif parsed_url.path == '/queries':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            queries = load_saved_queries()
            self.wfile.write(json.dumps(queries).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')

    def do_POST(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/query':
            content_length = int(self.headers['Content-Length'])
            query = self.rfile.read(content_length).decode()
            result = handle_query(query)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not found')