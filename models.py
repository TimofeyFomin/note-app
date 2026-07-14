import sqlite3
import hashlib
import secrets
from typing import Optional
from pydantic import ValidationError, BaseModel, Field
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()
def create_tables():
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY UNIQUE NOT NULL,
        name TEXT UNIQUE,
        password TEXT)'''
    )
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS notes
        (id INTEGER PRIMARY KEY UNIQUE NOT NULL,
        name TEXT,
        text TEXT,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)'''
    )
class User(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=150)
class Note(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    text: str
    user_id: int


def create_user(user:User) -> int:
    salt = secrets.token_hex(16)
    derived_key = hashlib.pbkdf2_hmac(hash_name="sha256", password=user.password.encode('utf-8'),
                                      salt=salt.encode('utf-8'), iterations=100_000).hex()
    password = salt + '$' + derived_key
    try:
        cursor.execute('''
        INSERT INTO users(name, password) VALUES(?, ?)''', (user.name, password))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return 0
def get_user(id:int) -> Optional[tuple]:
    cursor.execute('''
    SELECT name FROM users WHERE id = ?''', (id,))
    name = cursor.fetchone()
    return name
def create_note(note: Note) -> int:
    cursor.execute('''
    INSERT INTO notes(name, text, user_id) VALUES (?, ?, ?)''', (note.name, note.text, note.user_id))
    conn.commit()
    return cursor.lastrowid
def get_notes(user_id:int) -> Optional[list[tuple]]:
    cursor.execute('''
    SELECT id, name, text FROM notes WHERE user_id = ?''', (user_id,))
    notes = cursor.fetchall()
    return notes
def get_note(note_id: int) -> Optional[tuple]:
    cursor.execute('''
    SELECT name, text FROM notes WHERE id = ?''', (note_id,))
    note = cursor.fetchone()
    return note
def update_note(id: int, name: str, text: str) -> None:
    cursor.execute('''
    UPDATE notes SET name = ?, text = ? WHERE id = ?''', (name, text, id))
    conn.commit()
def delete_note(id: int) -> None:
    cursor.execute('''
    DELETE FROM notes WHERE id = ?''', (id,))


create_tables()

