import os
import base64
from datetime import datetime, timedelta
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

 # Michelle Chen rendition helped me here
 # https://stackoverflow.com/questions/28252103/sqlalchemy-lazy-dynamic-with-m2m-relationship-using-association-object-pattern

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')))
 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    token = db.Column(db.String(32), unique=True, index=True)
    token_expiration = db.Column(db.DateTime)
    recipe = db.relationship('Recipe', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.password = generate_password_hash(kwargs['password'])
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<User|{self.username}>"

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'date_created': self.date_created
        }

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(minutes=1):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.commit()
        return self.token

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, data):
        for field in data:
            if field not in {'username', 'email', 'password', 'is_admin', 'first_name'}:
                continue
            if field == 'password':
                setattr(self, field, generate_password_hash(data[field]))
            else:
                setattr(self, field, data[field])
        db.session.commit()
        
    def add_favorite(self, recipe):
        self.favorites.append(recipe)
        db.session.commit()

    def remove_favorite(self, recipe):
        self.favorites.remove(recipe)
        db.session.commit()

    def add_favorite(self, recipe):
        if recipe not in self.favorites:
            self.favorites.append(recipe)
            db.session.commit()

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    favorites = db.relationship('User', secondary=favorites, backref=db.backref('favorites', lazy='dynamic'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f"<Recipe {self.id}|{self.title}>"

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'date_created': self.date_created,
            'author': User.query.get(self.user_id).to_dict(), 
            # 'is_favorite': True if self.user_id in self.favorites else False
        }

    def update(self, data):
        for field in data:
            if field not in {'title', 'content', 'user_id'}:
                continue
            setattr(self, field, data[field])
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
