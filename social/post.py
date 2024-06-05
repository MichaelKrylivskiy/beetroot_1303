from datetime import datetime, timedelta
import sqlite3
import re
import bcrypt

# SQLite setup with custom datetime handling
def adapt_datetime(dt):
    return dt.isoformat()

def convert_datetime(dt_str):
    if isinstance(dt_str, str):
        return datetime.fromisoformat(dt_str)
    return dt_str  # If it's not a string, return it as-is

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("DATETIME", convert_datetime)

# Database setup
conn = sqlite3.connect('social.db', detect_types=sqlite3.PARSE_DECLTYPES)
c = conn.cursor()

# Create tables if they do not exist
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password_hash TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT,
    text TEXT,
    created_at DATETIME,
    likes INTEGER DEFAULT 0,
    dislikes INTEGER DEFAULT 0
)
''')

conn.commit()

class Content:
    def __init__(self):
        self.author = input("Enter nickname: ")
        self.text = input("Write your post: ")
        self.created_at = datetime.now()

    def __str__(self):
        return f"{self.author} said at {self.created_at}: {self.text}"

class Post(Content):
    def __init__(self):
        super().__init__()
        self.likes = 0
        self.dislikes = 0
        self.save_post()

    def save_post(self):
        c.execute('''
        INSERT INTO posts (author, text, created_at, likes, dislikes)
        VALUES (?, ?, ?, ?, ?)
        ''', (self.author, self.text, self.created_at, self.likes, self.dislikes))
        conn.commit()

    def __str__(self):
        return (f"#{self.id} {self.author} said: {self.text}. "
                + f"Likes: {self.likes} | Dislikes: {self.dislikes}")

    @classmethod
    def show_posts(cls):
        c.execute('SELECT * FROM posts ORDER BY id DESC')
        posts = c.fetchall()
        for post in posts:
            print(f"#{post[0]} {post[1]} said: {post[2]} at {post[3]}. Likes: {post[4]} | Dislikes: {post[5]}")

    @classmethod
    def find_by_id(cls, post_id):
        c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        post = c.fetchone()
        return post

    @classmethod
    def like(cls):
        post_id = input("Enter post id: ")
        post = cls.find_by_id(post_id)
        if post:
            c.execute('UPDATE posts SET likes = likes + 1 WHERE id = ?', (post_id,))
            conn.commit()
            print("Post liked.")
        else:
            print("Post not found.")

    @classmethod
    def dislike(cls):
        post_id = input("Enter post id: ")
        post = cls.find_by_id(post_id)
        if post:
            c.execute('UPDATE posts SET dislikes = dislikes + 1 WHERE id = ?', (post_id,))
            conn.commit()
            print("Post disliked.")
        else:
            print("Post not found.")

class User:
    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @staticmethod
    def check_password(password, password_hash):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash)

    @staticmethod
    def is_password_strong(password):
        if len(password) < 8:
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"\d", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    @classmethod
    def register_user(cls):
        username = input("Enter a unique login: ")
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        if c.fetchone():
            print("Username already exists.")
            return

        while True:
            password = input("Enter a strong password: ")
            if not cls.is_password_strong(password):
                print("Password is not strong enough.")
                continue
            confirm_password = input("Re-enter the password: ")
            if password == confirm_password:
                password_hash = cls.hash_password(password)
                c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
                conn.commit()
                print("User registered successfully.")
                break
            else:
                print("Passwords do not match.")

    @classmethod
    def authenticate_user(cls):
        username = input("Enter your login: ")
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        if not user:
            print("Username does not exist.")
            return False
        password = input("Enter your password: ")
        if cls.check_password(password, user[1]):
            print("Authentication successful.")
            return True
        else:
            print("Incorrect password.")
            return False

class Comment(Content):
    def __init__(self, post_id):
        super().__init__()
        self.post_id = post_id

    def __str__(self):
        return f"{self.author} commented on {self.post_id}: {self.text}"

if __name__ == "__main__":
    while True:
        print("Welcome to the new social")
        message = ("""
            Choose the option:
            1. Add post
            2. See all posts
            3. Like post
            4. Dislike post
            5. Register user
            6. Login
            0. Exit 

            Your Choice: """)
        choice = input(message)
        if choice == "1":
            Post()
        elif choice == "2":
            Post.show_posts()
        elif choice == "3":
            Post.like()
        elif choice == "4":
            Post.dislike()
        elif choice == "5":
            User.register_user()
        elif choice == "6":
            User.authenticate_user()
        elif choice == "0":
            break
        else:
            print("Wrong choice")

conn.close()
