# <-- БАЗА ДАННЫХ -->

import sqlite3

class Database:
    def __init__(self, db_path='village.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_database()
    
    def init_database(self):
        try:
            self.cursor.execute('SELECT COUNT(*) FROM users')
        except:
            self.create_new_database()
            return
        
        columns = [col[1] for col in self.cursor.execute("PRAGMA table_info(users)")]
        
        if len(columns) < 9:
            self.migrate_to_levels(columns)
    
    def create_new_database(self):
        self.cursor.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            nickname TEXT UNIQUE,
            villagers INTEGER DEFAULT 1,
            wood INTEGER DEFAULT 10,
            energy INTEGER DEFAULT 50,
            workers INTEGER DEFAULT 0,
            last_harvest TEXT,
            village_level INTEGER DEFAULT 0
        )
        ''')
        self.conn.commit()
    
    def migrate_to_levels(self, old_columns):
        temp_table = '''
        CREATE TABLE users_new (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            nickname TEXT UNIQUE,
            villagers INTEGER DEFAULT 1,
            wood INTEGER DEFAULT 10,
            energy INTEGER DEFAULT 50,
            workers INTEGER DEFAULT 0,
            last_harvest TEXT,
            village_level INTEGER DEFAULT 0
        )
        '''
        
        self.cursor.execute('ALTER TABLE users RENAME TO users_old')
        self.cursor.execute(temp_table)
        
        old_cols_str = ', '.join(old_columns)
        self.cursor.execute(f'''
            INSERT INTO users_new ({old_cols_str})
            SELECT {old_cols_str} FROM users_old
        ''')
        
        self.cursor.execute('DROP TABLE users_old')
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
            INSERT INTO users (user_id, username, nickname, villagers, wood, energy, workers, village_level) 
            VALUES (?, ?, ?, 1, 10, 50, 0, 0)
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
