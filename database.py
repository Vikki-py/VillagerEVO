# <-- БАЗА ДАННЫХ -->

import sqlite3

class Database:
    def __init__(self, db_path='village.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        self.upgrade_schema()
    
    def create_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            nickname TEXT UNIQUE,
            villagers INTEGER DEFAULT 1,
            wood INTEGER DEFAULT 10,
            energy INTEGER DEFAULT 5,  -- Изменено с 50 на 5
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
        self.conn.commit()
    
    def upgrade_schema(self):
        columns = []
        try:
            self.cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in self.cursor.fetchall()]
        except:
            pass
        
        add_columns = [
            ('energy', 'INTEGER DEFAULT 5'),
            ('stone', 'INTEGER DEFAULT 0'),
            ('last_mine', 'TEXT'),
            ('mine_repaired', 'INTEGER DEFAULT 0'),
            ('pickaxes', 'INTEGER DEFAULT 0'),
            ('mine_wood_workers', 'INTEGER DEFAULT 0'),
            ('mine_stone_workers', 'INTEGER DEFAULT 0')
        ]
        
        for col_name, col_type in add_columns:
            if col_name not in columns:
                try:
                    self.cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                except:
                    pass
        
        self.conn.commit()
    
    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = self.cursor.fetchone()
        if not user:
            nickname = f"Игрок_{user_id}"
            
            self.cursor.execute("SELECT COUNT(*) FROM users WHERE nickname = ?", (nickname,))
            count = self.cursor.fetchone()[0]
            
            counter = 1
            new_nickname = nickname
            while count > 0:
                new_nickname = f"{nickname}_{counter}"
                self.cursor.execute("SELECT COUNT(*) FROM users WHERE nickname = ?", (new_nickname,))
                count = self.cursor.fetchone()[0]
                counter += 1
            
            self.cursor.execute('''
            INSERT INTO users (user_id, username, nickname, villagers, wood, energy, stone, workers, 
                              village_level, coins, territory, mine_repaired, pickaxes, 
                              mine_wood_workers, mine_stone_workers) 
            VALUES (?, ?, ?, 1, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            ''', (user_id, '', new_nickname))
            self.conn.commit()
            return self.get_user(user_id)
        
        return user
    
    def update_user(self, user_id, **kwargs):
        set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        self.cursor.execute(f'UPDATE users SET {set_clause} WHERE user_id = ?', values)
        self.conn.commit()
    
    def update_nickname(self, user_id, nickname):
        try:
            self.cursor.execute('UPDATE users SET nickname = ? WHERE user_id = ?', (nickname, user_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return False
    
    def close(self):
        self.conn.close()
