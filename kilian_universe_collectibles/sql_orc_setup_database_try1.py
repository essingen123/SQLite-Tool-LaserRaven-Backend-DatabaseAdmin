import os

# Create project directory
project_dir = 'sqlite_server'
if not os.path.exists(project_dir):
    os.makedirs(project_dir)

# Create subdirectories
subdirs = ['models', 'queries', 'routes', 'utils']
for subdir in subdirs:
    os.makedirs(os.path.join(project_dir, subdir))

# Create __init__.py files
for subdir in subdirs:
    with open(os.path.join(project_dir, subdir, '__init__.py'), 'w') as f:
        f.write('')

# Create structure.txt file
with open(os.path.join(project_dir, 'structure.txt'), 'w') as f:
    f.write('''
sqlite_server/
sqlite_server.py
models/
__init__.py
database.py
queries/
__init__.py
query_handler.py
routes/
__init__.py
main_route.py
table_route.py
utils/
__init__.py
port_utils.py
structure.txt
''')

# Create sqlite_server.py file
with open(os.path.join(project_dir, 'sqlite_server.py'), 'w') as f:
    f.write('''
import os
import webbrowser
from http.server import HTTPServer
from routes.main_route import MainRoute
from utils.port_utils import find_available_port

def main():
    port = find_available_port()
    print(f"Server running on port {port}")
    httpd = HTTPServer(('localhost', port), MainRoute)
    print(f"Server running on http://localhost:{port}/")
    webbrowser.open(f"http://localhost:{port}/")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
''')

# Create models/database.py file
with open(os.path.join(project_dir, 'models', 'database.py'), 'w') as f:
    f.write('''
import sqlite3

def create_database():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(```CREATE TABLE IF NOT EXISTS data
                (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)```)
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
''')

# Create queries/query_handler.py file
with open(os.path.join(project_dir, 'queries', 'query_handler.py'), 'w') as f:
    f.write('''
import os
from models.database import handle_query, list_tables, list_data

def save_query(query, filename):
    with open(os.path.join('queries', f'{filename}.txt'), 'w') as f:
        f.write(query)

def load_saved_queries():
    saved_queries = {}
    for filename in os.listdir('queries'):
        if filename.endswith('.txt'):
            query_name = os.path.splitext(filename)[0]
            with open(os.path.join('queries', filename), 'r') as f:
                saved_queries[query_name] = f.read()
    return saved_queries
''')

# Create routes/main_route.py file
with open(os.path.join(project_dir, 'routes', 'main_route.py'), 'w') as f:
    f.write('''
import http.server
from urllib.parse import urlparse, parse_qs
from models.database import handle_query
from queries.query_handler import load_saved_queries

class MainRoute(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # ...
    def do_POST(self):
        # ...
''')

# Create utils/port_utils.py file
with open(os.path.join(project_dir, 'utils', 'port_utils.py'), 'w') as f:
    f.write('''
import socket

def find_available_port():
    port = 8000
    while not is_port_available(port):
        port += 1
    return port

def is_port_available(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    if result == 0:
        return False
    else:
        return True
''')

print("Project structure created successfully!")