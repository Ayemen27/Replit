from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from auth import bcrypt, jwt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    CORS(app)
    
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    with app.app_context():
        db.create_all()
        from seed_data import seed_database
        seed_database()
    
    from routes import register_routes
    register_routes(app)
    
    return app
