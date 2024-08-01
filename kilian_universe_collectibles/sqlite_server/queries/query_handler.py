
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
