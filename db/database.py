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
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

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


def save_diet_log(user_id, food_name, grams, calories, protein, carbs, fat):
    """保存一条饮食记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO diet_logs (user_id, date, food_name, grams, calories, protein, carbs, fat) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, datetime.now().strftime("%Y-%m-%d"), food_name, grams, calories, protein, carbs, fat),
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
