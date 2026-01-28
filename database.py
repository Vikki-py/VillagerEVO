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
        
        if len(columns) < 8:
            self.migrate_old_database(columns)
        elif 'nickname' not in columns:
            self.add_nickname_column()
        
        self.fix_nicknames()
        self.create_nickname_index()
    
    def create_nickname_index(self):
        self.cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_nickname ON users(nickname)')
        self.conn.commit()
    
    def create_new_database(self):
        self.cursor.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            nickname TEXT UNIQUE,
            villagers INTEGER DEFAULT 1,
            wood INTEGER DEFAULT 10,
            energy INTEGER DEFAULT 5,
            workers INTEGER DEFAULT 0,
            last_harvest TEXT
        )
        ''')
        self.conn.commit()
    
    def migrate_old_database(self, old_columns):
        temp_table = '''
        CREATE TABLE users_new (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            nickname TEXT UNIQUE,
            villagers INTEGER DEFAULT 1,
            wood INTEGER DEFAULT 10,
            energy INTEGER DEFAULT 5,
            workers INTEGER DEFAULT 0,
            last_harvest TEXT
        )
        '''
        
        self.cursor.execute('ALTER TABLE users RENAME TO users_old')
        self.cursor.execute(temp_table)
        
        column_map = {
            'user_id': 'user_id',
            'username': 'username',
            'villagers': 'villagers',
            'wood': 'wood', 
            'energy': 'energy',
            'workers': 'workers',
            'last_harvest': 'last_harvest'
        }
        
        select_cols = []
        insert_cols = []
        for old_col in old_columns:
            if old_col in column_map:
                select_cols.append(old_col)
                insert_cols.append(column_map[old_col])
        
        select_sql = f"SELECT {', '.join(select_cols)} FROM users_old"
        self.cursor.execute(select_sql)
        users = self.cursor.fetchall()
        
        used_nicknames = set()
        
        for user in users:
            user_id = user[0]
            base_nickname = f"Игрок_{user_id}"
            nickname = base_nickname
            
            counter = 1
            while nickname in used_nicknames:
                nickname = f"{base_nickname}_{counter}"
                counter += 1
            
            used_nicknames.add(nickname)
            new_values = list(user) + [nickname]
            
            placeholders = ', '.join(['?' for _ in range(len(new_values))])
            self.cursor.execute(f'''
                INSERT INTO users_new (user_id, username, villagers, wood, energy, workers, last_harvest, nickname)
                VALUES ({placeholders})
            ''', new_values)
        
        self.cursor.execute('DROP TABLE users_old')
        self.conn.commit()
    
    def add_nickname_column(self):
        try:
            self.cursor.execute("ALTER TABLE users ADD COLUMN nickname TEXT UNIQUE")
            self.fix_nicknames()
            self.conn.commit()
        except:
            pass
    
    def fix_nicknames(self):
        self.cursor.execute("SELECT user_id FROM users WHERE nickname IS NULL OR nickname = ''")
        users = self.cursor.fetchall()
        
        for (user_id,) in users:
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
            
            self.cursor.execute("UPDATE users SET nickname = ? WHERE user_id = ?", (new_nickname, user_id))
        
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
            INSERT INTO users (user_id, username, nickname, villagers, wood, energy, workers) 
            VALUES (?, ?, ?, 1, 10, 5, 0)
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
