import sqlite3
from datetime import datetime
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        credits INTEGER DEFAULT 0,
        referred_by INTEGER
    )''')
    
    # Referrals tracking table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer_id INTEGER,
        referred_id INTEGER UNIQUE,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Panels database
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS panels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        server_id TEXT UNIQUE,
        panel_username TEXT,
        server_type TEXT,
        url TEXT,
        expires_at TEXT
    )''')
    
    # Force join channels
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS channels (
        channel_id INTEGER PRIMARY KEY,
        channel_username TEXT
    )''')
    
    conn.commit()
    conn.close()

# Helper execution functions
async def add_user(user_id: int, username: str, referrer_id: int = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO users (user_id, username, referred_by) VALUES (?, ?, ?)", 
                       (user_id, username, referrer_id))
        conn.commit()
    finally:
        conn.close()

async def get_user(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, credits, referred_by FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"user_id": row[0], "username": row[1], "credits": row[2], "referred_by": row[3]}
    return None

async def add_referral(referrer_id: int, referred_id: int) -> bool:
    if referrer_id == referred_id:
        return False
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)", (referrer_id, referred_id))
        # Check milestones for credits award (3 referrals = 1 credit)
        cursor.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (referrer_id,))
        count = cursor.fetchone()[0]
        if count % 3 == 0:
            cursor.execute("UPDATE users SET credits = credits + 1 WHERE user_id = ?", (referrer_id,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

async def get_referral_count(user_id: int) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

async def update_credits(user_id: int, amount: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

async def add_panel(user_id: int, server_id: str, username: str, server_type: str, url: str, expires_at: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO panels (user_id, server_id, panel_username, server_type, url, expires_at) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, server_id, username, server_type, url, expires_at))
    conn.commit()
    conn.close()

async def get_user_panels(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT server_id, panel_username, server_type, url, expires_at FROM panels WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

async def get_all_panels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, server_id, expires_at FROM panels")
    rows = cursor.fetchall()
    conn.close()
    return rows

async def delete_panel(server_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM panels WHERE server_id = ?", (server_id,))
    conn.commit()
    conn.close()

async def add_channel(channel_id: int, channel_username: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO channels (channel_id, channel_username) VALUES (?, ?)", (channel_id, channel_username))
    conn.commit()
    conn.close()

async def remove_channel(channel_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
    conn.commit()
    conn.close()

async def get_channels():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT channel_id, channel_username FROM channels")
    rows = cursor.fetchall()
    conn.close()
    return rows

async def get_global_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM referrals")
    total_refs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM panels")
    total_panels = cursor.fetchone()[0]
    conn.close()
    return total_users, total_refs, total_panels

async def get_all_user_ids():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]
