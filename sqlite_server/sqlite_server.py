import http.server
import sqlite3

def create_database():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS data (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    value REAL
                )""")
    conn.commit()
    print("Database created successfully!")
    conn.close()

def handle_query(query):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute(query)
        rows = c.fetchall()
        headers = [desc[0] for desc in c.description]
        conn.close()
        return {'status': 'ok', 'headers': headers, 'rows': rows}
    except sqlite3.OperationalError as e:
        print(f"Error executing query: {e}")
        return {'status': 'error', 'message': str(e)}

def list_tables():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    conn.close()
    return [table[0] for table in tables]

def list_data(table):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table};")
    rows = c.fetchall()
    headers = [desc[0] for desc in c.description]
    conn.close()
    return {'status': 'ok', 'headers': headers, 'rows': rows}

class QueryHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = '''
            <html>
              <body>
                <h1>Welcome to the SQLite server!</h1>
                <form action="/query" method="post">
                  <textarea name="query" cols="40" rows="10"></textarea>
                  <br>
                  <input type="submit" value="Execute Query">
                </form>
              </body>
            </html>
            '''
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = '<h1>Not Found</h1>'
            self.wfile.write(html.encode())

    def do_POST(self):
        if self.path == '/query':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            query = post_data.decode('utf-8').split('=')[1]
            result = handle_query(query)
            if result['status'] == 'ok':
                html = '<h1>Query executed successfully!</h1>'
                if result['rows']:
                    html += '<table border="1">'
                    html += '<tr><th>' + '</th><th>'.join(result['headers']) + '</th></tr>'
                    for row in result['rows']:
                        html += '<tr><td>' + '</td><td>'.join(str(cell) for cell in row) + '</td></tr>'
                    html += '</table>'
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode())
            else:
                html = '<h1>Error</h1><p>' + result['message'] + '</p>'
                self.send_response(500)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode())
import os
import webbrowser
from http.server import HTTPServer
from routes.main_route import MainRoute
from utils.port_utils import find_available_port

def main():
    port = find_available_port()
    print(f"Server running on port {port}")
    httpd = HTTPServer(('localhost', port), QueryHandler)
    print(f"Server running on http://localhost:{port}/")
    webbrowser.open(f"http://localhost:{port}/")
    httpd.serve_forever()

if __name__ == "__main__":
    main()