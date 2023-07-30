import sqlite3



class DataBase:
    def __init__(self,db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()
        self.create_table()

    def create_table(self):
        with self.connect:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    user_id INTEGER
                                )''')

    def user_exist(self,user_id):
        with self.connect:
            data = self.cursor.execute('''SELECT user_id FROM users WHERE user_id=(?)''',
                                [user_id]).fetchall()
            return data if data else False

    def add_user(self,user_id):
        with self.connect:
            return self.cursor.execute('''INSERT INTO users(user_id) VALUES (?)''',
                                       [user_id])