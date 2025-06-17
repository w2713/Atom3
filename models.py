from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User:
    def __init__(self, data):
        self.id = str(data['_id'])
        self.name = data.get('name', '')
        self.email = data.get('email', '')
        self.password = data.get('password', '')
        self.phone = data.get('phone', '')
        self.bio = data.get('bio', '')
        self.birthday = data.get('birthday', '')
        self.country = data.get('country', '')
        self.city = data.get('city', '')

    @staticmethod
    def create(name, email, password):
        return {
            'name': name,
            'email': email,
            'password': generate_password_hash(password),
            'created_at': datetime.utcnow()
        }

    @staticmethod
    def check_password(hashed_password, password):
        return check_password_hash(hashed_password, password)


class Card:
    def __init__(self, data):
        self.id = str(data['_id'])
        self.user_id = data['user_id']
        self.title = data['title']
        self.content = data['content']
        self.content_type = data['content_type']
        self.created_at = data['created_at']
        self.updated_at = data.get('updated_at', datetime.utcnow())

    @staticmethod
    def create(user_id, title, content, content_type):
        return {
            'user_id': user_id,
            'title': title,
            'content': content,
            'content_type': content_type,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }