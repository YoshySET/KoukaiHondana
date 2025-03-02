from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

# ユーザーと本の中間テーブル（所有関係）
user_books = db.Table('user_books',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('rating', db.Integer, nullable=True),
    db.Column('review', db.Text, nullable=True),
    db.Column('is_public', db.Boolean, default=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow),
    db.Column('updated_at', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
)

# フォロー関係のテーブル
followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 本との関連
    books = db.relationship('Book', secondary=user_books, backref=db.backref('users', lazy='dynamic'))
    
    # フォロー関係
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
    
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(64), unique=True, nullable=True)
    title = db.Column(db.String(200), nullable=False)
    authors = db.Column(db.String(200))
    publisher = db.Column(db.String(100))
    published_date = db.Column(db.String(20))
    description = db.Column(db.Text)
    isbn = db.Column(db.String(20))
    page_count = db.Column(db.Integer)
    categories = db.Column(db.String(100))
    thumbnail = db.Column(db.String(200))
    language = db.Column(db.String(10))
    
    def __repr__(self):
        return f'<Book {self.title}>' 