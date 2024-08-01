import os
import webbrowser
import http.server
import sqlite3
import socket
import json
import urllib.parse

conn = sqlite3.connect('database.db'); c = conn.cursor();
c.execute("""CREATE TABLE IF NOT EXISTS data (
    id INTEGER PRIMARY KEY,
    name TEXT,
    value INTEGER
)""")
conn.commit()

with open('index.html', 'w') as f:
    f.write('''<!DOCTYPE html>
<html>
  <head>
    <title>SQLite Tool</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
  </head>
  <body>
    <h1>SQLite Tool</h1>
    <h2>Tables:</h2>
    <ul id="tables"></ul>
    <div id="table-content"></div>
    <form id="query-form">
      <textarea id="query" name="query" cols="40" rows="10" placeholder="Enter your query..."></textarea>
      <br>
      <button type="submit" class="btn btn-primary btn-lg">Execute Query</button>
    </form>
    <div class="btn-group">
<button class="btn btn-success btn-lg" onclick="executeQuery(event, 'SELECT * FROM data')">Select All</button>
<button class="btn btn-info btn-lg" onclick="executeQuery(event, 'CREATE TABLE IF NOT EXISTS data2 (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)')">Create Table</button>

<button class="btn btn-danger btn-lg" onclick="executeQuery(event, 'DROP TABLE data')">Drop Table</button>

<button onclick="executeQuery(event, 'data')">Insert Row</button>
<button onclick="executeQuery(event, 'PRAGMA table_info(data)')">Table Info</button>
<button onclick="executeQuery(event, 'SELECT * FROM data ORDER BY name ASC')">Sort by Name</button>
<button onclick="executeQuery(event, 'SELECT * FROM data ORDER BY value DESC')">Sort by Value</button>
    </div>

    <script>
function executeQuery(event, tableName) {
  event.preventDefault();
  if (tableName === 'data') {
    var columnNames = ['name', 'value']; // adjust this to match your column names
    var query = `INSERT INTO ${tableName} (${columnNames.join(', ')}) VALUES (${columnNames.map(() => '0').join(', ')})`;
  } else {
    var query = tableName;
  }
  document.querySelector('#query').value = query;
  var xhr = new XMLHttpRequest();
  xhr.open('POST', '/query', true);
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
    if (xhr.status === 200) {
      document.querySelector('#table-content').innerHTML = xhr.responseText;
    }
  };
  xhr.send('query=' + encodeURIComponent(query));
}

      document.querySelector('#query-form').addEventListener('submit', function(event) {
        event.preventDefault();
        var query = document.querySelector('#query').value;
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/query', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onload = function() {
          if (xhr.status === 200) {
            document.querySelector('#table-content').innerHTML = xhr.responseText;
          }
        };
        xhr.send('query=' + encodeURIComponent(query));
      });
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/tables', true);
      xhr.onload = function() {
        if (xhr.status === 200) {
          var tables = JSON.parse(xhr.responseText);
          var tableList = document.getElementById('tables');
          tables.forEach(function(table) {
            var tableLink = document.createElement('a');
            tableLink.href = '#';
            tableLink.onclick = function() {
              var xhr = new XMLHttpRequest();
              xhr.open('GET', '/table/' + table, true);
              xhr.onload = function() {
                if (xhr.status === 200) {
                  document.querySelector('#table-content').innerHTML = xhr.responseText;
                }
              };
              xhr.send();
            };
            tableLink.textContent = table;
            tableList.appendChild(tableLink);
          });
        }
      };
      xhr.send();
    </script>
  </body>
</html>
''')

class QueryHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())
        elif self.path.startswith('/table/'):
            table_name = self.path[7:]
            c.execute(f"SELECT * FROM {table_name}")
            rows = c.fetchall()
            headers = [desc[0] for desc in c.description]
            table_content = '<table><tr><th>' + '</th><th>'.join(headers) + '</th></tr>'
            for row in rows:
                table_content += '<tr><td>' + '</td><td>'.join(str(cell) for cell in row) + '</td></tr>'
            table_content += '</table>'
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(table_content.encode("utf-8"))
        elif self.path == '/tables':
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [table[0] for table in c.fetchall()]
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(tables).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode("utf-8")
        params = urllib.parse.parse_qs(post_data)
        if 'query' in params:
            query = params["query"][0]
            result = self.handle_query(query)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Error: No query parameter provided")

    def handle_query(self, query):
        try:
            c.execute(query)
            rows = c.fetchall()
            headers = [desc[0] for desc in c.description] if c.description else []
            return {'status': 'ok', 'headers': headers, 'rows': rows}
        except sqlite3.OperationalError as e:
            print(f"Error executing query: {e}")
            return {'status': 'error', 'message': str(e)}

def main():
    port = 1025
    httpd = http.server.HTTPServer(('localhost', port), QueryHandler)
    print(f"Server running on http://localhost:{port}/")
    webbrowser.open(f"http://localhost:{port}/")
    httpd.serve_forever()

if __name__ == "__main__":
    main()