# database_devops_automation_health_checks_procedure_1.py

import os
import sqlite3

def create_database():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS data
                (id INTEGER PRIMARY KEY, name TEXT, value INTEGER)''')
    conn.commit()
    conn.close()

def insert_test_data():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO data (name, value) VALUES ('Test 1', 10)")
    c.execute("INSERT INTO data (name, value) VALUES ('Test 2', 20)")
    c.execute("INSERT INTO data (name, value) VALUES ('Test 3', 30)")
    conn.commit()
    conn.close()

def get_latest_test_file():
    test_files = [f for f in os.listdir('health_tests') if f.startswith('test') and f.endswith('.py')]
    test_files.sort(key=lambda x: int(x[4:-3]))
    return os.path.join('health_tests', test_files[-1])

def get_sql_query_from_test_file(test_file):
    with open(test_file, 'r') as f:
        for line in f:
            if line.lstrip().startswith('sql_query = '):
                return line.split('=')[1].strip().strip("'")

def run_health_check():
    test_file = get_latest_test_file()
    sql_query = get_sql_query_from_test_file(test_file)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute(sql_query)
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    create_database()
    insert_test_data()
    result = run_health_check()
    print("Health check result:")
    for row in result:
        print(row)