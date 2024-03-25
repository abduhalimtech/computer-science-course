import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def get_database_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def execute_query(query, params=None, commit=False):
    conn = get_database_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        if commit:
            conn.commit()
            return cursor.lastrowid
        if query.lstrip().upper().startswith('SELECT'):
            return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
