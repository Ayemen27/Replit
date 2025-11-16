from flask import Flask, request
from flask_cors import CORS
from config import Config
from models import db
from auth import bcrypt, jwt
import os

def create_app(config_class=Config):
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static',
        static_url_path='/static'
    )
    app.config.from_object(config_class)

    CORS(app)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from routes import register_routes
    register_routes(app)

    # تهيئة قاعدة البيانات
    with app.app_context():
        db.create_all()
        print("✓ تم إنشاء جداول قاعدة البيانات")
        
        # إضافة البيانات التجريبية
        from seed_data import seed_database
        seed_database()

    @app.after_request
    def add_cache_headers(response):
        if request.path.startswith('/static/'):
            response.headers['Cache-Control'] = 'public, max-age=31536000'
        else:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response

    return app