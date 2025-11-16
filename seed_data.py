from models import db, User, Category, Project
from auth import hash_password
import os

def seed_database():
    # التحقق من وجود بيانات مسبقاً
    if Category.query.count() > 0:
        print("✓ البيانات موجودة مسبقاً")
        return

    categories_data = [
        {'name': 'تعليم', 'slug': 'education', 'description': 'تطبيقات تعليمية', 'icon': '📚'},
        {'name': 'ترفيه', 'slug': 'entertainment', 'description': 'تطبيقات ترفيهية', 'icon': '🎮'},
        {'name': 'إنتاجية', 'slug': 'productivity', 'description': 'أدوات الإنتاجية', 'icon': '⚡'},
        {'name': 'صحة ولياقة', 'slug': 'health-fitness', 'description': 'تطبيقات صحية', 'icon': '💪'},
        {'name': 'سفر', 'slug': 'travel', 'description': 'تطبيقات السفر', 'icon': '✈️'},
        {'name': 'مبيعات وتسويق', 'slug': 'marketing-sales', 'description': 'أدوات التسويق', 'icon': '📊'},
        {'name': 'عمليات', 'slug': 'operations', 'description': 'إدارة العمليات', 'icon': '⚙️'},
        {'name': 'أدوات المطورين', 'slug': 'developer-tools', 'description': 'أدوات التطوير', 'icon': '💻'},
    ]

    for cat_data in categories_data:
        category = Category(**cat_data)
        db.session.add(category)

    demo_user = User(
        email='demo@replit.com',
        username='demo',
        password_hash=hash_password('demo123'),
        first_name='Demo',
        last_name='User',
        is_active=True
    )
    db.session.add(demo_user)

    db.session.commit()

    education_cat = Category.query.filter_by(slug='education').first()

    demo_projects = [
        {
            'title': 'تطبيق تعليم الرياضيات',
            'slug': 'math-learning-app',
            'description': 'تطبيق تفاعلي لتعليم الرياضيات للأطفال',
            'image_url': 'https://via.placeholder.com/400x300',
            'is_featured': True,
            'is_published': True,
            'user_id': demo_user.id,
            'category_id': education_cat.id if education_cat else None
        },
        {
            'title': 'مدونة شخصية',
            'slug': 'personal-blog',
            'description': 'منصة للتدوين والكتابة',
            'image_url': 'https://via.placeholder.com/400x300',
            'is_featured': True,
            'is_published': True,
            'user_id': demo_user.id,
            'category_id': None
        }
    ]

    for proj_data in demo_projects:
        project = Project(**proj_data)
        db.session.add(project)

    db.session.commit()

    print("✅ تم إنشاء البيانات التجريبية بنجاح")