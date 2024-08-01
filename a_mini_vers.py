import http.server
import sqlite3
import webbrowser

# Create a SQLite database and
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS data
(id INTEGER PRIMARY KEY, name TEXT, value INTEGER)''')
conn.commit()

class QueryHandler(http.server.BaseHTTPRequestHandler):
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
                <button onclick="document.querySelector('textarea').value='DROP TABLE data';">Drop Table</button>
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
            query = post_data.decode('utf-8')
            try:
                c.execute(query)
                rows = c.fetchall()
                headers = [desc[0] for desc in c.description]
                html = '<table border="1">'
                html += '<tr><th>' + '</th><th>'.join(headers) + '</th></tr>'
                for row in rows:
                    html += '<tr><td>' + '</td><td>'.join(str(cell) for cell in row) + '</td></tr>'
                html += '</table>'
            except sqlite3.OperationalError as e:
                html = '<h1>Error</h1><p>' + str(e) + '</p>'
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = '<h1>Not Found</h1>'
            self.wfile.write(html.encode())

def main():
    httpd = http.server.HTTPServer(('localhost', 8000), QueryHandler)
    print("Server running on http://localhost:8000/")
    webbrowser.open("http://localhost:8000/")
    httpd.serve_forever()

if __name__ == "__main__":
    main()