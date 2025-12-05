import sqlite3
import json
from datetime import datetime

DATABASE = 'menu.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            is_preset INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            menu_data TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_all_dishes():
    conn = get_db_connection()
    dishes = conn.execute('SELECT * FROM dishes ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(dish) for dish in dishes]

def add_dish(name, category, is_preset=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO dishes (name, category, is_preset) VALUES (?, ?, ?)',
        (name, category, is_preset)
    )
    conn.commit()
    dish_id = cursor.lastrowid
    conn.close()
    return dish_id

def get_dishes_by_category(category):
    conn = get_db_connection()
    dishes = conn.execute(
        'SELECT * FROM dishes WHERE category = ?', (category,)
    ).fetchall()
    conn.close()
    return [dict(dish) for dish in dishes]

def add_favorite(menu_data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO favorites (menu_data) VALUES (?)',
        (json.dumps(menu_data, ensure_ascii=False),)
    )
    conn.commit()
    favorite_id = cursor.lastrowid
    conn.close()
    return favorite_id

def get_all_favorites():
    conn = get_db_connection()
    favorites = conn.execute('SELECT * FROM favorites ORDER BY created_at DESC').fetchall()
    conn.close()
    result = []
    for fav in favorites:
        fav_dict = dict(fav)
        fav_dict['menu_data'] = json.loads(fav_dict['menu_data'])
        result.append(fav_dict)
    return result

def delete_favorite(favorite_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM favorites WHERE id = ?', (favorite_id,))
    conn.commit()
    conn.close()
