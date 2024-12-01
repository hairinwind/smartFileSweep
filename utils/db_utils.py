import sqlite3

def initialize_db(db_path="file_hashes.db"):
    """初始化 SQLite 数据库"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT UNIQUE,
            file_hash TEXT,
            last_modified REAL,
            scan_time REAL
        )
    """)
    conn.commit()
    conn.close()

def get_connection(db_path="file_hashes.db"):
    """获取数据库连接"""
    return sqlite3.connect(db_path)