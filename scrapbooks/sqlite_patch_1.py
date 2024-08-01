  import http.server
  import sqlite3
  import json
  
  # Create a SQLite database and table
  conn = sqlite3.connect('database.db')
  c = conn.cursor()
  c.execute('''CREATE TABLE IF NOT EXISTS data
               (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)''')
  conn.commit()
  
  # Define a function to handle SQL queries
  def handle_query(query):
      try:
          c.execute(query)
          rows = c.fetchall()
          headers = [desc[0] for desc in c.description]
          return {'status': 'ok', 'headers': headers, 'rows': rows}
      except sqlite3.Error as e:
          return {'status': 'error', 'message': str(e)}
  
  # Define a simple HTTP server to respond to queries
  class QueryHandler(http.server.BaseHTTPRequestHandler):
      def do_GET(self):
          self.send_response(200)
          self.send_header("Content-type", "text/html")
          self.end_headers()
  
          # Parse the query from the URL
          query = self.path.split('?')[1] if '?' in self.path else ''
          query = query.replace('+', ' ')
  
          # Execute the query and generate HTML output
          result = handle_query(query)
          if result['status'] == 'ok':
              html = '<table>'
              html += '<tr><th>' + '</th><th>'.join(result['headers']) + '</th></tr>'
              for row in result['rows']:
                  html += '<tr><td>' + '</td><td>'.join(str(cell) for cell in row) + '</td></tr>'
              html += '</table>'
          else:
              html = '<h1>Error</h1><p>' + result['message'] + '</p>'
  
          self.wfile.write(html.encode())
  
  # Run the HTTP server
  httpd = http.server.HTTPServer(('localhost', 8000), QueryHandler)
  print('Server running on http://localhost:8000/')
  httpd.serve_forever()