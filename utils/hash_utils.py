import os
import hashlib
import time
from utils.db_utils import get_connection, initialize_db
from utils.filename_utils import load_ignore_patterns, should_ignore


def calculate_hash(file_path, block_size=65536):
    """计算文件的 MD5 哈希值"""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(block_size):
            hasher.update(chunk)
    return hasher.hexdigest()

def save_file_hash(file_path, file_hash, db_path="file_hashes.db"):
    """保存文件的哈希值到数据库"""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # 获取文件的最后修改时间
    last_modified = os.path.getmtime(file_path)
    scan_time = time.time()

    # 插入或更新数据库记录
    cursor.execute("""
        INSERT INTO files (file_path, file_hash, last_modified, scan_time)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(file_path) DO UPDATE SET
        file_hash=excluded.file_hash,
        last_modified=excluded.last_modified,
        scan_time=excluded.scan_time
    """, (file_path, file_hash, last_modified, scan_time))
    conn.commit()
    conn.close()

def get_all_scanned_file_paths(db_path="file_hashes.db"):
    """
    Retrieve all file paths stored in the SQLite database.
    
    :param db_path: Path to the SQLite database file.
    :return: A list of file paths.
    """
    try:
        conn = get_connection(db_path)
        cursor = conn.cursor()
        
        # Query to fetch all file paths
        cursor.execute("SELECT file_path FROM files")
        rows = cursor.fetchall()
        
        # Extract file paths from query result
        file_paths = [row[0] for row in rows]
        
        conn.close()
        return file_paths
    except Exception as e:
        print(f"Error retrieving file paths: {e}")
        return []

def find_duplicates(directory, db_path="file_hashes.db", config_path="config/ignore_files.txt"):
    print(f"Loading ignore patterns from {config_path}...")
    ignore_patterns = load_ignore_patterns(config_path)

    scanned_files = get_all_scanned_file_paths()

    """查找目录中的重复文件"""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    duplicates = []
    for root, _, files in os.walk(directory):
        for file in files:
            if should_ignore(file, ignore_patterns):
                continue

            file_path = os.path.join(root, file)
            if file_path in scanned_files:
                # print(f"Skipping already scanned file: {file_path}")
                continue
            else:  
                print("scanning ", file_path)

            try:
                file_hash = calculate_hash(file_path)
                save_file_hash(file_path, file_hash, db_path)

                # 检查是否已有重复文件
                cursor.execute("""
                    SELECT file_path FROM files WHERE file_hash = ? AND file_path != ?
                """, (file_hash, file_path))
                result = cursor.fetchall()
                if result:
                    duplicates.append((file_path, [row[0] for row in result]))
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    conn.close()
    return duplicates