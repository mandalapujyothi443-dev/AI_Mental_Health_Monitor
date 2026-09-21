import os
import sqlite3
from werkzeug.security import generate_password_hash
from flask import current_app

def get_db():
    db_path = current_app.config["DATABASE_PATH"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db_path = current_app.config["DATABASE_PATH"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        mood_score INTEGER NOT NULL,
        stress_score INTEGER NOT NULL,
        sleep_score INTEGER NOT NULL,
        activity_score INTEGER NOT NULL,
        text_input TEXT,
        distress_score REAL NOT NULL,
        risk_level TEXT NOT NULL,
        ai_summary TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        assessment_id INTEGER NOT NULL,
        risk_level TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(assessment_id) REFERENCES assessments(id)
    );
    """)

    demo_users = [
        ("Demo User", "user@example.com", "User@123", "user"),
        ("Demo Counselor", "counselor@example.com", "Counselor@123", "counselor"),
    ]

    for name, email, password, role in demo_users:
        existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)",
                (name, email, generate_password_hash(password), role)
            )

    conn.commit()
    conn.close()
