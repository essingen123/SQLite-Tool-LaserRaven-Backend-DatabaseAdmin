import os
import webbrowser
import http.server
import sqlite3
import socket
import json
import urllib.parse

# Create the directory structure
os.makedirs('sqlite_tool', exist_ok=True)
os.makedirs('sqlite_tool/queries', exist_ok=True)

# Create the HTML file
with open('sqlite_tool/index.html', 'w') as f:
    f.write('''<!DOCTYPE html>
<html>
  <body>
    <h1>SQLite Tool</h1>
    <form id="query-form">
      <textarea id="query" name="query" cols="40" rows="10"></textarea>
      <br>
      <input type="submit" value="Execute Query">
    </form>
    <br>
    <button onclick="document.querySelector('#query').value='SELECT * FROM data';">Select All</button>
    <button onclick="document.querySelector('#query').value='CREATE TABLE IF NOT EXISTS data2 (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)';">Create Table</button>
    <button onclick="document.querySelector('#query').value='INSERT INTO data (name, value) VALUES (\'test\', 1)';">Insert Row</button>
    <button onclick="document.querySelector('#query').value=\'DROP TABLE data\';">Drop Table</button>
    <h2>Saved Queries:</h2>
    <ul>
    {% for query_name in saved_queries %}
      <li><button onclick="document.querySelector('#query').value='{{ saved_queries[query_name] }}';">{{ query_name }}</button></li>
    {% endfor %}
    </ul>
    <div id="result"></div>
    <script>
      document.querySelector('#query-form').addEventListener('submit', function(event) {
        event.preventDefault();
        var query = document.querySelector('#query').value;
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/query', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onload = function() {
          if (xhr.status === 200) {
            document.querySelector('#result').innerHTML = xhr.responseText;
          }
        };
        xhr.send('query=' + encodeURIComponent(query));
      });
    </script>
  </body>
</html>
''')

# Create the Python script
with open('sqlite_tool/server.py', 'w') as f:
    f.write('''import os
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
import socket
import json
import urllib.parse

conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY,
    name TEXT,
    value INTEGER
)""")
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
    os.makedirs('queries', exist_ok=True)
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
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open("index.html", "rb") as f:
            self.wfile.write(f.read())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        query = urllib.parse.parse_qs(post_data)["query"][0]
        result = handle_query(query)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode("utf-8"))

def main():
    httpd = HTTPServer(('localhost', port), QueryHandler)
    print(f"Server running on http://localhost:{port}/")
    webbrowser.open(f"http://localhost:{port}/")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
''')

# Create the run script
with open('sqlite_tool/run.sh', 'w') as f:
    f.write('''#!/bin/bash

# Run the Python server in the background
python server.py &

# Open the HTML in the default web browser
open http://localhost:$(python -c "import server; print(server.port)")

# Wait for the Python server to finish
wait %1''')
os.chmod('sqlite_tool/run.sh', 0o755)

print("Files created successfully!")