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
            email TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    # 兼容旧数据库：如果 users 表没有 email 字段，则添加
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    except:
        pass
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

    # 气象模块：果园表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gardens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            location_id TEXT,
            plant_date TEXT,
            growth_stage TEXT NOT NULL DEFAULT 'dormant',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 气象模块：天气数据缓存表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            garden_id INTEGER NOT NULL,
            weather_json TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            FOREIGN KEY (garden_id) REFERENCES gardens(id)
        )
    ''')

    # 气象模块：天气预警记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            garden_id INTEGER NOT NULL,
            alert_title TEXT NOT NULL,
            alert_level TEXT,
            alert_content TEXT,
            start_time TEXT,
            end_time TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (garden_id) REFERENCES gardens(id)
        )
    ''')

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


def update_user_email(user_id, email):
    conn = get_db()
    conn.execute("UPDATE users SET email = ? WHERE id = ?", (email, user_id))
    conn.commit()
    conn.close()
    return True


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


# ===== 果园管理 =====

def create_garden(user_id, name, location, location_id=None, plant_date=None, growth_stage='dormant'):
    conn = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    try:
        cursor = conn.execute(
            "INSERT INTO gardens (user_id, name, location, location_id, plant_date, growth_stage, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, name, location, location_id, plant_date, growth_stage, now)
        )
        conn.commit()
        garden_id = cursor.lastrowid
        conn.close()
        return True, "果园创建成功", garden_id
    except Exception as e:
        conn.close()
        return False, str(e), None


def get_garden_by_id(garden_id):
    conn = get_db()
    garden = conn.execute("SELECT * FROM gardens WHERE id = ?", (garden_id,)).fetchone()
    conn.close()
    return garden


def get_gardens_by_user(user_id):
    conn = get_db()
    gardens = conn.execute(
        "SELECT * FROM gardens WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return gardens


def get_all_gardens():
    conn = get_db()
    gardens = conn.execute(
        "SELECT g.*, u.username FROM gardens g JOIN users u ON g.user_id = u.id ORDER BY g.created_at DESC"
    ).fetchall()
    conn.close()
    return gardens


def update_garden(garden_id, name=None, location=None, location_id=None, plant_date=None, growth_stage=None):
    conn = get_db()
    garden = conn.execute("SELECT * FROM gardens WHERE id = ?", (garden_id,)).fetchone()
    if not garden:
        conn.close()
        return False, "果园不存在"
    updates = []
    params = []
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if location is not None:
        updates.append("location = ?")
        params.append(location)
    if location_id is not None:
        updates.append("location_id = ?")
        params.append(location_id)
    if plant_date is not None:
        updates.append("plant_date = ?")
        params.append(plant_date)
    if growth_stage is not None:
        updates.append("growth_stage = ?")
        params.append(growth_stage)
    if updates:
        params.append(garden_id)
        conn.execute(f"UPDATE gardens SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
    conn.close()
    return True, "果园更新成功"


def delete_garden(garden_id):
    conn = get_db()
    conn.execute("DELETE FROM weather_data WHERE garden_id = ?", (garden_id,))
    conn.execute("DELETE FROM weather_alerts WHERE garden_id = ?", (garden_id,))
    conn.execute("DELETE FROM gardens WHERE id = ?", (garden_id,))
    conn.commit()
    conn.close()


# ===== 天气数据缓存 =====

def save_weather_data(garden_id, weather_json):
    conn = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute(
        "INSERT INTO weather_data (garden_id, weather_json, fetched_at) VALUES (?, ?, ?)",
        (garden_id, weather_json, now)
    )
    conn.commit()
    conn.close()


def get_latest_weather(garden_id):
    conn = get_db()
    record = conn.execute(
        "SELECT * FROM weather_data WHERE garden_id = ? ORDER BY fetched_at DESC LIMIT 1",
        (garden_id,)
    ).fetchone()
    conn.close()
    return record


# ===== 天气预警 =====

def save_weather_alert(garden_id, alert_title, alert_level, alert_content, start_time=None, end_time=None):
    conn = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute(
        "INSERT INTO weather_alerts (garden_id, alert_title, alert_level, alert_content, start_time, end_time, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (garden_id, alert_title, alert_level, alert_content, start_time, end_time, now)
    )
    conn.commit()
    conn.close()


def is_alert_duplicate(garden_id, alert_title, hours=24):
    """检查是否已存在相同标题的预警（避免重复保存和发送）"""
    conn = get_db()
    row = conn.execute(
        "SELECT COUNT(*) FROM weather_alerts WHERE garden_id = ? AND alert_title = ? AND created_at >= datetime('now', ?)",
        (garden_id, alert_title, f'-{hours} hours')
    ).fetchone()
    conn.close()
    return row[0] > 0


def get_active_alerts(garden_id):
    conn = get_db()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    alerts = conn.execute(
        "SELECT * FROM weather_alerts WHERE garden_id = ? AND (end_time IS NULL OR end_time > ?) ORDER BY created_at DESC",
        (garden_id, now)
    ).fetchall()
    conn.close()
    return alerts


def get_all_alerts(garden_id=None, limit=50):
    """获取历史预警记录（所有预警，含已过期的）"""
    conn = get_db()
    if garden_id:
        alerts = conn.execute(
            "SELECT a.*, g.name as garden_name FROM weather_alerts a "
            "JOIN gardens g ON a.garden_id = g.id "
            "WHERE a.garden_id = ? ORDER BY a.created_at DESC LIMIT ?",
            (garden_id, limit)
        ).fetchall()
    else:
        alerts = conn.execute(
            "SELECT a.*, g.name as garden_name FROM weather_alerts a "
            "JOIN gardens g ON a.garden_id = g.id "
            "ORDER BY a.created_at DESC LIMIT ?",
            (limit,)
        ).fetchall()
    conn.close()
    return alerts


def get_alert_stats(garden_id=None):
    """获取预警统计数据"""
    conn = get_db()
    stats = {}

    # 总数
    if garden_id:
        total = conn.execute("SELECT COUNT(*) FROM weather_alerts WHERE garden_id = ?", (garden_id,)).fetchone()[0]
    else:
        total = conn.execute("SELECT COUNT(*) FROM weather_alerts").fetchone()[0]
    stats['total'] = total

    # 按级别统计
    if garden_id:
        by_level = conn.execute(
            "SELECT alert_level, COUNT(*) as cnt FROM weather_alerts WHERE garden_id = ? GROUP BY alert_level",
            (garden_id,)
        ).fetchall()
    else:
        by_level = conn.execute(
            "SELECT alert_level, COUNT(*) as cnt FROM weather_alerts GROUP BY alert_level"
        ).fetchall()
    stats['by_level'] = [{'level': r['alert_level'], 'count': r['cnt']} for r in by_level]

    # 按果园统计
    by_garden = conn.execute(
        "SELECT g.name as garden_name, COUNT(*) as cnt FROM weather_alerts a "
        "JOIN gardens g ON a.garden_id = g.id GROUP BY a.garden_id ORDER BY cnt DESC"
    ).fetchall()
    stats['by_garden'] = [{'garden_name': r['garden_name'], 'count': r['cnt']} for r in by_garden]

    # 按日期统计（最近30天）
    by_date = conn.execute(
        "SELECT DATE(created_at) as date, COUNT(*) as cnt FROM weather_alerts "
        "WHERE created_at >= date('now', '-30 days') GROUP BY DATE(created_at) ORDER BY date"
    ).fetchall()
    stats['by_date'] = [{'date': r['date'], 'count': r['cnt']} for r in by_date]

    conn.close()
    return stats


# ===== 用户自定义预警阈值 =====

def ensure_thresholds_table():
    """确保 user_thresholds 表存在"""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS user_thresholds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            temp_high REAL DEFAULT 35,
            temp_low REAL DEFAULT 5,
            humidity_high REAL DEFAULT 85,
            humidity_low REAL DEFAULT 40,
            wind_speed_high REAL DEFAULT 30,
            precipitation_high REAL DEFAULT 30,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    conn.commit()
    conn.close()


def get_user_thresholds(user_id):
    """获取用户自定义预警阈值"""
    conn = get_db()
    row = conn.execute("SELECT * FROM user_thresholds WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if row:
        return {
            'temp_high': row['temp_high'],
            'temp_low': row['temp_low'],
            'humidity_high': row['humidity_high'],
            'humidity_low': row['humidity_low'],
            'wind_speed_high': row['wind_speed_high'],
            'precipitation_high': row['precipitation_high']
        }
    return {
        'temp_high': 35,
        'temp_low': 5,
        'humidity_high': 85,
        'humidity_low': 40,
        'wind_speed_high': 30,
        'precipitation_high': 30
    }


def save_user_thresholds(user_id, data):
    """保存用户自定义预警阈值"""
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO user_thresholds (user_id, temp_high, temp_low, humidity_high, humidity_low, wind_speed_high, precipitation_high)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                temp_high=excluded.temp_high,
                temp_low=excluded.temp_low,
                humidity_high=excluded.humidity_high,
                humidity_low=excluded.humidity_low,
                wind_speed_high=excluded.wind_speed_high,
                precipitation_high=excluded.precipitation_high
        ''', (
            user_id,
            float(data.get('temp_high', 35)),
            float(data.get('temp_low', 5)),
            float(data.get('humidity_high', 85)),
            float(data.get('humidity_low', 40)),
            float(data.get('wind_speed_high', 30)),
            float(data.get('precipitation_high', 30))
        ))
        conn.commit()
        conn.close()
        return True, "阈值保存成功"
    except Exception as e:
        conn.close()
        return False, str(e)