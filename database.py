# <-- БАЗА ДАННЫХ -->

import sqlite3

class Database:
    def __init__(self, db_path='village.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.upgrade_database()
    
    def upgrade_database(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            nickname TEXT,
            villagers INTEGER DEFAULT 1,
            wood INTEGER DEFAULT 10,
            energy INTEGER DEFAULT 5,
            workers INTEGER DEFAULT 0,
            last_harvest TEXT
        )
        ''')
    
        columns = [col[1] for col in self.cursor.execute("PRAGMA table_info(users)")]
    
        if 'nickname' not in columns:
            self.cursor.execute("ALTER TABLE users ADD COLUMN nickname TEXT")
    
        self.cursor.execute("UPDATE users SET nickname = 'Игрок_' || user_id WHERE nickname IS NULL OR nickname = ''")
    
        self.conn.commit()
    
    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = self.cursor.fetchone()
        if not user:
            nickname = f"Игрок_{user_id}"
            self.cursor.execute('''
            INSERT INTO users (user_id, username, nickname, villagers, wood, energy, workers) 
            VALUES (?, ?, ?, 1, 10, 50, 0)
            ''', (user_id, '', nickname))
            self.conn.commit()
            return self.get_user(user_id)
        
        return user
    
    def update_user(self, user_id, **kwargs):
        set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        self.cursor.execute(f'UPDATE users SET {set_clause} WHERE user_id = ?', values)
        self.conn.commit()
    
    def update_nickname(self, user_id, nickname):
        self.cursor.execute('UPDATE users SET nickname = ? WHERE user_id = ?', (nickname, user_id))
        self.conn.commit()
    
    def get_all_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()
    
    def close(self):
        self.conn.close()
