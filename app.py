from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import db, Project, Category # Assuming Project and Category are imported from models
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

    @app.route('/api/projects')
    def api_projects():
        """Get all projects with pagination"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 12, type=int)
            featured = request.args.get('featured', type=bool)

            query = Project.query

            if featured:
                query = query.filter_by(featured=True)

            pagination = query.paginate(page=page, per_page=per_page, error_out=False)

            projects_data = [{
                'id': p.id,
                'slug': p.slug,
                'title': p.title,
                'description': p.description,
                'image_url': p.image_url,
                'author': {'id': p.author.id, 'username': p.author.username} if p.author else None,
                'created_at': p.created_at.isoformat() if p.created_at else None
            } for p in pagination.items]

            return jsonify({
                'success': True,
                'projects': projects_data,
                'page': page,
                'pages': pagination.pages,
                'total': pagination.total
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'projects': [],
                'page': 1,
                'pages': 0,
                'total': 0
            }), 200

    @app.route('/api/categories')
    def api_categories():
        """Get all categories"""
        try:
            categories = Category.query.all()

            return jsonify({
                'success': True,
                'categories': [{
                    'id': c.id,
                    'slug': c.slug,
                    'name': c.name,
                    'description': c.description,
                    'icon': c.icon
                } for c in categories]
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'categories': []
            }), 200

    return app