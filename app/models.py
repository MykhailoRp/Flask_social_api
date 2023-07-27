from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from app import db
from app.utility import int_timestamp
from app.authentication import tokenizer

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    login = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='user', lazy='dynamic', cascade="all, delete")
    likes = db.relationship('Like', backref = 'user', lazy = 'dynamic', cascade="all, delete")
    tokens = db.relationship('Token', backref = 'user', lazy = 'dynamic', cascade="all, delete")
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    last_request = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.username}>'

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        return self.password_hash

    def log_request(self):
        self.last_request = datetime.utcnow()

    def login_account(self, login, password):
        if self.login == login and check_password_hash(self.password_hash, password):

            existing_token = self.tokens.first()

            if existing_token is not None:
                db.session.delete(existing_token)

            new_token = Token(
                token = self.__generate_token(),
                user_id = self.id
            )

            db.session.add(new_token)
            db.session.commit()

            self.last_login = datetime.utcnow()

            return new_token.token

        return None

    def __generate_token(self):
        return tokenizer.generate_token(self.id, self.password_hash)

    def dict(self):
        return {
            "username": self.username,
            "id": self.id,
        }

def expire_time(t = 36000):
    return int_timestamp() + t

class Token(db.Model):
    token = db.Column(db.String(128), primary_key = True, nullable = False)
    expires = db.Column(db.Integer, default=expire_time)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))

    def __repr__(self):
        return f'<Token {self.token}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    likes = db.relationship('Like', backref = 'post', lazy = 'dynamic', cascade="all, delete")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    content = db.Column(db.String(256))

    def __repr__(self):
        return f'<Post {self.id}>'

    def dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'likes': len(list(self.likes)),
            'author': self.user.dict(),
            'content': self.content,
        }

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.Integer, index=True, default=int_timestamp)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"))

    def __repr__(self):
        return f'<Like {self.timestamp}>'