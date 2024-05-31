from datetime import datetime, timedelta
import pickle


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


class Comment(Content):

    def __init__(self, post_id):
        super().__init__()
        self.post_id = post_id

    def __str__(self):
        return f"{self.author} commented on {self.post_id}: {self.text}"


if __name__ == "__main__":
    Post.load_posts()

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
        elif choice == "0":
            break
        else:
            print("Wrong choice")
