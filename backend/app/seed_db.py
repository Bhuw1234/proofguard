"""
Seed the demo SQLite database with fictional data.

This creates backend/data/wallet.db with users, orders, payments,
and audit_logs tables. All data is fake — no real personal information.

Run directly:
    cd backend && python -m app.seed_db
"""

import sqlite3
import os
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DB_DIR / "wallet.db"


def seed(db_path: Path = DB_PATH):
    """Create tables and insert demo data. Overwrites if already exists."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # --- Schema ---
    cur.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            last_login TEXT NOT NULL
        );

        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount_inr REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );

        CREATE TABLE audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            actor TEXT NOT NULL,
            action TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)

    # --- Users: mix of old (pre-2023) and recent logins ---
    users = [
        ("Aarav Sharma", "aarav@example.com", "2022-03-15"),
        ("Priya Patel", "priya@example.com", "2022-08-21"),
        ("Rohan Gupta", "rohan@example.com", "2022-11-02"),
        ("Ananya Desai", "ananya@example.com", "2024-06-10"),
        ("Vikram Singh", "vikram@example.com", "2025-01-18"),
        ("Meera Iyer", "meera@example.com", "2022-06-30"),
        ("Arjun Nair", "arjun@example.com", "2025-07-05"),
        ("Kavya Reddy", "kavya@example.com", "2024-11-22"),
        ("Siddharth Joshi", "siddharth@example.com", "2022-12-28"),
        ("Neha Kulkarni", "neha@example.com", "2025-03-14"),
    ]
    cur.executemany(
        "INSERT INTO users (name, email, last_login) VALUES (?, ?, ?);",
        users,
    )

    # --- Orders tied to old users (ids 1,2,3,6,9) so deletion is dangerous ---
    orders = [
        (1, 4500.00),
        (1, 1200.00),
        (2, 8900.00),
        (3, 3200.00),
        (6, 6700.00),
        (6, 2100.00),
        (9, 950.00),
        (4, 15000.00),
        (5, 7800.00),
    ]
    cur.executemany(
        "INSERT INTO orders (user_id, amount_inr) VALUES (?, ?);",
        orders,
    )

    # --- Payments tied to those orders ---
    payments = [
        (1, "completed"),
        (2, "completed"),
        (3, "pending"),
        (4, "completed"),
        (5, "completed"),
        (6, "failed"),
        (7, "completed"),
        (8, "pending"),
        (9, "completed"),
    ]
    cur.executemany(
        "INSERT INTO payments (order_id, status) VALUES (?, ?);",
        payments,
    )

    # --- A few audit entries ---
    audit_entries = [
        ("system", "database_seeded", "2024-01-01T00:00:00Z"),
        ("admin", "user_exported", "2024-06-15T10:30:00Z"),
        ("agent", "simulation_ran", "2025-08-01T14:22:00Z"),
    ]
    cur.executemany(
        "INSERT INTO audit_logs (actor, action, created_at) VALUES (?, ?, ?);",
        audit_entries,
    )

    conn.commit()
    conn.close()
    print(f"Seeded database at {db_path}")
    print(f"  users: 10, orders: 9, payments: 9, audit_logs: 3")


if __name__ == "__main__":
    seed()
