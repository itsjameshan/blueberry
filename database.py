import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


DATABASE = 'blueberry.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            created_at TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            image_name TEXT NOT NULL,
            result_image TEXT,
            total_count INTEGER DEFAULT 0,
            ripe_count INTEGER DEFAULT 0,
            semi_ripe_count INTEGER DEFAULT 0,
            unripe_count INTEGER DEFAULT 0,
            conf_threshold REAL DEFAULT 0.5,
            results_json TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    try:
        cursor.execute("ALTER TABLE detection_records ADD COLUMN results_json TEXT DEFAULT ''")
    except:
        pass
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            model_path TEXT NOT NULL,
            is_active INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')

    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'admin'")
    if cursor.fetchone()['cnt'] == 0:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            ('admin', generate_password_hash('admin123'), 'admin', now)
        )

    conn.commit()
    conn.close()


def get_user_by_username(username):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user


def create_user(username, password, role='user'):
    conn = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (username, generate_password_hash(password), role, now)
        )
        conn.commit()
        conn.close()
        return True, "用户创建成功"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "用户名已存在"


def delete_user(user_id):
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id = ? AND role != 'admin'", (user_id,))
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_db()
    users = conn.execute("SELECT id, username, role, created_at FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return users


def save_detection_record(user_id, image_name, result_image, total_count, ripe_count, semi_ripe_count, unripe_count, conf_threshold, results_json=''):
    conn = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute(
        "INSERT INTO detection_records (user_id, image_name, result_image, total_count, ripe_count, semi_ripe_count, unripe_count, conf_threshold, results_json, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, image_name, result_image, total_count, ripe_count, semi_ripe_count, unripe_count, conf_threshold, results_json, now)
    )
    conn.commit()
    conn.close()


def get_user_records(user_id=None):
    conn = get_db()
    if user_id:
        records = conn.execute(
            "SELECT dr.*, u.username FROM detection_records dr JOIN users u ON dr.user_id = u.id WHERE dr.user_id = ? ORDER BY dr.created_at DESC",
            (user_id,)
        ).fetchall()
    else:
        records = conn.execute(
            "SELECT dr.*, u.username FROM detection_records dr JOIN users u ON dr.user_id = u.id ORDER BY dr.created_at DESC"
        ).fetchall()
    conn.close()
    return records


def get_detection_stats():
    conn = get_db()
    stats = {}
    total = conn.execute("SELECT COUNT(*) as cnt FROM detection_records").fetchone()['cnt']
    stats['total_detections'] = total
    stats['total_ripe'] = conn.execute("SELECT COALESCE(SUM(ripe_count), 0) as cnt FROM detection_records").fetchone()['cnt']
    stats['total_semi_ripe'] = conn.execute("SELECT COALESCE(SUM(semi_ripe_count), 0) as cnt FROM detection_records").fetchone()['cnt']
    stats['total_unripe'] = conn.execute("SELECT COALESCE(SUM(unripe_count), 0) as cnt FROM detection_records").fetchone()['cnt']
    stats['total_boxes'] = conn.execute("SELECT COALESCE(SUM(total_count), 0) as cnt FROM detection_records").fetchone()['cnt']
    stats['user_count'] = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()['cnt']
    stats['daily_stats'] = conn.execute(
        "SELECT date(created_at) as day, COUNT(*) as cnt FROM detection_records GROUP BY day ORDER BY day DESC LIMIT 7"
    ).fetchall()
    conn.close()
    return stats


def save_model_config(model_name, model_path, is_active=0):
    conn = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if is_active:
        conn.execute("UPDATE model_config SET is_active = 0")
    conn.execute(
        "INSERT INTO model_config (model_name, model_path, is_active, created_at) VALUES (?, ?, ?, ?)",
        (model_name, model_path, is_active, now)
    )
    conn.commit()
    conn.close()


def get_active_model():
    conn = get_db()
    model = conn.execute("SELECT * FROM model_config WHERE is_active = 1").fetchone()
    conn.close()
    return model


def get_all_models():
    conn = get_db()
    models = conn.execute("SELECT * FROM model_config ORDER BY created_at DESC").fetchall()
    conn.close()
    return models


def set_active_model(model_id):
    conn = get_db()
    conn.execute("UPDATE model_config SET is_active = 0")
    conn.execute("UPDATE model_config SET is_active = 1 WHERE id = ?", (model_id,))
    conn.commit()
    conn.close()


def delete_model(model_id):
    conn = get_db()
    conn.execute("DELETE FROM model_config WHERE id = ?", (model_id,))
    conn.commit()
    conn.close()