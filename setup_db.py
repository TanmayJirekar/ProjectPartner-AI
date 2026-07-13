"""Initialize ProjectPartner AI database."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import mysql.connector
from backend.config import DB_CONFIG


def init_db():
    schema_path = ROOT / "database" / "schema.sql"
    sql = schema_path.read_text(encoding="utf-8")

    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
    )
    cursor = conn.cursor()

    for statement in sql.split(";"):
        statement = statement.strip()
        if statement:
            try:
                cursor.execute(statement)
            except mysql.connector.Error as e:
                if "already exists" not in str(e).lower():
                    print(f"Warning: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized successfully!")


if __name__ == "__main__":
    init_db()
