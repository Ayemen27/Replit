from functools import wraps
from flask import jsonify, request
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, get_jwt_identity, verify_jwt_in_request
from models import db, User

bcrypt = Bcrypt()
jwt = JWTManager()

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(password_hash, password):
    return bcrypt.check_password_hash(password_hash, password)

def create_user(email, username, password, first_name=None, last_name=None):
    if User.query.filter_by(email=email).first():
        return None, "البريد الإلكتروني مستخدم بالفعل"
    
    if User.query.filter_by(username=username).first():
        return None, "اسم المستخدم مستخدم بالفعل"
    
    user = User(
        email=email,
        username=username,
        password_hash=hash_password(password),
        first_name=first_name,
        last_name=last_name
    )
    
    db.session.add(user)
    db.session.commit()
    
    return user, None

def authenticate_user(email_or_username, password):
    user = User.query.filter(
        (User.email == email_or_username) | (User.username == email_or_username)
    ).first()
    
    if user and check_password(user.password_hash, password):
        if not user.is_active:
            return None, "الحساب غير مفعل"
        return user, None
    
    return None, "بيانات الدخول غير صحيحة"

def generate_tokens(user_id):
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    return access_token, refresh_token

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'يجب تسجيل الدخول أولاً'}), 401
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user = get_current_user()
            if not user or not user.is_admin:
                return jsonify({'error': 'غير مصرح لك بالوصول'}), 403
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'يجب تسجيل الدخول كمسؤول'}), 401
    return wrapper
