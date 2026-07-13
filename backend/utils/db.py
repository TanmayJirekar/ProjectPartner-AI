import json
import mysql.connector
from mysql.connector import Error
from backend.config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def execute_query(query, params=None, fetch=False, fetch_one=False, commit=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        if commit:
            conn.commit()
            return cursor.lastrowid
        if fetch_one:
            return cursor.fetchone()
        if fetch:
            return cursor.fetchall()
        return None
    except Error as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def parse_json_field(value, default=None):
    if default is None:
        default = []
    if value is None:
        return default
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default
