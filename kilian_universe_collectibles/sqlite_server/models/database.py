import os
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
import socket
import json
import urllib.parse

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS data
(id INTEGER PRIMARY KEY, name TEXT, value INTEGER)''')
conn.commit()
print("Database created successfully!")

def handle_query(query):
    try:
        c.execute(query)
        rows = c.fetchall()
        headers = [desc[0] for desc in c.description]
        return {'status': 'ok', 'headers': headers, 'rows': rows}
    except sqlite3.OperationalError as e:
        print(f"Error executing query: {e}")
        return {'status': 'error', 'message': str(e)}

def is_port_available(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    return result != 0

def find_available_port():
    for port in range(1024, 65536):
        if is_port_available(port):
            return port
    return None

port = find_available_port()
print(f"Server running on port {port}")

if not os.path.exists('queries'):
    os.makedirs('queries')
print("Queries directory created successfully!")

saved_queries = {}
for filename in os.listdir('queries'):
    if filename.endswith('.txt'):
        query_name = os.path.splitext(filename)[0]
        with open(os.path.join('queries', filename), 'r') as f:
            saved_queries[query_name] = f.read()
print("Saved queries loaded successfully!")

def save_query(query, filename):
    with open(os.path.join('queries', f'{filename}.txt'), 'w') as f:
        f.write(query)

def list_tables():
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [table[0] for table in c.fetchall()]

print("Tables listed successfully!")

def list_data(table):
    c.execute(f"SELECT * FROM {table};")
    rows = c.fetchall()
    headers = [desc[0] for desc in c.description]
    return {'status': 'ok', 'headers': headers, 'rows': rows}

class QueryHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = '''
            <html>
              <body>
                <h1>SQLite Query Tool</h1>
                <form action="/query" method="post">
                  <textarea name="query" cols="40" rows="10"></textarea>
                  <br>
                  <input type="submit" value="Execute Query">
                </form>
                <br>
                <button onclick="document.querySelector('textarea').value='SELECT * FROM data';">Select All</button>
                <button onclick="document.querySelector('textarea').value='CREATE TABLE IF NOT EXISTS data2 (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)';">Create Table</button>
                <button onclick="document.querySelector('textarea').value='INSERT INTO data (name, value) VALUES (\'test\', 1)';">Insert Row</button>
                <button onclick="document.querySelector('textarea').value=\'DROP TABLE data\';">Drop Table</button>
                <h2>Saved Queries:</h2>
                <ul>
            '''
            for query_name in saved_queries:
                html += f'<li><button onclick="document.querySelector(\'textarea\').value=\'{saved_queries[query_name]}\';">{query_name}</button></li>'
            html += '''
                </ul>
                <div id="result"></div>
              </body>
            </html>
            '''
            self.wfile.write(html.encode())
        elif self.path == '/tables':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            tables = list_tables()
            html = '<h1>Tables:</h1><ul>'
            for table in tables:
                html += f'<li><a href="/table/{table}">{table}</a></li>'
            html += '</ul>'
            self.wfile.write(html.encode())
        elif self.path.startswith('/table/'):
            table = self.path.split('/')[-1]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            result = list_data(table)
            if result['status'] == 'ok':
                html = '<table border="1">'
                html += '<tr><th>' + '</th><th>'.join(result['headers']) + '</th></tr>'
                for row in result['rows']:
                    html += '<tr><td>' + '</td><td>'.join(str(cell) for cell in row) + '</td></tr>'
                html += '</table>'
            else:
                html = '<h1>Error</h1><p>' + result['message'] + '</p>'
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
            query = post_data.decode('utf-8')
            print(f"Received query: {query}")
            result = handle_query(query)
            if result['status'] == 'ok':
                html = '<table border="1">'
                html += '<tr><th>' + '</th><th>'.join(result['headers']) + '</th></tr>'
                for row in result['rows']:
                    html += '<tr><td>' + '</td><td>'.join(str(cell) for cell in row) + '</td></tr>'
                html += '</table>'
            else:
                html = '<h1>Error</h1><p>' + result['message'] + '</p>'
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        elif self.path == '/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            query_name = post_data.decode('utf-8').split('=')[0]
            query = post_data.decode('utf-8').split('=')[1]
            save_query(query, query_name)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = '<h1>Query saved successfully!</h1>'
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = '<h1>Not Found</h1>'
            self.wfile.write(html.encode())

def main():
    httpd = HTTPServer(('localhost', port), QueryHandler)
    print(f"Server running on http://localhost:{port}/")
    webbrowser.open(f"http://localhost:{port}/")
    httpd.serve_forever()

if __name__ == "__main__":
    main()