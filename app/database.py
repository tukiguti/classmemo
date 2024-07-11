import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('class_management.db')
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (email TEXT PRIMARY KEY, name TEXT, password TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS courses
                            (id INTEGER PRIMARY KEY, user_email TEXT, name TEXT, classroom TEXT, teacher TEXT, day TEXT, content TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS comments
                            (id INTEGER PRIMARY KEY, course_id INTEGER, user_email TEXT, content TEXT, timestamp TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS files
                            (id INTEGER PRIMARY KEY, course_id INTEGER, filename TEXT, filepath TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS events
                            (id INTEGER PRIMARY KEY, user_email TEXT, date TEXT, name TEXT, start_time TEXT, end_time TEXT)''')
        self.conn.commit()

    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetchone(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetchall(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()

    def fetchall(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()