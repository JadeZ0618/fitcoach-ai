"""
数据库模块 - 使用 SQLite 存储用户数据

SQLite 是最简单的数据库——不需要安装服务器，数据就存在一个文件里。
对新手项目来说完全够用。

表结构：
- users: 用户身体数据（身高、体重、年龄等）
- diet_logs: 每日饮食记录
- weight_logs: 体重变化记录
"""

import sqlite3
import os
from datetime import datetime

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "fitcoach.db")


def get_connection():
    """获取数据库连接"""
    # 确保数据目录存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    """
    初始化数据库（创建表）
    如果表已经存在就跳过，不会删数据
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 用户表 - 存储身体数据
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            gender TEXT,
            age INTEGER,
            height REAL,
            weight REAL,
            activity_level TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 饮食记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diet_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            food_name TEXT,
            grams REAL,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            meal_type TEXT DEFAULT 'snack',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    # 兼容旧数据库：如果 diet_logs 表已存在但缺少 meal_type 列，自动补上
    try:
        cursor.execute("SELECT meal_type FROM diet_logs LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE diet_logs ADD COLUMN meal_type TEXT DEFAULT 'snack'")

    # 体重记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT,
            weight REAL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()


def save_user_profile(name, gender, age, height, weight, activity_level):
    """保存用户身体数据，返回 user_id"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, gender, age, height, weight, activity_level) VALUES (?, ?, ?, ?, ?, ?)",
        (name, gender, age, height, weight, activity_level),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_latest_user():
    """获取最新的用户数据（用于页面间共享）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row


def save_diet_log(user_id, food_name, grams, calories, protein, carbs, fat, meal_type="snack"):
    """保存一条饮食记录

    Args:
        meal_type: 餐次，可选 'breakfast' / 'lunch' / 'dinner' / 'snack'
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO diet_logs (user_id, date, food_name, grams, calories, protein, carbs, fat, meal_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, datetime.now().strftime("%Y-%m-%d"), food_name, grams, calories, protein, carbs, fat, meal_type),
    )
    conn.commit()
    conn.close()


def get_today_diet_logs(user_id):
    """获取今天的所有饮食记录"""
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT * FROM diet_logs WHERE user_id = ? AND date = ?", (user_id, today))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_meal_completion(user_id):
    """检查今日三餐打卡完成情况

    返回: dict，包含各餐是否已记录 + 完成率
        {
            'breakfast': bool,
            'lunch': bool,
            'dinner': bool,
            'completed_count': int,   # 已完成餐数 (0-3)
            'total_meals': 3,
            'all_done': bool,         # 三餐是否全部记录
        }
    """
    logs = get_today_diet_logs(user_id)
    # diet_logs 行结构: (id, user_id, date, food_name, grams, calories, protein, carbs, fat, meal_type)
    recorded_meals = set()
    for log in logs:
        # meal_type 在第 10 列（index 9）；兼容旧数据无 meal_type 的情况
        meal_type = log[9] if len(log) > 9 else "snack"
        recorded_meals.add(meal_type)

    breakfast_done = "breakfast" in recorded_meals
    lunch_done = "lunch" in recorded_meals
    dinner_done = "dinner" in recorded_meals
    completed = sum([breakfast_done, lunch_done, dinner_done])

    return {
        "breakfast": breakfast_done,
        "lunch": lunch_done,
        "dinner": dinner_done,
        "completed_count": completed,
        "total_meals": 3,
        "all_done": completed == 3,
    }


def get_diet_logs_by_date(user_id, date_str):
    """获取指定日期的饮食记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diet_logs WHERE user_id = ? AND date = ?", (user_id, date_str))
    rows = cursor.fetchall()
    conn.close()
    return rows


def save_weight_log(user_id, weight):
    """保存一条体重记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO weight_logs (user_id, date, weight) VALUES (?, ?, ?)",
        (user_id, datetime.now().strftime("%Y-%m-%d"), weight),
    )
    conn.commit()
    conn.close()


def get_weight_history(user_id):
    """获取体重历史记录（按日期排序）"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT date, weight FROM weight_logs WHERE user_id = ? ORDER BY date", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows
