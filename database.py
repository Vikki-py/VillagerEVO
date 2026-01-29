# <-- БАЗА ДАННЫХ -->
import sqlite3
import os

class Database:
    def __init__(self, db_path='village.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.backup_database()
    
    def backup_database(self):
        if os.path.exists('village.db'):
            backup_path = 'village_backup.db'
            if os.path.exists(backup_path):
                os.remove(backup_path)
            os.system(f'cp village.db {backup_path}')
    
    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            nickname TEXT DEFAULT 'Игрок',
            villagers INTEGER DEFAULT 1,
            wood INTEGER DEFAULT 10,
            energy INTEGER DEFAULT 5,
            stone INTEGER DEFAULT 0,
            workers INTEGER DEFAULT 0,
            last_harvest TEXT,
            last_mine TEXT,
            village_level INTEGER DEFAULT 0,
            coins INTEGER DEFAULT 0,
            territory INTEGER DEFAULT 0,
            mine_repaired INTEGER DEFAULT 0,
            pickaxes INTEGER DEFAULT 0,
            mine_wood_workers INTEGER DEFAULT 0,
            mine_stone_workers INTEGER DEFAULT 0
        )
        ''')
        self.add_missing_columns()
        self.conn.commit()
    
    def add_missing_columns(self):
        columns = [
            ('nickname', 'TEXT DEFAULT "Игрок"'),
            ('stone', 'INTEGER DEFAULT 0'),
            ('last_mine', 'TEXT'),
            ('mine_repaired', 'INTEGER DEFAULT 0'),
            ('pickaxes', 'INTEGER DEFAULT 0'),
            ('mine_wood_workers', 'INTEGER DEFAULT 0'),
            ('mine_stone_workers', 'INTEGER DEFAULT 0')
        ]
        
        self.cursor.execute("PRAGMA table_info(users)")
        existing_columns = [col[1] for col in self.cursor.fetchall()]
        
        for col_name, col_type in columns:
            if col_name not in existing_columns:
                try:
                    self.cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                except:
                    pass
    
    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = self.cursor.fetchone()
        
        if not user:
            nickname = f"Игрок_{user_id}"
            self.cursor.execute('''
            INSERT INTO users (user_id, nickname) VALUES (?, ?)
            ''', (user_id, nickname))
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
        return True
    
    def close(self):
        self.conn.close()
