# database.py
import sqlite3
import random

def init_db():
    conn = sqlite3.connect('store_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            password TEXT,
            balance REAL DEFAULT 0.0,
            language TEXT DEFAULT 'ar'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_ar TEXT,
            name_en TEXT,
            name_ru TEXT,
            price REAL,
            details_ar TEXT,
            details_en TEXT,
            details_ru TEXT
        )
    ''')
    
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ("سيرفر VIP", "VIP Server", "VIP Сервер", 20.0, "بيانات الدخول: user:pass_123", "Login data: user:pass_123", "Данные для входа: user:pass_123"),
            ("اشتراك شهري", "Monthly Subscription", "Месячная подписка", 15.0, "كود التفعيل: ABC-XYZ-789", "Activation code: ABC-XYZ-789", "Код активации: ABC-XYZ-789"),
            ("أداة تليجرام", "Telegram Tool", "Инструмент Telegram", 30.0, "رابط التحميل: https://example.com/tool", "Download link: https://example.com/tool", "Ссылка для скачивания: https://example.com/tool")
        ]
        cursor.executemany('''
            INSERT INTO products (name_ar, name_en, name_ru, price, details_ar, details_en, details_ru)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_products)
        
    conn.commit()
    conn.close()

def get_or_create_user(user_id):
    conn = sqlite3.connect('store_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password, balance, language FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        password = str(random.randint(1000, 9999))
        cursor.execute('INSERT INTO users (user_id, password, balance, language) VALUES (?, ?, ?, ?)', (user_id, password, 0.0, 'ar'))
        conn.commit()
        user = (password, 0.0, 'ar')
        
    conn.close()
    return {"password": user[0], "balance": user[1], "language": user[2]}

def update_user_language(user_id, lang):
    conn = sqlite3.connect('store_bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (lang, user_id))
    conn.commit()
    conn.close()

def update_balance(user_id, amount):
    conn = sqlite3.connect('store_bot.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect('store_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT product_id, name_ar, name_en, name_ru, price FROM products')
    products = cursor.fetchall()
    conn.close()
    return products

def get_product(product_id):
    conn = sqlite3.connect('store_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name_ar, name_en, name_ru, price, details_ar, details_en, details_ru FROM products WHERE product_id = ?', (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def add_product(name_ar, name_en, name_ru, price, details_ar, details_en, details_ru):
    conn = sqlite3.connect('store_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (name_ar, name_en, name_ru, price, details_ar, details_en, details_ru)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name_ar, name_en, name_ru, price, details_ar, details_en, details_ru))
    conn.commit()
    conn.close()
