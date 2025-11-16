from flask import Blueprint, request, jsonify, send_from_directory, render_template, abort
from models import db, User, Project, Category, FormSubmission
from auth import create_user, authenticate_user, generate_tokens, get_current_user, jwt_required_custom, admin_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import os

api = Blueprint('api', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
main_bp = Blueprint('main', __name__)

# معالج لطلبات Replit التي لا نحتاجها
@main_bp.route('/graphql', methods=['GET', 'POST'])
@main_bp.route('/data/user/exists', methods=['GET', 'POST'])
def ignore_replit_requests():
    """تجاهل طلبات Replit الداخلية"""
    return jsonify({'message': 'Not implemented'}), 200

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if not email or not username or not password:
        return jsonify({'error': 'جميع الحقول المطلوبة يجب ملؤها'}), 400

    user, error = create_user(email, username, password, first_name, last_name)

    if error:
        return jsonify({'error': error}), 400

    access_token, refresh_token = generate_tokens(user.id)

    return jsonify({
        'message': 'تم إنشاء الحساب بنجاح',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email_or_username = data.get('email_or_username')
    password = data.get('password')

    if not email_or_username or not password:
        return jsonify({'error': 'البريد الإلكتروني وكلمة المرور مطلوبان'}), 400

    user, error = authenticate_user(email_or_username, password)

    if error:
        return jsonify({'error': error}), 401

    access_token, refresh_token = generate_tokens(user.id)

    return jsonify({
        'message': 'تم تسجيل الدخول بنجاح',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user = get_current_user()
    if not user:
        return jsonify({'error': 'المستخدم غير موجود'}), 404
    return jsonify({'user': user.to_dict()}), 200


@api.route('/projects', methods=['GET'])
def get_projects():
    category_slug = request.args.get('category')
    is_featured = request.args.get('featured', '').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    query = Project.query.filter_by(is_published=True)

    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first()
        if category:
            query = query.filter_by(category_id=category.id)

    if is_featured:
        query = query.filter_by(is_featured=True)

    query = query.order_by(Project.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'projects': [project.to_dict() for project in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@api.route('/projects/<slug>', methods=['GET'])
def get_project(slug):
    project = Project.query.filter_by(slug=slug, is_published=True).first()

    if not project:
        return jsonify({'error': 'المشروع غير موجود'}), 404

    project.views_count += 1
    db.session.commit()

    return jsonify({'project': project.to_dict()}), 200


@api.route('/projects', methods=['POST'])
@jwt_required()
def create_project():
    user = get_current_user()

    if not user:
        return jsonify({'error': 'المستخدم غير موجود'}), 401

    data = request.get_json()

    title = data.get('title')
    slug = data.get('slug')
    description = data.get('description')

    if not title or not slug or not description:
        return jsonify({'error': 'العنوان والوصف مطلوبان'}), 400

    if Project.query.filter_by(slug=slug).first():
        return jsonify({'error': 'هذا العنوان مستخدم بالفعل'}), 400

    project = Project(
        title=title,
        slug=slug,
        description=description,
        image_url=data.get('image_url'),
        demo_url=data.get('demo_url'),
        repl_url=data.get('repl_url'),
        user_id=user.id,
        category_id=data.get('category_id'),
        is_published=data.get('is_published', False)
    )

    db.session.add(project)
    db.session.commit()

    return jsonify({
        'message': 'تم إنشاء المشروع بنجاح',
        'project': project.to_dict()
    }), 201


@api.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify({
        'categories': [category.to_dict() for category in categories]
    }), 200


@api.route('/forms/submit', methods=['POST'])
def submit_form():
    data = request.get_json()

    form_type = data.get('form_type')
    email = data.get('email')

    if not form_type or not email:
        return jsonify({'error': 'نوع النموذج والبريد الإلكتروني مطلوبان'}), 400

    submission = FormSubmission(
        form_type=form_type,
        name=data.get('name'),
        email=email,
        company=data.get('company'),
        message=data.get('message'),
        phone=data.get('phone'),
        extra_data=data.get('extra_data')
    )

    db.session.add(submission)
    db.session.commit()

    return jsonify({
        'message': 'تم إرسال النموذج بنجاح',
        'submission': submission.to_dict()
    }), 201


@main_bp.route('/')
def home():
    return send_from_directory('.', 'index.html')


@main_bp.route('/login')
def login_page():
    return render_template('pages/auth/login.html')


@main_bp.route('/signup')
def signup_page():
    return render_template('pages/auth/signup.html')


@main_bp.route('/dashboard')
def dashboard_page():
    return render_template('pages/dashboard.html')


@main_bp.route('/projects/create')
def create_project_page():
    return render_template('pages/projects/create.html')


@main_bp.route('/<path:path>')
def serve_static_pages(path):
    # إذا كان path ملف موجود مباشرة، قدمه
    if os.path.isfile(path):
        return send_from_directory('.', path)

    # إذا كان path.html موجود، قدمه
    html_path = path + '.html'
    if os.path.isfile(html_path):
        return send_from_directory('.', html_path)

    # إذا كان path/ مجلد، ابحث عن index.html داخله
    if os.path.isdir(path):
        index_path = os.path.join(path, 'index.html')
        if os.path.isfile(index_path):
            return send_from_directory('.', index_path)

    # fallback: أعد index.html الرئيسي
    # ملاحظة: المجلدات بدون index.html (مثل /products) ستعيد الصفحة الرئيسية
    # هذا سلوك مؤقت - يمكن تحسينه لاحقاً
    return send_from_directory('.', 'index.html')


def register_routes(app):
    app.register_blueprint(api)
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    @app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.now().year,
            'current_user': get_current_user() if hasattr(request, 'headers') and 'Authorization' in request.headers else None
        }