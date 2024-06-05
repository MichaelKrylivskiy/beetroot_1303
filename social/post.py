from datetime import datetime, timedelta
import pickle
import re
import bcrypt

class Content:
    def __init__(self):
        self.author = input("Enter nickname: ")
        self.text = input("Write your post: ")
        self.created_at = datetime.now()

    def __str__(self):
        return f"{self.author} said at {self.created_at}: {self.text}"

class Post(Content):
    entries = list()

    def __init__(self):
        super().__init__()
        self.entries.append(self)
        self.id = len(self.entries)
        self.likes = 0
        self.dislikes = 0

    def __str__(self):
        return (f"#{self.id} {self.author} said: {self.text}. "
                + f"Likes: {self.likes} | Dislikes: {self.dislikes}")

    def __eq__(self, other):
        if hasattr(other, "rating"):
            return self.rating == other.rating
        else:
            return NotImplemented

    def __lt__(self, other):
        return self.rating < other.rating

    def __le__(self, other):
        return self.rating <= other.rating

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.rating > other.rating

    def __ge__(self, other):
        return self.rating >= other.rating

    @staticmethod
    def week_ago():
        return datetime.now() - timedelta(days=7)

    @classmethod
    def show_last_week(cls):
        for entry in cls.entries:
            if entry.created_at > cls.week_ago():
                print(entry)

    @classmethod
    def show_posts(cls):
        for entry in sorted(cls.entries, reverse=True):
            print(entry)

    @classmethod
    def find_by_id(cls):
        post_id = input("Enter post id: ")
        for post in cls.entries:
            if post.id == int(post_id):
                return post

    @classmethod
    def like(cls):
        post = cls.find_by_id()
        post.likes += 1

    @classmethod
    def dislike(cls):
        post = cls.find_by_id()
        post.dislikes += 1

    @property
    def rating(self):
        return self.likes - self.dislikes

    @staticmethod
    def save_posts():
        with open("posts.pkl", "wb") as file:
            pickle.dump(Post.entries, file)

    @staticmethod
    def load_posts():
        try:
            with open("posts.pkl", "rb") as file:
                Post.entries = pickle.load(file)
        except FileNotFoundError:
            print("No saved posts found.")

class User:
    users = {}

    def __init__(self, username, password):
        self.username = username
        self.password_hash = self.hash_password(password)
        self.save_user()

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    @staticmethod
    def check_password(password, password_hash):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash)

    def save_user(self):
        User.users[self.username] = self.password_hash
        self.save_users_to_file()

    @staticmethod
    def save_users_to_file():
        with open("users.pkl", "wb") as file:
            pickle.dump(User.users, file)

    @staticmethod
    def load_users_from_file():
        try:
            with open("users.pkl", "rb") as file:
                User.users = pickle.load(file)
        except FileNotFoundError:
            print("No saved users found.")

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
        if username in cls.users:
            print("Username already exists.")
            return

        while True:
            password = input("Enter a strong password: ")
            if not cls.is_password_strong(password):
                print("Password is not strong enough.")
                continue
            confirm_password = input("Re-enter the password: ")
            if password == confirm_password:
                cls(username, password)
                print("User registered successfully.")
                break
            else:
                print("Passwords do not match.")

    @classmethod
    def authenticate_user(cls):
        username = input("Enter your login: ")
        if username not in cls.users:
            print("Username does not exist.")
            return False
        password = input("Enter your password: ")
        if cls.check_password(password, cls.users[username]):
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
    Post.load_posts()
    User.load_users_from_file()

    while True:
        print("Welcome to the new social")
        message = ("""
            Choose the option:
            1. Add post
            2. See all posts
            3. Like post
            4. Dislike post
            5. Save posts
            6. Load posts
            7. Register user
            8. Login
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
            Post.save_posts()
        elif choice == "6":
            Post.load_posts()
        elif choice == "7":
            User.register_user()
        elif choice == "8":
            User.authenticate_user()
        elif choice == "0":
            break
        else:
            print("Wrong choice")
