"""
Runs every analytical query in sql/ against the generated database and
prints the results — a small orchestration layer on top of the SQL, showing
how the queries would feed into a reporting pipeline or dashboard.
"""
import sqlite3
import os
import glob

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "equipment_sizing.db")
SQL_DIR = os.path.join(os.path.dirname(__file__), "..", "sql")


def run_query(conn, sql_path: str):
    with open(sql_path) as f:
        sql = f.read()
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    return cols, rows


def print_table(name: str, cols: list, rows: list, limit: int = 10):
    print(f"\n{'=' * 70}\n{name}\n{'=' * 70}")
    print(" | ".join(cols))
    for row in rows[:limit]:
        print(" | ".join(str(v) for v in row))
    if len(rows) > limit:
        print(f"... ({len(rows) - limit} more rows)")


def main():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            "Database not found — run data/generate_synthetic_data.py first."
        )

    conn = sqlite3.connect(DB_PATH)
    sql_files = sorted(glob.glob(os.path.join(SQL_DIR, "*.sql")))

    for sql_file in sql_files:
        name = os.path.basename(sql_file)
        cols, rows = run_query(conn, sql_file)
        print_table(name, cols, rows)

    conn.close()


if __name__ == "__main__":
    main()
