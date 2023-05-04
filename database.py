import hashlib
import sqlite3

connection = sqlite3.connect(':memory:', check_same_thread=False)
cursor = connection.cursor()

def init_database():
    with open('schema.sql') as f:
        connection.executescript(f.read())

init_database()