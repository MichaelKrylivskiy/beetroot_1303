from datetime import datetime
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

# Check if the user_id column exists, if not add it
c.execute("PRAGMA table_info(posts)")
columns = [column[1] for column in c.fetchall()]
if 'user_id' not in columns:
    c.execute('ALTER TABLE posts ADD COLUMN user_id TEXT')
else:
    # Drop and recreate the posts table with the new schema
    c.execute('DROP TABLE IF EXISTS posts')
    c.execute('''
    CREATE TABLE posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT,
        text TEXT,
        created_at DATETIME,
        likes INTEGER DEFAULT 0,
        dislikes INTEGER DEFAULT 0,
        user_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users(username)
    )
    ''')

conn.commit()

class Content:
    def __init__(self, author):
        self.author = author
        self.text = input("Write your post: ")
        self.created_at = datetime.now()

    def __str__(self):
        return f"{self.author} said at {self.created_at}: {self.text}"

class Post(Content):
    entries = []

    def __init__(self, author):
        super().__init__(author)
        self.likes = 0
        self.dislikes = 0
        self.save_post()
        Post.entries.append(self)

    @property
    def rating(self):
        return self.likes - self.dislikes

    def save_post(self):
        c.execute('''
        INSERT INTO posts (author, text, created_at, likes, dislikes, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.author, self.text, self.created_at, self.likes, self.dislikes, self.author))
        self.id = c.lastrowid
        conn.commit()

    def __str__(self):
        return (f"#{self.id} {self.author} said: {self.text}. "
                + f"Likes: {self.likes} | Dislikes: {self.dislikes}")

    def __lt__(self, other):
        return self.rating < other.rating

    def __le__(self, other):
        return self.rating <= other.rating

    def __eq__(self, other):
        return self.rating == other.rating

    def __ne__(self, other):
        return self.rating != other.rating

    def __gt__(self, other):
        return self.rating > other.rating

    def __ge__(self, other):
        return self.rating >= other.rating

    @classmethod
    def show_posts(cls):
        for entry in sorted(cls.entries, reverse=True):
            print(entry)

    @classmethod
    def find_by_id(cls, post_id):
        c.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
        post = c.fetchone()
        return post

    @classmethod
    def like(cls):
        post_id = int(input("Enter post id: "))
        post = cls.find_by_id(post_id)
        if post:
            c.execute('UPDATE posts SET likes = likes + 1 WHERE id = ?', (post_id,))
            conn.commit()
            for entry in cls.entries:
                if entry.id == post_id:
                    entry.likes += 1
            print("Post liked.")
        else:
            print("Post not found.")

    @classmethod
    def dislike(cls):
        post_id = int(input("Enter post id: "))
        post = cls.find_by_id(post_id)
        if post:
            c.execute('UPDATE posts SET dislikes = dislikes + 1 WHERE id = ?', (post_id,))
            conn.commit()
            for entry in cls.entries:
                if entry.id == post_id:
                    entry.dislikes += 1
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
            return username  # Return the username if authentication is successful
        else:
            print("Incorrect password.")
            return False

class Comment(Content):
    def __init__(self, author, post_id):
        super().__init__(author)
        self.post_id = post_id

    def __str__(self):
        return f"{self.author} commented on {self.post_id}: {self.text}"

if __name__ == "__main__":
    logged_in_user = None

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
            if logged_in_user:
                Post(logged_in_user)
            else:
                print("You need to log in to add a post.")
        elif choice == "2":
            Post.show_posts()
        elif choice == "3":
            Post.like()
        elif choice == "4":
            Post.dislike()
        elif choice == "5":
            User.register_user()
        elif choice == "6":
            logged_in_user = User.authenticate_user()
        elif choice == "0":
            break
        else:
            print("Wrong choice")

conn.close()
